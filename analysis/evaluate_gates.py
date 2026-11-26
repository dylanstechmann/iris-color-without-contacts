#!/usr/bin/env python3
"""Phase-1 feasibility-gate evaluator.

Applies predeclared gate criteria from a JSON criteria file to facility-reported
gate data and emits mechanical pass/fail output with receipt discipline.
Malformed reports are rejected before any evaluation output is created.

Developed by AI assistant; owner-reviewed before interpretation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path


__version__ = "1.1.0"
REPORT_SCHEMA_VERSION = "1.1"
CRITERIA_SCHEMA_VERSION = "1.1"
DATA_KINDS = {"synthetic", "measured"}


class InputError(ValueError):
    """A criteria or facility-report input violates the declared schema."""


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _require_object(value, location: str) -> dict:
    if not isinstance(value, dict):
        raise InputError(f"{location} must be a JSON object")
    return value


def _exact_fields(value, required, *, optional=(), location: str) -> None:
    obj = _require_object(value, location)
    required = set(required)
    optional = set(optional)
    missing = sorted(required - obj.keys())
    unknown = sorted(obj.keys() - required - optional)
    if missing:
        raise InputError(f"{location} missing required field(s): {', '.join(missing)}")
    if unknown:
        raise InputError(f"{location} has unknown field(s): {', '.join(unknown)}")


def _require_text(value, location: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise InputError(f"{location} must be a non-empty string without surrounding whitespace")
    return value


def _require_number(value, location: str) -> None:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise InputError(f"{location} must be a finite JSON number (not a boolean or string)")


def _reject_nonfinite(value, location: str) -> None:
    if type(value) is float and not math.isfinite(value):
        raise InputError(f"{location} contains a non-finite number")
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_nonfinite(item, f"{location}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_nonfinite(item, f"{location}[{index}]")


def _load_json(path: Path):
    """Load JSON while rejecting duplicate keys and non-standard non-finite values."""
    def no_duplicate_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise InputError(f"{path}: duplicate field {key!r}")
            result[key] = value
        return result

    def no_nonfinite_constant(constant):
        raise InputError(f"{path}: non-finite JSON constant {constant!r} is not allowed")

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=no_duplicate_keys,
            parse_constant=no_nonfinite_constant,
        )
    except InputError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputError(f"cannot read valid JSON from {path}: {exc}") from exc
    _reject_nonfinite(value, str(path))
    return value


def validate_criteria(criteria: dict) -> None:
    """Validate the evaluator's predeclared criteria without changing thresholds."""
    _exact_fields(
        criteria, {"schema_version", "gates"},
        optional={"source", "data_kind", "notes"}, location="criteria",
    )
    if criteria["schema_version"] != CRITERIA_SCHEMA_VERSION:
        raise InputError(
            f"criteria.schema_version must be {CRITERIA_SCHEMA_VERSION!r}"
        )
    for field in ("source", "data_kind", "notes"):
        if field in criteria:
            _require_text(criteria[field], f"criteria.{field}")
    gates = _require_object(criteria["gates"], "criteria.gates")
    if not gates:
        raise InputError("criteria.gates must not be empty")

    for gate_id, gate_spec in gates.items():
        location = f"criteria.gates.{gate_id}"
        _exact_fields(
            gate_spec, {"name", "per_compound", "criteria"},
            optional={"fallback", "required_compounds", "compound"}, location=location,
        )
        _require_text(gate_spec["name"], f"{location}.name")
        if "fallback" in gate_spec:
            _require_text(gate_spec["fallback"], f"{location}.fallback")
        per_compound = gate_spec["per_compound"]
        if type(per_compound) is not bool:
            raise InputError(f"{location}.per_compound must be a JSON boolean")
        if per_compound:
            if "required_compounds" not in gate_spec:
                raise InputError(f"{location} missing required field(s): required_compounds")
            compounds = gate_spec["required_compounds"]
            if not isinstance(compounds, list) or not compounds:
                raise InputError(f"{location}.required_compounds must be a non-empty array")
            for index, compound in enumerate(compounds):
                _require_text(compound, f"{location}.required_compounds[{index}]")
            if len(set(compounds)) != len(compounds):
                raise InputError(f"{location}.required_compounds must not contain duplicates")
            if "compound" in gate_spec:
                raise InputError(f"{location}.compound is not valid for a per-compound gate")
        else:
            if "required_compounds" in gate_spec:
                raise InputError(f"{location}.required_compounds requires per_compound=true")
            if "compound" in gate_spec:
                _require_text(gate_spec["compound"], f"{location}.compound")

        criteria_specs = _require_object(gate_spec["criteria"], f"{location}.criteria")
        if not criteria_specs:
            raise InputError(f"{location}.criteria must not be empty")
        for criterion_id, cspec in criteria_specs.items():
            cloc = f"{location}.criteria.{criterion_id}"
            _exact_fields(
                cspec, {"comparator", "unit", "provenance", "status"},
                optional={"description", "target", "target_lo", "target_hi"}, location=cloc,
            )
            comparator = _require_text(cspec["comparator"], f"{cloc}.comparator")
            if comparator not in {"==", "<=", ">=", "<", ">", "range"}:
                raise InputError(f"{cloc}.comparator is unsupported: {comparator!r}")
            unit = _require_text(cspec["unit"], f"{cloc}.unit")
            _require_text(cspec["provenance"], f"{cloc}.provenance")
            if _require_text(cspec["status"], f"{cloc}.status") not in {"CONFIRMED", "PROPOSED"}:
                raise InputError(f"{cloc}.status must be CONFIRMED or PROPOSED")
            if "description" in cspec:
                _require_text(cspec["description"], f"{cloc}.description")

            if comparator == "range":
                if "target" in cspec:
                    raise InputError(f"{cloc}.target is ambiguous with range bounds")
                for field in ("target_lo", "target_hi"):
                    if field not in cspec:
                        raise InputError(f"{cloc} missing required field(s): {field}")
                    _require_number(cspec[field], f"{cloc}.{field}")
                if cspec["target_lo"] > cspec["target_hi"]:
                    raise InputError(f"{cloc} range lower bound exceeds upper bound")
                if unit == "boolean":
                    raise InputError(f"{cloc} boolean criteria only support ==")
            else:
                if "target" not in cspec:
                    raise InputError(f"{cloc} missing required field(s): target")
                if "target_lo" in cspec or "target_hi" in cspec:
                    raise InputError(f"{cloc} range bounds require comparator=range")
                target = cspec["target"]
                if unit == "boolean":
                    if comparator != "==" or type(target) is not bool:
                        raise InputError(f"{cloc} boolean criteria require == and a JSON boolean target")
                else:
                    _require_number(target, f"{cloc}.target")


def evaluate_value(observed, criterion: dict) -> tuple[str, str | None]:
    """Return (result, detail) without coercing booleans, strings, or non-finite numbers."""
    if observed is None:
        return "not_evaluable", "field value is null"

    comparator = criterion.get("comparator")
    target = criterion.get("target")
    target_lo = criterion.get("target_lo")
    target_hi = criterion.get("target_hi")
    boolean_criterion = criterion.get("unit") == "boolean" or type(target) is bool

    if boolean_criterion:
        if comparator != "==" or type(target) is not bool or type(observed) is not bool:
            return "not_evaluable", "boolean criterion and observation must both be JSON true or false"
        if observed is target:
            return "pass", None
        return "fail", f"observed={observed}, target={target}"

    if type(observed) not in (int, float) or not math.isfinite(observed):
        return "not_evaluable", "observed value must be a finite JSON number"
    targets = (target_lo, target_hi) if comparator == "range" else (target,)
    if any(type(value) not in (int, float) or not math.isfinite(value) for value in targets):
        return "not_evaluable", "criterion target must be a finite JSON number"

    if comparator == "==":
        result = observed == target
    elif comparator == "<=":
        result = observed <= target
    elif comparator == ">=":
        result = observed >= target
    elif comparator == "<":
        result = observed < target
    elif comparator == ">":
        result = observed > target
    elif comparator == "range":
        result = target_lo <= observed <= target_hi
    else:
        return "not_evaluable", f"unknown comparator {comparator}"

    if result:
        return "pass", None
    if comparator == "range":
        return "fail", f"observed={observed}, target_range=[{target_lo},{target_hi}]"
    return "fail", f"observed={observed}, target{comparator}{target}"


def _report_path(report_dir: Path, gate_id: str) -> Path | None:
    candidates = [report_dir / f"{gate_id}.json", report_dir / f"{gate_id}_report.json"]
    existing = [candidate for candidate in candidates if candidate.exists()]
    if len(existing) > 1:
        raise InputError(f"ambiguous reports for {gate_id}: both accepted filenames exist")
    return existing[0] if existing else None


def read_report(report_dir: Path, gate_id: str) -> dict:
    """Read one strict JSON gate report; an absent report remains not evaluable."""
    path = _report_path(report_dir, gate_id)
    return _load_json(path) if path is not None else {}


def _validate_observations(observations, criteria: dict, location: str) -> None:
    _exact_fields(observations, criteria.keys(), location=location)
    for criterion_id, cspec in criteria.items():
        oloc = f"{location}.{criterion_id}"
        observation = observations[criterion_id]
        _exact_fields(observation, {"value", "unit"}, location=oloc)
        if observation["unit"] != cspec["unit"]:
            raise InputError(
                f"{oloc}.unit must be {cspec['unit']!r}, got {observation['unit']!r}"
            )
        value = observation["value"]
        if value is None:
            continue
        if cspec["unit"] == "boolean":
            if type(value) is not bool:
                raise InputError(f"{oloc}.value must be JSON true or false, not a coercible value")
        else:
            _require_number(value, f"{oloc}.value")


def validate_report(report: dict, gate_id: str, gate_spec: dict) -> dict:
    """Validate one report and return its common run/provenance metadata."""
    per_compound = gate_spec["per_compound"]
    payload_field = "compounds" if per_compound else "observations"
    required = {
        "report_version", "gate_id", "facility_id", "run_id", "data_kind",
        "provenance", payload_field,
    }
    if not per_compound and "compound" in gate_spec:
        required.add("compound")
    _exact_fields(report, required, location=gate_id)

    if report["report_version"] != REPORT_SCHEMA_VERSION:
        raise InputError(f"{gate_id}.report_version must be {REPORT_SCHEMA_VERSION!r}")
    if report["gate_id"] != gate_id:
        raise InputError(f"{gate_id}.gate_id does not match its report filename")
    facility_id = _require_text(report["facility_id"], f"{gate_id}.facility_id")
    run_id = _require_text(report["run_id"], f"{gate_id}.run_id")
    data_kind = _require_text(report["data_kind"], f"{gate_id}.data_kind")
    if data_kind not in DATA_KINDS:
        raise InputError(f"{gate_id}.data_kind must be synthetic or measured")

    provenance = _require_object(report["provenance"], f"{gate_id}.provenance")
    expected_source = "facility_measurement" if data_kind == "measured" else "synthetic_fixture"
    if provenance.get("source_kind") != expected_source:
        raise InputError(
            f"{gate_id} provenance mismatch: data_kind={data_kind!r} requires "
            f"source_kind={expected_source!r}"
        )
    provenance_fields = {"source_kind", "source_reference"}
    if data_kind == "measured":
        provenance_fields.add("raw_data_reference")
    _exact_fields(provenance, provenance_fields, location=f"{gate_id}.provenance")
    _require_text(provenance["source_reference"], f"{gate_id}.provenance.source_reference")
    if data_kind == "measured":
        _require_text(provenance["raw_data_reference"], f"{gate_id}.provenance.raw_data_reference")

    if not per_compound and "compound" in gate_spec:
        if report["compound"] != gate_spec["compound"]:
            raise InputError(f"{gate_id}.compound must be {gate_spec['compound']!r}")

    criteria = gate_spec["criteria"]
    if per_compound:
        compounds = report["compounds"]
        _exact_fields(
            compounds, gate_spec["required_compounds"], location=f"{gate_id}.compounds",
        )
        for compound in gate_spec["required_compounds"]:
            _validate_observations(
                compounds[compound], criteria, f"{gate_id}.compounds.{compound}",
            )
    else:
        _validate_observations(report["observations"], criteria, f"{gate_id}.observations")

    return {"facility_id": facility_id, "run_id": run_id, "data_kind": data_kind}


def evaluate_gate(gate_id: str, gate_spec: dict, report: dict) -> dict:
    """Evaluate one already validated gate report and return per-criterion results."""
    per_compound = gate_spec.get("per_compound", False)
    criteria = gate_spec.get("criteria", {})
    results = {}

    if not report:
        for cid, cspec in criteria.items():
            results[cid] = {
                "criterion": cid,
                "observed": None,
                "result": "not_evaluable",
                "detail": "gate report missing",
                "threshold": _format_threshold(cspec),
                "status": cspec.get("status", ""),
            }
        return results

    if per_compound:
        compounds = report.get("compounds", {})
        for cid, cspec in criteria.items():
            for compound_name, compound_obs in compounds.items():
                key = f"{compound_name}:{cid}"
                obs = compound_obs.get(cid)
                if obs is None:
                    results[key] = {
                        "criterion": cid,
                        "compound": compound_name,
                        "observed": None,
                        "result": "not_evaluable",
                        "detail": "field missing in report",
                        "threshold": _format_threshold(cspec),
                        "status": cspec.get("status", ""),
                    }
                    continue
                observed = obs["value"] if isinstance(obs, dict) and "value" in obs else obs
                result, detail = evaluate_value(observed, cspec)
                results[key] = {
                    "criterion": cid,
                    "compound": compound_name,
                    "observed": observed,
                    "result": result,
                    "detail": detail,
                    "threshold": _format_threshold(cspec),
                    "status": cspec.get("status", ""),
                }
        if not compounds:
            for cid, cspec in criteria.items():
                results[cid] = {
                    "criterion": cid,
                    "observed": None,
                    "result": "not_evaluable",
                    "detail": "no compounds section in report",
                    "threshold": _format_threshold(cspec),
                    "status": cspec.get("status", ""),
                }
    else:
        observations = report.get("observations", {})
        for cid, cspec in criteria.items():
            obs = observations.get(cid)
            if obs is None:
                results[cid] = {
                    "criterion": cid,
                    "observed": None,
                    "result": "not_evaluable",
                    "detail": "field missing in report",
                    "threshold": _format_threshold(cspec),
                    "status": cspec.get("status", ""),
                }
                continue
            observed = obs["value"] if isinstance(obs, dict) and "value" in obs else obs
            result, detail = evaluate_value(observed, cspec)
            results[cid] = {
                "criterion": cid,
                "observed": observed,
                "result": result,
                "detail": detail,
                "threshold": _format_threshold(cspec),
                "status": cspec.get("status", ""),
            }
    return results


def _format_threshold(cspec: dict) -> str:
    comp = cspec["comparator"]
    if comp == "range":
        return f"{comp} [{cspec['target_lo']}, {cspec['target_hi']}] {cspec.get('unit','')}"
    if comp == "==":
        return f"== {cspec['target']} {cspec.get('unit','')}"
    return f"{comp} {cspec['target']} {cspec.get('unit','')}"


def generate_evaluation_report(eval_data: dict, criteria: dict) -> str:
    lines = [
        "# Feasibility Gate Evaluation Report",
        "",
        "**Status:** mechanical pass/fail on predeclared criteria; no feasibility verdict",
        "**Evaluator version:** {}".format(__version__),
        "**Data kind:** {}".format(eval_data["data_kind"]),
        "**Facility ID:** {}".format(eval_data["facility_id"]),
        "**Run ID:** {}".format(eval_data["run_id"]),
        "",
        "## Summary",
        "",
    ]

    total = 0
    passed = 0
    failed = 0
    not_eval = 0
    proposed_affected = []

    for gate_id, gate_eval in eval_data["gate_evaluations"].items():
        gate_name = criteria["gates"][gate_id]["name"]
        for key, res in gate_eval["results"].items():
            total += 1
            if res["result"] == "pass":
                passed += 1
            elif res["result"] == "fail":
                failed += 1
                if res.get("status") == "PROPOSED":
                    proposed_affected.append((gate_name, key, res))
            else:
                not_eval += 1
                if res.get("status") == "PROPOSED":
                    proposed_affected.append((gate_name, key, res))

    lines.append(f"- Total criteria evaluated: {total}")
    lines.append(f"- Passed: {passed}")
    lines.append(f"- Failed: {failed}")
    lines.append(f"- Not evaluable: {not_eval}")
    lines.append("")

    if failed > 0:
        lines.append("## Failures")
        lines.append("")
        for gate_id, gate_eval in eval_data["gate_evaluations"].items():
            gate_name = criteria["gates"][gate_id]["name"]
            gate_fails = [(k, r) for k, r in gate_eval["results"].items() if r["result"] == "fail"]
            if gate_fails:
                lines.append(f"### {gate_name}")
                lines.append("")
                for key, res in gate_fails:
                    prop = " **(PROPOSED threshold)**" if res.get("status") == "PROPOSED" else ""
                    lines.append(f"- **{key}**: FAIL{prop} — observed {res['observed']} vs {res['threshold']}")
                    if res.get("detail"):
                        lines.append(f"  - detail: {res['detail']}")
                lines.append("")

    if not_eval > 0:
        lines.append("## Not evaluable")
        lines.append("")
        for gate_id, gate_eval in eval_data["gate_evaluations"].items():
            gate_name = criteria["gates"][gate_id]["name"]
            gate_ne = [(k, r) for k, r in gate_eval["results"].items() if r["result"] == "not_evaluable"]
            if gate_ne:
                lines.append(f"### {gate_name}")
                lines.append("")
                for key, res in gate_ne:
                    lines.append(f"- **{key}**: NOT EVALUABLE — {res['detail']}")
                lines.append("")

    lines.append("## Per-gate details")
    lines.append("")
    for gate_id, gate_eval in eval_data["gate_evaluations"].items():
        gate_name = criteria["gates"][gate_id]["name"]
        gate_fails = [r for r in gate_eval["results"].values() if r["result"] == "fail"]
        gate_ne = [r for r in gate_eval["results"].values() if r["result"] == "not_evaluable"]
        status = "FAIL" if gate_fails or gate_ne else "PASS"
        lines.append(f"### {gate_name} — {status}")
        lines.append("")
        if gate_fails:
            lines.append("Failed criteria:")
            for res in gate_fails:
                prop = " **(PROPOSED)**" if res.get("status") == "PROPOSED" else ""
                lines.append(f"- {res['criterion']}{prop}: {res['observed']} vs {res['threshold']}")
            lines.append("")
        if gate_ne:
            lines.append("Not evaluable:")
            for res in gate_ne:
                lines.append(f"- {res['criterion']}: {res['detail']}")
            lines.append("")
        if not gate_fails and not gate_ne:
            lines.append("All criteria passed.")
            lines.append("")

    lines.append("## Criteria provenance")
    lines.append("")
    for gate_id, gate_spec in criteria["gates"].items():
        for cid, cspec in gate_spec["criteria"].items():
            prop = " **(PROPOSED)**" if cspec.get("status") == "PROPOSED" else ""
            lines.append(f"- `{cid}`{prop}: {cspec.get('provenance', 'unspecified')}")
    lines.append("")

    lines.append("## Limitations")
    lines.append("")
    lines.append("- This report is a mechanical application of predeclared thresholds to reported values, not a feasibility verdict.")
    lines.append("- No statistical inference, model fitting, or biological interpretation is performed.")
    lines.append("- Malformed reports are rejected; an entirely missing gate report is 'not evaluable', never silently passed.")
    lines.append("- Data kind is propagated from consistent schema/provenance declarations; references are not authenticated and do not establish biological or clinical validity.")
    lines.append("- Thresholds marked PROPOSED are awaiting owner confirmation.")
    lines.append("- Developed by AI assistant; owner-reviewed before interpretation.")
    lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase-1 feasibility-gate evaluator")
    parser.add_argument("--report", required=True, help="Directory containing gate-report JSON files")
    parser.add_argument("--criteria", required=True, help="Path to gate_criteria.json")
    parser.add_argument("--out", required=True, help="Output directory (must not exist)")
    args = parser.parse_args(argv)

    report_dir = Path(args.report)
    criteria_path = Path(args.criteria)
    out_dir = Path(args.out)

    if not report_dir.is_dir():
        print(f"ERROR: report directory does not exist: {report_dir}", file=sys.stderr)
        return 2
    if not criteria_path.is_file():
        print(f"ERROR: criteria file does not exist: {criteria_path}", file=sys.stderr)
        return 2
    if out_dir.exists():
        print(f"ERROR: output directory already exists: {out_dir}", file=sys.stderr)
        return 2

    try:
        criteria = _load_json(criteria_path)
        validate_criteria(criteria)
        gates = criteria["gates"]
        accepted_names = {
            filename
            for gate_id in gates
            for filename in (f"{gate_id}.json", f"{gate_id}_report.json")
        }
        unknown_files = sorted(
            path.name for path in report_dir.glob("*.json") if path.name not in accepted_names
        )
        if unknown_files:
            raise InputError(f"unknown gate report JSON file(s): {', '.join(unknown_files)}")

        reports = {}
        report_paths = {}
        metadata = []
        for gate_id, gate_spec in gates.items():
            path = _report_path(report_dir, gate_id)
            if path is None:
                reports[gate_id] = {}
                continue
            report = _load_json(path)
            metadata.append(validate_report(report, gate_id, gate_spec))
            reports[gate_id] = report
            report_paths[gate_id] = path
        if not metadata:
            raise InputError("no gate reports found; data_kind cannot be established")
        for field in ("facility_id", "run_id", "data_kind"):
            expected = metadata[0][field]
            if any(item[field] != expected for item in metadata[1:]):
                raise InputError(f"inconsistent run metadata across gate reports: {field}")

        eval_data = {
            "evaluator_version": __version__,
            "report_schema_version": REPORT_SCHEMA_VERSION,
            "data_kind": metadata[0]["data_kind"],
            "facility_id": metadata[0]["facility_id"],
            "run_id": metadata[0]["run_id"],
            "criteria_sha256": _sha256_file(criteria_path),
            "gate_evaluations": {},
        }
        input_hashes = {criteria_path.name: _sha256_file(criteria_path)}
        for gate_id, path in sorted(report_paths.items()):
            input_hashes[path.name] = _sha256_file(path)

        for gate_id, gate_spec in gates.items():
            results = evaluate_gate(gate_id, gate_spec, reports[gate_id])
            eval_data["gate_evaluations"][gate_id] = {
                "name": gate_spec["name"],
                "fallback": gate_spec.get("fallback", ""),
                "results": results,
            }
    except (InputError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True)

    ge_path = out_dir / "gate_evaluation.json"
    ge_text = json.dumps(eval_data, indent=2, allow_nan=False)
    ge_path.write_text(ge_text, encoding="utf-8")

    er_path = out_dir / "EVALUATION_REPORT.md"
    er_text = generate_evaluation_report(eval_data, criteria)
    er_path.write_text(er_text, encoding="utf-8")

    receipt = {
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "evaluator_version": __version__,
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "criteria_sha256": eval_data["criteria_sha256"],
        "inputs": input_hashes,
        "outputs": {
            "gate_evaluation.json": {
                "sha256": _sha256_file(ge_path),
                "bytes": ge_path.stat().st_size,
            },
            "EVALUATION_REPORT.md": {
                "sha256": _sha256_file(er_path),
                "bytes": er_path.stat().st_size,
            },
        },
        "command": f"python3 analysis/evaluate_gates.py --report {report_dir} --criteria {criteria_path} --out {out_dir}",
        "data_kind": eval_data["data_kind"],
        "facility_id": eval_data["facility_id"],
        "run_id": eval_data["run_id"],
    }
    receipt_path = out_dir / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False), encoding="utf-8")

    total = passed = failed = not_eval = 0
    for gate_eval in eval_data["gate_evaluations"].values():
        for res in gate_eval["results"].values():
            total += 1
            if res["result"] == "pass":
                passed += 1
            elif res["result"] == "fail":
                failed += 1
            else:
                not_eval += 1

    print(f"Evaluated {total} criteria: {passed} pass, {failed} fail, {not_eval} not evaluable")
    print(f"Output written to {out_dir}")
    return 0 if failed == 0 and not_eval == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

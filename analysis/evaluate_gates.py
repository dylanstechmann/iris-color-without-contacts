#!/usr/bin/env python3
"""Phase-1 feasibility-gate evaluator.

Applies predeclared gate criteria from a JSON criteria file to facility-reported
gate data and emits mechanical pass/fail output with receipt discipline.

Developed by AI assistant; owner-reviewed before interpretation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


__version__ = "1.0.0"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _sha256_text(text: str) -> str:
    h = hashlib.sha256()
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def evaluate_value(observed, criterion: dict) -> tuple[str, str | None]:
    """Return (result, detail) where result is 'pass', 'fail', or 'not_evaluable'."""
    if observed is None:
        return "not_evaluable", "field missing or null"

    comparator = criterion["comparator"]
    target = criterion.get("target")
    target_lo = criterion.get("target_lo")
    target_hi = criterion.get("target_hi")

    try:
        if comparator == "==":
            if bool(observed) == bool(target):
                return "pass", None
            return "fail", f"observed={observed}, target={target}"
        elif comparator == "<=":
            if observed <= target:
                return "pass", None
            return "fail", f"observed={observed}, target<={target}"
        elif comparator == ">=":
            if observed >= target:
                return "pass", None
            return "fail", f"observed={observed}, target>={target}"
        elif comparator == "<":
            if observed < target:
                return "pass", None
            return "fail", f"observed={observed}, target<{target}"
        elif comparator == ">":
            if observed > target:
                return "pass", None
            return "fail", f"observed={observed}, target>{target}"
        elif comparator == "range":
            if target_lo <= observed <= target_hi:
                return "pass", None
            return "fail", f"observed={observed}, target_range=[{target_lo},{target_hi}]"
        else:
            return "not_evaluable", f"unknown comparator {comparator}"
    except Exception as exc:
        return "not_evaluable", str(exc)


def read_report(report_dir: Path, gate_id: str) -> dict:
    """Read a gate report JSON from the report directory."""
    # Allow either gate_id.json or gate_id_report.json naming
    candidates = [
        report_dir / f"{gate_id}.json",
        report_dir / f"{gate_id}_report.json",
    ]
    for cand in candidates:
        if cand.exists():
            return json.loads(cand.read_text(encoding="utf-8"))
    # Return empty dict if no report file found — will produce "not_evaluable"
    return {}


def evaluate_gate(gate_id: str, gate_spec: dict, report: dict) -> dict:
    """Evaluate one gate and return per-criterion results."""
    per_compound = gate_spec.get("per_compound", False)
    criteria = gate_spec.get("criteria", {})
    results = {}

    if per_compound:
        # Report should have compound -> observations mapping under a key
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
                # Normalize: accept either direct value or {"value": ...}
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
            # No compounds reported at all
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
        "**Status:** mechanical pass/fail on predeclared criteria",
        "**Evaluator version:** {}".format(__version__),
        "**Data kind:** {}".format(eval_data["data_kind"]),
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
                    proposed_a.append((gate_name, key, res))
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
        if gate_fails or gate_ne:
            status = "FAIL"
        else:
            status = "PASS"
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
    lines.append("- This report is a mechanical application of predeclared thresholds to reported values.")
    lines.append("- No statistical inference, model fitting, or biological interpretation is performed.")
    lines.append("- Unknown or missing fields are reported as 'not evaluable', never silently passed.")
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
    if not criteria_path.exists():
        print(f"ERROR: criteria file does not exist: {criteria_path}", file=sys.stderr)
        return 2
    if out_dir.exists():
        print(f"ERROR: output directory already exists: {out_dir}", file=sys.stderr)
        return 2

    criteria = json.loads(criteria_path.read_text(encoding="utf-8"))

    # Validate criteria schema basics
    if "gates" not in criteria:
        print("ERROR: criteria file missing 'gates'", file=sys.stderr)
        return 2

    eval_data = {
        "evaluator_version": __version__,
        "data_kind": "synthetic",
        "criteria_sha256": _sha256_file(criteria_path),
        "gate_evaluations": {},
    }

    # Gather input file hashes for receipt
    input_hashes = {criteria_path.name: _sha256_file(criteria_path)}
    report_files = sorted(report_dir.glob("*.json"))
    for rf in report_files:
        input_hashes[rf.name] = _sha256_file(rf)

    for gate_id, gate_spec in criteria["gates"].items():
        report = read_report(report_dir, gate_id)
        results = evaluate_gate(gate_id, gate_spec, report)
        eval_data["gate_evaluations"][gate_id] = {
            "name": gate_spec["name"],
            "fallback": gate_spec.get("fallback", ""),
            "results": results,
        }

    out_dir.mkdir(parents=True)

    # Write gate_evaluation.json
    ge_path = out_dir / "gate_evaluation.json"
    ge_text = json.dumps(eval_data, indent=2)
    ge_path.write_text(ge_text, encoding="utf-8")

    # Write EVALUATION_REPORT.md
    er_path = out_dir / "EVALUATION_REPORT.md"
    er_text = generate_evaluation_report(eval_data, criteria)
    er_path.write_text(er_text, encoding="utf-8")

    # Write receipt.json
    receipt = {
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "evaluator_version": __version__,
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
        "data_kind": "synthetic",
    }
    receipt_path = out_dir / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    # Print short summary
    total = 0
    passed = 0
    failed = 0
    not_eval = 0
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

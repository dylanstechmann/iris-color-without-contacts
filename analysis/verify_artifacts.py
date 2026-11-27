"""Verify the selected computational artifact bytes; this is not scientific validation."""
import argparse
import hashlib
import json
from math import isfinite
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent
PAIRED_RECEIPT_SCHEMA = "washout-paired-design-simulation-receipt/2"
PAIRED_SOURCES = {"simulate_washout_design.py", "washout_design.py", "washout_model.py", "fit_washout.py"}
PAIRED_OUTPUTS = {"results.json", "MODEL_REPORT.md"}
NESTED_DESIGNS = (("full", "reduced"), ("full", "minimal"), ("reduced", "minimal"))
DECISION_FIELDS = (
    "half_time_ratio_below_proposed_threshold",
    "both_arms_day14_recovery_at_least_proposed_threshold",
    "both_proposed_conditions_met",
)


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def verify_paired_washout(folder, assumptions, *, source_root=ROOT):
    """Check the paired run's two outputs, frozen assumptions and four sources."""
    receipt = json.loads((folder / "receipt.json").read_text(encoding="utf-8-sig"))
    if not isinstance(receipt, dict) or receipt.get("schema_version") != PAIRED_RECEIPT_SCHEMA:
        raise ValueError("Expected a version 2 paired washout receipt.")
    sources = receipt.get("analysis_scripts")
    outputs = receipt.get("outputs")
    if not isinstance(sources, dict) or set(sources) != PAIRED_SOURCES:
        raise ValueError("Paired washout receipt must name all four runtime sources.")
    if not isinstance(outputs, dict) or set(outputs) != PAIRED_OUTPUTS:
        raise ValueError("Paired washout receipt must name both output files.")
    if receipt.get("script_sha256") != sources["simulate_washout_design.py"]:
        raise ValueError("Paired washout CLI hashes disagree in the receipt.")
    if digest(assumptions) != receipt.get("assumptions_sha256"):
        raise ValueError(f"Paired washout assumptions differ from the receipt: {assumptions}")
    for name, expected_hash in sorted(sources.items()):
        if digest(source_root / name) != expected_hash:
            raise ValueError(f"Paired washout source differs from the receipt: {name}")
    for name, spec in sorted(outputs.items()):
        path = (folder / name).resolve()
        if not path.is_relative_to(folder.resolve()):
            raise ValueError(f"Paired washout output points outside the run directory: {name}")
        if (not isinstance(spec, dict) or not path.is_file() or
                path.stat().st_size != spec.get("bytes") or digest(path) != spec.get("sha256")):
            raise ValueError(f"Paired washout output differs from the receipt: {name}")
    return {
        "run_directory": str(folder),
        "receipt_schema": PAIRED_RECEIPT_SCHEMA,
        "outputs_verified": len(outputs),
        "results_sha256": outputs["results.json"]["sha256"],
        "sources_verified": len(sources),
        "assumptions_verified": True,
        "scientific_validity": "not established by file hashes",
    }


def _paired_decisions(records):
    decisions = {}
    for record in records:
        system, replicate = record["system"], record["replicate"]
        if not isinstance(system, str) or not system or system.strip() != system:
            raise ValueError("Synthetic pair system must be a nonempty, unpadded string")
        if type(replicate) is not int or replicate < 0:
            raise ValueError("Synthetic pair replicate must be a nonnegative integer")
        key = (system, replicate)
        if key in decisions:
            raise ValueError(f"Duplicate synthetic pair: {key}")
        decision = record["decision"]
        if decision["status"] == "evaluable":
            ratio = decision.get("symmetric_half_time_ratio")
            if type(ratio) not in (int, float) or ratio < 1 or not isfinite(ratio):
                raise ValueError("Evaluable fits require a finite symmetric half-time ratio of at least one")
        decisions[key] = decision
    return decisions


def _condition_state(decision, field):
    if decision["status"] == "not_evaluable":
        return "not_evaluable"
    value = decision.get(field)
    if decision["status"] != "evaluable" or type(value) is not bool:
        raise ValueError(f"Invalid synthetic decision for {field}")
    return "met" if value else "unmet"


def _ratio_cutoff_sensitivity(ratios, cutoffs):
    """Describe strict ratio-only comparisons for the same evaluable pairs."""
    counts = []
    for cutoff in cutoffs:
        classifications = [(before < cutoff, after < cutoff) for _, before, after in ratios]
        counts.append({
            "cutoff": cutoff,
            "baseline_below": sum(before for before, _ in classifications),
            "nested_below": sum(after for _, after in classifications),
            "disagreements": sum(before != after for before, after in classifications),
        })
    windows = [
        {
            "system": system,
            "replicate": replicate,
            "baseline_ratio": before,
            "nested_ratio": after,
            "lower_exclusive": min(before, after),
            "upper_inclusive": max(before, after),
        }
        for (system, replicate), before, after in ratios
        if before != after
    ]
    return {"operator": "<", "counts": counts, "disagreement_windows": windows}


def _three_design_agreement(decisions, cutoffs):
    common = set.intersection(*(set(pairs) for pairs in decisions.values()))
    total_distinct_pairs = len(set().union(*decisions.values()))
    coverage = {
        design: {
            "observed_pairs": len(pairs),
            "absent_pairs": total_distinct_pairs - len(pairs),
            "observed_outside_match": len(pairs) - len(common),
        }
        for design, pairs in decisions.items()
    }
    ratios = []
    for key in sorted(common):
        fits = [pairs[key] for pairs in decisions.values()]
        if all(fit["status"] == "evaluable" for fit in fits):
            ratios.append([fit["symmetric_half_time_ratio"] for fit in fits])
    counts = []
    for cutoff in cutoffs:
        all_below = sum(max(values) < cutoff for values in ratios)
        all_at_or_above = sum(min(values) >= cutoff for values in ratios)
        counts.append({"cutoff": cutoff, "all_below": all_below, "all_at_or_above": all_at_or_above,
                       "designs_disagree": len(ratios) - all_below - all_at_or_above})
    return {"pairs_in_any_design": total_distinct_pairs, "coverage_by_design": coverage,
            "matched_pairs": len(common), "evaluable_in_all_three": len(ratios),
            "unevaluable_in_one_or_more": len(common) - len(ratios), "operator": "<", "counts": counts}


def compare_nested_designs(results, *, additional_cutoffs=()):
    """Compare proposed conditions over exact system/replicate matches per scenario."""
    if (results.get("schema_version") != "washout-paired-design-simulation/2"
            or results.get("data_kind") != "synthetic"):
        raise ValueError("Expected version 2 paired synthetic washout results.")
    proposed_cutoff = results["proposed_decision_metadata"]["symmetric_half_time_ratio"]["threshold"]
    cutoffs = sorted({proposed_cutoff - 0.01, proposed_cutoff, proposed_cutoff + 0.01, *additional_cutoffs})
    comparisons = []
    three_design_agreement = []
    for scenario in results["scenarios"]:
        decisions = {
            name: _paired_decisions(scenario["designs"][name]["records"])
            for name in ("full", "reduced", "minimal")
        }
        for baseline, nested in NESTED_DESIGNS:
            parent = decisions[baseline]
            child = decisions[nested]
            if not child or child.keys() - parent.keys():
                raise ValueError(f"Expected {nested} pairs nested in {baseline} for {scenario['name']}")
            matches = [(key, parent[key], child[key]) for key in sorted(child)]
            condition_counts = {}
            for field in DECISION_FIELDS:
                transitions = {}
                for _, before, after in matches:
                    label = f"{_condition_state(before, field)}_to_{_condition_state(after, field)}"
                    transitions[label] = transitions.get(label, 0) + 1
                condition_counts[field] = transitions
            ratios = [
                (key, before["symmetric_half_time_ratio"], after["symmetric_half_time_ratio"])
                for key, before, after in matches
                if before["status"] == after["status"] == "evaluable"
            ]
            changes = [abs(after - before) for _, before, after in ratios]
            comparisons.append({
                "scenario": scenario["name"],
                "true_synthetic_ratio": scenario["half_time_ratio"],
                "baseline_design": baseline,
                "nested_design": nested,
                "matched_pairs": len(matches),
                "baseline_only_pairs": len(parent) - len(matches),
                "ratio_change_evaluable_pairs": len(changes),
                "median_absolute_ratio_change": median(changes) if changes else None,
                "conditions": condition_counts,
                "ratio_only_cutoff_sensitivity": _ratio_cutoff_sensitivity(ratios, cutoffs),
            })
        three_design_agreement.append({"scenario": scenario["name"],
                                       **_three_design_agreement(decisions, cutoffs)})
    return {
        "interpretation": "descriptive matched synthetic fits per scenario",
        "three_design_ratio_agreement": three_design_agreement,
        "proposed_ratio_cutoff": proposed_cutoff,
        "comparisons": comparisons,
    }


def check():
    checked = 0
    for name, key in [
        ("feasibility-run-2026-10-17", "outputs"),
        ("exposure-run-2026-10-17", "outputs"),
        ("binding-benchmark-run-2026-10-17", "outputs"),
        ("ampyrone-data-run-2026-10-17", "outputs"),
        ("withdrawal-evidence-run-2026-10-17", "outputs"),
        ("recovery-identifiability-run-2026-10-17", "outputs"),
        ("kt939-comparison-run-2026-10-22", "outputs"),
        ("hue-window-run-2026-10-26-calibrated", "outputs"),
        ("iris-atlas-run-2026-10-17", "outputs"),
        ("workbench-comparison-2026-10-17", "files"),
        ("target-snapshots-2026-10-17", None),
    ]:
        folder = ROOT / name
        receipt = json.loads((folder / "receipt.json").read_text(encoding="utf-8-sig"))
        entries = ((row["file"], row) for row in receipt) if key is None else receipt[key].items()
        for relative, spec in entries:
            path = (folder / relative).resolve()
            if not path.is_relative_to(folder.resolve()):
                raise ValueError("Unexpected path outside receipt folder.")
            if not path.is_file() or path.stat().st_size != spec["bytes"] or digest(path) != spec["sha256"]:
                raise ValueError("Artifact mismatch: " + str(path))
            checked += 1
    model = json.loads((ROOT / "feasibility-run-2026-10-17" / "receipt.json").read_text())
    atlas = json.loads((ROOT / "iris-atlas-run-2026-10-17" / "receipt.json").read_text())
    if digest(ROOT / "simulate_feasibility.py") != model["script_sha256"]:
        raise ValueError("Model source differs from run receipt.")
    if digest(ROOT / "check_iris_targets.py") != atlas["script_sha256"]:
        raise ValueError("Iris analysis source differs from run receipt.")
    hue = json.loads((ROOT / "hue-window-run-2026-10-26-calibrated" / "receipt.json").read_text())
    if digest(ROOT / "simulate_hue_window.py") != hue["script_sha256"]:
        raise ValueError("Hue-window source differs from run receipt.")
    if json.loads((ROOT / "hue_window_assumptions.json").read_text()) != hue["assumptions"]:
        raise ValueError("Hue-window assumptions differ from run receipt.")
    for relative, spec in hue["inputs"].items():
        path = ROOT / relative
        if path.stat().st_size != spec["bytes"] or digest(path) != spec["sha256"]:
            raise ValueError("Hue-window input differs from run receipt: " + relative)
        checked += 1
    exposure = json.loads((ROOT / "exposure-run-2026-10-17" / "receipt.json").read_text())
    if digest(ROOT / "simulate_exposure.py") != exposure["script_sha256"]:
        raise ValueError("Exposure source differs from run receipt.")
    if json.loads((ROOT / "exposure_assumptions.json").read_text()) != exposure["assumptions"]:
        raise ValueError("Exposure assumptions differ from run receipt.")
    binding = json.loads((ROOT / "binding-benchmark-run-2026-10-17" / "receipt.json").read_text())
    if digest(ROOT / "build_binding_benchmark.py") != binding["script_sha256"]:
        raise ValueError("Binding benchmark source differs from run receipt.")
    if digest(ROOT / "binding_benchmark_inputs.json") != binding["input_sha256"]:
        raise ValueError("Binding benchmark inputs differ from run receipt.")
    ampyrone = json.loads((ROOT / "ampyrone-data-run-2026-10-17" / "receipt.json").read_text())
    for script, expected_hash in ampyrone["analysis_scripts"].items():
        if digest(ROOT / script) != expected_hash:
            raise ValueError("Ampyrone analysis source differs from receipt: " + script)
    for folder, script, input_file, input_key in [
        ("withdrawal-evidence-run-2026-10-17", "extract_withdrawal_evidence.py", "withdrawal_clinical_inputs.json", "clinical_inputs_sha256"),
        ("recovery-identifiability-run-2026-10-17", "demonstrate_recovery_identifiability.py", "recovery_identifiability_assumptions.json", "assumptions_sha256"),
    ]:
        run_receipt = json.loads((ROOT / folder / "receipt.json").read_text())
        if digest(ROOT / script) != run_receipt["script_sha256"] or digest(ROOT / input_file) != run_receipt[input_key]:
            raise ValueError("Recovery/withdrawal source or input differs from receipt: " + script)
    comparison = json.loads((ROOT / "kt939-comparison-run-2026-10-22" / "receipt.json").read_text())
    if digest(ROOT / "compare_kt939_thiamidol.py") != comparison["script_sha256"]:
        raise ValueError("KT-939 comparison script differs from run receipt.")
    reference = ROOT / "binding-benchmark-run-2026-10-17/pubchem/thiamidol.pubchem.json"
    if digest(reference) != comparison["reference_sha256"]:
        raise ValueError("KT-939 comparison reference differs from run receipt.")
    prior_sources = json.loads((ROOT / "withdrawal-evidence-run-2026-10-17/sources.json").read_text())
    if comparison["source_xml_sha256"] != next(row["sha256"] for row in prior_sources if row["file"] == "kt939.xml"):
        raise ValueError("KT-939 XML source hash differs from qualified withdrawal snapshot.")
    for name, receipt_name, script in [
        ("tyr-assay-audit-final-2026-10-17", "receipt.json", "audit_tyr_assays.py"),
        ("tyr-assay-audit-final-2026-10-17", "qualification_receipt.json", "qualify_tyr_records.py"),
        ("ip3r2-data-run-2026-10-17", "receipt.json", "extract_ip3r2_data.py"),
    ]:
        folder = ROOT / name
        receipt = json.loads((folder / receipt_name).read_text(encoding="utf-8"))
        entries = receipt["files"]
        if isinstance(entries, list):
            entries = {row["path"]: row for row in entries}
        for relative, spec in entries.items():
            path = (folder / relative).resolve()
            if not path.is_relative_to(folder.resolve()):
                raise ValueError("Unexpected path outside receipt folder.")
            if not path.is_file() or path.stat().st_size != spec["bytes"] or digest(path) != spec["sha256"]:
                raise ValueError("Artifact mismatch: " + str(path))
            checked += 1
        if digest(ROOT / script) != receipt["source_script_sha256"]:
            raise ValueError("Source differs from run receipt: " + script)
    print(json.dumps({"selected_artifacts_verified": checked, "analysis_scripts_match_receipts": True,
                      "scientific_validity": "not established by file hashes"}))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paired-washout", type=Path, metavar="RUN_DIR",
                        help="Verify one paired synthetic washout run")
    parser.add_argument("--assumptions", type=Path,
                        help="Assumptions file used for the paired washout run")
    parser.add_argument("--compare-nested", action="store_true",
                        help="Summarize matched changes between verified synthetic designs")
    parser.add_argument("--ratio-cutoff", type=float, action="append", default=[], metavar="RATIO",
                        help="Include an extra illustrative cutoff in the nested comparison (repeatable)")
    args = parser.parse_args(argv)
    if args.ratio_cutoff and not args.compare_nested:
        parser.error("--ratio-cutoff requires --compare-nested")
    if any(not isfinite(cutoff) or cutoff < 1 for cutoff in args.ratio_cutoff):
        parser.error("--ratio-cutoff must be finite and at least 1")
    if args.paired_washout is None:
        if args.assumptions is not None:
            parser.error("--assumptions requires --paired-washout")
        if args.compare_nested:
            parser.error("--compare-nested requires --paired-washout")
        check()
        return 0
    assumptions = args.assumptions or ROOT / "washout_design_assumptions.json"
    try:
        verified = verify_paired_washout(args.paired_washout, assumptions)
        if args.compare_nested:
            result_bytes = (args.paired_washout / "results.json").read_bytes()
            if hashlib.sha256(result_bytes).hexdigest() != verified["results_sha256"]:
                raise ValueError("Paired washout results changed after verification.")
            verified["nested_design_comparison"] = compare_nested_designs(
                json.loads(result_bytes), additional_cutoffs=args.ratio_cutoff,
            )
    except (KeyError, OSError, TypeError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")
    print(json.dumps(verified, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

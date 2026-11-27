#!/usr/bin/env python3
"""Run the paired generic synthetic KT-939/thiamidol G1 design simulation.

Usage:
    .venv/bin/python3 analysis/simulate_washout_design.py \
        --assumptions analysis/washout_design_assumptions.json \
        --out analysis/washout-paired-design-simulation-run-2026-11-15

The output path must not exist.  No real compounds, cells, donors, facilities,
or clinical/ocular endpoints are represented by this synthetic software run.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from washout_design import (
    ARM_NAMES,
    compare_no_isotope,
    fit_paired_experiment,
    generate_paired_experiment,
    json_safe,
    subset_paired_experiment,
    summarize_paired_records,
    validate_design_assumptions,
)
from washout_model import build_receipt, write_json


LIMITATIONS = [
    "All ground truths, system effects, pair effects, readouts, and noise are generic synthetic assumptions; neither arm is compound-calibrated.",
    "The ic50 inputs represent generic free-compound synthesis inhibition, never accumulated-pigment IC50 substitutions.",
    "The isotope old_fraction readout is mandatory for old/new pool identifiability; its recoverability is not an assay LOD measurement.",
    "MNT-1 is one represented reference cell-line system, not a donor and not evidence of donor or tissue generalizability.",
    "Synthetic donor/system multipliers are shared across arms but are not fitted with a donor mixed-effects model; fits are separate arm-level fits.",
    "Confidence intervals are legacy Jacobian-linearized parameter intervals and delta-method derived intervals; coverage is a descriptive synthetic diagnostic, not a guarantee.",
    "Within-system replicates are correlated and ratio scenarios/nested designs reuse random streams and observations. Record summaries are descriptive counts/fractions within one scenario/design only, with no independent-Bernoulli assumption, Wilson or other record-level inferential interval, decision probability, or scenario-pooled primary/control aggregate.",
    "The proposed ratio <1.5 and both-arm day-14 recovery >=0.80 metadata are unapproved simulation conditions, not go/no-go criteria or formal equivalence.",
    "No-isotope controls diagnose loss of old/new identifiability and never authorize dropping isotope from a candidate design.",
    "Nested reduced/minimal results share full-design observations; they do not establish biological sufficiency, cost effectiveness, owner adoption, or a preferred design.",
    "No ocular, clinical, safety, efficacy, procurement, facility-contact, spending, or gate-passage conclusion follows from this run.",
]


def _record_design(config: dict, name: str, system: str, system_index: int, replicate: int) -> dict:
    design = copy.deepcopy(config["designs"][name])
    design.update({
        "name": name, "system": system, "system_index": system_index,
        "replicate": replicate,
        "synthetic_ground_truths": config["synthetic_ground_truths"],
        "system_kinds": config["system_kinds"],
    })
    return design


def _generate_full(config: dict, scenario: dict) -> list:
    design = config["designs"]["full"]
    records = []
    for system_index, system in enumerate(design["systems"]):
        for replicate in range(design["replicates"]):
            record_design = _record_design(config, "full", system, system_index, replicate)
            records.append(generate_paired_experiment(
                record_design, scenario, config["noise_levels"], config["seeds"]["master"]
            ))
    return records


def _fit_all(raw_records: list, design: dict, config: dict, *, no_isotope=False) -> list:
    fit_design = copy.deepcopy(design)
    if no_isotope:
        fit_design["readout_flags"]["old_fraction"] = False
    return [fit_paired_experiment(record, fit_design, config) for record in raw_records]


def execute_simulation(config: dict) -> dict:
    """Run full grids and keep every summary within one scenario/design."""
    proposed = config["proposed_decision_metadata"]
    scenario_outputs = []
    for scenario in config["scenarios"]:
        full_raw = _generate_full(config, scenario)
        design_outputs = {}
        for name in ("full", "reduced", "minimal"):
            if name == "full":
                raw_records = full_raw
            else:
                selected = []
                for record in full_raw:
                    if record["system"] not in config["designs"][name]["systems"] or record["replicate"] >= config["designs"][name]["replicates"]:
                        continue
                    record_design = _record_design(
                        config, name, record["system"], record["system_index"], record["replicate"]
                    )
                    selected.append(subset_paired_experiment(record, record_design))
                raw_records = selected
            fitted = _fit_all(raw_records, config["designs"][name], config)
            control = _fit_all(raw_records, config["designs"][name], config, no_isotope=True)
            design_outputs[name] = {
                "system_accounting": copy.deepcopy(config["designs"][name]["system_accounting"]),
                "summary": summarize_paired_records(fitted, proposed),
                "records": fitted,
                "no_isotope_control": compare_no_isotope(fitted, control, proposed),
            }
        scenario_outputs.append({
            "name": scenario["name"], "half_time_ratio": scenario["half_time_ratio"],
            "designs": design_outputs,
        })
    return {
        "schema_version": "washout-paired-design-simulation/2",
        "date": config["date"], "data_kind": config["data_kind"],
        "calibration_status": config["calibration_status"],
        "ground_truth_semantics": copy.deepcopy(config["ground_truth_semantics"]),
        "synthetic_ground_truths": copy.deepcopy(config["synthetic_ground_truths"]),
        "scenario_ratio_definition": config["scenario_ratio_definition"],
        "designs": copy.deepcopy(config["designs"]),
        "system_kinds": copy.deepcopy(config["system_kinds"]),
        "isotope_readout": copy.deepcopy(config["isotope_readout"]),
        "seeds": copy.deepcopy(config["seeds"]),
        "noise_levels": copy.deepcopy(config["noise_levels"]),
        "proposed_decision_metadata": copy.deepcopy(proposed),
        "record_summary_semantics": "descriptive_matched_fit_counts_and_fractions_separately_within_each_scenario_design_no_independence_assumption_no_probability_intervals_no_scenario_pooling",
        "review_correction": "Regenerated after independent review removed invalid record-level Wilson intervals and scenario-mixed primary/control aggregates from the superseded development output; that output is not valid evidence.",
        "scenarios": scenario_outputs,
        "negative_controls": {
            "no_isotope": {
                "status": "diagnostic_only_isotope_remains_mandatory",
                "reporting": "matched_comparisons_nested_under_each_scenario_and_design_only",
            }
        },
        "limitations": LIMITATIONS,
    }


def _fraction(row: dict) -> str:
    if row["total"] == 0 or row["fraction"] is None:
        return f"NE (0/0; NE={row['not_evaluable']})"
    return f"{row['count']}/{row['total']} ({100 * row['fraction']:.1f}% descriptive)"


def _number(value, digits=3) -> str:
    return "NE" if value is None else f"{value:.{digits}f}"


def _coverage(row: dict) -> str:
    if row["n_intervals"] == 0:
        return "NE"
    return f"{row['covered']}/{row['n_intervals']}"


def build_model_report(results: dict) -> str:
    """Render only observed simulation output, without selecting a design."""
    lines = [
        "# Paired generic synthetic G1 washout-design simulation",
        "",
        "**Status:** AI-run synthetic software simulation; not biological validation.",
        f"**Date:** {results['date']}",
        "**Arms:** `KT-939_synthetic` and `thiamidol_synthetic` (generic labels, not calibrated compounds).",
        "",
        "The fullest grid was generated first. Reduced and minimal fits reused exact nested observations, common random numbers, and shared system/pair effects. No preferred design is selected.",
        "",
        "## Independent-review correction",
        "",
        "This run supersedes the earlier development output that incorrectly displayed record-level Wilson intervals and scenario-mixed no-isotope aggregates. Within-system replicates are correlated, scenario copies use common random numbers, and scenario-mixed records have no single probability meaning. The earlier intervals/aggregates are not valid evidence. This corrected run reports only descriptive matched-fit counts/fractions separately for each scenario/design and contains no scenario-pooled primary or control summary.",
        "",
        "## Proposed, unapproved decision metadata",
        "",
        "The simulated conditions are symmetric half-time ratio **<1.5** and both-arm day-14 synthesis recovery **>=0.80**. They are `proposed_not_owner_approved_not_go_no_go`; neither is a go/no-go criterion or formal equivalence test.",
        "",
        "## System and MNT-1 accounting",
        "",
        "| Design | Systems | Synthetic donors | Reference cell lines | MNT-1 represented | Replicates/system | Timepoints |",
        "| --- | ---: | ---: | ---: | --- | ---: | --- |",
    ]
    for name, design in results["designs"].items():
        account = design["system_accounting"]
        lines.append(
            f"| {name} | {account['system_count']} | {account['donor_count']} | {account['reference_cell_line_count']} | {str(account['mnt1_represented']).lower()} ({account['mnt1_count']}) | {design['replicates']} | {', '.join(str(t) for t in design['timepoints_days'])} |"
        )
    lines.extend([
        "",
        "MNT-1 is a single reference cell-line system, not a donor. Synthetic donor labels and multipliers do not establish donor-population inference.",
        "",
        "## Descriptive decision counts and fractions",
        "",
        "Each row describes only the matched fits for that one scenario/design. Fractions are observed record fractions, not independent-Bernoulli estimates, decision probabilities, or inferential intervals. `NE` means not evaluable and is never counted as zero or success. No rows are pooled across scenarios.",
        "",
        "| True ratio | Design | Pairs | Ratio <1.5 | Both recoveries >=0.80 | Both proposed conditions | Mean fitted ratio |",
        "| ---: | --- | ---: | --- | --- | --- | ---: |",
    ])
    for scenario in results["scenarios"]:
        for name, output in scenario["designs"].items():
            summary = output["summary"]
            decisions = summary["decision_counts"]
            lines.append(
                f"| {scenario['half_time_ratio']:.2f} | {name} | {summary['n_pairs']} | "
                f"{_fraction(decisions['half_time_ratio_below_proposed_threshold'])} | "
                f"{_fraction(decisions['both_arms_day14_recovery_at_least_proposed_threshold'])} | "
                f"{_fraction(decisions['both_proposed_conditions_met'])} | "
                f"{_number(summary['symmetric_half_time_ratio']['mean'])} |"
            )
    lines.extend([
        "",
        "## Day-14 recovery and fit/covariance failures",
        "",
        "| True ratio | Design | Arm | Mean day-14 recovery | Fit failures / pairs | Covariance failures / successful fits |",
        "| ---: | --- | --- | ---: | ---: | ---: |",
    ])
    for scenario in results["scenarios"]:
        for name, output in scenario["designs"].items():
            summary = output["summary"]
            for arm in ARM_NAMES:
                fit_failure = summary["fit_failures"][arm]
                cov_failure = summary["covariance_failures"][arm]
                lines.append(
                    f"| {scenario['half_time_ratio']:.2f} | {name} | {arm} | "
                    f"{_number(summary['day14_recovery'][arm]['mean'])} | "
                    f"{fit_failure['count']}/{fit_failure['total']} | "
                    f"{cov_failure['count']}/{cov_failure['total']} |"
                )
    lines.extend([
        "",
        "## Linearized CI diagnostics",
        "",
        "Coverage is the descriptive count/fraction of intervals containing the known synthetic truth within one scenario/design, including shared system/pair multipliers. It is not an estimated coverage probability or inferential interval. Widths are medians over available finite intervals. `k_c` uses the legacy parameter interval; day-14 recovery uses a delta-method interval. These are local linear approximations.",
        "",
        "| True ratio | Design | Arm | k_c coverage | k_c median width | Recovery coverage | Recovery median width |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: |",
    ])
    for scenario in results["scenarios"]:
        for name, output in scenario["designs"].items():
            summary = output["summary"]
            for arm in ARM_NAMES:
                k_c = summary["parameter_ci"][arm]["k_c"]
                recovery = summary["derived_metric_ci"][arm]["synthesis_recovery_day_14"]
                lines.append(
                    f"| {scenario['half_time_ratio']:.2f} | {name} | {arm} | {_coverage(k_c)} | "
                    f"{_number(k_c['median_width'], 5)} | {_coverage(recovery)} | {_number(recovery['median_width'], 5)} |"
                )
    lines.extend([
        "",
        "## Matched no-isotope negative controls by scenario/design",
        "",
        "Controls retain the generated isotope array but omit `old_fraction` only from the diagnostic fit. Each row compares primary/control fits matched on scenario, design, system, replicate, and observations. There is no scenario-mixed aggregate. A missing interval or width ratio is `NE`, not zero. This is an identifiability result, never an assay LOD estimate.",
        "",
        "| True ratio | Design | Arm | Pool | Isotope median CI width | No-isotope median CI width | Width ratio | No-isotope covariance failures / fits |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ])
    for scenario in results["scenarios"]:
        for name, output in scenario["designs"].items():
            comparison = output["no_isotope_control"]
            for arm in ARM_NAMES:
                for pool in ("m_old0", "m_new0"):
                    row = comparison["old_new_pool_ci_comparison"][arm][pool]
                    cov = comparison["no_isotope_summary"]["covariance_failures"][arm]
                    lines.append(
                        f"| {scenario['half_time_ratio']:.2f} | {name} | {arm} | {pool} | {_number(row['isotope_median_ci_width'], 5)} | "
                        f"{_number(row['no_isotope_median_ci_width'], 5)} | {_number(row['no_isotope_to_isotope_width_ratio'], 2)} | "
                        f"{cov['count']}/{cov['total']} |"
                    )
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in results["limitations"])
    lines.extend([
        "",
        "## Receipt",
        "",
        "`receipt.json` pins the frozen assumptions, CLI and reusable/legacy source hashes, software versions, deterministic seed hierarchy, scenarios, design accounting, proposed metadata, and output hashes. Hashes establish file identity only.",
        "",
    ])
    return "\n".join(lines)


def run(assumptions_path: Path, out: Path) -> None:
    """Execute and publish a fresh receipted output directory without overwrite."""
    if out.exists():
        raise FileExistsError(f"output path already exists; refusing overwrite: {out}")
    def invalid_constant(value):
        raise ValueError(f"nonfinite JSON constant is forbidden: {value}")
    config = json.loads(assumptions_path.read_text(encoding="utf-8"), parse_constant=invalid_constant)
    validate_design_assumptions(config)
    raw_results = execute_simulation(config)
    results, nonfinite_statuses = json_safe(raw_results)
    results["nonfinite_status"] = {
        "status": "nulls_present" if nonfinite_statuses else "all_values_finite_or_explicitly_not_evaluable",
        "values": nonfinite_statuses,
    }
    report = build_model_report(results)
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "results.json", results)
    (out / "MODEL_REPORT.md").write_text(report, encoding="utf-8")
    analysis_dir = Path(__file__).resolve().parent
    source_names = (
        "simulate_washout_design.py", "washout_design.py",
        "washout_model.py", "fit_washout.py",
    )
    analysis_scripts = {
        name: hashlib.sha256((analysis_dir / name).read_bytes()).hexdigest()
        for name in source_names
    }
    receipt = build_receipt(out, assumptions_path, Path(__file__), extra={
        "schema_version": "washout-paired-design-simulation-receipt/2",
        "record_summary_semantics": "descriptive_per_scenario_per_design_only_no_record_level_inference_no_scenario_pooling",
        "review_correction": "record_level_Wilson_intervals_and_scenario_mixed_aggregates_removed_superseded_output_not_valid_evidence",
        "data_kind": config["data_kind"],
        "calibration_status": config["calibration_status"],
        "analysis_scripts": analysis_scripts,
        "fit_primitive": "washout_model.fit_washout",
        "seeds": config["seeds"],
        "scenarios": config["scenarios"],
        "designs": config["designs"],
        "proposed_decision_metadata": config["proposed_decision_metadata"],
        "isotope_readout": config["isotope_readout"],
        "limitations": LIMITATIONS,
        "facility_contact": False, "spending": False, "wet_lab_work": False,
        "ocular_or_clinical_claims": False, "owner_design_adoption": False,
        "gate_passage": False,
    })
    write_json(out / "receipt.json", receipt)
    print(json.dumps({
        "output": str(out), "scenarios": len(results["scenarios"]),
        "designs": list(config["designs"]),
        "primary_pairs": sum(
            output["summary"]["n_pairs"]
            for scenario in results["scenarios"] for output in scenario["designs"].values()
        ),
        "nonfinite_nulls": len(nonfinite_statuses),
    }))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assumptions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="New output directory; existing paths are never overwritten")
    args = parser.parse_args(argv)
    try:
        run(args.assumptions, args.out)
    except (FileExistsError, ValueError, KeyError, OSError) as error:
        parser.exit(2, f"error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

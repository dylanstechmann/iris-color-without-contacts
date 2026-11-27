import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from verify_artifacts import DECISION_FIELDS, compare_nested_designs, digest, verify_paired_washout


class PairedReceiptTest(unittest.TestCase):
    def test_cli_reproduces_archive_cutoff_example(self):
        root = Path(__file__).resolve().parent
        output = subprocess.check_output([
            sys.executable, str(root / "verify_artifacts.py"),
            "--paired-washout", str(root / "washout-paired-design-simulation-run-2026-11-15"),
            "--compare-nested", "--ratio-cutoff", "1.497",
        ])
        report = json.loads(output)
        self.assertEqual((report["outputs_verified"], report["sources_verified"]), (2, 4))
        comparisons = report["nested_design_comparison"]["comparisons"]
        self.assertEqual(len(comparisons), 12)
        boundary = next(row for row in comparisons
                        if row["scenario"] == "ratio_1_50" and row["baseline_design"] == "full"
                        and row["nested_design"] == "minimal")
        self.assertEqual(boundary["matched_pairs"], 4)
        counts = {row["cutoff"]: row["disagreements"]
                  for row in boundary["ratio_only_cutoff_sensitivity"]["counts"]}
        self.assertEqual(counts, {1.49: 0, 1.497: 1, 1.5: 0, 1.51: 0})

    def test_nested_comparison_matches_pair_identity_and_preserves_not_evaluable(self):
        def fit(replicate, ratio):
            if ratio is None:
                decision = {"status": "not_evaluable"}
            else:
                decision = dict.fromkeys(DECISION_FIELDS, ratio < 1.50)
                decision.update(status="evaluable", symmetric_half_time_ratio=ratio)
            return {"system": "synthetic_donor", "replicate": replicate, "decision": decision}

        results = {
            "schema_version": "washout-paired-design-simulation/2", "data_kind": "synthetic",
            "proposed_decision_metadata": {"symmetric_half_time_ratio": {"threshold": 1.50}},
            "scenarios": [{
                "name": "ratio_1_50", "half_time_ratio": 1.50,
                "designs": {
                    "full": {"records": [fit(0, 1.25), fit(1, 1.75), fit(2, 1.0)]},
                    "reduced": {"records": [fit(1, None), fit(0, 1.50)]},
                    "minimal": {"records": [fit(0, 1.50)]},
                },
            }],
        }
        rows = compare_nested_designs(results, additional_cutoffs=[1.497, 1.50])["comparisons"]
        self.assertEqual(len(rows), 3)
        row = rows[0]
        self.assertEqual((row["matched_pairs"], row["baseline_only_pairs"]), (2, 1))
        self.assertEqual(row["conditions"][DECISION_FIELDS[0]], {"met_to_unmet": 1, "unmet_to_not_evaluable": 1})
        self.assertEqual((row["ratio_change_evaluable_pairs"], row["median_absolute_ratio_change"]), (1, 0.25))
        sensitivity = row["ratio_only_cutoff_sensitivity"]
        self.assertEqual(sensitivity["counts"], [
            {"cutoff": 1.49, "baseline_below": 1, "nested_below": 0, "disagreements": 1},
            {"cutoff": 1.497, "baseline_below": 1, "nested_below": 0, "disagreements": 1},
            {"cutoff": 1.50, "baseline_below": 1, "nested_below": 0, "disagreements": 1},
            {"cutoff": 1.51, "baseline_below": 1, "nested_below": 1, "disagreements": 0},
        ])
        self.assertEqual(sensitivity["disagreement_windows"], [{
            "system": "synthetic_donor", "replicate": 0,
            "baseline_ratio": 1.25, "nested_ratio": 1.50,
            "lower_exclusive": 1.25, "upper_inclusive": 1.50,
        }])
        for invalid in (float("nan"), float("inf"), True, 0.9):
            results["scenarios"][0]["designs"]["minimal"]["records"] = [fit(0, invalid)]
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "finite symmetric"):
                compare_nested_designs(results)
        results["scenarios"][0]["designs"]["minimal"]["records"] = [fit(2, 1.25)]
        with self.assertRaisesRegex(ValueError, "minimal pairs nested in reduced"):
            compare_nested_designs(results)

    def test_three_design_agreement_uses_only_common_pairs_and_preserves_missing_fits(self):
        def record(rep, ratio):
            decision = dict.fromkeys(DECISION_FIELDS, False)
            decision["status"] = "not_evaluable" if ratio is None else "evaluable"
            decision["symmetric_half_time_ratio"] = ratio
            return {"system": "fixture", "replicate": rep, "decision": decision}

        designs = {
            "full": [record(3, None), record(2, 1.4), record(1, 1.6), record(0, 1.4)],
            "reduced": [record(0, 1.4), record(1, None), record(2, 1.4)],
            "minimal": [record(1, 1.6), record(0, 1.5)],
        }
        result = compare_nested_designs({
            "schema_version": "washout-paired-design-simulation/2", "data_kind": "synthetic",
            "proposed_decision_metadata": {"symmetric_half_time_ratio": {"threshold": 1.5}},
            "scenarios": [{"name": "fixture", "half_time_ratio": 1.5,
                           "designs": {key: {"records": rows} for key, rows in designs.items()}}],
        }, additional_cutoffs=[1.4])
        report, = result["three_design_ratio_agreement"]
        self.assertEqual(report["pairs_in_any_design"], 4)
        self.assertEqual(report["coverage_by_design"], {
            "full": {"observed_pairs": 4, "absent_pairs": 0, "observed_outside_match": 2},
            "reduced": {"observed_pairs": 3, "absent_pairs": 1, "observed_outside_match": 1},
            "minimal": {"observed_pairs": 2, "absent_pairs": 2, "observed_outside_match": 0},
        })
        self.assertEqual((report["matched_pairs"], report["evaluable_in_all_three"],
                          report["unevaluable_in_one_or_more"]), (2, 1, 1))
        self.assertEqual([(row["cutoff"], row["all_below"], row["all_at_or_above"], row["designs_disagree"])
                          for row in report["counts"]],
                         [(1.4, 0, 1, 0), (1.49, 0, 0, 1), (1.50, 0, 0, 1), (1.51, 1, 0, 0)])

    def test_nested_comparisons_require_exact_synthetic_pair_identifiers(self):
        decision = dict.fromkeys(DECISION_FIELDS, True)
        decision.update(status="evaluable", symmetric_half_time_ratio=1.0)
        row = {"system": "fixture", "replicate": 0, "decision": decision}
        designs = {name: {"records": [row]} for name in ("full", "reduced", "minimal")}
        inputs = {
            "schema_version": "washout-paired-design-simulation/2", "data_kind": "synthetic",
            "proposed_decision_metadata": {"symmetric_half_time_ratio": {"threshold": 1.5}},
            "scenarios": [{"name": "fixture", "half_time_ratio": 1.5, "designs": designs}],
        }
        for field, value in (("replicate", False), ("replicate", 0.0), ("replicate", -1),
                             ("system", " fixture"), ("system", "")):
            with self.subTest(field=field, value=value):
                designs["minimal"] = {"records": [{**row, field: value}]}
                with self.assertRaisesRegex(ValueError, f"Synthetic pair {field}"):
                    compare_nested_designs(inputs)

    def test_verifies_complete_receipt_and_rejects_missing_or_tampered_output(self):
        with TemporaryDirectory() as tmp:
            source = Path(tmp)
            run = source / "run"
            run.mkdir()
            assumptions = source / "config.json"
            assumptions.write_text("{}", encoding="utf-8")
            sources = {}
            for name in ("simulate_washout_design.py", "washout_design.py", "washout_model.py", "fit_washout.py"):
                path = source / name
                path.write_text(name, encoding="utf-8")
                sources[name] = digest(path)
            outputs = {}
            for name in ("results.json", "MODEL_REPORT.md"):
                path = run / name
                path.write_text("example", encoding="utf-8")
                outputs[name] = {"bytes": path.stat().st_size, "sha256": digest(path)}
            receipt = {
                "schema_version": "washout-paired-design-simulation-receipt/2",
                "assumptions_sha256": digest(assumptions),
                "script_sha256": sources["simulate_washout_design.py"],
                "analysis_scripts": sources,
                "outputs": outputs,
            }
            receipt_path = run / "receipt.json"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            report = verify_paired_washout(run, assumptions, source_root=source)
            self.assertEqual((report["outputs_verified"], report["sources_verified"]), (2, 4))

            (run / "results.json").write_text("tamper!", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "output differs.*results.json"):
                verify_paired_washout(run, assumptions, source_root=source)

            del outputs["results.json"]
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must name both output files"):
                verify_paired_washout(run, assumptions, source_root=source)

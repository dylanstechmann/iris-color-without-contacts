"""Tests for the paired generic synthetic washout design simulation."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

import simulate_washout_design as cli
from washout_design import (
    ARM_NAMES,
    compound_half_time,
    fit_paired_experiment,
    generate_paired_experiment,
    json_safe,
    subset_paired_experiment,
    summarize_paired_records,
    symmetric_half_time_ratio,
    synthesis_recovery,
    validate_design_assumptions,
)
from washout_model import fit_washout as legacy_fit_washout, simulate_washout


ASSUMPTIONS_PATH = Path(__file__).parent / "washout_design_assumptions.json"
CONFIG = json.loads(ASSUMPTIONS_PATH.read_text(encoding="utf-8"))


def one_pair_design(name="full", timepoints=None):
    design = copy.deepcopy(CONFIG["designs"][name])
    design["systems"] = ["MNT-1"]
    design["system_accounting"] = {
        "system_count": 1, "donor_count": 0,
        "reference_cell_line_count": 1,
        "mnt1_represented": True, "mnt1_count": 1,
    }
    design["replicates"] = 1
    if timepoints is not None:
        design["timepoints_days"] = timepoints
    design["system"] = "MNT-1"
    design["system_index"] = 0
    design["replicate"] = 0
    design["synthetic_ground_truths"] = CONFIG["synthetic_ground_truths"]
    design["system_kinds"] = CONFIG["system_kinds"]
    return design


def generated(timepoints=None):
    return generate_paired_experiment(
        one_pair_design(timepoints=timepoints),
        CONFIG["scenarios"][0], CONFIG["noise_levels"],
        CONFIG["seeds"]["master"],
    )


def fake_fitted(ratio, recovery_a=0.9, recovery_b=0.9):
    k_a = 0.5
    k_b = k_a / ratio
    arms = {}
    for name, k_c, recovery in zip(ARM_NAMES, (k_a, k_b), (recovery_a, recovery_b)):
        params = {
            "c0": 0.0, "k_c": k_c, "m_old0": 0.6, "m_new0": 0.2,
            "k_old": 0.05, "k_new": 0.15, "s_max": 0.3,
            "ic50": 40.0,
        }
        arms[name] = {
            "status": "evaluable", "covariance_status": "not_evaluable",
            "parameters": params, "true_parameters": params,
            "confidence_intervals": {},
            "derived_metrics": {
                "compound_half_time_days": {"value": math.log(2) / k_c, "status": "evaluable"},
                "synthesis_recovery_day_14": {"value": recovery, "status": "evaluable"},
            },
            "true_metrics": {
                "compound_half_time_days": math.log(2) / k_c,
                "synthesis_recovery_day_14": recovery,
            },
        }
    return {"arms": arms}


class ValidationTests(unittest.TestCase):
    def test_frozen_config_is_valid_and_accounts_for_mnt1(self):
        validate_design_assumptions(CONFIG)
        self.assertEqual(CONFIG["designs"]["full"]["system_accounting"]["mnt1_count"], 1)
        self.assertEqual(CONFIG["designs"]["full"]["system_accounting"]["donor_count"], 2)

    def test_isotope_cannot_be_omitted(self):
        cfg = copy.deepcopy(CONFIG)
        cfg["designs"]["minimal"]["readout_flags"]["old_fraction"] = False
        with self.assertRaisesRegex(ValueError, "isotope"):
            validate_design_assumptions(cfg)

    def test_designs_must_be_nested(self):
        cfg = copy.deepcopy(CONFIG)
        cfg["designs"]["minimal"]["timepoints_days"] = [0, 2, 7, 14]
        with self.assertRaisesRegex(ValueError, "nested"):
            validate_design_assumptions(cfg)

    def test_nonfinite_and_ambiguous_config_rejected(self):
        cfg = copy.deepcopy(CONFIG)
        cfg["noise_levels"]["total_sd"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite"):
            validate_design_assumptions(cfg)
        cfg = copy.deepcopy(CONFIG)
        cfg["ground_truth_semantics"]["ic50"] = "accumulated_pigment_ic50"
        with self.assertRaisesRegex(ValueError, "free-compound"):
            validate_design_assumptions(cfg)

    def test_mnt1_accounting_must_match_systems(self):
        cfg = copy.deepcopy(CONFIG)
        cfg["designs"]["full"]["system_accounting"]["mnt1_count"] = 0
        with self.assertRaisesRegex(ValueError, "MNT-1"):
            validate_design_assumptions(cfg)


class MetricTests(unittest.TestCase):
    def test_derived_metrics_and_symmetry(self):
        a = {"k_c": 0.5, "c0": 100.0, "ic50": 50.0}
        b = {"k_c": 0.25, "c0": 100.0, "ic50": 50.0}
        self.assertAlmostEqual(compound_half_time(a), 2 * math.log(2))
        self.assertAlmostEqual(symmetric_half_time_ratio(a, b), 2.0)
        self.assertAlmostEqual(symmetric_half_time_ratio(a, b), symmetric_half_time_ratio(b, a))
        self.assertAlmostEqual(synthesis_recovery(a, 0), 1 / 3)

    def test_zero_washout_boundary(self):
        self.assertTrue(math.isinf(compound_half_time({"k_c": 0.0})))
        self.assertTrue(math.isinf(symmetric_half_time_ratio({"k_c": 0.0}, {"k_c": 1.0})))
        self.assertTrue(math.isnan(symmetric_half_time_ratio({"k_c": 0.0}, {"k_c": 0.0})))
        with self.assertRaises(ValueError):
            compound_half_time({"k_c": -1.0})

    def test_proposed_boundaries_are_strict_and_inclusive_as_declared(self):
        summary = summarize_paired_records([
            fake_fitted(1.5, 0.8, 0.8), fake_fitted(1.499, 0.799, 1.0),
        ])
        decisions = summary["decision_counts"]
        self.assertEqual(decisions["half_time_ratio_below_proposed_threshold"]["count"], 1)
        self.assertEqual(decisions["both_arms_day14_recovery_at_least_proposed_threshold"]["count"], 1)
        self.assertEqual(decisions["both_proposed_conditions_met"]["count"], 0)


def noiseless_config(*, include_effects):
    noise = copy.deepcopy(CONFIG["noise_levels"])
    for key in ("total_sd", "old_fraction_sd", "compound_sd", "cell_count_sd"):
        noise[key] = 0.0
    if not include_effects:
        noise["system_log_sd"] = {key: 0.0 for key in noise["system_log_sd"]}
        noise["pair_log_sd"] = {key: 0.0 for key in noise["pair_log_sd"]}
    return noise


class GenerationTests(unittest.TestCase):
    def test_noiseless_forward_truths_and_configured_ratio_are_realized(self):
        design = one_pair_design(timepoints=[0, 1, 3, 7, 14])
        scenario = CONFIG["scenarios"][-1]
        pair = generate_paired_experiment(
            design, scenario, noiseless_config(include_effects=False), CONFIG["seeds"]["master"]
        )
        realized_half_times = {}
        for arm in ARM_NAMES:
            expected = copy.deepcopy(CONFIG["synthetic_ground_truths"][arm])
            if arm == ARM_NAMES[1]:
                expected["k_c"] = CONFIG["synthetic_ground_truths"][ARM_NAMES[0]]["k_c"] / 2.0
            direct = simulate_washout(design["timepoints_days"], **expected, hill=1.0)
            data = pair["arms"][arm]["data"]
            np.testing.assert_allclose(data["total"], direct["total"], rtol=0, atol=1e-12)
            np.testing.assert_allclose(data["old_fraction"], direct["old_fraction"], rtol=0, atol=1e-12)
            np.testing.assert_allclose(data["compound"], direct["compound"], rtol=0, atol=1e-12)
            np.testing.assert_array_equal(data["cell_count"], np.ones(5))
            realized_k_c = -math.log(data["compound"][1] / data["compound"][0])
            self.assertAlmostEqual(realized_k_c, expected["k_c"], places=12)
            realized_half_times[arm] = math.log(2.0) / realized_k_c
        realized_ratio = max(realized_half_times.values()) / min(realized_half_times.values())
        self.assertAlmostEqual(realized_ratio, 2.0, places=12)

    def test_nonidentity_shared_arm_multipliers_are_realized_in_noiseless_data(self):
        design = one_pair_design(timepoints=[0, 1, 3, 7, 14])
        scenario = CONFIG["scenarios"][1]
        pair = generate_paired_experiment(
            design, scenario, noiseless_config(include_effects=True), CONFIG["seeds"]["master"]
        )
        multipliers = {
            key: pair["effects"]["system"][key] * pair["effects"]["pair"][key]
            for key in pair["effects"]["system"]
        }
        self.assertTrue(any(not math.isclose(value, 1.0) for value in multipliers.values()))
        realized_initial_multipliers = []
        for arm in ARM_NAMES:
            expected = copy.deepcopy(CONFIG["synthetic_ground_truths"][arm])
            if arm == ARM_NAMES[1]:
                expected["k_c"] /= scenario["half_time_ratio"]
            for key, multiplier in multipliers.items():
                expected[key] *= multiplier
            direct = simulate_washout(design["timepoints_days"], **expected, hill=1.0)
            data = pair["arms"][arm]["data"]
            np.testing.assert_allclose(data["total"], direct["total"], rtol=0, atol=1e-12)
            np.testing.assert_allclose(data["old_fraction"], direct["old_fraction"], rtol=0, atol=1e-12)
            baseline_initial = (
                CONFIG["synthetic_ground_truths"][arm]["m_old0"]
                + CONFIG["synthetic_ground_truths"][arm]["m_new0"]
            )
            expected_initial = (
                CONFIG["synthetic_ground_truths"][arm]["m_old0"] * multipliers["m_old0"]
                + CONFIG["synthetic_ground_truths"][arm]["m_new0"] * multipliers["m_new0"]
            )
            realized_initial_multipliers.append(data["total"][0] / baseline_initial)
            self.assertAlmostEqual(data["total"][0], expected_initial, places=12)
            self.assertEqual(pair["arms"][arm]["effects"]["system"], pair["effects"]["system"])
            self.assertEqual(pair["arms"][arm]["effects"]["pair"], pair["effects"]["pair"])
        self.assertAlmostEqual(realized_initial_multipliers[0], realized_initial_multipliers[1], places=12)

    def test_deterministic_labels_and_fit_compatible_arrays(self):
        a = generated()
        b = generated()
        self.assertEqual(set(a["arms"]), set(ARM_NAMES))
        for arm in ARM_NAMES:
            for key in ("time", "total", "old_fraction", "compound", "cell_count"):
                np.testing.assert_array_equal(a["arms"][arm]["data"][key], b["arms"][arm]["data"][key])
            self.assertEqual(len(a["arms"][arm]["data"]["time"]), 9)

    def test_shared_system_and_pair_effects_across_arms(self):
        pair = generated()
        self.assertEqual(pair["effects"]["system"], pair["arms"][ARM_NAMES[0]]["effects"]["system"])
        self.assertEqual(pair["effects"]["system"], pair["arms"][ARM_NAMES[1]]["effects"]["system"])
        self.assertEqual(pair["effects"]["pair"], pair["arms"][ARM_NAMES[0]]["effects"]["pair"])
        self.assertEqual(pair["effects"]["pair"], pair["arms"][ARM_NAMES[1]]["effects"]["pair"])

    def test_common_random_numbers_across_ratio_scenarios(self):
        second = generate_paired_experiment(
            one_pair_design(), CONFIG["scenarios"][-1],
            CONFIG["noise_levels"], CONFIG["seeds"]["master"],
        )
        first = generated()
        for arm in ARM_NAMES:
            np.testing.assert_array_equal(
                first["arms"][arm]["noise"]["shared_total"],
                second["arms"][arm]["noise"]["shared_total"],
            )
            np.testing.assert_array_equal(
                first["arms"][arm]["noise"]["independent_total"],
                second["arms"][arm]["noise"]["independent_total"],
            )

    def test_nested_subset_reuses_exact_observations(self):
        full = generated()
        design = one_pair_design("reduced")
        reduced = subset_paired_experiment(full, design)
        indices = [0, 2, 4, 7, 8]
        for arm in ARM_NAMES:
            for key in ("time", "total", "old_fraction", "compound", "cell_count"):
                np.testing.assert_array_equal(
                    reduced["arms"][arm]["data"][key],
                    full["arms"][arm]["data"][key][indices],
                )
            self.assertEqual(reduced["arms"][arm]["true_parameters"], full["arms"][arm]["true_parameters"])


class FittingTests(unittest.TestCase):
    def test_each_arm_uses_existing_fitter_independently(self):
        pair = generated([0, 1, 3, 7, 14])
        with mock.patch("washout_design.fit_washout", wraps=legacy_fit_washout) as fitter:
            fitted = fit_paired_experiment(pair, one_pair_design(timepoints=[0, 1, 3, 7, 14]), CONFIG)
        self.assertEqual(fitter.call_count, 2)
        self.assertEqual({r["status"] for r in fitted["arms"].values()}, {"evaluable"})

    def test_one_arm_failed_one_succeeded_makes_pair_decision_not_evaluable(self):
        pair = generated([0, 1, 3, 7, 14])
        calls = {"n": 0}
        def fail_first_only(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("injected one-arm failure")
            return legacy_fit_washout(*args, **kwargs)
        with mock.patch("washout_design.fit_washout", side_effect=fail_first_only):
            fitted = fit_paired_experiment(pair, one_pair_design(timepoints=[0, 1, 3, 7, 14]), CONFIG)
        self.assertEqual(fitted["arms"][ARM_NAMES[0]]["status"], "not_evaluable")
        self.assertEqual(fitted["arms"][ARM_NAMES[1]]["status"], "evaluable")
        self.assertEqual(fitted["decision"]["status"], "not_evaluable")
        summary = summarize_paired_records([fitted])
        decision = summary["decision_counts"]["both_proposed_conditions_met"]
        self.assertEqual((decision["count"], decision["total"], decision["not_evaluable"]), (0, 0, 1))
        self.assertIsNone(decision["fraction"])
        self.assertEqual(summary["fit_failures"][ARM_NAMES[0]]["count"], 1)
        self.assertEqual(summary["fit_failures"][ARM_NAMES[1]]["count"], 0)

    def test_failed_arms_are_not_evaluable_without_numeric_estimates(self):
        pair = generated([0, 1, 3, 7, 14])
        with mock.patch("washout_design.fit_washout", side_effect=RuntimeError("injected failure")):
            fitted = fit_paired_experiment(pair, one_pair_design(timepoints=[0, 1, 3, 7, 14]), CONFIG)
        for arm in fitted["arms"].values():
            self.assertEqual(arm["status"], "not_evaluable")
            self.assertIsNone(arm["parameters"])
            self.assertEqual(arm["failure"]["type"], "RuntimeError")
        self.assertEqual(fitted["decision"]["status"], "not_evaluable")
        summary = summarize_paired_records([fitted])
        self.assertEqual(summary["decision_counts"]["both_proposed_conditions_met"]["total"], 0)
        self.assertEqual(summary["decision_counts"]["both_proposed_conditions_met"]["not_evaluable"], 1)

    def test_covariance_failure_does_not_fabricate_intervals(self):
        pair = generated([0, 1, 3, 7, 14])
        def no_cov(*args, **kwargs):
            result = legacy_fit_washout(*args, **kwargs)
            result["cov_success"] = False
            result["cov"] = None
            result["confidence_intervals"] = {"note": "injected covariance failure"}
            return result
        with mock.patch("washout_design.fit_washout", side_effect=no_cov):
            fitted = fit_paired_experiment(pair, one_pair_design(timepoints=[0, 1, 3, 7, 14]), CONFIG)
        for arm in fitted["arms"].values():
            self.assertEqual(arm["status"], "evaluable")
            self.assertEqual(arm["covariance_status"], "not_evaluable")
            self.assertIsNone(arm["derived_metrics"]["compound_half_time_days"]["ci95_lower"])

    def test_no_isotope_control_retains_data_but_omits_it_from_fit(self):
        pair = generated([0, 1, 3, 7, 14])
        design = one_pair_design(timepoints=[0, 1, 3, 7, 14])
        design["readout_flags"]["old_fraction"] = False
        fitted = fit_paired_experiment(pair, design, CONFIG)
        for name in ARM_NAMES:
            self.assertIn("old_fraction", pair["arms"][name]["data"])
            self.assertFalse(fitted["arms"][name]["readout_flags"]["old_fraction"])
            self.assertIn("cannot be separated", " ".join(fitted["arms"][name]["identifiability_notes"]))

    def test_summary_has_recovery_failures_and_ci_diagnostics(self):
        pair = generated([0, 1, 3, 7, 14])
        fitted = fit_paired_experiment(pair, one_pair_design(timepoints=[0, 1, 3, 7, 14]), CONFIG)
        summary = summarize_paired_records([fitted])
        self.assertIn("day14_recovery", summary)
        self.assertIn("fit_failures", summary)
        self.assertIn("covariance_failures", summary)
        self.assertIn("parameter_ci", summary)
        self.assertIn("derived_metric_ci", summary)


RUNTIME_SOURCE_NAMES = {
    "simulate_washout_design.py", "washout_design.py", "washout_model.py", "fit_washout.py"
}


def verify_receipt_artifacts(out: Path, assumptions: Path) -> dict:
    """Read-only independent hash verification for generated or saved runs."""
    analysis_dir = Path(__file__).resolve().parent
    receipt = json.loads((out / "receipt.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(assumptions.read_bytes()).hexdigest() == receipt["assumptions_sha256"]
    assert set(receipt["analysis_scripts"]) == RUNTIME_SOURCE_NAMES
    for name in RUNTIME_SOURCE_NAMES:
        digest = hashlib.sha256((analysis_dir / name).read_bytes()).hexdigest()
        assert receipt["analysis_scripts"][name] == digest, name
    script_digest = hashlib.sha256((analysis_dir / "simulate_washout_design.py").read_bytes()).hexdigest()
    assert receipt["script_sha256"] == script_digest
    for name, spec in receipt["outputs"].items():
        path = out / name
        assert path.parent == out and path.is_file()
        payload = path.read_bytes()
        assert len(payload) == spec["bytes"]
        assert hashlib.sha256(payload).hexdigest() == spec["sha256"]
    results = json.loads((out / "results.json").read_text(encoding="utf-8"))
    assert results["schema_version"] == "washout-paired-design-simulation/2"
    for scenario in results["scenarios"]:
        for output in scenario["designs"].values():
            summary = output["summary"]
            assert "summary_semantics" in summary
            for row in summary["decision_counts"].values():
                assert set(row) == {"count", "total", "not_evaluable", "fraction", "status", "interpretation"}
            comparison = output["no_isotope_control"]
            assert comparison["primary_summary"]["n_pairs"] == summary["n_pairs"]
            assert "no_scenario_pooling" in comparison["matching"]
    serialized = json.dumps(results)
    assert "wilson_95_interval" not in serialized
    assert "matched_aggregate" not in serialized
    return {"outputs": len(receipt["outputs"]), "sources": len(RUNTIME_SOURCE_NAMES) + 1}


class OutputTests(unittest.TestCase):
    def small_config(self):
        cfg = copy.deepcopy(CONFIG)
        times = {
            "full": [0, 3, 7, 14],
            "reduced": [0, 3, 7, 14],
            "minimal": [0, 7, 14],
        }
        for name, design in cfg["designs"].items():
            design["systems"] = ["MNT-1"]
            design["replicates"] = 1
            design["timepoints_days"] = times[name]
            design["system_accounting"].update({
                "system_count": 1, "donor_count": 0,
                "reference_cell_line_count": 1,
                "mnt1_represented": True, "mnt1_count": 1,
            })
        return cfg

    def test_json_nonfinite_values_have_status(self):
        safe, statuses = json_safe({"a": float("nan"), "b": [float("inf")]})
        self.assertIsNone(safe["a"])
        self.assertIsNone(safe["b"][0])
        self.assertEqual(len(statuses), 2)
        json.dumps(safe, allow_nan=False)

    def test_small_end_to_end_hashes_and_no_overwrite(self):
        cfg = self.small_config()
        with tempfile.TemporaryDirectory() as tmp:
            assumptions = Path(tmp) / "assumptions.json"
            out = Path(tmp) / "run"
            assumptions.write_text(json.dumps(cfg), encoding="utf-8")
            cli.run(assumptions, out)
            results = json.loads((out / "results.json").read_text())
            receipt = json.loads((out / "receipt.json").read_text())
            self.assertEqual(results["data_kind"], "synthetic")
            self.assertEqual(len(results["scenarios"]), 4)
            self.assertEqual(set(results["scenarios"][0]["designs"]), {"full", "reduced", "minimal"})
            self.assertIn("no_isotope", results["negative_controls"])
            self.assertIn("not_owner_approved", (out / "MODEL_REPORT.md").read_text())
            verification = verify_receipt_artifacts(out, assumptions)
            self.assertEqual(verification, {"outputs": 2, "sources": 5})
            self.assertNotIn("receipt.json", receipt["outputs"])
            self.assertEqual(receipt["schema_version"], "washout-paired-design-simulation-receipt/2")
            for scenario in results["scenarios"]:
                for output in scenario["designs"].values():
                    self.assertIn("no_isotope_control", output)
                    self.assertNotIn("matched_aggregate", output)
            before = (out / "results.json").read_bytes()
            with self.assertRaises(FileExistsError):
                cli.run(assumptions, out)
            self.assertEqual((out / "results.json").read_bytes(), before)


class SavedNov15ArtifactTests(unittest.TestCase):
    def test_saved_receipt_and_artifacts_verify_read_only(self):
        out = Path(__file__).resolve().parent / "washout-paired-design-simulation-run-2026-11-15"
        tracked = [out / "results.json", out / "MODEL_REPORT.md", out / "receipt.json", ASSUMPTIONS_PATH]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in tracked}
        verification = verify_receipt_artifacts(out, ASSUMPTIONS_PATH)
        self.assertEqual(verification, {"outputs": 2, "sources": 5})
        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in tracked}
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()

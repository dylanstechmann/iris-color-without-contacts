#!/usr/bin/env python3
"""Unit tests for the Phase-1 feasibility-gate evaluator.

All data are synthetic/hypothetical. No facility data are claimed.
Developed by AI assistant; owner-reviewed before interpretation.
"""
from __future__ import annotations

import json
import os
from contextlib import redirect_stderr
from io import StringIO
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure evaluate_gates is importable
sys.path.insert(0, str(Path(__file__).parent))
from evaluate_gates import (
    evaluate_value,
    evaluate_gate,
    read_report,
    _sha256_file,
    main,
)


class TestEvaluateValue(unittest.TestCase):
    def test_boolean_equality_pass(self):
        self.assertEqual(evaluate_value(True, {"comparator": "==", "target": True})[0], "pass")

    def test_boolean_equality_fail(self):
        self.assertEqual(evaluate_value(False, {"comparator": "==", "target": True})[0], "fail")

    def test_le_pass(self):
        self.assertEqual(evaluate_value(5.0, {"comparator": "<=", "target": 10.0})[0], "pass")

    def test_le_fail(self):
        self.assertEqual(evaluate_value(15.0, {"comparator": "<=", "target": 10.0})[0], "fail")

    def test_ge_pass(self):
        self.assertEqual(evaluate_value(75.0, {"comparator": ">=", "target": 70.0})[0], "pass")

    def test_ge_fail(self):
        self.assertEqual(evaluate_value(65.0, {"comparator": ">=", "target": 70.0})[0], "fail")

    def test_lt_pass(self):
        self.assertEqual(evaluate_value(10.0, {"comparator": "<", "target": 15.0})[0], "pass")

    def test_lt_fail(self):
        self.assertEqual(evaluate_value(18.0, {"comparator": "<", "target": 15.0})[0], "fail")

    def test_range_pass(self):
        self.assertEqual(evaluate_value(95.0, {"comparator": "range", "target_lo": 80.0, "target_hi": 120.0})[0], "pass")

    def test_range_fail_low(self):
        self.assertEqual(evaluate_value(75.0, {"comparator": "range", "target_lo": 80.0, "target_hi": 120.0})[0], "fail")

    def test_range_fail_high(self):
        self.assertEqual(evaluate_value(125.0, {"comparator": "range", "target_lo": 80.0, "target_hi": 120.0})[0], "fail")

    def test_none_not_evaluable(self):
        self.assertEqual(evaluate_value(None, {"comparator": "<=", "target": 10.0})[0], "not_evaluable")

    def test_unknown_comparator(self):
        self.assertEqual(evaluate_value(5.0, {"comparator": "?"})[0], "not_evaluable")

    def test_ambiguous_booleans_are_not_coerced(self):
        criterion = {"comparator": "==", "target": True, "unit": "boolean"}
        for observed in ("true", "false", 1, 0, 1.0, None):
            with self.subTest(observed=observed):
                self.assertEqual(evaluate_value(observed, criterion)[0], "not_evaluable")

    def test_nonfinite_and_wrong_numeric_types_are_not_evaluable(self):
        criterion = {"comparator": "<=", "target": 10.0, "unit": "%"}
        for observed in (float("nan"), float("inf"), float("-inf"), "5", True):
            with self.subTest(observed=observed):
                self.assertEqual(evaluate_value(observed, criterion)[0], "not_evaluable")


class TestEvaluateGatePerCompound(unittest.TestCase):
    def test_gate_2_pass(self):
        gate_spec = {
            "per_compound": True,
            "criteria": {
                "c1_spike_recovery": {"comparator": "range", "target_lo": 80.0, "target_hi": 120.0, "unit": "%", "status": "CONFIRMED"},
            }
        }
        report = {
            "compounds": {
                "KT-939": {"c1_spike_recovery": {"value": 95.0}}
            }
        }
        results = evaluate_gate("gate_2", gate_spec, report)
        self.assertEqual(results["KT-939:c1_spike_recovery"]["result"], "pass")

    def test_gate_2_fail(self):
        gate_spec = {
            "per_compound": True,
            "criteria": {
                "c1_spike_recovery": {"comparator": "range", "target_lo": 80.0, "target_hi": 120.0, "unit": "%", "status": "CONFIRMED"},
            }
        }
        report = {
            "compounds": {
                "KT-939": {"c1_spike_recovery": {"value": 75.0}}
            }
        }
        results = evaluate_gate("gate_2", gate_spec, report)
        self.assertEqual(results["KT-939:c1_spike_recovery"]["result"], "fail")
        self.assertIn("observed=75.0", results["KT-939:c1_spike_recovery"]["detail"])

    def test_gate_2_cv_fail(self):
        gate_spec = {
            "per_compound": True,
            "criteria": {
                "c3_intra_day_cv": {"comparator": "<", "target": 15.0, "unit": "%", "status": "CONFIRMED"},
            }
        }
        report = {
            "compounds": {
                "Thiamidol": {"c3_intra_day_cv": {"value": 18.0}}
            }
        }
        results = evaluate_gate("gate_2", gate_spec, report)
        self.assertEqual(results["Thiamidol:c3_intra_day_cv"]["result"], "fail")

    def test_missing_field_not_evaluable(self):
        gate_spec = {
            "per_compound": False,
            "criteria": {
                "c1_baseline_separation": {"comparator": "==", "target": True, "unit": "boolean", "status": "CONFIRMED"},
            }
        }
        report = {"observations": {}}
        results = evaluate_gate("gate_1", gate_spec, report)
        self.assertEqual(results["c1_baseline_separation"]["result"], "not_evaluable")
        self.assertIn("field missing", results["c1_baseline_separation"]["detail"])


class TestMainIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def _write_criteria(self, overrides=None):
        criteria = {
            "schema_version": "1.1",
            "gates": {
                "gate_1_old_pigment_labeling": {
                    "name": "Gate 1",
                    "per_compound": False,
                    "criteria": {
                        "c1_baseline_separation": {
                            "comparator": "==", "target": True, "unit": "boolean", "status": "CONFIRMED",
                            "provenance": "test"
                        },
                        "c2_old_pool_fraction_lod": {
                            "comparator": "<=", "target": 0.10, "unit": "fraction", "status": "PROPOSED",
                            "provenance": "test"
                        },
                    }
                },
                "gate_2_free_compound_validation": {
                    "name": "Gate 2",
                    "per_compound": True,
                    "required_compounds": ["KT-939"],
                    "criteria": {
                        "c1_spike_recovery": {
                            "comparator": "range", "target_lo": 80.0, "target_hi": 120.0, "unit": "%", "status": "CONFIRMED",
                            "provenance": "test"
                        },
                        "c3_intra_day_cv": {
                            "comparator": "<", "target": 15.0, "unit": "%", "status": "CONFIRMED",
                            "provenance": "test"
                        },
                    }
                },
                "gate_3_ampyrone_solubility": {
                    "name": "Gate 3",
                    "per_compound": False,
                    "compound": "Ampyrone",
                    "criteria": {
                        "c3_cell_viability": {
                            "comparator": ">=", "target": 70.0, "unit": "%", "status": "PROPOSED",
                            "provenance": "test"
                        },
                    }
                },
            }
        }
        if overrides:
            criteria["gates"].update(overrides)
        p = Path(self.tmp) / "criteria.json"
        p.write_text(json.dumps(criteria), encoding="utf-8")
        return p

    def _write_reports(self, reports: dict):
        rdir = Path(self.tmp) / "reports"
        rdir.mkdir()
        for name, data in reports.items():
            data.setdefault("report_version", "1.1")
            data.setdefault("gate_id", name)
            data.setdefault("facility_id", "SYNTHETIC-TEST")
            data.setdefault("run_id", "synthetic-shared-run")
            data.setdefault("data_kind", "synthetic")
            data.setdefault("provenance", {
                "source_kind": "synthetic_fixture",
                "source_reference": "analysis/test_evaluate_gates.py",
            })
            if name == "gate_3_ampyrone_solubility":
                data.setdefault("compound", "Ampyrone")
            units = {
                "c1_baseline_separation": "boolean",
                "c2_old_pool_fraction_lod": "fraction",
                "c1_spike_recovery": "%",
                "c3_intra_day_cv": "%",
                "c3_cell_viability": "%",
            }
            observation_groups = [data.get("observations", {})]
            observation_groups.extend(data.get("compounds", {}).values())
            for group in observation_groups:
                for criterion_id, observation in group.items():
                    observation.setdefault("unit", units[criterion_id])
            (rdir / f"{name}_report.json").write_text(json.dumps(data), encoding="utf-8")
        return rdir

    def test_clean_pass(self):
        crit = self._write_criteria()
        rdir = self._write_reports({
            "gate_1_old_pigment_labeling": {
                "observations": {
                    "c1_baseline_separation": {"value": True},
                    "c2_old_pool_fraction_lod": {"value": 0.05},
                }
            },
            "gate_2_free_compound_validation": {
                "compounds": {
                    "KT-939": {
                        "c1_spike_recovery": {"value": 95.0},
                        "c3_intra_day_cv": {"value": 8.0},
                    }
                }
            },
            "gate_3_ampyrone_solubility": {
                "observations": {
                    "c3_cell_viability": {"value": 85.0},
                }
            },
        })
        out = Path(self.tmp) / "out"
        rc = main(["--report", str(rdir), "--criteria", str(crit), "--out", str(out)])
        self.assertEqual(rc, 0)
        ge = json.loads((out / "gate_evaluation.json").read_text())
        for gate_eval in ge["gate_evaluations"].values():
            for res in gate_eval["results"].values():
                self.assertEqual(res["result"], "pass")

    def test_spike_recovery_failure(self):
        crit = self._write_criteria()
        rdir = self._write_reports({
            "gate_1_old_pigment_labeling": {
                "observations": {
                    "c1_baseline_separation": {"value": True},
                    "c2_old_pool_fraction_lod": {"value": 0.05},
                }
            },
            "gate_2_free_compound_validation": {
                "compounds": {
                    "KT-939": {
                        "c1_spike_recovery": {"value": 75.0},
                        "c3_intra_day_cv": {"value": 8.0},
                    }
                }
            },
            "gate_3_ampyrone_solubility": {
                "observations": {
                    "c3_cell_viability": {"value": 85.0},
                }
            },
        })
        out = Path(self.tmp) / "out"
        rc = main(["--report", str(rdir), "--criteria", str(crit), "--out", str(out)])
        self.assertEqual(rc, 1)
        ge = json.loads((out / "gate_evaluation.json").read_text())
        g2 = ge["gate_evaluations"]["gate_2_free_compound_validation"]["results"]
        self.assertEqual(g2["KT-939:c1_spike_recovery"]["result"], "fail")
        self.assertEqual(g2["KT-939:c3_intra_day_cv"]["result"], "pass")

    def test_cv_failure(self):
        crit = self._write_criteria()
        rdir = self._write_reports({
            "gate_1_old_pigment_labeling": {
                "observations": {
                    "c1_baseline_separation": {"value": True},
                    "c2_old_pool_fraction_lod": {"value": 0.05},
                }
            },
            "gate_2_free_compound_validation": {
                "compounds": {
                    "KT-939": {
                        "c1_spike_recovery": {"value": 95.0},
                        "c3_intra_day_cv": {"value": 18.0},
                    }
                }
            },
            "gate_3_ampyrone_solubility": {
                "observations": {
                    "c3_cell_viability": {"value": 85.0},
                }
            },
        })
        out = Path(self.tmp) / "out"
        rc = main(["--report", str(rdir), "--criteria", str(crit), "--out", str(out)])
        self.assertEqual(rc, 1)
        ge = json.loads((out / "gate_evaluation.json").read_text())
        g2 = ge["gate_evaluations"]["gate_2_free_compound_validation"]["results"]
        self.assertEqual(g2["KT-939:c3_intra_day_cv"]["result"], "fail")

    def test_missing_readout_rejected(self):
        crit = self._write_criteria()
        rdir = self._write_reports({
            "gate_1_old_pigment_labeling": {
                "observations": {
                    "c2_old_pool_fraction_lod": {"value": 0.05},
                }
            },
            "gate_2_free_compound_validation": {
                "compounds": {
                    "KT-939": {
                        "c1_spike_recovery": {"value": 95.0},
                        "c3_intra_day_cv": {"value": 8.0},
                    }
                }
            },
            "gate_3_ampyrone_solubility": {
                "observations": {
                    "c3_cell_viability": {"value": 85.0},
                }
            },
        })
        out = Path(self.tmp) / "out"
        rc = main(["--report", str(rdir), "--criteria", str(crit), "--out", str(out)])
        self.assertEqual(rc, 2)
        self.assertFalse(out.exists())

    def test_criteria_override(self):
        # Owner changes a PROPOSED threshold via criteria file edit
        crit = self._write_criteria(overrides={
            "gate_3_ampyrone_solubility": {
                "name": "Gate 3",
                "per_compound": False,
                "compound": "Ampyrone",
                "criteria": {
                    "c3_cell_viability": {
                        "comparator": ">=", "target": 80.0, "unit": "%", "status": "CONFIRMED",
                        "provenance": "test"
                    },
                }
            }
        })
        rdir = self._write_reports({
            "gate_1_old_pigment_labeling": {
                "observations": {
                    "c1_baseline_separation": {"value": True},
                    "c2_old_pool_fraction_lod": {"value": 0.05},
                }
            },
            "gate_2_free_compound_validation": {
                "compounds": {
                    "KT-939": {
                        "c1_spike_recovery": {"value": 95.0},
                        "c3_intra_day_cv": {"value": 8.0},
                    }
                }
            },
            "gate_3_ampyrone_solubility": {
                "observations": {
                    "c3_cell_viability": {"value": 82.0},
                }
            },
        })
        out = Path(self.tmp) / "out"
        rc = main(["--report", str(rdir), "--criteria", str(crit), "--out", str(out)])
        self.assertEqual(rc, 0)
        ge = json.loads((out / "gate_evaluation.json").read_text())
        g3 = ge["gate_evaluations"]["gate_3_ampyrone_solubility"]["results"]
        self.assertEqual(g3["c3_cell_viability"]["result"], "pass")
        # The threshold string should reflect the override value 80.0
        self.assertIn("80.0", g3["c3_cell_viability"]["threshold"])

    def test_out_dir_exists_error(self):
        crit = self._write_criteria()
        rdir = self._write_reports({})
        out = Path(self.tmp) / "out"
        out.mkdir()
        rc = main(["--report", str(rdir), "--criteria", str(crit), "--out", str(out)])
        self.assertEqual(rc, 2)


class TestStrictFacilityReports(unittest.TestCase):
    """Fail-closed schema tests using only synthetic/hypothetical fixtures."""

    fixture = Path(__file__).parent / "gate-evaluator-fixtures" / "valid-synthetic"
    criteria_path = Path(__file__).parent / "gate_criteria.json"
    gate1 = "gate_1_old_pigment_labeling"
    gate2 = "gate_2_free_compound_validation"
    gate3 = "gate_3_ampyrone_solubility"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def _new_case(self):
        case = Path(tempfile.mkdtemp(dir=self.tmp))
        reports = case / "reports"
        shutil.copytree(self.fixture, reports)
        return case, reports

    def _edit(self, reports, gate_id, editor):
        path = reports / f"{gate_id}_report.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        editor(data)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _assert_rejected(self, gate_id, editor, expected):
        case, reports = self._new_case()
        self._edit(reports, gate_id, editor)
        out = case / "out"
        stderr = StringIO()
        with redirect_stderr(stderr):
            rc = main([
                "--report", str(reports), "--criteria", str(self.criteria_path),
                "--out", str(out),
            ])
        self.assertEqual(rc, 2, stderr.getvalue())
        self.assertFalse(out.exists())
        self.assertIn(expected, stderr.getvalue())

    def _assert_criteria_rejected(self, editor, expected):
        case, reports = self._new_case()
        criteria = json.loads(self.criteria_path.read_text(encoding="utf-8"))
        editor(criteria)
        path = case / "criteria.json"
        path.write_text(json.dumps(criteria), encoding="utf-8")
        out = case / "out"
        stderr = StringIO()
        with redirect_stderr(stderr):
            rc = main(["--report", str(reports), "--criteria", str(path), "--out", str(out)])
        self.assertEqual(rc, 2, stderr.getvalue())
        self.assertFalse(out.exists())
        self.assertIn(expected, stderr.getvalue())

    def test_valid_synthetic_facility_style_fixture(self):
        case, reports = self._new_case()
        out = case / "out"
        rc = main([
            "--report", str(reports), "--criteria", str(self.criteria_path),
            "--out", str(out),
        ])
        self.assertEqual(rc, 0)
        evaluation = json.loads((out / "gate_evaluation.json").read_text(encoding="utf-8"))
        receipt = json.loads((out / "receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(evaluation["data_kind"], "synthetic")
        self.assertEqual(receipt["data_kind"], "synthetic")
        self.assertEqual(evaluation["facility_id"], "SYNTHETIC-FIXTURE")
        self.assertEqual(evaluation["run_id"], "synthetic-phase1-fixture-2026-11-26")
        self.assertEqual(receipt["run_id"], evaluation["run_id"])
        results = [
            result
            for gate in evaluation["gate_evaluations"].values()
            for result in gate["results"].values()
        ]
        self.assertEqual(len(results), 18)
        self.assertTrue(all(result["result"] == "pass" for result in results))
        self.assertEqual(len(receipt["inputs"]), 4)

    def test_validated_measured_metadata_is_propagated(self):
        """This exercises metadata propagation only; no measured facility data are used."""
        case, reports = self._new_case()
        for path in reports.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            data["facility_id"] = "HYPOTHETICAL-FACILITY"
            data["data_kind"] = "measured"
            data["provenance"] = {
                "source_kind": "facility_measurement",
                "source_reference": f"processed/{path.name}",
                "raw_data_reference": f"raw/{path.stem}.manifest.json",
            }
            path.write_text(json.dumps(data), encoding="utf-8")
        out = case / "out"
        rc = main([
            "--report", str(reports), "--criteria", str(self.criteria_path),
            "--out", str(out),
        ])
        self.assertEqual(rc, 0)
        evaluation = json.loads((out / "gate_evaluation.json").read_text(encoding="utf-8"))
        receipt = json.loads((out / "receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(evaluation["data_kind"], "measured")
        self.assertEqual(receipt["data_kind"], "measured")

    def test_measured_label_alone_cannot_override_synthetic_provenance(self):
        self._assert_rejected(
            self.gate1, lambda data: data.update(data_kind="measured"),
            "provenance mismatch",
        )

    def test_measured_provenance_requires_raw_data_reference(self):
        def edit(data):
            data["data_kind"] = "measured"
            data["provenance"] = {
                "source_kind": "facility_measurement",
                "source_reference": "processed/gate-1.json",
            }
        self._assert_rejected(self.gate1, edit, "raw_data_reference")

    def test_synthetic_provenance_rejects_facility_source_and_missing_reference(self):
        self._assert_rejected(
            self.gate1,
            lambda data: data["provenance"].update(source_kind="facility_measurement"),
            "provenance mismatch",
        )
        self._assert_rejected(
            self.gate1, lambda data: data["provenance"].pop("source_reference"),
            "source_reference",
        )

    def test_missing_compound_declarations_rejected(self):
        self._assert_rejected(
            self.gate2, lambda data: data["compounds"].pop("Thiamidol"),
            "Thiamidol",
        )
        self._assert_rejected(self.gate3, lambda data: data.pop("compound"), "compound")
        self._assert_rejected(
            self.gate3, lambda data: data.update(compound="KT-939"),
            "must be 'Ampyrone'",
        )
        self._assert_rejected(self.gate2, lambda data: data.pop("compounds"), "compounds")

    def test_missing_required_readouts_rejected(self):
        self._assert_rejected(
            self.gate1, lambda data: data["observations"].pop("c2_old_pool_fraction_lod"),
            "c2_old_pool_fraction_lod",
        )
        self._assert_rejected(
            self.gate2,
            lambda data: data["compounds"]["KT-939"].pop("c4_freeze_thaw_stability"),
            "c4_freeze_thaw_stability",
        )

    def test_wrong_and_missing_units_rejected(self):
        self._assert_rejected(
            self.gate1,
            lambda data: data["observations"]["c2_old_pool_fraction_lod"].update(unit="%"),
            "fraction_of_total",
        )
        self._assert_rejected(
            self.gate1,
            lambda data: data["observations"]["c2_old_pool_fraction_lod"].pop("unit"),
            "unit",
        )
        self._assert_rejected(
            self.gate2,
            lambda data: data["compounds"]["KT-939"].update(c1_spike_recovery=95.0),
            "must be a JSON object",
        )

    def test_ambiguous_boolean_observations_rejected(self):
        for value in ("true", "false", 1, 0, 1.0):
            with self.subTest(value=value):
                self._assert_rejected(
                    self.gate1,
                    lambda data, value=value: data["observations"]["c1_baseline_separation"].update(value=value),
                    "JSON true or false",
                )

    def test_nonfinite_and_wrong_numeric_observations_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf"), "0.05", True):
            with self.subTest(value=value):
                self._assert_rejected(
                    self.gate1,
                    lambda data, value=value: data["observations"]["c2_old_pool_fraction_lod"].update(value=value),
                    "finite",
                )

    def test_overflowing_json_number_rejected(self):
        case, reports = self._new_case()
        path = reports / f"{self.gate1}_report.json"
        text = path.read_text(encoding="utf-8").replace('"value": 0.05', '"value": 1e999')
        path.write_text(text, encoding="utf-8")
        stderr = StringIO()
        with redirect_stderr(stderr):
            rc = main([
                "--report", str(reports), "--criteria", str(self.criteria_path),
                "--out", str(case / "out"),
            ])
        self.assertEqual(rc, 2)
        self.assertIn("non-finite", stderr.getvalue())
        self.assertFalse((case / "out").exists())

    def test_unknown_fields_compounds_and_readouts_rejected(self):
        editors = [
            (self.gate1, lambda data: data.update(extra=True), "unknown field(s): extra"),
            (self.gate1, lambda data: data["observations"].update(unknown={"value": 1, "unit": "%"}), "unknown field(s): unknown"),
            (self.gate1, lambda data: data["observations"]["c1_baseline_separation"].update(note="typo"), "unknown field(s): note"),
            (self.gate2, lambda data: data["compounds"].update(Unknown={}), "unknown field(s): Unknown"),
        ]
        for gate_id, editor, expected in editors:
            with self.subTest(expected=expected):
                self._assert_rejected(gate_id, editor, expected)

    def test_gate_and_run_metadata_failures_rejected(self):
        self._assert_rejected(
            self.gate1, lambda data: data.update(gate_id=self.gate2),
            "does not match",
        )
        self._assert_rejected(
            self.gate1, lambda data: data.update(run_id="different-run"),
            "inconsistent run metadata",
        )
        self._assert_rejected(
            self.gate1, lambda data: data.update(facility_id="OTHER-FACILITY"),
            "inconsistent run metadata",
        )

        def inconsistent_kind(data):
            data["data_kind"] = "measured"
            data["provenance"] = {
                "source_kind": "facility_measurement",
                "source_reference": "processed/gate-1.json",
                "raw_data_reference": "raw/gate-1.manifest.json",
            }
        self._assert_rejected(self.gate1, inconsistent_kind, "inconsistent run metadata")

    def test_report_version_and_data_kind_type_are_strict(self):
        self._assert_rejected(
            self.gate1, lambda data: data.update(report_version="1.0"),
            "report_version",
        )
        self._assert_rejected(
            self.gate1, lambda data: data.update(data_kind=[]),
            "data_kind",
        )
        self._assert_rejected(
            self.gate1, lambda data: data.update(data_kind="Measured"),
            "synthetic or measured",
        )

    def test_duplicate_keys_unknown_json_and_ambiguous_filenames_rejected(self):
        case, reports = self._new_case()
        path = reports / f"{self.gate1}_report.json"
        text = path.read_text(encoding="utf-8").replace(
            '"gate_id":', f'"gate_id": "{self.gate1}", "gate_id":', 1,
        )
        path.write_text(text, encoding="utf-8")
        stderr = StringIO()
        with redirect_stderr(stderr):
            rc = main([
                "--report", str(reports), "--criteria", str(self.criteria_path),
                "--out", str(case / "out"),
            ])
        self.assertEqual(rc, 2)
        self.assertIn("duplicate field", stderr.getvalue())

        case, reports = self._new_case()
        (reports / "gate_1_typo.json").write_text("{}", encoding="utf-8")
        stderr = StringIO()
        with redirect_stderr(stderr):
            rc = main([
                "--report", str(reports), "--criteria", str(self.criteria_path),
                "--out", str(case / "out"),
            ])
        self.assertEqual(rc, 2)
        self.assertIn("unknown gate report JSON", stderr.getvalue())

        case, reports = self._new_case()
        shutil.copyfile(reports / f"{self.gate1}_report.json", reports / f"{self.gate1}.json")
        stderr = StringIO()
        with redirect_stderr(stderr):
            rc = main([
                "--report", str(reports), "--criteria", str(self.criteria_path),
                "--out", str(case / "out"),
            ])
        self.assertEqual(rc, 2)
        self.assertIn("ambiguous reports", stderr.getvalue())

    def test_missing_gate_is_not_evaluable_but_null_readout_is_explicit(self):
        case, reports = self._new_case()
        (reports / f"{self.gate1}_report.json").unlink()
        out = case / "out"
        rc = main([
            "--report", str(reports), "--criteria", str(self.criteria_path),
            "--out", str(out),
        ])
        self.assertEqual(rc, 1)
        evaluation = json.loads((out / "gate_evaluation.json").read_text(encoding="utf-8"))
        results = evaluation["gate_evaluations"][self.gate1]["results"]
        self.assertEqual(len(results), 3)
        self.assertTrue(all(result["result"] == "not_evaluable" for result in results.values()))
        self.assertTrue(all(result["detail"] == "gate report missing" for result in results.values()))

        case, reports = self._new_case()
        self._edit(
            reports, self.gate1,
            lambda data: data["observations"]["c2_old_pool_fraction_lod"].update(value=None),
        )
        out = case / "out"
        rc = main([
            "--report", str(reports), "--criteria", str(self.criteria_path),
            "--out", str(out),
        ])
        self.assertEqual(rc, 1)
        evaluation = json.loads((out / "gate_evaluation.json").read_text(encoding="utf-8"))
        result = evaluation["gate_evaluations"][self.gate1]["results"]["c2_old_pool_fraction_lod"]
        self.assertEqual(result["result"], "not_evaluable")

    def test_no_reports_cannot_default_to_synthetic(self):
        case, reports = self._new_case()
        for path in reports.glob("*.json"):
            path.unlink()
        stderr = StringIO()
        with redirect_stderr(stderr):
            rc = main([
                "--report", str(reports), "--criteria", str(self.criteria_path),
                "--out", str(case / "out"),
            ])
        self.assertEqual(rc, 2)
        self.assertIn("data_kind cannot be established", stderr.getvalue())

    def test_malformed_criteria_rejected(self):
        self._assert_criteria_rejected(
            lambda data: data.update(schema_version="1.0"), "schema_version",
        )
        self._assert_criteria_rejected(
            lambda data: data["gates"][self.gate2].pop("required_compounds"),
            "required_compounds",
        )
        self._assert_criteria_rejected(
            lambda data: data["gates"][self.gate1]["criteria"]["c2_old_pool_fraction_lod"].update(target=float("nan")),
            "non-finite",
        )

    def test_predeclared_thresholds_are_unchanged(self):
        criteria = json.loads(self.criteria_path.read_text(encoding="utf-8"))
        gates = criteria["gates"]
        expected = {
            self.gate1: {
                "c1_baseline_separation": True,
                "c2_old_pool_fraction_lod": 0.10,
                "c3_chemical_melanin_agreement": 15.0,
            },
            self.gate2: {
                "c2_calibration_r2": 0.99,
                "c3_intra_day_cv": 15.0,
                "c4_freeze_thaw_stability": True,
            },
            self.gate3: {
                "c1_no_visible_precipitate": False,
                "c2_concentration_drop": 10.0,
                "c3_cell_viability": 70.0,
            },
        }
        for gate_id, criteria_values in expected.items():
            for criterion_id, target in criteria_values.items():
                self.assertEqual(gates[gate_id]["criteria"][criterion_id]["target"], target)
        self.assertEqual(gates[self.gate2]["criteria"]["c1_spike_recovery"]["target_lo"], 80.0)
        self.assertEqual(gates[self.gate2]["criteria"]["c1_spike_recovery"]["target_hi"], 120.0)

    def test_failed_proposed_criterion_generates_report_without_name_error(self):
        case, reports = self._new_case()
        criteria = json.loads(self.criteria_path.read_text(encoding="utf-8"))
        criteria["gates"][self.gate3]["criteria"]["c3_cell_viability"]["target"] = 95.0
        criteria_file = case / "criteria.json"
        criteria_file.write_text(json.dumps(criteria), encoding="utf-8")
        out = case / "out"
        rc = main(["--report", str(reports), "--criteria", str(criteria_file), "--out", str(out)])
        self.assertEqual(rc, 1)
        self.assertTrue((out / "gate_evaluation.json").is_file())
        report = (out / "EVALUATION_REPORT.md").read_text(encoding="utf-8")
        self.assertIn("c3_cell_viability", report)
        self.assertIn("PROPOSED", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""Unit tests for the Phase-1 feasibility-gate evaluator.

All data are synthetic/hypothetical. No facility data are claimed.
Developed by AI assistant; owner-reviewed before interpretation.
"""
from __future__ import annotations

import json
import os
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
            "schema_version": "1.0",
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

    def test_missing_field_not_evaluable(self):
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
        self.assertEqual(rc, 1)
        ge = json.loads((out / "gate_evaluation.json").read_text())
        g1 = ge["gate_evaluations"]["gate_1_old_pigment_labeling"]["results"]
        self.assertEqual(g1["c1_baseline_separation"]["result"], "not_evaluable")

    def test_criteria_override(self):
        # Owner changes a PROPOSED threshold via criteria file edit
        crit = self._write_criteria(overrides={
            "gate_3_ampyrone_solubility": {
                "name": "Gate 3",
                "per_compound": False,
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


if __name__ == "__main__":
    unittest.main(verbosity=2)

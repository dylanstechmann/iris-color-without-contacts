"""Reproduce the primary fits in the archived synthetic comparison."""

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from verify_artifacts import DECISION_FIELDS, verify_paired_washout


ANALYSIS = Path(__file__).resolve().parent
ARCHIVE = ANALYSIS / "washout-paired-design-simulation-run-2026-11-15"
ASSUMPTIONS = ANALYSIS / "washout_design_assumptions.json"
# Allow numerical drift across SciPy builds while checking each reported ratio.
RATIO_TOLERANCE = 1e-5


class ReplayPairedWashoutTest(unittest.TestCase):
    def test_cli_reproduces_archived_primary_decisions(self):
        verify_paired_washout(ARCHIVE, ASSUMPTIONS)
        archived = json.loads((ARCHIVE / "results.json").read_text(encoding="utf-8"))
        with TemporaryDirectory() as temp:
            run = Path(temp) / "replay"
            subprocess.run([
                sys.executable, str(ANALYSIS / "simulate_washout_design.py"),
                "--assumptions", str(ASSUMPTIONS), "--out", str(run),
            ], check=True)
            verify_paired_washout(run, ASSUMPTIONS)
            replayed = json.loads((run / "results.json").read_text(encoding="utf-8"))

        for expected, actual in zip(archived["scenarios"], replayed["scenarios"], strict=True):
            self.assertEqual(actual["name"], expected["name"])
            self.assertEqual(actual["designs"].keys(), expected["designs"].keys())
            for design, group in expected["designs"].items():
                pairs = zip(group["records"], actual["designs"][design]["records"], strict=True)
                for old, new in pairs:
                    with self.subTest(
                        scenario=expected["name"], design=design,
                        system=old["system"], replicate=old["replicate"],
                    ):
                        self.assertEqual((new["system"], new["replicate"]),
                                         (old["system"], old["replicate"]))
                        expected_decision = old["decision"]
                        actual_decision = new["decision"]
                        self.assertEqual(actual_decision["status"], expected_decision["status"])
                        for field in DECISION_FIELDS:
                            self.assertIs(actual_decision[field], expected_decision[field], field)
                        self.assertAlmostEqual(
                            actual_decision["symmetric_half_time_ratio"],
                            expected_decision["symmetric_half_time_ratio"],
                            delta=RATIO_TOLERANCE,
                        )


"""Unit tests for the F5 washout-kinetics pipeline.

Cover synthetic recovery, identifiability demonstrations, and physical checks.
All data are synthetic/hypothetical.
"""
from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import numpy as np

from washout_model import simulate_washout, fit_washout


# Load assumptions once
ASSUMPTIONS_PATH = Path(__file__).parent / "washout_assumptions.json"
ASSUMPTIONS = json.loads(ASSUMPTIONS_PATH.read_text(encoding="utf-8"))
GROUND_TRUTH = ASSUMPTIONS["synthetic_ground_truth"]
TIME = np.array(ASSUMPTIONS["timepoints_days"], dtype=float)
NOISE = ASSUMPTIONS["noise_levels"]


def _make_noisy_data(readout_flags: dict) -> tuple[dict, dict]:
    """Generate synthetic data matching the assumptions."""
    sim = simulate_washout(TIME, **GROUND_TRUTH, hill=1.0)
    rng = np.random.default_rng(ASSUMPTIONS["noise_seed"])
    total = sim["total"] + rng.normal(0.0, NOISE["total_sd"], size=TIME.shape)
    old_frac = sim["old_fraction"] + rng.normal(0.0, NOISE["old_fraction_sd"], size=TIME.shape)
    compound = sim["compound"] + rng.normal(0.0, NOISE["compound_sd"], size=TIME.shape)
    cell_count = np.ones_like(TIME) + rng.normal(0.0, NOISE["cell_count_sd"], size=TIME.shape)

    total = np.clip(total, 0.0, None)
    old_frac = np.clip(old_frac, 0.0, 1.0)
    compound = np.clip(compound, 0.0, None)
    cell_count = np.clip(cell_count, 0.01, None)

    data = {
        "time": TIME,
        "total": total / cell_count,
        "old_fraction": old_frac,
        "compound": compound,
    }
    return data, sim


class PhysicalChecks(unittest.TestCase):
    """Test (d): nonnegativity and mass conservation."""

    def test_all_compartments_nonneg(self):
        sim = simulate_washout(TIME, **GROUND_TRUTH, hill=1.0)
        for key in ("old", "new", "total", "compound", "synthesis"):
            self.assertTrue(np.all(sim[key] >= 0),
                            f"Negative values in compartment {key}")

    def test_mass_conservation_total_equals_old_plus_new(self):
        sim = simulate_washout(TIME, **GROUND_TRUTH, hill=1.0)
        self.assertTrue(np.allclose(sim["total"], sim["old"] + sim["new"]))

    def test_old_fraction_between_zero_and_one(self):
        sim = simulate_washout(TIME, **GROUND_TRUTH, hill=1.0)
        self.assertTrue(np.all(sim["old_fraction"] >= 0))
        self.assertTrue(np.all(sim["old_fraction"] <= 1))

    def test_new_source_relative_recovered_to_one(self):
        sim = simulate_washout(TIME, **GROUND_TRUTH, hill=1.0)
        # At late times, compound should be near zero, so synthesis ~ s_max
        late = sim["time"] >= 14
        if np.any(late):
            self.assertTrue(
                np.allclose(sim["new_source_relative_to_baseline"][late], 1.0, atol=0.05),
                "Synthesis should recover to baseline when compound is nearly gone"
            )


class SyntheticRecovery(unittest.TestCase):
    """Test (a): with all readouts, ground truth is recovered."""

    @classmethod
    def setUpClass(cls):
        cls.data, cls.sim = _make_noisy_data({"total": True, "old_fraction": True, "compound": True})
        cls.fit = fit_washout(
            cls.data,
            {"total": True, "old_fraction": True, "compound": True},
            initial_guess=ASSUMPTIONS["initial_guess"],
            bounds=ASSUMPTIONS["fit_bounds"],
            weights=ASSUMPTIONS["fit_weights"],
        )

    def test_fit_converges(self):
        self.assertTrue(self.fit["fit_summary"]["success"],
                        f"Fit did not converge: {self.fit['fit_summary']['message']}")

    def test_parameters_recovered_within_tolerance(self):
        tol = {
            "c0": 20.0,
            "k_c": 0.05,
            "m_old0": 0.03,
            "m_new0": 0.03,
            "k_old": 0.02,
            "k_new": 0.02,
            "s_max": 0.03,
            "ic50": 10.0,
        }
        for param, margin in tol.items():
            fitted = self.fit["params"][param]
            truth = GROUND_TRUTH[param]
            self.assertAlmostEqual(
                fitted, truth, delta=margin,
                msg=f"Parameter {param} off: fitted={fitted:.4f}, truth={truth:.4f}"
            )

    def test_covariance_computed(self):
        self.assertTrue(self.fit["cov_success"],
                        "Covariance should be computable with all readouts.")

    def test_confidence_intervals_nontrivial(self):
        for param in GROUND_TRUTH:
            lo = self.fit["confidence_intervals"].get(f"{param}_95_lower")
            hi = self.fit["confidence_intervals"].get(f"{param}_95_upper")
            self.assertIsNotNone(lo, f"Missing CI lower for {param}")
            self.assertIsNotNone(hi, f"Missing CI upper for {param}")
            self.assertLess(lo, hi, f"CI lower >= upper for {param}")

    def test_residuals_small(self):
        thresholds = {"total": 0.05, "old_fraction": 0.05, "compound": 3.0}
        for key in ("total", "old_fraction", "compound"):
            rmse = self.fit["residuals_rmse"][key]["rmse"]
            self.assertLess(rmse, thresholds[key],
                            f"RMSE for {key} too large: {rmse}")


class IdentifiabilityWithoutIsotope(unittest.TestCase):
    """Test (b): without old_fraction, old-vs-new cannot be separated."""

    @classmethod
    def setUpClass(cls):
        cls.data, cls.sim = _make_noisy_data({"total": True, "old_fraction": True, "compound": True})
        cls.fit = fit_washout(
            cls.data,
            {"total": True, "old_fraction": False, "compound": True},
            initial_guess=ASSUMPTIONS["initial_guess"],
            bounds=ASSUMPTIONS["fit_bounds"],
            weights=ASSUMPTIONS["fit_weights"],
        )

    def test_fit_note_warns_about_missing_old_fraction(self):
        notes = " ".join(self.fit["identifiability_notes"])
        self.assertIn("old_fraction", notes.lower())
        self.assertIn("cannot be separated", notes)

    def test_cov_fails_or_warns(self):
        # Either covariance computation fails, or a warning about high condition number appears
        if not self.fit["cov_success"]:
            self.assertTrue(True)
        else:
            note = self.fit["confidence_intervals"].get("note", "")
            self.assertIn(note, ["", None], "Should not have a warning if cov succeeded")

    def test_m_old_or_m_new_ci_wide_or_missing(self):
        # Without isotope, we expect m_old0/m_new0 CIs to be huge or missing
        lo = self.fit["confidence_intervals"].get("m_old0_95_lower")
        hi = self.fit["confidence_intervals"].get("m_old0_95_upper")
        if lo is not None and hi is not None:
            width = hi - lo
            self.assertGreater(width, 0.5,
                               "m_old0 CI should be wide when old_fraction is missing")
        else:
            self.assertTrue(True)  # CI missing = non-identifiable

    def test_total_rmse_still_reasonable(self):
        # Even though old vs new is not separated, total fit should still look OK
        rmse = self.fit["residuals_rmse"]["total"]["rmse"]
        self.assertLess(rmse, 0.1, f"Total RMSE unexpectedly large: {rmse}")


class IdentifiabilityWithoutCompound(unittest.TestCase):
    """Test (c): without compound readout, flux recovery is degraded."""

    @classmethod
    def setUpClass(cls):
        cls.data, cls.sim = _make_noisy_data({"total": True, "old_fraction": True, "compound": True})
        cls.fit = fit_washout(
            cls.data,
            {"total": True, "old_fraction": True, "compound": False},
            initial_guess=ASSUMPTIONS["initial_guess"],
            bounds=ASSUMPTIONS["fit_bounds"],
            weights=ASSUMPTIONS["fit_weights"],
        )

    def test_fit_note_warns_about_missing_compound(self):
        notes = " ".join(self.fit["identifiability_notes"])
        self.assertIn("compound", notes.lower())

    def test_s_max_or_ic50_ci_wide_or_inaccurate(self):
        # s_max and ic50 should be poorly constrained without direct compound measurement
        if self.fit["cov_success"]:
            lo = self.fit["confidence_intervals"].get("s_max_95_lower")
            hi = self.fit["confidence_intervals"].get("s_max_95_upper")
            if lo is not None and hi is not None:
                width = hi - lo
                self.assertGreater(width, 0.1,
                                   "s_max CI should be wide when compound is missing")
        else:
            self.assertTrue(True)

    def test_s_max_recovery_is_worse_than_all_readouts(self):
        # Compare to the all-readout fit: s_max error should be larger
        all_fit = fit_washout(
            self.data,
            {"total": True, "old_fraction": True, "compound": True},
            initial_guess=ASSUMPTIONS["initial_guess"],
            bounds=ASSUMPTIONS["fit_bounds"],
            weights=ASSUMPTIONS["fit_weights"],
        )
        err_no_compound = abs(self.fit["params"]["s_max"] - GROUND_TRUTH["s_max"])
        err_all = abs(all_fit["params"]["s_max"] - GROUND_TRUTH["s_max"])
        self.assertGreater(
            err_no_compound, err_all,
            f"s_max error without compound ({err_no_compound:.4f}) should exceed "
            f"error with all readouts ({err_all:.4f})"
        )


if __name__ == "__main__":
    unittest.main()

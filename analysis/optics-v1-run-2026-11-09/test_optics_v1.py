"""Unit tests for Phase 3 optics model v1."""
import json
import math
import unittest
from pathlib import Path

from simulate_optics_v1 import OpticsV1Model, lab, load_colorimetry, wavelengths

CONFIG = json.loads((Path(__file__).parent / "assumptions.json").read_text(encoding="utf-8"))
WLS = wavelengths(CONFIG["wavelengths_nm"])
COLORIMETRY = load_colorimetry(CONFIG, WLS)


class OpticsV1Checks(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model = OpticsV1Model(CONFIG)

    # 1. spectrum → CIELAB against known reference ---------------------------------

    def test_perfect_reflector_is_white_point(self):
        """A uniform reflectance of 1.0 across all wavelengths must give L* = 100, a* = 0, b* = 0."""
        c = lab([1.0] * len(WLS), COLORIMETRY)
        self.assertAlmostEqual(c["L_star"], 100.0, places=6)
        self.assertAlmostEqual(c["a_star"], 0.0, places=5)
        self.assertAlmostEqual(c["b_star"], 0.0, places=5)

    def test_flat_grey_is_neutral(self):
        """A uniform reflectance of 0.5 must have near-zero chroma."""
        c = lab([0.5] * len(WLS), COLORIMETRY)
        self.assertAlmostEqual(c["chroma"], 0.0, places=5)

    def test_dimming_preserves_hue_for_bright_spectra(self):
        """Halving a bright spectrum preserves hue angle; very dark spectra may shift due to CIELAB linear toe."""
        # Use pigment-free stroma (bright) for this invariant
        full_spec = self.model.compute(0.0, 0.0)["reflectance"]
        dim_spec = [0.5 * r for r in full_spec]
        full_lab = lab(full_spec, COLORIMETRY)
        dim_lab = lab(dim_spec, COLORIMETRY)
        self.assertAlmostEqual(full_lab["hue_degrees"], dim_lab["hue_degrees"], places=6)

    # 2. Nonnegativity of reflectance ------------------------------------------------

    def test_reflectance_is_never_negative(self):
        """Reflectance must be >= 0 for all explored parameter combinations."""
        for M_eu in (0.0, 0.5, 2.0, 10.0):
            for M_ph in (0.0, 0.5, 2.0):
                res = self.model.compute(M_eu, M_ph)
                self.assertTrue(all(r >= 0.0 for r in res["reflectance"]),
                                f"Negative reflectance at M_eu={M_eu}, M_ph={M_ph}")

    def test_reflectance_never_exceeds_one(self):
        """Reflectance must be <= 1 for all explored parameter combinations."""
        for M_eu in (0.0, 0.5, 2.0, 10.0):
            for M_ph in (0.0, 0.5, 2.0):
                res = self.model.compute(M_eu, M_ph)
                self.assertTrue(all(r <= 1.0 for r in res["reflectance"]),
                                f"Reflectance > 1 at M_eu={M_eu}, M_ph={M_ph}")

    # 3. Monotonic darkening with increasing eumelanin --------------------------------

    def test_increasing_eumelanin_monotonically_darkens(self):
        """L* must decrease (or stay equal) as stromal eumelanin increases."""
        masses = [0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
        L_stars = [self.model.compute(M_eu, 0.0)["L_star"] for M_eu in masses]
        self.assertEqual(L_stars, sorted(L_stars, reverse=True),
                         "L* is not monotonically non-increasing with eumelanin mass")

    def test_luminance_also_darkens(self):
        """CIE luminance Y must decrease as eumelanin increases."""
        masses = [0.0, 0.5, 1.0, 2.0, 5.0, 10.0]
        lums = [self.model.compute(M_eu, 0.0)["luminance"] for M_eu in masses]
        self.assertEqual(lums, sorted(lums, reverse=True))

    # 4. Model structure tests -------------------------------------------------------

    def test_pigment_free_stroma_has_nonzero_reflectance(self):
        """Without pigment, the stroma still backscatters, giving nonzero reflectance."""
        res = self.model.compute(0.0, 0.0)
        self.assertTrue(any(r > 0.01 for r in res["reflectance"]))

    def test_uncertainty_intervals_are_sensible(self):
        """Monte-Carlo CI must be wider than zero and contain the central estimate."""
        res = self.model.compute_with_uncertainty(2.0, 0.5)
        self.assertLess(res["CI_L_star"]["p2.5"], res["L_star"])
        self.assertGreater(res["CI_L_star"]["p97.5"], res["L_star"])

    def test_mie_Qsca_is_finite_and_reasonable(self):
        """Mie scattering efficiency must be finite and within [0, 4]."""
        from simulate_optics_v1 import mie_Qsca
        m = complex(1.7, 0.3) / 1.35
        for x in (1.0, 2.0, 3.0, 5.0, 8.0):
            q = mie_Qsca(m, x)
            self.assertTrue(math.isfinite(q), f"Qsca not finite at x={x}")
            self.assertGreaterEqual(q, 0.0)
            self.assertLessEqual(q, 4.0)


if __name__ == "__main__":
    unittest.main()

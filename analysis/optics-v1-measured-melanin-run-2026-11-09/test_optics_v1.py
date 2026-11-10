"""Unit tests for Phase 3 optics model v1."""
import json
import math
import unittest
from pathlib import Path

from simulate_optics_v1 import OpticsV1Model, lab, load_colorimetry, wavelengths, ROOT

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



    # 5. Measured melanin spectrum tests ------------------------------------------------

    def test_measured_eumelanin_normalized_at_550(self):
        from simulate_optics_v1 import read_melanin_table, melanin_shape
        cfg = CONFIG
        ms = cfg['melanin_spectra']
        shape_550 = melanin_shape(ROOT / ms['eumelanin_csv'], ms['eumelanin_sha256'], 550)
        self.assertAlmostEqual(shape_550, 1.0, places=6)

    def test_measured_pheomelanin_normalized_at_550(self):
        from simulate_optics_v1 import read_melanin_table, melanin_shape
        cfg = CONFIG
        ms = cfg['melanin_spectra']
        shape_550 = melanin_shape(ROOT / ms['pheomelanin_csv'], ms['pheomelanin_sha256'], 550)
        self.assertAlmostEqual(shape_550, 1.0, places=6)

    def test_eumelanin_shape_is_higher_at_400_than_700(self):
        from simulate_optics_v1 import melanin_shape
        cfg = CONFIG
        ms = cfg['melanin_spectra']
        eu_400 = melanin_shape(ROOT / ms['eumelanin_csv'], ms['eumelanin_sha256'], 400)
        eu_700 = melanin_shape(ROOT / ms['eumelanin_csv'], ms['eumelanin_sha256'], 700)
        self.assertGreater(eu_400, eu_700)

    def test_pheomelanin_has_red_shoulder_above_700(self):
        from simulate_optics_v1 import melanin_shape
        cfg = CONFIG
        ms = cfg['melanin_spectra']
        ph_755 = melanin_shape(ROOT / ms['pheomelanin_csv'], ms['pheomelanin_sha256'], 755)
        ph_760 = melanin_shape(ROOT / ms['pheomelanin_csv'], ms['pheomelanin_sha256'], 760)
        ph_770 = melanin_shape(ROOT / ms['pheomelanin_csv'], ms['pheomelanin_sha256'], 770)
        # The red shoulder is a local rise from 755→770, not a global exceedance of 700.
        self.assertGreater(ph_760, ph_755)
        self.assertGreater(ph_770, ph_755)

    def test_absorption_mass_coefficient_returns_finite_positive(self):
        for wl in self.model.wls:
            eu, ph = self.model.absorption_mass_coefficient(wl)
            self.assertTrue(math.isfinite(eu) and eu > 0, f'eumelanin not positive at {wl}')
            self.assertTrue(math.isfinite(ph) and ph > 0, f'pheomelanin not positive at {wl}')

    def test_pheomelanin_shape_is_more_peaked_than_eumelanin_at_400(self):
        # After normalization, both are 1.0 at 550. The measured pheomelanin shape at 400 is
        # higher relative to 550 than eumelanin (12.11/2.994 ≈ 4.04 vs 14.64/5.79 ≈ 2.53),
        # meaning pheomelanin falls off slower toward the blue than the old assumed exponent
        # predicted, and more slowly than eumelanin on a 550-normalized basis.
        from simulate_optics_v1 import melanin_shape
        cfg = CONFIG
        ms = cfg['melanin_spectra']
        eu = melanin_shape(ROOT / ms['eumelanin_csv'], ms['eumelanin_sha256'], 400)
        ph = melanin_shape(ROOT / ms['pheomelanin_csv'], ms['pheomelanin_sha256'], 400)
        self.assertGreater(ph, eu)


if __name__ == "__main__":
    unittest.main()

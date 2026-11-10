import json
import math
import unittest
from pathlib import Path

from simulate_hue_window_measured import (ROOT, angle_gap, classify, lab, load_colorimetry,
                                          load_melanin_shapes, melanin_shape, reference_reflectance,
                                          reflectance, wavelengths)

CONFIG = json.loads((Path(__file__).parent / "hue_window_assumptions_measured.json").read_text(encoding="utf-8"))
WLS = wavelengths(CONFIG["wavelengths_nm"])
COLORIMETRY = load_colorimetry(CONFIG, WLS)
EU_SHAPE, PH_SHAPE = load_melanin_shapes(CONFIG, WLS)
DARK = CONFIG["back_return_modes"]["dark_pigment_epithelium"]
REFERENCES = {n: [reference_reflectance(w, r) for w in WLS] for n, r in CONFIG["reference_stimuli"].items()}
WINDOWS = {n: lab(spectrum, COLORIMETRY) for n, spectrum in REFERENCES.items()}
MS = CONFIG["melanin_spectra"]


def spectrum(amount, share, stroma=(0.25, 4), phi=0.5, mode=DARK):
    return [reflectance(w, stroma, phi, amount, share, EU_SHAPE, PH_SHAPE, mode) for w in WLS]


def coords(*args, **kwargs):
    return lab(spectrum(*args, **kwargs), COLORIMETRY)


class HueWindowMeasuredChecks(unittest.TestCase):
    def test_flat_reflector_is_neutral(self):
        c = lab([0.4] * len(WLS), COLORIMETRY)
        self.assertAlmostEqual(c["chroma"], 0, places=9)
        self.assertAlmostEqual(c["luminance"], 0.4)

    def test_perfect_reflector_is_the_white_point(self):
        self.assertAlmostEqual(lab([1.0] * len(WLS), COLORIMETRY)["L_star"], 100)

    def test_dimming_a_spectrum_keeps_its_hue(self):
        for reference in REFERENCES.values():
            full, dim = lab(reference, COLORIMETRY), lab([.25 * r for r in reference], COLORIMETRY)
            self.assertAlmostEqual(full["hue_degrees"], dim["hue_degrees"], places=6)
            self.assertLess(dim["luminance"], full["luminance"])

    def test_references_fall_in_their_own_windows_only(self):
        for name, ref in WINDOWS.items():
            self.assertEqual(classify(ref, WINDOWS, 20, 1.0, 1.0), [name])

    def test_reflectance_is_a_fraction(self):
        for mode in CONFIG["back_return_modes"].values():
            for amount in CONFIG["pigment_absorbance_at_550nm"]:
                for stroma in ((0.1, 2), (1.0, 2), (1.0, 6)):
                    self.assertTrue(all(0 <= r <= 1 for r in spectrum(amount, .5, stroma, mode=mode)))

    def test_calibration_keeps_the_original_stroma_and_rejects_a_whitish_one(self):
        blue = lambda stroma: "blue" in classify(coords(0, 0, stroma), WINDOWS, 20, .25, .5)
        self.assertTrue(blue((0.25, 4)))
        self.assertFalse(blue((1.0, 2)))
        self.assertFalse(blue((0.25, 2)))

    def test_more_pigment_darkens_at_fixed_composition(self):
        lum = [coords(m, .3)["luminance"] for m in CONFIG["pigment_absorbance_at_550nm"]]
        self.assertEqual(lum, sorted(lum, reverse=True))

    def test_luminance_floor_excludes_dim_hue_matches(self):
        dim = lab([.1 * r for r in REFERENCES["orange"]], COLORIMETRY)
        self.assertIn("orange", classify(dim, WINDOWS, 20, 0))
        self.assertNotIn("orange", classify(dim, WINDOWS, 20, 0, .5))

    def test_every_translucent_return_exceeds_the_round_trip_of_the_measured_normal_iris(self):
        anchor = CONFIG["measured_anchors"][0]["effective_transmission"]["red"]
        for mode in CONFIG["back_return_modes"].values():
            if mode["type"] == "red_edge":
                self.assertGreater(mode["plateau"], anchor ** 2)
                self.assertGreater(math.sqrt(mode["plateau"]), anchor)

    def test_angle_gap_wraps(self):
        self.assertAlmostEqual(angle_gap(350, 10), 20)

    # Measured-spectrum checks ----------------------------------------------------

    def test_measured_eumelanin_normalized_at_550(self):
        shape_550 = melanin_shape(ROOT / MS["eumelanin_csv"], MS["eumelanin_sha256"], 550)
        self.assertAlmostEqual(shape_550, 1.0, places=6)

    def test_measured_pheomelanin_normalized_at_550(self):
        shape_550 = melanin_shape(ROOT / MS["pheomelanin_csv"], MS["pheomelanin_sha256"], 550)
        self.assertAlmostEqual(shape_550, 1.0, places=6)

    def test_eumelanin_shape_is_higher_at_400_than_700(self):
        eu_400 = melanin_shape(ROOT / MS["eumelanin_csv"], MS["eumelanin_sha256"], 400)
        eu_700 = melanin_shape(ROOT / MS["eumelanin_csv"], MS["eumelanin_sha256"], 700)
        self.assertGreater(eu_400, eu_700)

    def test_pheomelanin_has_red_shoulder_above_700(self):
        ph_755 = melanin_shape(ROOT / MS["pheomelanin_csv"], MS["pheomelanin_sha256"], 755)
        ph_760 = melanin_shape(ROOT / MS["pheomelanin_csv"], MS["pheomelanin_sha256"], 760)
        ph_770 = melanin_shape(ROOT / MS["pheomelanin_csv"], MS["pheomelanin_sha256"], 770)
        # The red shoulder is a local rise from 755→770, not a global exceedance of 700.
        self.assertGreater(ph_760, ph_755)
        self.assertGreater(ph_770, ph_755)

    def test_pheomelanin_shape_is_more_peaked_than_eumelanin_at_400(self):
        # After normalization, both are 1.0 at 550. The measured pheomelanin shape at 400 is
        # higher relative to 550 than eumelanin (12.11/2.994 ≈ 4.04 vs 14.64/5.79 ≈ 2.53).
        eu = melanin_shape(ROOT / MS["eumelanin_csv"], MS["eumelanin_sha256"], 400)
        ph = melanin_shape(ROOT / MS["pheomelanin_csv"], MS["pheomelanin_sha256"], 400)
        self.assertGreater(ph, eu)

    def test_pure_pheomelanin_differs_from_pure_eumelanin(self):
        eu, pheo = (spectrum(1, q) for q in (0, 1))
        self.assertTrue(any(abs(a - b) > 1e-9 for a, b in zip(eu, pheo)))

    def test_dimming_a_bright_model_spectrum_preserves_hue(self):
        bright = spectrum(0, 0)  # pigment-free stroma is bright
        full, dim = lab(bright, COLORIMETRY), lab([.25 * r for r in bright], COLORIMETRY)
        self.assertAlmostEqual(full["hue_degrees"], dim["hue_degrees"], places=6)


if __name__ == "__main__":
    unittest.main()

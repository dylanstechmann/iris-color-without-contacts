import json
import math
import unittest
from pathlib import Path

from simulate_hue_window import (angle_gap, classify, lab, load_colorimetry, reference_reflectance,
                                 reflectance, wavelengths)

CONFIG = json.loads((Path(__file__).parent / "hue_window_assumptions.json").read_text(encoding="utf-8"))
WLS = wavelengths(CONFIG["wavelengths_nm"])
COLORIMETRY = load_colorimetry(CONFIG, WLS)
DARK = CONFIG["back_return_modes"]["dark_pigment_epithelium"]
EU = CONFIG["eumelanin_spectral_exponent"]
REFERENCES = {n: [reference_reflectance(w, r) for w in WLS] for n, r in CONFIG["reference_stimuli"].items()}
WINDOWS = {n: lab(spectrum, COLORIMETRY) for n, spectrum in REFERENCES.items()}


def spectrum(amount, share, stroma=(0.25, 4), phi=0.5, mode=DARK, np_=10):
    return [reflectance(w, stroma, phi, amount, share, EU, np_, mode) for w in WLS]


def coords(*args, **kwargs):
    return lab(spectrum(*args, **kwargs), COLORIMETRY)


class HueWindowChecks(unittest.TestCase):
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

    def test_steeper_pheomelanin_trades_blue_for_red_and_yellows_the_hue(self):
        eu, pheo = (spectrum(1, q, np_=10) for q in (0, 1))
        self.assertGreater(pheo[WLS.index(650)], eu[WLS.index(650)])
        self.assertLess(pheo[WLS.index(450)], eu[WLS.index(450)])
        self.assertGreater(lab(pheo, COLORIMETRY)["b_star"], lab(eu, COLORIMETRY)["b_star"])

    def test_pheomelanin_with_the_eumelanin_exponent_changes_nothing(self):
        same = (spectrum(1, q, np_=EU) for q in (0, 1))
        for a, b in zip(*same):
            self.assertAlmostEqual(a, b)

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


if __name__ == "__main__":
    unittest.main()

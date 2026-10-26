import json
import unittest
from pathlib import Path

from simulate_hue_window import (angle_gap, classify, lab, load_colorimetry, reference_reflectance,
                                 reflectance, wavelengths)

CONFIG = json.loads((Path(__file__).parent / "hue_window_assumptions.json").read_text(encoding="utf-8"))
WLS = wavelengths(CONFIG["wavelengths_nm"])
COLORIMETRY = load_colorimetry(CONFIG, WLS)
DARK = CONFIG["back_return_modes"]["dark_pigment_epithelium"]
REFERENCES = {n: [reference_reflectance(w, r) for w in WLS] for n, r in CONFIG["reference_stimuli"].items()}
WINDOWS = {n: lab(spectrum, COLORIMETRY) for n, spectrum in REFERENCES.items()}


def coords(amount, share, mode=DARK, ne=3.3, np_=4.5):
    return lab([reflectance(w, CONFIG, amount, share, ne, np_, mode) for w in WLS], COLORIMETRY)


class HueWindowChecks(unittest.TestCase):
    def test_flat_reflector_is_neutral(self):
        c = lab([0.4] * len(WLS), COLORIMETRY)
        self.assertAlmostEqual(c["chroma"], 0, places=9)
        self.assertAlmostEqual(c["luminance"], 0.4)

    def test_perfect_reflector_is_the_white_point(self):
        self.assertAlmostEqual(lab([1.0] * len(WLS), COLORIMETRY)["L_star"], 100)

    def test_dimming_a_spectrum_keeps_its_hue(self):
        for spectrum in REFERENCES.values():
            full, dim = lab(spectrum, COLORIMETRY), lab([.25 * r for r in spectrum], COLORIMETRY)
            self.assertAlmostEqual(full["hue_degrees"], dim["hue_degrees"], places=6)
            self.assertLess(dim["luminance"], full["luminance"])

    def test_references_fall_in_their_own_windows_only(self):
        for name, ref in WINDOWS.items():
            self.assertEqual(classify(ref, WINDOWS, 20, 1.0, 1.0), [name])

    def test_reflectance_is_a_fraction(self):
        for mode in CONFIG["back_return_modes"].values():
            for amount in CONFIG["pigment_absorbance_at_550nm"]:
                for w in WLS:
                    self.assertTrue(0 <= reflectance(w, CONFIG, amount, .5, 3.3, 6, mode) <= 1)

    def test_unpigmented_stroma_over_dark_back_is_blue_window(self):
        self.assertIn("blue", classify(coords(0, 0), WINDOWS, 20, .25))

    def test_more_pigment_darkens_at_fixed_composition(self):
        lum = [coords(m, .3)["luminance"] for m in CONFIG["pigment_absorbance_at_550nm"]]
        self.assertEqual(lum, sorted(lum, reverse=True))

    def test_steeper_pheomelanin_trades_blue_for_red_and_yellows_the_hue(self):
        eu, pheo = ([reflectance(w, CONFIG, 1, q, 3.3, 4.5, DARK) for w in WLS] for q in (0, 1))
        self.assertGreater(pheo[WLS.index(650)], eu[WLS.index(650)])
        self.assertLess(pheo[WLS.index(450)], eu[WLS.index(450)])
        self.assertGreater(lab(pheo, COLORIMETRY)["b_star"], lab(eu, COLORIMETRY)["b_star"])

    def test_luminance_floor_excludes_dim_hue_matches(self):
        dim = lab([.1 * r for r in REFERENCES["orange"]], COLORIMETRY)
        self.assertIn("orange", classify(dim, WINDOWS, 20, 0))
        self.assertNotIn("orange", classify(dim, WINDOWS, 20, 0, .5))

    def test_angle_gap_wraps(self):
        self.assertAlmostEqual(angle_gap(350, 10), 20)


if __name__ == "__main__":
    unittest.main()

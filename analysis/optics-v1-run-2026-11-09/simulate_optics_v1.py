"""Phase 3 optics model v1: layered Beer–Lambert with first-scattering correction.

Maps pigment inventory (stromal eumelanin/pheomelanin mass/area, melanosome size/density,
IPE background) to spectral reflectance 400–700 nm and CIELAB, with uncertainty intervals.

Reuses the hue-window CIE table loading and CIELAB conversion.
Standard library + numpy only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import random
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent


def wavelengths(spec):
    return list(range(spec["start"], spec["stop"] + 1, spec["step"]))


def read_table(path, expected_sha256):
    blob = path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != expected_sha256:
        raise ValueError("Table differs from its pinned CIE checksum: " + str(path))
    return {int(row[0]): [float(v) for v in row[1:]] for row in csv.reader(blob.decode("utf-8").splitlines())}


def load_colorimetry(config, wls):
    """Illuminant-weighted colour-matching functions at the model wavelengths, plus the perfect-reflector white."""
    spec = config["colorimetry"]
    cmf = read_table(ROOT / spec["observer_csv"], spec["observer_sha256"])
    illuminant = read_table(ROOT / spec["illuminant_csv"], spec["illuminant_sha256"])
    weights = [[illuminant[wl][0] * value for value in cmf[wl]] for wl in wls]
    return {"weights": weights, "white": [sum(w[i] for w in weights) for i in range(3)]}


def lab(spectrum, colorimetry):
    """CIE 1976 L*a*b*."""
    xyz = [sum(r * w[i] for r, w in zip(spectrum, colorimetry["weights"])) / colorimetry["white"][i]
           for i in range(3)]
    f = [t ** (1 / 3) if t > (6 / 29) ** 3 else t / (3 * (6 / 29) ** 2) + 4 / 29 for t in xyz]
    a, b = 500 * (f[0] - f[1]), 200 * (f[1] - f[2])
    return {"L_star": 116 * f[1] - 16, "a_star": a, "b_star": b, "chroma": math.hypot(a, b),
            "hue_degrees": math.degrees(math.atan2(b, a)) % 360, "luminance": xyz[1]}


def delta_E(lab1, lab2):
    return math.sqrt((lab1["L_star"] - lab2["L_star"]) ** 2
                     + (lab1["a_star"] - lab2["a_star"]) ** 2
                     + (lab1["b_star"] - lab2["b_star"]) ** 2)


# ---------------------------------------------------------------------------
# Mie scattering for spherical particles (Riccati-Bessel upward recurrence)
# ---------------------------------------------------------------------------

def _riccati_psi(z, n_max):
    """Riccati-Bessel ψ_n(z) = z * j_n(z) via upward recurrence."""
    psi = np.zeros(n_max + 1, dtype=complex)
    psi[0] = np.sin(z)
    if n_max >= 1:
        psi[1] = np.sin(z) / z - np.cos(z)
    for n in range(2, n_max + 1):
        psi[n] = (2 * n - 1) / z * psi[n - 1] - psi[n - 2]
    return psi


def _riccati_chi(x, n_max):
    """Riccati-Bessel χ_n(x) = -x * y_n(x) for real x."""
    chi = np.zeros(n_max + 1)
    chi[0] = np.cos(x)
    if n_max >= 1:
        chi[1] = np.cos(x) / x + np.sin(x)
    for n in range(2, n_max + 1):
        chi[n] = (2 * n - 1) / x * chi[n - 1] - chi[n - 2]
    return chi


def mie_Qsca(m, x):
    """
    Scattering efficiency Qsca for a sphere with complex relative refractive index m
    and size parameter x = π*d/λ.  Returns Qsca (float, clipped to [0, 4]).
    Uses Riccati-Bessel upward recurrence; stable for x < ~10.
    """
    if x <= 0.01:
        return 0.0

    n_max = int(np.ceil(x + 4 * x ** (1 / 3) + 2))

    psi_x = _riccati_psi(x, n_max)
    chi_x = _riccati_chi(x, n_max)
    xi_x = psi_x + 1j * chi_x

    mx = m * x
    psi_mx = _riccati_psi(mx, n_max)

    # Derivatives: S_n'(z) = S_{n-1}(z) - n/z * S_n(z)
    dpsi_x = np.zeros(n_max + 1, dtype=complex)
    dpsi_mx = np.zeros(n_max + 1, dtype=complex)
    dxi_x = np.zeros(n_max + 1, dtype=complex)

    dpsi_x[0] = np.cos(x)
    dpsi_mx[0] = np.cos(mx)
    dxi_x[0] = np.cos(x) - 1j * np.sin(x)

    for n in range(1, n_max + 1):
        dpsi_x[n] = psi_x[n - 1] - n / x * psi_x[n]
        dpsi_mx[n] = psi_mx[n - 1] - n / mx * psi_mx[n]
        dxi_x[n] = xi_x[n - 1] - n / x * xi_x[n]

    a = np.zeros(n_max, dtype=complex)
    b = np.zeros(n_max, dtype=complex)

    for n in range(1, n_max + 1):
        denom_a = m * psi_mx[n] * dxi_x[n] - xi_x[n] * dpsi_mx[n]
        denom_b = psi_mx[n] * dxi_x[n] - m * xi_x[n] * dpsi_mx[n]

        if abs(denom_a) < 1e-30:
            a[n - 1] = 0
        else:
            a[n - 1] = (m * psi_mx[n] * dpsi_x[n] - psi_x[n] * dpsi_mx[n]) / denom_a

        if abs(denom_b) < 1e-30:
            b[n - 1] = 0
        else:
            b[n - 1] = (psi_mx[n] * dpsi_x[n] - m * psi_x[n] * dpsi_mx[n]) / denom_b

    n_vals = np.arange(1, n_max + 1)
    Qsca = (2 / x ** 2) * np.sum((2 * n_vals + 1) * (np.abs(a) ** 2 + np.abs(b) ** 2))
    return float(max(0.0, min(Qsca, 4.0)))


# ---------------------------------------------------------------------------
# Model physics
# ---------------------------------------------------------------------------

class OpticsV1Model:
    """Layered forward model: pigment inventory → reflectance → CIELAB."""

    def __init__(self, assumptions):
        self.assumptions = assumptions
        self.wls = wavelengths(assumptions["wavelengths_nm"])
        self.colorimetry = load_colorimetry(assumptions, self.wls)

        # Convenience aliases
        self.mel = assumptions["melanin_absorption"]
        self.opt = assumptions["melanosome_optics"]
        self.geom = assumptions["layer_geometry"]
        self.dens = assumptions["melanosome_density"]
        self.ipe = assumptions["ipe_background"]

    def absorption_mass_coefficient(self, wl_nm):
        """Specific absorption ε(λ) in cm²/µg for each melanin type."""
        eu = self.mel["eumelanin_specific_absorbance_550_cm2_per_ug"] * (550.0 / wl_nm) ** self.mel["eumelanin_spectral_exponent"]
        ph = self.mel["pheomelanin_specific_absorbance_550_cm2_per_ug"] * (550.0 / wl_nm) ** self.mel["pheomelanin_spectral_exponent"]
        return eu, ph

    def mie_scattering(self, wl_nm):
        """Return Qsca at wavelength wl_nm for the stated melanosome diameter and refractive index."""
        d_nm = self.opt["melanosome_diameter_nm"]
        x = math.pi * d_nm / wl_nm  # size parameter
        n_mel = complex(self.opt["melanosome_refractive_index_real"], self.opt["melanosome_refractive_index_imag"])
        n_med = self.opt["stromal_medium_refractive_index"]
        m_rel = n_mel / n_med
        return mie_Qsca(m_rel, x)

    def scattering_coefficient(self, wl_nm):
        """Reduced backscattering-related coefficient components."""
        d_nm = self.opt["melanosome_diameter_nm"]
        d_cm = d_nm * 1e-7  # nm → cm
        r_cm = d_cm / 2.0

        Qsca = self.mie_scattering(wl_nm)
        sigma_sc_cm2 = Qsca * math.pi * r_cm ** 2

        N = self.dens["number_density_cm3"]
        mus = N * sigma_sc_cm2  # cm⁻¹
        g = self.opt["scattering_anisotropy_g"]
        mus_back = mus * (1.0 - g) / 2.0
        return mus, mus_back

    def compute(self, M_eu, M_ph, d_mel=None, N_mel=None, M_ipe=None):
        """
        Forward evaluation for a single parameter set.

        Inputs:
            M_eu  — stromal eumelanin mass per area (µg/cm²)
            M_ph  — stromal pheomelanin mass per area (µg/cm²)
            d_mel — melanosome diameter (nm); default from assumptions
            N_mel — melanosome number density (cm⁻³); default from assumptions
            M_ipe — IPE eumelanin mass per area (µg/cm²); default from assumptions

        Returns dict with reflectance_spectrum, CIELAB, and component spectra.
        """
        if d_mel is None:
            d_mel = self.opt["melanosome_diameter_nm"]
        if N_mel is None:
            N_mel = self.dens["number_density_cm3"]
        if M_ipe is None:
            M_ipe = self.ipe["ipe_eumelanin_mass_ug_per_cm2"]

        L_s = self.geom["stromal_thickness_cm"]
        phi = self.assumptions["path_fraction"]

        reflectance = []
        for wl in self.wls:
            eu_eps, ph_eps = self.absorption_mass_coefficient(wl)

            # Single-pass dimensionless absorbance A = ε * M
            A_eu = eu_eps * M_eu
            A_ph = ph_eps * M_ph
            A_total = A_eu + A_ph

            # Scattering (using temporary overrides for d_mel and N_mel)
            # We recompute Qsca with the supplied d_mel; anisotropy g stays from assumptions.
            d_cm = d_mel * 1e-7
            r_cm = d_cm / 2.0
            x = math.pi * d_mel / wl
            n_mel = complex(self.opt["melanosome_refractive_index_real"],
                            self.opt["melanosome_refractive_index_imag"])
            n_med = self.opt["stromal_medium_refractive_index"]
            m_rel = n_mel / n_med
            Qsca = mie_Qsca(m_rel, x)
            sigma_sc = Qsca * math.pi * r_cm ** 2
            mus = N_mel * sigma_sc
            g = self.opt["scattering_anisotropy_g"]
            mus_back = mus * (1.0 - g) / 2.0

            # Backscatter fraction: probability of at least one backscattering event
            # in a single pass through the stroma. Bounded at 1.
            B = 1.0 - math.exp(-mus_back * L_s)
            B = min(B, 1.0)

            # IPE reflectance (Beer–Lambert through IPE and back)
            ipe_base = self.ipe["ipe_base_reflectance"]
            ipe_eps = eu_eps  # IPE absorption uses eumelanin spectrum
            ipe_absorbance = ipe_eps * M_ipe  # dimensionless
            rho = ipe_base * math.exp(-2.0 * ipe_absorbance)

            # Layered reflectance (same functional form as hue-window)
            R = B * math.exp(-2.0 * phi * A_total) + (1.0 - B) * math.exp(-2.0 * A_total) * rho
            R = max(0.0, min(R, 1.0))
            reflectance.append(R)

        coords = lab(reflectance, self.colorimetry)
        return {
            "wavelengths_nm": self.wls,
            "reflectance": reflectance,
            "L_star": coords["L_star"],
            "a_star": coords["a_star"],
            "b_star": coords["b_star"],
            "chroma": coords["chroma"],
            "hue_degrees": coords["hue_degrees"],
            "luminance": coords["luminance"],
        }

    def compute_with_uncertainty(self, M_eu, M_ph, d_mel=None, N_mel=None, M_ipe=None):
        """
        Monte-Carlo prediction with 95 % confidence intervals.
        Perturbs the uncertain physical parameters log-normally.
        """
        rng = random.Random(self.assumptions["monte_carlo"]["random_seed"])
        n_samples = self.assumptions["monte_carlo"]["samples"]

        spectra = []
        labs = []

        def lognormal_sample(log_mean, log_sigma):
            return math.exp(rng.gauss(log_mean, log_sigma))

        for _ in range(n_samples):
            snapshot = json.loads(json.dumps(self.assumptions))  # deep copy
            mod = OpticsV1Model(snapshot)

            # Perturb positive physical parameters using assumed ranges
            def perturb(key, base, lo, hi):
                # Approximate log-normal: mean = base, ±2σ ≈ [lo, hi]
                if base <= 0 or lo <= 0 or hi <= lo:
                    return base
                log_mean = math.log(base)
                log_sigma = (math.log(hi) - math.log(lo)) / 4.0
                return lognormal_sample(log_mean, log_sigma)

            mel = mod.mel
            mel["eumelanin_specific_absorbance_550_cm2_per_ug"] = perturb(
                "eu_eps", mel["eumelanin_specific_absorbance_550_cm2_per_ug"],
                *mel["eumelanin_specific_absorbance_range"])
            mel["pheomelanin_specific_absorbance_550_cm2_per_ug"] = perturb(
                "ph_eps", mel["pheomelanin_specific_absorbance_550_cm2_per_ug"],
                *mel["pheomelanin_specific_absorbance_range"])

            opt = mod.opt
            opt["melanosome_diameter_nm"] = perturb(
                "d_mel", opt["melanosome_diameter_nm"],
                *opt["melanosome_diameter_nm_range"])
            opt["scattering_anisotropy_g"] = max(0.5, min(0.99, rng.gauss(
                opt["scattering_anisotropy_g"],
                (opt["scattering_anisotropy_g_range"][1] - opt["scattering_anisotropy_g_range"][0]) / 4.0)))

            mod.geom["stromal_thickness_cm"] = perturb(
                "L_s", mod.geom["stromal_thickness_cm"],
                *mod.geom["stromal_thickness_cm_range"])

            mod.dens["number_density_cm3"] = perturb(
                "N_mel", mod.dens["number_density_cm3"],
                *mod.dens["number_density_cm3_range"])

            mod.ipe["ipe_eumelanin_mass_ug_per_cm2"] = perturb(
                "M_ipe", mod.ipe["ipe_eumelanin_mass_ug_per_cm2"],
                *mod.ipe["ipe_eumelanin_mass_range"])

            # Optionally perturb the exponents slightly
            mel["pheomelanin_spectral_exponent"] = max(2.0, rng.gauss(
                mel["pheomelanin_spectral_exponent"],
                (mel["pheomelanin_spectral_exponent_range"][1] - mel["pheomelanin_spectral_exponent_range"][0]) / 4.0))

            res = mod.compute(M_eu, M_ph, d_mel, N_mel, M_ipe)
            spectra.append(res["reflectance"])
            labs.append({k: res[k] for k in ("L_star", "a_star", "b_star", "chroma", "hue_degrees", "luminance")})

        # Aggregate percentiles
        spectra_arr = np.array(spectra)
        labs_arr = {k: np.array([l[k] for l in labs]) for k in labs[0]}

        def pct(arr, p):
            return float(np.percentile(arr, p))

        ci_reflectance = [{"p2.5": pct(spectra_arr[:, i], 2.5),
                           "p97.5": pct(spectra_arr[:, i], 97.5)}
                          for i in range(len(self.wls))]

        ci_lab = {k: {"p2.5": pct(v, 2.5), "p97.5": pct(v, 97.5)} for k, v in labs_arr.items()}

        # Central estimate uses nominal parameters
        central = self.compute(M_eu, M_ph, d_mel, N_mel, M_ipe)
        central["CI_reflectance"] = ci_reflectance
        central["CI_L_star"] = ci_lab["L_star"]
        central["CI_a_star"] = ci_lab["a_star"]
        central["CI_b_star"] = ci_lab["b_star"]
        central["CI_chroma"] = ci_lab["chroma"]
        central["CI_hue_degrees"] = ci_lab["hue_degrees"]
        central["CI_luminance"] = ci_lab["luminance"]
        central["monte_carlo_samples"] = n_samples
        return central


# ---------------------------------------------------------------------------
# CLI and report generation
# ---------------------------------------------------------------------------

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def run(config, out):
    out.mkdir(parents=True, exist_ok=False)
    model = OpticsV1Model(config)
    wls = model.wls

    # Scenario grid: vary the key inventory variables
    scenarios = []
    grid = []
    for M_eu in (0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0):
        for M_ph in (0.0, 0.2, 0.5, 1.0, 2.0):
            # Skip redundant pigment-free cases
            if M_eu == 0.0 and M_ph not in (0.0, 0.5):
                continue
            grid.append((M_eu, M_ph))

    for M_eu, M_ph in grid:
        result = model.compute_with_uncertainty(M_eu, M_ph)
        scenarios.append({
            "M_eu_ug_cm2": M_eu,
            "M_ph_ug_cm2": M_ph,
            "L_star": result["L_star"],
            "a_star": result["a_star"],
            "b_star": result["b_star"],
            "chroma": result["chroma"],
            "hue_degrees": result["hue_degrees"],
            "luminance": result["luminance"],
            "CI_L_star": result["CI_L_star"],
            "CI_a_star": result["CI_a_star"],
            "CI_b_star": result["CI_b_star"],
        })

    # Save scenario sweep
    write_json(out / "scenario_sweep.json", {
        "activity": "Phase 3 optics model v1 forward sweep",
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
    })

    # Save a representative spectrum (medium pigment)
    representative = model.compute_with_uncertainty(5.0, 0.5)
    write_json(out / "representative_spectrum.json", {
        "M_eu_ug_cm2": 5.0,
        "M_ph_ug_cm2": 0.5,
        "wavelengths_nm": representative["wavelengths_nm"],
        "reflectance": representative["reflectance"],
        "CI_reflectance": representative["CI_reflectance"],
        "CIELAB": {k: representative[k] for k in ("L_star", "a_star", "b_star", "chroma", "hue_degrees", "luminance")},
        "CI_CIELAB": {k: representative["CI_" + k] for k in ("L_star", "a_star", "b_star", "chroma", "hue_degrees", "luminance")},
    })

    # Hue-window calibration comparison: pigment-free stroma over dark IPE
    pigment_free = model.compute(0.0, 0.0)

    # Calibration-style stroma backscatter check: compute B at 550 nm with nominal params
    wl_550 = 550
    d_nm = model.opt["melanosome_diameter_nm"]
    x = math.pi * d_nm / wl_550
    n_mel = complex(model.opt["melanosome_refractive_index_real"], model.opt["melanosome_refractive_index_imag"])
    m_rel = n_mel / model.opt["stromal_medium_refractive_index"]
    Qsca_550 = mie_Qsca(m_rel, x)
    r_cm = d_nm * 1e-7 / 2.0
    sigma_sc_550 = Qsca_550 * math.pi * r_cm ** 2
    mus_550 = model.dens["number_density_cm3"] * sigma_sc_550
    mus_back_550 = mus_550 * (1.0 - model.opt["scattering_anisotropy_g"]) / 2.0
    L_s = model.geom["stromal_thickness_cm"]
    B_550 = 1.0 - math.exp(-mus_back_550 * L_s)

    # Validation metrics against hue-window calibrated blue stroma
    # The hue-window stroma settings that were blue-calibrated had backscatter_550nm in {0.1,0.25,0.4}
    # and exponents that fell in the blue window. Our B_550 is a single computed value.
    hue_window_blue_settings = [
        {"backscatter_550nm": 0.1, "exponent": 4, "blue_calibrated": True},
        {"backscatter_550nm": 0.1, "exponent": 6, "blue_calibrated": True},
        {"backscatter_550nm": 0.25, "exponent": 4, "blue_calibrated": True},
        {"backscatter_550nm": 0.25, "exponent": 6, "blue_calibrated": True},
        {"backscatter_550nm": 0.4, "exponent": 4, "blue_calibrated": True},
    ]

    calibration = {
        "computed_B_550nm": B_550,
        "computed_Qsca_550nm": Qsca_550,
        "computed_mus_550nm_cm1": mus_550,
        "computed_mus_back_550nm_cm1": mus_back_550,
        "hue_window_blue_settings": hue_window_blue_settings,
        "comparison_note": "B_550 is a single nominal value; hue-window explored a grid. The model should be compared to the calibrated stroma settings that read blue when pigment-free.",
        "pigment_free_CIELAB": {k: pigment_free[k] for k in ("L_star", "a_star", "b_star", "chroma", "hue_degrees")},
    }
    write_json(out / "calibration_comparison.json", calibration)

    # Decision gate: tolerance residuals (placeholder until calibration data obtained)
    # We can compute self-consistency checks but not true held-out validation.
    gate = {
        "status": "unevaluated — no published iris reflectance spectra obtained for calibration",
        "delta_E_tolerance": config["model_limits"]["delta_E_tolerance"],
        "reflectance_rmse_tolerance_percent": config["model_limits"]["reflectance_rmse_tolerance_percent"],
        "self_consistency_checks": {
            "pigment_free_nonnegative_reflectance": all(r >= 0 for r in pigment_free["reflectance"]),
            "pigment_free_reflectance_leq_one": all(r <= 1 for r in pigment_free["reflectance"]),
            "monotonic_L_star_with_eu": True,  # verified below
        },
        "calibration_data_access": "Attempted programmatic fetch — see MODEL_REPORT.md for result.",
    }

    # Verify monotonic darkening with eumelanin
    prev_L = None
    monotonic = True
    for M_eu in (0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0):
        res = model.compute(M_eu, 0.0)
        if prev_L is not None and res["L_star"] > prev_L:
            monotonic = False
        prev_L = res["L_star"]
    gate["self_consistency_checks"]["monotonic_L_star_with_eu"] = monotonic

    write_json(out / "gate_status.json", gate)

    # Receipt
    source = Path(__file__).resolve()
    script_sha = hashlib.sha256(source.read_bytes()).hexdigest()

    files = {}
    for path in sorted(out.iterdir()):
        if path.is_file():
            blob = path.read_bytes()
            files[path.name] = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}

    inputs = {}
    for key in ("observer_csv", "illuminant_csv"):
        p = ROOT / config["colorimetry"][key]
        blob = p.read_bytes()
        inputs[config["colorimetry"][key]] = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}

    write_json(out / "receipt.json", {
        "model_status": "Phase 3 optics v1 forward model",
        "python": platform.python_version(),
        "numpy": str(np.__version__),
        "assumptions_sha256": hashlib.sha256((ROOT / "assumptions.json").read_bytes()).hexdigest(),
        "script_sha256": script_sha,
        "inputs": inputs,
        "scenario_count": len(scenarios),
        "outputs": files,
    })

    print(json.dumps({
        "scenarios": len(scenarios),
        "output": str(out),
        "B_550nm": round(B_550, 4),
        "pigment_free_L_star": round(pigment_free["L_star"], 2),
        "monotonic_L_star": monotonic,
    }))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assumptions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(json.loads(args.assumptions.read_text(encoding="utf-8")), args.out)

# Phase 3 optics model v1 — inventory-to-appearance forward mapping (measured melanin spectra)

*November 9, 2026. AI-assisted implementation, owner-reviewed planning document. This is a tissue-optics research model, not a clinical prediction, product design, or safety assessment.*

## 1. What the model does

Maps pigment **inventory** variables to iris **appearance** predictions:

- **Inputs:** stromal eumelanin mass/area (µg/cm²), stromal pheomelanin mass/area (µg/cm²), melanosome effective diameter (nm), melanosome number density (cm⁻³), IPE background pigment mass/area (µg/cm²).
- **Outputs:** spectral reflectance 400–700 nm at 10 nm intervals; CIE 1976 L*a*b* under D65, 2° observer; 95 % Monte-Carlo confidence intervals from parameter uncertainty propagation.

This run replaces the previously assumed power-law melanin absorption spectra with the measured Sarna & Swartz 1988 extinction coefficients (Oregon Medical Laser Center / Waterloo NPSG), linearly interpolated and normalized to 1.0 at 550 nm. The 550 nm specific-absorbance magnitudes remain order-of-magnitude assumptions because no iris-specific mass-absorption calibration was found.

The forward path is:
1. Convert pigment mass/area to wavelength-dependent absorption coefficients using the measured Sarna & Swartz 1988 spectral shapes (550-normalized), multiplied by the assumed 550 nm specific-absorbance magnitude.
2. Approximate melanosome scattering by Mie theory (Riccati-Bessel upward recurrence for Qsca) with a representative forward-peaked anisotropy g = 0.85.
3. Beer–Lambert v1 with first-scattering correction: backscatter probability B(λ) = 1 − exp(−μs,back·L), bounded at 1, plus a transmitted term through the IPE background.
4. Reflectance → CIE XYZ → CIELAB using the repo's SHA-pinned CIE tables (CIE 1931 2° observer, illuminant D65).

## 2. Software and reuse

- **Standard library + NumPy** (permitted by spec; hue-window scripts use standard library only).
- **Reused machinery:** CIE table loading with SHA-256 verification and CIELAB conversion are copied unchanged from `analysis/simulate_hue_window.py`. The v1 model reuses the same pinned CIE tables in `analysis/cie-tables/`.
- **Measured melanin spectra:** `analysis/melanin-spectra/sarna_swartz_1988_eumelanin.csv` and `sarna_swartz_1988_pheomelanin.csv`, SHA-256 pinned, with a `README.md` documenting provenance.
- **New code:** `simulate_optics_v1.py` implements the layered physics, Mie Qsca, and Monte-Carlo uncertainty. A module-level cache was added to `read_melanin_table` to avoid re-reading the CSV file on every wavelength during model construction; this is a pure performance optimization with no effect on computed results.

## 3. Calibration / validation attempt

### 3.1 Published iris reflectance data — access gap documented

The specification requires a calibration against published iris reflectance spectra. The following primary sources were attempted:

| Source | Attempt | Result |
|---|---|---|
| Bashkatov et al. 2006, Proc. SPIE 6085, DOI [10.1117/12.659176](https://doi.org/10.1117/12.659176) | DOI fetch | Citation metadata only; paywalled PDF; no open spectral dataset |
| Baranoski & Lam 2006, "A Predictive Light Transport Model for the Human Iris," Eurographics 2006 | PDF fetch from `npsg.uwaterloo.ca` | Paywalled / binary PDF returned; no open reflectance tabulated data |
| Vilaseca et al. 2008, *Applied Optics* 47:5622, DOI [10.1364/AO.47.005622](https://doi.org/10.1364/AO.47.005622) | Web search and Optica abstract | Behind Optica paywall; 100 real-iris measurements exist in the paper but were not accessible programmatically |
| Vilaseca et al. 2006, CGIV, "Estimation of Human Iris Spectral Reflectance" | Web search | Conference abstract available; no open dataset found |

**Conclusion:** No published iris reflectance spectrum dataset was obtainable programmatically on this attempt. The project expansion plan's $0-compute path for G3 cannot complete a full independent-spectrum calibration until either (a) an institutional login provides access to the Bashkatov or Vilaseca data, or (b) a library request is fulfilled. This gap is recorded as a project risk per the optics specification Section 8.2.

### 3.2 Fallback calibration against hue-window stroma settings

Because the primary calibration spectra were not accessible, the v1 model was checked against the existing hue-window run's calibrated stroma settings as a **self-consistency and parameter-range sanity check**, not as an independent validation.

| Check | Hue-window calibrated setting | Optics v1 nominal output | Interpretation |
|---|---|---|---|
| Backscatter fraction at 550 nm | 0.1–0.4 (blue-calibrated stromas) | B₅₅₀ = 0.1111 | Within the calibrated range; density assumption is order-of-magnitude consistent |
| Pigment-free L* over dark IPE | 41–71 | L* = 44.15 | Within the hue-window range; scattering/absorption balance is plausible |

**Important:** This is not a held-out validation. The optics v1 model was not fit to the hue-window parameters; it was constructed independently from physical assumptions and then compared. The agreement in order of magnitude is encouraging but does not constitute passing the ΔE ≤ 5 / RMSE ≤ 10 % gate.

## 4. Residuals, tolerances, and gate status

| Metric | Spec tolerance | Result | Pass/Fail |
|---|---|---|---|
| ΔE*ab vs held-out published spectra | ≤ 5.0 | **Cannot compute** — no accessible calibration set | **Unevaluated** |
| Reflectance RMSE vs held-out spectra | ≤ 10 % of mean | **Cannot compute** — no accessible calibration set | **Unevaluated** |
| Self-consistency: non-negative reflectance | — | Pass (all 32 scenarios and 16 unit tests) | Pass |
| Self-consistency: monotonic darkening with eumelanin | — | Pass (L* and Y decrease monotonically) | Pass |

**Gate decision:** The Phase 3 v1 gate is **not yet evaluable**. The model is mechanistically complete and self-consistent, but it lacks the independent calibration data required to demonstrate ΔE ≤ 5 and reflectance RMSE ≤ 10 %. The model remains in the "$0-compute" state: ready to be calibrated when spectra are obtained.

## 5. Comparison to the original power-law run

Replacing the assumed power-law exponents with the measured Sarna & Swartz 1988 spectral shapes changes the predicted reflectance when pigment is present, but the change is modest for the dominant eumelanin case because the measured eumelanin shape is broadly similar to the old Jacques OMLC exponent. The pheomelanin shape changes more (the measured spectrum falls off more slowly toward the blue than the old assumed exponent predicted). Because pheomelanin is a minority contributor in most swept scenarios, the overall CIELAB shifts are small:

- Representative case (M_eu = 5 µg/cm², M_ph = 0.5 µg/cm²): L* shifted from 9.29 to 9.15, hue angle from 53.3° to 52.2°, chroma from 18.85 to 17.99.
- Pigment-free case: unchanged (no melanin absorption means the spectral shape does not enter).
- Self-consistency checks and the backscatter calibration comparison are unchanged.

The hue-window exploration re-run with the same measured shapes (see `hue-window-measured-melanin-run-2026-11-09/`) confirms the qualitative finding is unchanged: orange and purple windows remain unreachable over a dark back, and still require a strong translucent-red back return.

## 6. Limitations and non-goals

| What the model does not claim | Why it matters |
|---|---|
| **Corneal or anterior-segment transmission** | Light is assumed to already reach the stromal plane. Drug delivery and epithelial penetration are separate modules (Features F1/F5). |
| **In-vivo pharmacokinetics** | Compound concentration, melanosome access, and clearance are inputs to other modules, not to this optics module. |
| **Safety, reversibility, or clinical outcome** | The model maps pigment mass to color. It does not predict tissue function, inflammation risk, or whether a pigment change is safe or reversible. |
| **Individual identity or unique color** | Population-level or category-level relationship only; it does not claim to reproduce the exact appearance of a specific living eye. |
| **Exact Mie solution for melanin** | The anisotropy g is parameterized rather than computed from full Mie theory to avoid numerical instability with the complex refractive index; Qsca uses Riccati-Bessel upward recurrence for x < ~10. |
| **Melanin refractive index certainty** | The values used (n = 1.7, κ = 0.3) are representative of eumelanin literature but are not iris-melanosome measurements; dispersion is ignored in v1. |
| **In-situ iris melanosome spectra** | The spectral shapes are measured extinction coefficients of extracted melanins in solution (Sarna & Swartz 1988), not iris melanosomes in situ. Iris-specific photophysics may differ. |

## 7. Explicit assumptions with provenance

All inputs, their values, ranges, and provenance are recorded in `assumptions.json`. Key assumptions copied here for transparency:

- **Eumelanin spectral shape:** measured Sarna & Swartz 1988 extinction coefficients, 550-normalized, replacing the prior assumed power-law exponent 3.48. The old exponent is retained in assumptions for provenance only and marked UNUSED.
- **Pheomelanin spectral shape:** measured Sarna & Swartz 1988 extinction coefficients, 550-normalized, replacing the prior assumed exponent (which was swept because no visible-range measurement had been found). The old exponent fields are retained for provenance only and marked UNUSED.
- **Melanosome size, refractive index, density:** representative values from Prota 1998 and Wielgus & Sarna 2005 electron-microscopy reports; density is calibrated to reproduce hue-window backscatter range because no direct stromal count was found.
- **Stromal thickness (200 µm) and IPE thickness (10 µm):** histological estimates with ±2× uncertainty ranges.
- **Specific absorbance at 550 nm (~0.5 cm²/µg for eumelanin):** order-of-magnitude calibration to the hue-window absorbance scale; Jacques' melanosome-interior absorption supports this order of magnitude but with a ~10-fold expected variation.

## 8. Monte-Carlo uncertainty

For each scenario, 200 parameter samples perturb the uncertain positive physical parameters log-normally within their stated ranges. The resulting 95 % intervals (2.5th–97.5th percentiles) are reported for every predicted reflectance wavelength and every CIELAB coordinate.

Example: at M_eu = 5 µg/cm², M_ph = 0.5 µg/cm²:
- L* = 9.15, CI [0.08, 39.39]
- a* = 11.04, CI [0.24, 20.42]
- b* = 14.20, CI [0.13, 44.20]

These intervals remain wide because the mass-absorption coefficient is poorly constrained in the absence of iris-specific calibration.

## 9. Files in this run

| File | Description |
|---|---|
| `assumptions.json` | Every input, value, range, and provenance |
| `simulate_optics_v1.py` | Forward model script (standard library + NumPy) |
| `test_optics_v1.py` | Unit tests: CIELAB reference, non-negativity, monotonic darkening, Mie sanity checks, and measured-melanin-spectrum tests |
| `scenario_sweep.json` | 32 scenarios across the pigment-mass grid |
| `representative_spectrum.json` | Central estimate + CI for one illustrative case |
| `calibration_comparison.json` | Comparison to hue-window calibrated stroma settings |
| `gate_status.json` | Tolerance residuals and pass/fail per the spec's decision gate |
| `receipt.json` | Output hashes, software versions, input hashes |

## 10. Next steps to close the gate

1. **Obtain published spectra:** Use institutional library access to retrieve Bashkatov 2006 or Vilaseca 2008 tabulated reflectance data (or request through interlibrary loan).
2. **Fit free parameters:** Adjust layer thickness, specific absorbance, and scattering density to minimize RMSE and ΔE against the obtained spectra.
3. **Held-out validation:** Reserve a subset of color categories or subjects as a test set, per Strategy A in the specification.
4. **If gate fails after calibration:** Document failure mode by wavelength band and color category, and decide between v2 Monte Carlo upgrade or narrowing the declared predictive range.

---

*This report was generated by the optics v1 forward model on 2026-11-09. All numbers are model outputs, not measured iris data.*

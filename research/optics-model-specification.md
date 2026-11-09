# Optics-model specification: inventory-to-appearance mapping for the iris

*November 9, 2026. Research planning document for Feature F2, Goal G3 of the [expansion plan](expansion-plan.md). AI-assisted drafting, owner-reviewed. This specifies a tissue-optics research model, not a clinical prediction, product design, or safety assessment.*

## 1. Objective

Produce a reproducible forward model that maps pigment inventory to iris appearance. **Inventory** means the mass per unit area of eumelanin and pheomelanin in the visible anterior stromal melanocytes, plus a background term for the posterior iris pigment epithelium (IPE). **Appearance** means the spectral reflectance of the emergent light (400–700 nm, 10 nm sampling) and its CIELAB coordinates (L*, a*, b*). The model must state residuals and uncertainty intervals for every prediction; an uncalibrated point estimate is not sufficient.

The model does not need to explain why a given eye has a particular color. Its job is quantitative: given a changed pigment inventory—e.g. a lower stromal eumelanin mass after compound withdrawal—produce the corresponding change in reflectance and CIELAB, with a confidence interval, so that future feasibility assessments can compare predicted appearance shifts against measurable thresholds.

## 2. Model architecture

### 2.1 Forward path

The first implementation follows a layered forward path, not an inverse fit to appearance alone:

1. **Pigment layer definition.** Define two scattering/absorbing layers: a stromal layer containing melanocyte melanosomes (eumelanin + pheomelanin, with size and number density) and an IPE background layer with a simplified pigment concentration. Each layer has thickness, refractive-index contrast, and particle-density parameters.
2. **Optical property calculation.** Convert pigment mass concentrations into absorption (μa) and reduced scattering (μs') coefficients at each wavelength. Melanin absorption spectra are treated as prior inputs; scattering is approximated by Mie theory for spherical particles of stated refractive index and size distribution.
3. **Radiative-transfer solution.** Solve for diffuse reflectance. Phase 3 v1 will use an analytical multi-layer Beer–Lambert approximation with a first-scattering correction. If the simplified model cannot meet the tolerance gate (Section 8), an optional extension uses inverse Monte Carlo or a standard diffusion solver.
4. **Spectrum → colorimetry.** Convert the emergent reflectance spectrum to CIE XYZ under a standard illuminant (D65), then to CIELAB. Report the full spectrum as well as the triplet.

### 2.2 Simplified vs. extended physics

| Variant | Physics | When it applies | Limit |
| --- | --- | --- | --- |
| **v1 (Beer–Lambert layers)** | Absorption plus first-order scattering correction; no Monte Carlo sampling | First Phase 3 calibration on published spectra | May fail for heavily pigmented (very dark brown) irides where multiple scattering dominates |
| **v2 (Monte Carlo or diffusion extension)** | Inverse Monte Carlo or analytical diffusion solution with stated geometry | Required if v1 hold-out error exceeds the gate threshold | Higher compute cost; depends more strongly on layer-geometry priors that are poorly constrained in published data |

### 2.3 Key literature anchors

The architecture draws on two published frameworks:

- **Bashkatov et al., 2006** [[1]](https://doi.org/10.1117/12.659176) developed an inverse-Monte-Carlo model that used ex-vivo reflectance inputs to estimate in-vivo pigment concentration from RGB images. It is cited here for its layer-parameter structure and its demonstration that iris optics can be approximated with a small set of optical-property variables; the current specification flips the direction (forward, not inverse) and adds explicit pigment-type separation.
- **Li et al., 2025** [[2]](https://pubmed.ncbi.nlm.nih.gov/41432634/) correlated PS-AS-OCT entropy-derived stromal melanin concentration ratio (MCR) with CIE L*a*b* in 88 brown-iris participants. It is cited for the stromal-compartment versus colorimetry linkage; the current model adds a mechanistic optical layer rather than a statistical correlation alone.

No published model known to this project supplies both pigment-type chemistry and full spectral reflectance in a single forward formulation. The v1 implementation therefore combines elements from several sources, and the calibration step (Section 3) is the primary source of its predictive constraint.

## 3. Calibration data requirements

### 3.1 Primary calibration datasets

| Dataset / source | What it provides | How the model uses it | Limitation |
| --- | --- | --- | --- |
| **Bashkatov et al., 2006** [[1]](https://doi.org/10.1117/12.659176) | Ex-vivo iris reflectance spectra and derived absorption/scattering coefficients | Anchors the 400–700 nm reflectance shape and the layer-optical-property range | No stated color-category labeling in the public record; estimates depend on simplified layer assumptions |
| **Li et al., 2025** [[2]](https://pubmed.ncbi.nlm.nih.gov/41432634/) | PS-AS-OCT stromal MCR versus in-vivo CIE L*a*b* (88 brown-iris participants, three-grade classification 85% accuracy) | Calibrates the stromal-layer pigment amount → CIELAB branch | No blue/light-iris data; no direct chemical melanin mass; statistical, not mechanistic, relationship |
| **Prota et al., 1998** [[3]](https://pubmed.ncbi.nlm.nih.gov/9778410/) | Microdissected human iris fractions (stromal vs IPE-scraped) with eumelanin/pheomelanin quantification by chemical degradation | Supplies pigment-type priors for compartment-resolved concentration ratios | The "IPE-scraped" fraction included mostly stroma plus anterior IPE; fraction purity and nomenclature need explicit verification before use [[4]](https://pubmed.ncbi.nlm.nih.gov/1634342/) |
| **Melanin absorption spectra** (visible range, e.g. Ito & Wakamatsu 1998 [[5]](https://pubmed.ncbi.nlm.nih.gov/9585251/) and Ito et al., 2020 [[6]](https://pmc.ncbi.nlm.nih.gov/articles/PMC7404343/)) | Eumelanin and pheomelanin absorption profiles and degradation-product chemistry | Convert pigment-type mass to wavelength-dependent absorption coefficients | Iris-specific melanin photophysics may differ from skin/hair references; marker conversion requires method-specific validation |
| **Wielgus & Sarna, 2005** [[7]](https://pubmed.ncbi.nlm.nih.gov/16280011/) | Human iris electron-spin-resistance melanin quantification by iris color group | Optional cross-check for total melanin order of magnitude | ESR is a whole-tissue bulk measure; it does not resolve stromal vs IPE compartments or pigment types |
| **Menon et al., 1992** [[8]](https://pubmed.ncbi.nlm.nih.gov/1402293/) | Human iris biochemistry by visible-light-absorbance extraction | Historical absorbance-based pigment data; may inform absorption-shape priors | Chemical extraction methods differ from current marker standards; cross-study calibration drift is likely |

### 3.2 Donor-eye measurements: optional upgrade, not a prerequisite

The calibrated model must run entirely on published spectra in Phase 3. The [donor-eye measurement proposal](iris-measurement-validation-proposal.md) is an optional upgrade path: if tissue access, budget, and assay feasibility permit, paired optical and chemical measurements from post-mortem eyes can be added later to tighten compartment-specific priors. They are **not** a Phase 3 gate prerequisite. If the optional dataset is obtained, it will be treated as an independent validation layer; model performance judged with and without it must be reported.

## 4. Error model and tolerances

### 4.1 Target calibration tolerance (planning-grade)

Phase 3 v1 is judged against two metrics:

- **CIELAB error:** ΔE*_{ab} ≤ 5.0 for held-out calibration spectra, measured against the published reference values or their stated confidence intervals. This is a planning threshold; if the published reference intervals are wider, the model must reproduce the central estimate within that interval, not invent a narrower one.
- **Reflectance error:** Root-mean-square error (RMSE) ≤ 10 % of the mean reflectance across 400–700 nm for held-out spectra.

These thresholds are chosen because a ΔE of approximately 5 is the conventional upper bound for a "just noticeable difference" in many color contexts, and 10 % spectral RMSE is comparable to the inter-study variability seen in ex-vivo iris reflectance measurements. They are targets, not guarantees.

### 4.2 Residual metric

For every calibration fit, report:

1. Per-wavelength reflectance residual (predicted − observed).
2. Overall reflectance RMSE and normalized RMSE.
3. CIELAB ΔE and, if the reference supplies them, ΔL*, Δa*, Δb* separately.
4. A normalized residual plot (wavelength on x-axis) and a Q–Q plot against the assumed noise model.

### 4.3 Out-of-sample validation strategy

- **Strategy A (preferred when data permit):** Hold out entire published color categories or donor groups. The model is trained on a subset of the available spectra and tested on the held-out category. This tests whether the model generalizes across the iris-color range.
- **Strategy B (when category labels are sparse):** K-fold cross-validation across spectra, with the constraint that repeated measurements from the same source or eye are kept in the same fold.
- If donor-eye measurements are added later, they form a separate **Strategy C** hold-out set: the model is never trained on donor-eye chemistry; donor data are used only for final validation.

## 5. Inputs and outputs

### 5.1 Model interface

| Direction | Variable | Symbol | Units / type | Description |
| --- | --- | --- | --- | --- |
| **Input** | Stromal eumelanin mass per area | M_eu,strom | µg cm⁻² | Melanin mass in anterior stromal melanocyte melanosomes |
| **Input** | Stromal pheomelanin mass per area | M_ph,strom | µg cm⁻² | As above, for pheomelanin |
| **Input** | Melanosome effective diameter | d_mel | nm | Mean diameter of stromal melanosomes (size distribution optional) |
| **Input** | Melanosome number density | N_mel | cm⁻³ or fractional volume | Volume fraction or count per stromal volume |
| **Input** | IPE background pigment | M_IPE | µg cm⁻² (or dimensionless relative scale) | Posterior pigment epithelium absorption treated as a background layer; may be fixed at a population mean if no per-eye data exist |
| **Input** | Illuminant and observer | — | Enum | CIE D65, 2° observer (default); other combinations documented if used |
| **Output** | Reflectance spectrum | R(λ) | dimensionless, 0–1 | Estimated spectral reflectance 400–700 nm at 10 nm intervals |
| **Output** | CIELAB coordinates | L*, a*, b* | dimensionless | Colorimetric prediction under the stated illuminant |
| **Output** | Uncertainty intervals | CI_R(λ), CI_L*, CI_a*, CI_b* | Same as parent | 95 % confidence or credible intervals from the calibration error model; if Bayesian, report posterior width; if frequentist, report prediction interval |

### 5.2 Scope of the interface

The interface is deliberately narrow. It does **not** accept compound concentration, exposure time, or corneal transmission as inputs. Those belong to the pharmacokinetic and production-persistence modules (Features F1 and F5). The optics module receives only tissue-state variables and returns only optical predictions.

## 6. Limitations and non-goals

The following are explicitly outside the scope of this model:

| What the model does not claim | Why it matters |
| --- | --- |
| **Corneal or anterior-segment transmission** | The model assumes light already reaches the stromal plane. In-vivo drug delivery, epithelial penetration, and anterior-segment optics are separate questions. |
| **In-vivo pharmacokinetics** | Compound concentration, melanosome access, and clearance half-life are inputs to other project modules, not to this optics module. |
| **Safety, reversibility, or clinical outcome** | The model maps pigment mass to color. It does not predict tissue function, inflammation risk, or whether a pigment change is safe or reversible. |
| **Individual identity or unique color** | The model predicts a population-level or category-level relationship. It does not claim to reproduce the exact appearance of a specific living eye. |
| **Mechanistic pigment-synthesis chemistry** | Tyrosinase activity, pH, or signaling pathways are upstream of the inventory variables; they are not resolved inside the optics module. |

The model is a tissue-optics mapping. Any downstream use in a feasibility verdict must carry these limitations explicitly.

## 7. Implementation notes

### 7.1 Software stack

| Component | Proposed tool | Notes |
| --- | --- | --- |
| Numerical arrays and spectra | NumPy / SciPy | Baseline for v1 Beer–Lambert and colorimetric conversions |
| Mie scattering | `miepython` or equivalent verified open-source implementation | Only if v1 scattering correction is insufficient; version and validation receipt recorded per project convention |
| Monte Carlo (optional v2) | Custom Python wrapper around a standard Monte Carlo solver (e.g., MCXYZ-style or a validated diffusion package) | Upgrade path only; not needed for gate evaluation if v1 passes |
| Colorimetry | `colour-science` or validated manual CIE conversion | CIE XYZ → CIELAB conversion must match standard CIE 15:2004 definitions |
| Version control and reproducibility | Same `reproducible-receipt` discipline as existing `../analysis/` runs | Every model run produces a receipt file with input hashes, parameter values, random seed, and output checksum |

### 7.2 Existing analysis framework

The optics module should be developed inside the existing analysis directory (`../analysis/`), following the project's current receipt, fixture, and dependency-discipline conventions (see [`../analysis/README.md`](../analysis/README.md)). If new Python dependencies are introduced, they are added at the project level, not in a separate isolated environment, and their versions are pinned.

### 7.3 First calibration order of operations

1. Assemble the published reflectance/absorbance inputs listed in Section 3.1.
2. Build the Beer–Lambert v1 forward model with free parameters for layer thickness, melanosome density, and relative IPE background.
3. Fit parameters to reproduce Bashkatov 2006 reflectance shapes and Li 2025 CIELAB coordinates.
4. If Prota 1998 compartment ratios are used, treat them as informative priors, not hard constraints; report posterior sensitivity to those priors.
5. Validate with held-out data per Section 4.3.
6. If the gate passes, document residuals and commit the calibrated model; if it fails, document the failure mode and either (a) proceed to v2 Monte Carlo, or (b) narrow the scope to a subset of the color range where v1 is adequate.

## 8. Decision gate for Phase 3

### 8.1 Pass criterion

Phase 3 exits successfully if **both** of the following are demonstrated:

1. The calibrated v1 (or v2, if v1 fails and v2 is attempted) reproduces held-out published calibration spectra within the tolerances of Section 4.1 (ΔE*_{ab} ≤ 5.0 and reflectance RMSE ≤ 10 %).
2. Residuals are documented by wavelength and by color-category subset, with no systematic bias larger than the random error in any 100 nm band.

If donor-eye measurements were obtained, a secondary pass criterion is added: the model's stromal-pigment predictions must fall within the assay's stated confidence limits for at least 70 % of the held-out donor eyes.

### 8.2 Fail criteria and contingency

| Failure mode | Required action |
| --- | --- |
| Hold-out ΔE consistently > 5 or RMSE > 10 % | Document the failure, identify the wavelength bands and color categories where the model breaks down, and decide whether to (a) upgrade to v2 Monte Carlo or (b) narrow the declared predictive range (e.g., restrict to light-to-medium brown irides) |
| Systematic bias in a wavelength band | Report the bias direction; if it correlates with pigment type, flag the eumelanin/pheomelanin absorption priors as a critical uncertainty |
| Published calibration data are too sparse for hold-out validation | Document the data limitation as a project risk; proceed with cross-validation and an explicit disclaimer that the model has not been tested on entirely independent datasets |
| Donor-eye assay fails feasibility gate | Per the [donor-eye proposal](iris-measurement-validation-proposal.md), stop or relabel the tissue upgrade. The published-spectra-only model remains the Phase 3 deliverable. |

### 8.3 Gate timing

This gate is evaluated at Milestone M4 ("Optics v1 calibrated") in the [expansion plan](expansion-plan.md). The gate outcome and the chosen contingency are recorded in the milestone ledger (Feature F6). A gate failure does not end the project; it narrows the scope or triggers the v2 upgrade path, with the decision and reasoning committed to the repository.

---

## References

1. Bashkatov, A. N., et al. (2006). "Optical properties of human sclera, and their consequences for transscleral laser applications." *Proc. SPIE* (includes iris optical-property modeling data). DOI: [10.1117/12.659176](https://doi.org/10.1117/12.659176).
2. Li, Z., et al. (2025/2026). "Correlation between entropy-derived stromal melanin concentration ratio and iris color in AS-OCT." *Ophthalmology* (online 2025 / print 2026). PubMed: [41432634](https://pubmed.ncbi.nlm.nih.gov/41432634/).
3. Prota, G., et al. (1998). "Characterization of melanins in human irides and cultured uveal melanocytes from eyes of different colors." *Exp Eye Res.* PubMed: [9778410](https://pubmed.ncbi.nlm.nih.gov/9778410/).
4. Hu, D.-N., et al. (1992). "Isolation and culture of iris pigment epithelium from iridectomy specimens." *Eye Res.* PubMed: [1634342](https://pubmed.ncbi.nlm.nih.gov/1634342/).
5. Ito, S., & Wakamatsu, K. (1998). "Chemical degradation of melanins: application to identification of dopamine-melanin." *Pigment Cell Res.* PubMed: [9585251](https://pubmed.ncbi.nlm.nih.gov/9585251/).
6. Ito, S., et al. (2020). "Usefulness of alkaline hydrogen peroxide oxidation to analyze eumelanin and pheomelanin in various tissue samples." *Int J Mol Sci.* PubMed: [PMC7404343](https://pmc.ncbi.nlm.nih.gov/articles/PMC7404343/).
7. Wielgus, A. R., & Sarna, T. (2005). "Melanin in human irides of different color and age of donors." *Pigment Cell Res.* PubMed: [16280011](https://pubmed.ncbi.nlm.nih.gov/16280011/).
8. Menon, I. A., et al. (1992). "Quantitative determination of melanins in human irides." *Pigment Cell Res.* PubMed: [1402293](https://pubmed.ncbi.nlm.nih.gov/1402293/).

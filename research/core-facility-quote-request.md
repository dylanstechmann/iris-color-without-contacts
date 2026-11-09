# Core-facility / CRO quote-request package: paired exposure and withdrawal study

*November 9, 2026. Personal hobby and learning-project planning document; AI-assisted drafting, owner-reviewed. Derived from the [paired exposure/withdrawal protocol](paired-exposure-withdrawal-protocol.md) for the purpose of obtaining written quotes. Not a treatment protocol, dosing regimen, or clinical suitability statement for any living eye or person.*

---

## 1. Executive summary

This package requests a written quote for a six-arm paired exposure/withdrawal cell-study program in human pigment-cell models. The study asks whether each of five mechanistic candidates (three production-down, two production-up, plus an optional transcriptional comparator) produces a reversible pigment change in a single human-cell system, with old pigment tracked separately from new and free intracellular compound measured at every washout timepoint. The answer matters to this project's feasibility verdict because the [identifiability calculation](../analysis/withdrawal-and-recovery.md#a-calculation-that-changes-what-to-measure-next) shows that total pigment alone cannot distinguish a fixed persistent pool, partial production suppression, and added pigment loss — three causes that share one total-inventory curve. Every readout listed below was chosen to break that symmetry. This document is a personal research-planning artifact; no treatment instructions for any person or eye are stated or implied.

---

## 2. Experiment list

The full matrix is derived directly from Table 1 of the paired protocol. Each arm is an independent ladder of four concentrations with matched vehicle-only controls, run in parallel.

| Arm | Candidate | Expected direction | Concentration rationale |
| --- | --- | --- | --- |
| 1 | **KT‑939** [1] | Lower pigment | 0.1×, 1×, 3×, 10× the registered six-day MNT‑1 melanin IC50 (0.36 μM), giving 0.036–3.6 μM |
| 2 | **Thiamidol** [1,2] | Lower pigment | 0.1×, 1×, 3×, 10× the registered six-day IC50 (1.3 μM), giving 0.13–13 μM |
| 3 | **Ampyrone** [3] | Raise pigment | Brackets the registered recombinant-human-TYR EC50 (0.67 mM) within demonstrated solubility |
| 4 | **TPC2‑A1‑P** [4] | Lower pigment | Set by its published active range: whole-cell Ca2+ EC50 10.5 μM, patch Na+ EC50 0.6 μM [4] |
| 5 | **MT‑8** [5] | Raise pigment | 0.1×, 1×, 3×, 10× the registered TPC2 IC50 (2.6 μM), giving 0.26–26 μM |
| 6 | **UM‑9** [5] | Raise pigment | 0.1×, 1×, 3×, 10× the registered TPC2 IC50 (9.5 μM), giving 0.95–95 μM |
| 7 (optional) | **SIK inhibitor series** [6] | Raise pigment | To be agreed if quoted separately; the registered precedent used YKL 06‑061/062 |

**Time courses.** Every arm runs a primary **six-day exposure** (matching the registered melanin endpoints) and a parallel **21-day exposure** arm to address mature-pigment questions. After exposure ends, cultures are switched to compound-free medium and sampled at washout days **0, 1, 3, 5, 7, 9, 11, 14 and 21** — extending the published KT‑939 day‑3‑to‑11 series [1].

**Cell systems required:**

1. **Primary platform:** MNT‑1 human melanoma cells [1,5] — the only system with registered paired KT‑939/thiamidol potencies and existing wild-type versus TPC2-knockout specificity controls.
2. **Required secondary:** Primary normal human melanocytes from **at least three independent donors** [2,6] — MNT‑1 is transformed and must not stand alone.
3. **Translation check:** Human **3D reconstructed epidermis** [3] — for the ampyrone and TPC2 arms, matching the registered darkening endpoint.
4. **Declared extension (not an assumption in this quote):** Iris-derived melanocytes, if a sourced line is available at quote time; otherwise excluded from the first-stage scope.

**Explicit exclusions:** No mushroom-tyrosinase-only assays; no living-eye or donor-eye tissue in Phase 1 or 2.

---

## 3. Readouts and controls

Each readout below maps to one required observation from the [identifiability analysis](../analysis/withdrawal-and-recovery.md#which-added-observations-answer-which-question). The measurement method, sampling frequency, and required control are stated for quoting.

| Required observation | Measurement method | Sampling frequency | Required control |
| --- | --- | --- | --- |
| New synthesis relative to its own pretreatment baseline | Pulse-window incorporation of isotope-labeled L-tyrosine into melanin, measured by LC‑MS/MS isotope-ratio detection [7] | Every washout timepoint (days 0, 1, 3, 5, 7, 9, 11, 14, 21) plus a matched pretreatment pulse on each culture | Vehicle-only within the same donor/line; isotope-ratio baseline from the same culture's pre-exposure pulse |
| Old pigment tracked separately from new | Pre-label starting pigment by growing cultures in heavy-isotope tyrosine medium before any drug, then switching to light medium at first exposure; quantify heavy versus light melanin fractions by LC‑MS/MS isotope ratio [7] | Heavy/light ratio at every washout timepoint; heavy-fraction decay reports old-pool loss | Vehicle-only with identical heavy→light switch; no-drug heavy-maintained control for non-exchange baseline |
| Free active compound and target activity after withdrawal | LC‑MS/MS intracellular free compound (parent and major metabolites if known); lysate tyrosinase activity assay (405 nm dopachrome) | Every washout timepoint; compound at 0 h (washout start) defines initial decay | Vehicle-only zero-compound baseline; spike-recovery control in matrix for LC‑MS/MS quantification |
| Melanosomal pH (TPC2 arms only) | Ratio-metric pH-sensitive fluorescent probe or LysoSensor-based readout, calibrated in situ [8] | Days 0, 3, 7, 14 of washout for TPC2‑A1‑P, MT‑8 and UM‑9 arms | Wild-type vs TPC2-knockout MNT‑1 cells [5,8]; knockout must show no pH or pigment response |
| Cell-population accounting | Automated cell counts (Trypan blue or imaging); total protein per well; division marker (EdU or Ki‑67) at selected timepoints; extracellular melanin in spent medium | Every washout timepoint for counts and medium pigment; protein and division markers at days 0, 7 and 21 | Vehicle-only within same donor/line; population-doubling reference from parallel no-drug culture |
| Appearance-linked endpoint (secondary, 3D tissue only) | Gross photography under standardized illumination; spectrophotometric reflectance (400–700 nm); chemical melanin extraction from the same tissue [3] | Endpoint only (day 6 and day 21 for 3D epidermis) | Vehicle-only 3D tissue from the same production batch; intra-batch positive control if available |

**Cell-population accounting details:** The intention is that pigment per surviving cell is never confounded with population change, dilution by division, or pigment export into medium. Every pigment value reported to the analysis pipeline must be accompanied by matched cell count, total protein, and extracellular-pigment fraction from the same well at the same timepoint. Donor is treated as a random effect in the statistical analysis plan; replicate wells per donor per condition are required.

---

## 4. Deliverables

The facility should deliver the following items, with a reproducible identifier (run ID, batch number, instrument method file name) for every raw data file:

| Deliverable | Format | Minimum content |
| --- | --- | --- |
| **Raw data** | Vendor-native mass-spectrometry files (.raw, .wiff, .d, or agreed open format) | LC‑MS/MS chromatograms for isotope-ratio melanin fractions; intracellular free-compound quantification chromatograms; tyrosinase-activity absorbance plate reads; cell-count and microscopy image sets |
| **Processed data files** | Tab-separated values (.tsv) or agreed open format with column metadata | Isotope-ratio heavy/light fraction per well per timepoint; compound concentration (pg/cell or ng/mg protein) per well per timepoint; melanin absorbance at 405 nm normalized to protein and cell count; pH calibration curve and derived pH per well; cell-count, total-protein and medium-pigment time series |
| **LC‑MS/MS method documentation** | PDF plus method-export file | Full method parameters for the isotope-ratio assay and the free-compound assay: column, gradient, MRM transitions (or DIA acquisition scheme), internal standard, LOD/LOQ estimates in matrix, and a brief validation note on linearity and within-run precision |
| **Isotope-ratio validation report** | PDF | Demonstrated separation of heavy- versus light-labeled melanin markers in pigmented human melanocytes; detection-limit estimate for the old-pool fraction; cross-check against total chemical melanin (NaOH-solubilized absorbance) on a subset of samples |
| **Feasibility-gate pass/fail outcomes** | PDF summary plus committed data files | For each of the three gates (see §5): stated numerical criterion, observed value, pass/fail call, and fallback trigger if failed |

---

## 5. Three feasibility gates — quoted separately as a first stage

Each gate must be passed before the full washout matrix proceeds. A gate failure triggers the declared fallback; it does not automatically end the program. The facility is asked to quote these three gates as a bounded first-stage package.

### Gate 1 — Old-pigment pre-labeling

**Scope:** Demonstrate heavy/light melanin isotope-ratio measurement in pigmented human melanocytes (primary normal or MNT‑1, facility's choice for method-development efficiency) using a stable-isotope L-tyrosine pre-label followed by light-medium chase.

**Pass criterion:** Quantifiable separation of heavy- and light-melanin fractions at baseline; old-pool fraction detectable above LOD after a 7-day chase; agreement with total chemical melanin within a stated tolerance on a validation subset.

**Fallback if failed:** Replace old/new separation with melanosome counting via electron-microscopy pulse-chase. The old-pool term is then recorded as unidentified in the washout model, leaving some mechanisms indistinguishable by design.

### Gate 2 — Intracellular free-compound assay validation

**Scope:** Validate LC‑MS/MS quantification of intracellular free compound for each candidate used in the washout matrix: KT‑939, thiamidol, ampyrone, TPC2‑A1‑P, MT‑8 and UM‑9. Matrix: MNT‑1 or primary melanocyte lysate.

**Pass criterion:** Spike recovery 80–120% in cell lysate matrix; calibration-linearity R² ≥ 0.99; intra-day CV < 15% at the LOQ; demonstrated stability through at least one freeze-thaw cycle. A compound that fails its validation is excluded from free-compound-corrected washout fitting for that arm.

### Gate 3 — Ampyrone solubility window

**Scope:** Confirm that ampyrone remains in solution at its millimolar working-concentration scale in the chosen cell-culture medium (including any DMSO or co-solvent carrier) at 37 °C for the duration of a 6-day exposure.

**Pass criterion:** No visible precipitate and no >10% drop in nominal concentration by LC‑MS/MS at 6 days; confirmed cell viability ≥70% of vehicle at the highest soluble concentration. If solubility is insufficient to reach the registered 0.67 mM EC50 [3], the ampyrone arm is run at its highest soluble concentration with the limitation declared, and the 21-day mature-pigment arm for ampyrone is deferred until a formulation route is found.

**Staging rule:** Gate 1 and Gate 2 may be run in parallel during method development. Gate 3 may also parallelize if medium-analysis resources are independent. The full six-arm × two-duration × nine-timepoint matrix (§2) is committed only after all three gates are documented pass/fail.

---

## 6. Sample-size and replication requirements

| Requirement | Minimum standard |
| --- | --- |
| Donors or independent lines | ≥3 independent donors for primary melanocytes; MNT‑1 wild-type and TPC2-knockout sublines considered independent lines for the TPC2 arms [5] |
| Replicate wells | ≥3 replicate wells per condition per donor/line per timepoint for the primary six-day arm; ≥2 replicates for the extended 21-day arm if material limits apply |
| Statistical treatment | Donor/line as a random effect; mixed-effects model for repeated measures; no pooling across donors without explicit justification and acknowledgement |
| Positive control per batch | If the facility maintains a validated melanin-modulator positive control (e.g., α‑MSH or a known tyrosinase inhibitor), include one well per plate/run to flag batch drift |

---

## 7. Timeline assumption for quoting

The project assumes a **facility queue of 4–8 weeks after written quote acceptance** before the first bench work begins, based on core-facility and CRO norms. The owner recognizes that actual queue time depends on the specific facility's calendar and does not bind the facility to this range; the purpose is to align milestone expectations in the [expansion plan](expansion-plan.md) with realistic quoting inputs.

Suggested timeline for the facility's quote:

| Phase | Estimated duration | Activity |
| --- | --- | --- |
| Method development | 4–6 weeks | Gate 1 (isotope labeling) and Gate 2 (LC‑MS/MS validation) in parallel |
| Gate 3 (ampyrone solubility) | 1–2 weeks | Medium-stability and cell-viability assay |
| Gate decision buffer | 1 week | Owner review; go/no-go for full matrix |
| Full matrix — six-day arm | 6–8 weeks | All six arms + 3D tissue endpoint; includes KT‑939/thiamidol primary comparison |
| Full matrix — 21-day arm | 8–10 weeks | Parallel extended exposure and washout; staged after six-day arm confirms compound-handling feasibility |
| Data delivery and QC | 2–3 weeks | Raw-file handoff, method-documentation transfer, and a brief QC call |

---

## 8. Budget context

The figures below are copied from the project's [expansion plan](expansion-plan.md) for planning-grade context only. They are **not authorizations to spend** and do not replace a written facility quote.

| Stage | Planning-grade rough range | Scope covered |
| --- | --- | --- |
| Phase 1 — feasibility gates | **$8,000–30,000** | Method development and validation at core-facility or CRO rates; this quote-request package |
| Phase 2 — paired washout matrix | **$20,000–75,000** | Full six-arm × two-duration × nine-timepoint matrix; scales with arms, timepoints, donors, and 3D tissue work; KT‑939/thiamidol pairing is staged first |

**Quote superseding statement:** Any written quote received from the facility supersedes all planning-grade figures above. The owner may negotiate scope reduction or pause the program at any gate without penalty beyond work already performed.

---

## 9. Interpretation limits and use constraints

- MNT‑1 is a melanoma line; primary-melanocyte and 3D-tissue results override it wherever they disagree [1,5].
- Cell-culture washout is not iris pharmacology. Corneal penetration, uveal delivery, and in-vivo clearance are unmeasured here. The registered ocular pharmacokinetic literature motivates but does not substitute for those controls.
- This document proposes measurements only. It does not provide a regimen, dose, or clinical suitability statement for any living eye or person.
- AI-assisted development is visible in this document's drafting history; the owner retains authority over scope, budget, and scientific interpretation.

---

## References

1. [Hou et al., 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12569736/) — MNT‑1 lysate and six-day melanin IC50 values for KT‑939 and thiamidol; KT‑939 washout series (10 μM: 66.6% inhibition day 3 falling to recovery by day 11; 1 μM recovers by day 7).
2. [Mann et al., 2018](https://pubmed.ncbi.nlm.nih.gov/29427586/) — Thiamidol reversibility precedent in donor-derived human melanocyte cultures; two weeks exposure followed by two weeks without compound.
3. [Dolinska et al., 2026](https://doi.org/10.1172/jci.insight.202947) — Ampyrone recombinant human TYR EC50 0.67 mM (wild-type); darkens human 3D epidermis; no washout data exist.
4. [Gerndt et al., 2020](https://pubmed.ncbi.nlm.nih.gov/32167471/) — Human TPC2 pharmacology: TPC2‑A1‑P EC50 10.5 ± 1.9 μM (cell Ca2+) and 0.6 ± 0.2 μM (patch Na+); mechanism is Na+-selective channel opening without lysosomal pH alkalinization.
5. [Netcharoensirisuk et al., 2021](https://pubmed.ncbi.nlm.nih.gov/33875769/) — MT‑8 (IC50 2.6 ± 0.3 μM) and UM‑9 (IC50 9.5 ± 2.8 μM) blocked human TPC2 and raised melanin and tyrosinase activity in wild-type but not knockout MNT‑1; TPC2‑A1‑P lowered melanin TPC2-dependently.
6. [Mujahid et al., 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5549921/) — Salt-inducible kinase inhibitors YKL 06‑061/062 darkened human skin explants within eight days; reversal observed about two weeks after stopping, with pretreatment state persisting 26 days later.
7. [Chen et al., 2021](https://pubmed.ncbi.nlm.nih.gov/33549605/) — Stable-isotope [U‑13C]‑L‑tyrosine LC‑MS fate tracing in live human and mouse melanocyte models; precedent for de novo melanin-pathway intermediate quantification.
8. [Ambrosio et al., 2016](https://pubmed.ncbi.nlm.nih.gov/27140606/) — TPC2 knockout in human MNT‑1 cells and siRNA knockdown in primary human melanocytes with melanosomal pH sensing; TPC2 loss raised melanosomal pH and increased melanin.

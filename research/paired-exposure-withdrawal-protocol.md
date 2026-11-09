# Proposed cell study: paired exposure and withdrawal across pigment candidates

*November 9, 2026. Personal learning project; a proposed study design for discussion, not a treatment regimen or dosing advice. Every numeric anchor below traces to a row of the [pigment evidence register](pigment-evidence-register.md).*

## Decision question

Five mechanistic branches share one missing observation: whether each named candidate's effect washes out and the cell returns to baseline, measured in one human pigment-cell system with exposure and withdrawal paired. The [November 9, 2026 sweep](mechanism-shortlist.md#shortlist-refresh-november-9-2026) confirmed no published study provides this for any candidate: KT-939 and thiamidol have never been followed through washout in the same system, ampyrone has no washout experiment at all, and the registered TPC2 modulators have no withdrawal test.

This design exists to separate the causes the [identifiability calculation](../analysis/withdrawal-and-recovery.md#a-calculation-that-changes-what-to-measure-next) shows cannot be separated by total pigment alone: a fixed persistent pool, partial production suppression, and added loss produce the same total-inventory curve. Every readout below supplies one of the observations that calculation requires.

## Candidates and registered anchors

| Arm | Candidate | Registered anchor | Expected direction |
| --- | --- | --- | --- |
| Primary pair, down | KT-939 | MNT-1 lysate IC50 0.07 μM; six-day melanin IC50 0.36 μM; the only washout series (10 μM: 66.6% inhibition day 3 falling to recovery by day 11; 1 μM recovers by day 7) — [Hou et al., 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12569736/) | Lower pigment |
| Primary pair, down | Thiamidol | Same-study lysate IC50 0.33 μM; six-day melanin IC50 1.3 μM; reversibility precedent predating KT-939 — [Hou et al., 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12569736/); [Mann et al., 2018](https://pubmed.ncbi.nlm.nih.gov/29427586/) | Lower pigment |
| Production-up probe | Ampyrone | Recombinant human TYR EC50 0.67 mM (wild-type); darkens human 3D epidermis; no washout data exist — [Dolinska et al., 2026](https://doi.org/10.1172/jci.insight.202947) | Raise pigment |
| pH branch, down | TPC2-A1-P | Lowers melanin in wild-type but not TPC2-knockout MNT-1 cells — [Netcharoensirisuk et al., 2021](https://pubmed.ncbi.nlm.nih.gov/33875769/); TPC2 activation active range defined in HEK293 cells — [Gerndt et al., 2020](https://pubmed.ncbi.nlm.nih.gov/32167471/) | Lower pigment |
| pH branch, up | MT-8 (TPC2 IC50 2.6 μM) and UM-9 (9.5 μM) | Raise melanin and tyrosinase activity in wild-type not knockout MNT-1 — [Netcharoensirisuk et al., 2021](https://pubmed.ncbi.nlm.nih.gov/33875769/) | Raise pigment |
| Optional transcriptional up-comparator | SIK inhibitor series | Human skin explants darkened with reversal about two weeks after stopping — [Mujahid et al., 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5549921/) | Raise pigment |

The paired KT-939/thiamidol arms are the primary comparison because comparative recovery is the sweep's confirmed open gap. Potencies must not transfer between assay types: lysate, six-day cell pigment and 3D tissue are different endpoints.

## Cell systems

- **Primary system: MNT-1 human melanoma cells.** It is the only system with registered paired KT-939/thiamidol potencies and existing wild-type versus TPC2-knockout specificity controls, so all six arms can share one platform.
- **Required secondary: primary normal human melanocytes from at least three donors.** MNT-1 results are melanoma-derived and must not stand alone; iris-derived melanocytes would be a declared extension, not an assumption.
- **Translation check: human 3D epidermis** for the ampyrone and TPC2 arms, matching ampyrone's registered darkening endpoint.
- **Explicit non-goals:** no mushroom-tyrosinase-only assays; no living-eye or donor-eye tissue in this first version.

## Concentration and exposure logic

Anchor each ladder to the registered six-day cell-pigment IC50 in the same system, not the lysate value: 0.1×, 1×, 3× and 10× gives KT-939 0.036–3.6 μM and thiamidol 0.13–13 μM, spanning Hou et al.'s washout concentrations (1 and 10 μM) so the existing KT-939 series becomes an internal reference. Ampyrone brackets its registered 0.67 mM wild-type EC50 within solubility. TPC2 modulators bracket their registered IC50s (MT-8 0.26–26 μM; UM-9 0.95–95 μM; TPC2-A1-P 1.05–105 μM around its 10.5 ± 1.9 μM whole-cell Ca²⁺ EC50 — [Gerndt et al., 2020](https://pubmed.ncbi.nlm.nih.gov/32167471/)). Caution: the same paper's much lower excised-patch Na⁺ EC50 (0.6 ± 0.2 μM) shows strong assay dependence, and neither HEK293 value is a melanocyte melanin endpoint, so the ladder must be treated as exploratory pending gate results (solubility/cytotoxicity may bind the upper end at 105 μM).

Exposure runs six days (matching the registered melanin endpoints) with a parallel 21-day arm for mature-pigment questions. Washout sampling at days 0, 1, 3, 5, 7, 9, 11, 14 and 21 extends Hou et al.'s day-3-to-11 series and catches slower recovery. Free compound is a measured quantity, not an assumption: the [exposure model](../analysis/exposure-run-2026-10-17/MODEL_REPORT.md) shows pigment-associated drug can keep acting after dosing stops.

## Readouts mapped to the identifiability requirements

| Required observation ([source](../analysis/withdrawal-and-recovery.md#which-added-observations-answer-which-question)) | Proposed measurement |
| --- | --- |
| New synthesis relative to its own pretreatment baseline | Pulse-window isotope-labeled tyrosine incorporation into melanin at each timepoint, normalized to the same culture's pretreatment pulse. Registered precedent: the ampyrone study performed isotope tracing of newly labeled intermediates (in mouse cells). |
| Old pigment tracked separately from new | Pre-label starting pigment by growing cultures in heavy tyrosine before any drug, then switch to light medium at first exposure; quantify heavy versus light melanin fractions by isotope ratio. Feasibility gate 1 below. |
| Free active compound and target activity after withdrawal | LC-MS/MS intracellular free compound plus lysate tyrosinase activity at every washout timepoint; melanosomal-pH readout for the TPC2 arms (registered pH-sensing precedent; the registered TPC2-A1-P mechanism of Na⁺-selective channel opening reported no lysosomal pH alkalinization in HEK293 cells, so a null pH readout for the agonist arm would be mechanism-consistent rather than evidence of absence, whereas the MT-8/UM-9 blocker arms should still be expected to raise melanosomal pH per the registered knockout phenotype). |
| Cell-population accounting | Cell counts, total protein, division markers and an extracellular pigment fraction at every timepoint, so pigment per surviving cell is never confounded with population change or export. |
| Appearance-linked endpoint (secondary only) | Gross and spectrophotometric color of 3D epidermis alongside its chemical melanin. A tissue-culture color is not an iris prediction. |

## Analysis plan and decision gates

- **Primary comparison:** KT-939 versus thiamidol washout kinetics in the same system with matched free-compound measurements. Any difference in synthesis recovery that persists after free compound is gone is evidence for scaffold-dependent retention — the unresolved question left by KT-939's washout having no thiamidol arm.
- **Predeclared constraint:** washout of intracellular free compound, recovery of synthesis flux and old-pool loss are fitted separately; total pigment alone is never fitted as a recovery rate, because the counterexample shows three mechanisms can share one total curve.
- **TPC2 arms:** wild-type versus TPC2-knockout cells replicate the registered specificity design; washout differences seen only in wild-type support an on-target interpretation.
- **Ampyrone:** darkening that outlasts measurable free compound elevates the product-handling question; full fast washout would give the production-up branch its first measured on/off cycle.
- **Decision gates:** fast and complete TPC2-A1-P repigmentation in wild-type (absent in knockout) would promote melanosomal pH from strongest alternative to demonstrated reversible pharmacology in human pigment cells; an ampyrone or SIK-inhibitor cycle that returns to baseline would give the blue → brown → blue goal a measured production-up precedent.
- **Replication:** at least three donors or independent lines, replicate wells, donor as a random effect. The register's single-donor and affiliation caveats motivate predeclared sample counts.

## Feasibility gates before the full matrix

1. **Old-pigment pre-labeling.** Verify heavy/light melanin isotope-ratio measurement in pigmented human melanocytes. If it fails, fall back to melanosome counting with pulse-chase and record the old-pool term as unidentified — some mechanisms then remain indistinguishable by design.
2. **Intracellular free-compound assay** validated per candidate before washout fitting.
3. **Ampyrone solubility window** at its millimolar EC50 scale in the chosen system.

## Interpretation limits

- MNT-1 is a melanoma line; primary-melanocyte and 3D-tissue results override it wherever they disagree.
- Cell-culture washout is not iris pharmacology: corneal penetration, uveal delivery and in-vivo clearance are unmeasured here. The registered ocular pharmacokinetic study motivates but does not substitute for these controls.
- This document proposes measurements only. It does not provide a regimen, dose or clinical suitability statement for any living eye or person.

## Links

- Identifiability requirements: [withdrawal and recovery analysis](../analysis/withdrawal-and-recovery.md)
- Registered evidence rows: [pigment evidence register](pigment-evidence-register.md)
- Prioritization context: [mechanism shortlist](mechanism-shortlist.md)

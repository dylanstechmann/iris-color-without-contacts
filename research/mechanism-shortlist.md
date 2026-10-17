# Mechanism shortlist and computational feasibility

*October 17, 2026. Personal learning project; AI-run calculations and public-data analysis. This ranks research directions, not treatments.*

## Current judgment

The clearest production-control hypothesis is **reversible inhibition of human tyrosinase (TYR)**. The largest unresolved part of the lightening problem is **net loss of existing pigment**. Investigate these as separate controls, then ask whether combining them improves the balance while preserving the target cells.

A synthesis inhibitor could be enough if ordinary turnover is useful. A disposal mechanism becomes more valuable when ordinary turnover is slow. Returning to baseline is a third control question: quickly ending drug activity does not ensure fast repigmentation.

## Priority by mechanism

| Research priority | Why it follows from the goal | Concrete starting point | Main reason it might fail |
| --- | --- | --- | --- |
| **First production controller: reversible human TYR inhibition** | Acts on pigment production without logically requiring cell replacement or permanent genome change. | Thiamidol as a reference scaffold; 4-butylresorcinol as an alternative comparator. | Mature pigment persists, delivery to the relevant intracellular compartment fails, or useful modulation cannot preserve/recover cell function. |
| **First disposal question: selective handling of mature melanosomes/pigment** | Adds an outlet when reducing input is too slow. | OPTN/RCHY1/TBK1-related melanophagy; beta-mangostin as a mechanism probe. | Organelle proteins disappear while the pigment core persists; products accumulate elsewhere; or selectivity fails in normal iris cells. |
| **Alternative production controller: melanosomal pH regulation** | Pigment synthesis depends on an organelle environment as well as enzyme abundance. | OCA2-related regulation, with TPC2 as an interacting pathway to examine. | Genetic or non-iris effects fail to translate to reversible adult-iris pharmacology, or other pigment compartments are affected. |
| **Indirect signaling comparator** | Could influence production upstream. | Levobunolol-related signaling hypothesis; latanoprost as an opposite-direction comparator. | Pigment response is indirect, inconsistent, or tied to other functions; a temporal association does not identify a controllable mechanism. |

The TYR priority is a mechanism judgment. The 2018 human-enzyme/skin-melanocyte work reports reversible inhibition by thiamidol and substantial human-versus-mushroom enzyme differences. It supplies a useful probe and a specificity check; it does not establish an ocular product. [Primary study](https://doi.org/10.1016/j.jid.2018.01.019), [structure–activity work](https://pmc.ncbi.nlm.nih.gov/articles/PMC5877551/).

The melanophagy lead comes from mouse melanoma-cell work linking beta-mangostin effects to OPTN, RCHY1 and TBK1. This is a reason to examine the machinery in normal human iris cells. Mature polymer fate and tissue function remain separate questions. [Primary study](https://doi.org/10.1073/pnas.2318039121). OCA2's melanosomal role is recorded in [UniProt Q04671](https://www.uniprot.org/uniprotkb/Q04671/entry) and supported by [channel physiology](https://pubmed.ncbi.nlm.nih.gov/25513726/).

## What the workbench actually ran

The existing Research Desk now has an iris-pigment campaign under appearance research. Seven public compound identities resolved to one structure each. RDKit 2026.03.6 calculated these properties from the resolved structures:

| Comparator | Role in this exploration | Molecular weight (g/mol) | Calculated logP |
| --- | --- | ---: | ---: |
| Thiamidol | Direct synthesis reference | 278.33 | 2.82 |
| 4-Butylresorcinol | Alternative synthesis reference | 166.22 | 2.44 |
| Kojic acid | Enzyme-specificity comparator | 142.11 | -0.16 |
| Metyrosine | Catecholamine-versus-melanogenesis comparator | 195.22 | 0.74 |
| Beta-mangostin | Pigment-disposal mechanism probe | 424.49 | 5.39 |
| Levobunolol | Indirect signaling comparator | 291.39 | 2.33 |
| Latanoprost | Opposite-direction comparator | 432.60 | 4.19 |

These are structural calculations, not measured solubility, ionization, corneal penetration, melanosome access, binding, or efficacy. Beta-mangostin's relatively high calculated lipophilicity is a formulation/exposure question to investigate, rather than proof of success or failure. A shared descriptor does not imply shared biological effects.

The [compound table](../analysis/workbench-comparison-2026-10-17/compounds.csv), exact PubChem snapshots, RDKit outputs, and imported hash receipts are retained in the analysis directory. Full original run folders remain in the local workbench. The copied workbench manifests describe those original folders; the comparison receipt hashes the selected files actually copied here.

## What the balance calculation adds

The [720-case sweep](../analysis/feasibility-run-2026-10-17/MODEL_REPORT.md) holds the original source fixed while adding a hypothetical loss pathway. This matters: changing a clearance rate must not silently increase baseline synthesis.

For one deliberately hypothetical case—20-year native pigment half-life, production reduced to 5%, no persistent pool—seven years leaves **79.5%** of initial pigment. Adding a separate three-year loss half-life lowers the model result to **16.1%**. If 30% remains persistent, the combined result is **41.3%** and a 25%-inventory target is unreachable while that pool stays persistent.

The same example takes about **61 years after withdrawal** to return to 90% of baseline if original slow production resumes. A higher recovery-source assumption shortens that in the model, but would require its own controllable mechanism and could overshoot if maintained. These are consequences of assumptions, not human forecasts. The inventory targets have no assigned eye colors.

![Hypothetical pigment balance](../analysis/feasibility-run-2026-10-17/hypothetical_balance.svg)

## Target and structure checks

Public target snapshots identify human TYR as P14679 and OCA2 as Q04671. Checking the TYR cross-reference exposed a useful mismatch: PDB 7RK7 contains a nine-residue TYR-derived peptide in an immune complex, rather than the enzyme's catalytic structure. It is unsuitable as a TYR inhibitor-docking receptor. [RCSB structure record](https://www.rcsb.org/structure/7RK7).

Regen also fetched the predicted AF-P14679-F1 model. A predicted protein scaffold is not a prepared copper-containing catalytic site; no docking score was generated. Any structural comparison needs the correct target, metal/cofactor state, binding-site preparation, and controls before it can inform ranking.

## Next discriminating work

The fixed-panel check of the existing [human iris atlas](../analysis/iris-atlas-run-2026-10-17/IRIS_TARGET_REPORT.md) is now complete: 57,422 nuclei, including 17,811 author-labeled uveal melanocytes and 15,583 posterior pigment epithelial nuclei. TYR transcripts were detected in 93.3% of melanocyte nuclei and 76.4% of posterior pigment epithelial nuclei; OCA2 in 54.7% and 87.4%, respectively. OPTN, RCHY1 and TBK1 transcripts were also detected in subsets of melanocyte nuclei. These are agent-calculated raw-count detection fractions, not reported drug-response rates.

This supports examining the proposed machinery in iris cells and makes a key distinction explicit: enzyme specificity does not establish specificity for the visible anterior iris. Detection in both target and posterior pigment populations makes compartment-selective exposure a separate question. Nuclear capture, sequencing depth, ambient RNA and dropout complicate interpretation; detection does not establish functional protein or pigment processing. The source has four individually labeled donors plus two overlapping pooled labels, which cannot be counted as six independent donors. [Dataset source](https://cellxgene.cziscience.com/collections/63d03351-06be-478e-a0db-f7a653b6b19b).

Next, qualify human-TYR functional assay data by exact target, assay system, reversibility and cell-function effects. The fetched target annotation points to ChEMBL1973, giving a concrete data query. In parallel at the hypothesis level, separate mature-pigment processing from organelle-marker loss and compare the two with the model's required loss rates. Delivery, activity and recovery should stay separate from any combined ranking score.

## Reproduction and checks

See [analysis methods](../analysis/README.md) for commands, assumptions, source IDs, and limitations. Eight independent model checks pass, including numerical integration against the analytical solution. The full existing workbench suite had fixture/dependency failures in the shared dev image; those are recorded separately and are not represented as a passing workbench validation.

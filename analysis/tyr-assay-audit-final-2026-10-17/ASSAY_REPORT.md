# Human TYR assay audit

*October 17, 2026. AI-run public-data analysis through the existing Regen HTTP and provenance functions.*

## Finding that changes the search

The ChEMBL target **CHEMBL1973** correctly identifies human TYR/P14679. Its activity endpoint nevertheless returns a mixture of source species, biological systems, measurements and secondary reports. Selecting that target is insufficient to produce a table of independently measured human-enzyme inhibitor potencies.

The frozen retrieval contains **870 activity records, 205 assays, 567 unique molecule identifiers and 68 document records**. A record is not an experiment, a molecule is not a validated inhibitor, and a document is not necessarily an original study. These counts describe this query snapshot, rather than all research available in 2026.

| Automated provenance triage | Activity records | Assays |
| --- | ---: | ---: |
| Description explicitly mentions a nonhuman system, or mixed systems | 35 | 13 |
| Nonhuman assay-organism metadata, without the preceding description flag | 22 | 4 |
| Explicit human description, without either preceding flag | 362 | 100 |
| Human metadata only; description does not establish species | 397 | 75 |
| Species unresolved by those rules | 54 | 13 |
| **Total** | **870** | **205** |

The rule is deliberately conservative. It scans assay descriptions and organism metadata, not full original methods. In particular, host cells expressing a recombinant human protein must not be confused with the protein's species. The 22-record metadata category contains **10 records from two conflicting annotations**: CHEMBL5518344 and CHEMBL5518347 describe human enzyme while listing *Agaricus bisporus* as assay organism. Those remain unresolved pending original-method review.

A concrete mismatch is activity **35518 / CHEMBL814341**: target organism is human, while its description states mushroom tyrosinase. It is not usable as human TYR potency merely because of its target assignment.

## Repeated reports and incomparable endpoints

Among the 362 records with explicit human descriptions, **120 occur in five manually identified reviews/perspectives**. ChEMBL flags 55 of those 362 records as potential duplicates. These flags overlap; subtracting both totals would double-count some exclusions. Review entries can lead to an original experiment, but do not independently reproduce it. The five-source classification is partial and uses the documents' own titles/abstracts.

The export includes IC50, Ki, single-concentration inhibition, enzyme kinetic parameters, ratios and calculated free energies. These are different quantities. Even measurements with the same unit require attention to substrate, enzyme preparation, incubation, readout and cellular context. No pooled potency, efficacy probability or composite candidate score was calculated.

## Useful comparator questions

| Comparator or series | Specific information in this snapshot | Research use |
| --- | --- | --- |
| Thiamidol, CHEMBL4743159 | Repeated 1.1 micromolar IC50 and 0.25 micromolar Ki entries include secondary reports. A different lysate experiment reports 0.17 micromolar IC50. | Keep as a production-control reference; trace each endpoint to its original measurement. |
| HOPNO aurone, CHEMBL3978212 | Original-study records distinguish 0.35 micromolar Ki for recombinant human enzyme, 16.6 micromolar IC50 in MNT1 lysate, and 85.3 micromolar IC50 for the whole-cell melanin endpoint. | Ask why biochemical binding fails to translate proportionately into cellular pigmentation. Do not divide Ki by cellular IC50 as if they measured the same endpoint. |
| 4-amino/4-amido indanones, including CHEMBL5562348 | The 2024 source has a 0.14 micromolar lysate IC50 for this molecule, alongside the 0.17 micromolar thiamidol comparator. Its abstract reports improvements over its parent scaffold in intact melanoma cells. | Expand the comparator set beyond one commercial scaffold. Lysate potency alone does not establish better intact-cell performance, reversibility or iris exposure. |

The aurone and indanone values are the returned database annotations, with exact assay and activity IDs retained in the exports. The primary indanone abstract supports a cellular improvement relative to its parent; its original full methods still need qualification before promoting an individual analogue. [Aurone primary study](https://doi.org/10.1021/acsmedchemlett.6b00369), [indanone primary study](https://doi.org/10.1016/j.ejmech.2024.116165).

The thiamidol source already reviewed reports recovery of melanogenesis in cultured skin melanocytes after withdrawal. That supports its role as a reversible synthesis reference, without measuring an iris lightening rate or proving elimination of mature pigment. [Original study](https://doi.org/10.1016/j.jid.2018.01.019).

## What happens next

Follow each retained scaffold through a consistent chain: **human enzyme → intact human pigment cell → withdrawal response → intracellular exposure and retention**. Record missing links explicitly. The new production-up and disposal leads are summarized in the [mechanism shortlist](../../research/mechanism-shortlist.md).

For the next computational comparison, prioritize measured free-drug exposure and pigment binding over an unvalidated docking score. Drug stored on melanin may be released after external exposure stops. As pigment changes, binding capacity might change too; that feedback is a hypothesis requiring measurements for each scaffold.

## Files and reproducibility

- [activities.csv](activities.csv): 870 records with endpoint, relation, unit, validity and duplicate annotations.
- [assays.csv](assays.csv): descriptions, organisms, tissue/cell annotations and the declared triage label.
- [record_flags.csv](record_flags.csv): partial review/conflict flags keyed to all activity IDs. Join to assays by assay ID and to documents by document ID; no activity records were removed.
- [documents.json](documents.json), [target.json](target.json): returned source annotations.
- [summary.json](summary.json), [qualification_summary.json](qualification_summary.json): counts and method limits.
- Receipts retain exact source URLs, hashes and source-script hashes. Full activity/assay JSON snapshots stay in local workbench data; selected field exports are committed here. The new raw-data folders are currently untracked in that separate checkout. Snapshots are serialized decoded API responses, not hashes of the original HTTP wire bytes.

Source endpoints: [target](https://www.ebi.ac.uk/chembl/api/data/target/CHEMBL1973.json), [activity query](https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id=CHEMBL1973&limit=1000), [assay query](https://www.ebi.ac.uk/chembl/api/data/assay.json?target_chembl_id=CHEMBL1973&limit=1000). ChEMBL standardization and source curation may change; preserve this snapshot when reproducing these counts.

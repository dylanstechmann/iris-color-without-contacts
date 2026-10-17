# Computational exploration of iris drug mechanisms

These are AI-run research calculations on hypothetical balances and existing public data. No drug was administered and no new tissue was obtained.

## Outputs

- [Model report](feasibility-run-2026-10-17/MODEL_REPORT.md): 720 combinations of production, baseline loss, added loss and persistent pigment.
- [Human iris target-location report](iris-atlas-run-2026-10-17/IRIS_TARGET_REPORT.md): fixed-panel reanalysis of 57,422 existing human iris nuclei.
- [Compound properties](workbench-comparison-2026-10-17/compounds.csv): seven PubChem identities with RDKit descriptors.
- [Target snapshots](target-snapshots-2026-10-17): human TYR/OCA2 sequence and annotation snapshots.
- [Workbench status](WORKBENCH_STATUS.md): actual runtime and check outcomes.

## Reproduce the balance

Run from this repository with Python 3.11 or later:

    python analysis/simulate_feasibility.py --assumptions analysis/feasibility_assumptions.json --out analysis/new-feasibility-run --plot
    python -m unittest discover -s analysis -p test_feasibility.py -v

Only the optional figure needs matplotlib and numpy. The model is analytical and uses the standard library. Output directories must be new. Null threshold times mean unreachable in finite time under the stated continuing assumptions.

Native loss k0 is derived from the assumed baseline pigment half-life. Baseline synthesis equals k0 for a mobile pool initially normalized to one. A drug hypothesis changes synthesis to f*k0 and adds loss a:

    dm/dt = f*k0 - (k0+a)*m
    total pigment fraction = p + (1-p)*m

The added loss is kept separate from the baseline source. During hypothetical recovery, the added pathway stops and production becomes b*k0. The default b=1 returns toward the modeled starting balance; b=5 explores an additional recovery-control assumption. Keeping b>1 active could overshoot the original balance.

No parameter value is fitted to iris biology. Neither threshold times nor grid counts are clinical forecasts or probabilities. A pigment fraction is not an eye color.

## Repeat the workbench chemistry

With the existing Regen Research Desk running locally on port 8092:

    python analysis/run_workbench_comparison.py --out analysis/new-compound-comparison

The script creates or reuses its named iris campaign within appearance research, then submits seven free public-identity/descriptor jobs through the existing service. It does not edit workbench source or read credentials. It exports only this campaign and the corresponding public results. Original complete job folders stay in workbench data; the imported manifests still describe those originals. The local receipt identifies the selected exported files.

Reference structures came from exact returned PubChem CIDs, including stereochemistry. Calculated logP is RDKit's descriptor for the represented structure; it is not a measured pH-dependent distribution coefficient. TPSA uses square angstroms and molecular weight uses g/mol.

## Repeat the human iris check

Inside the full Regen Workbench image, with this repository mounted as /lab/projects/iris-color:

    python /lab/projects/iris-color/analysis/intake_iris_atlas.py --data /lab/data/iris-pigment-2026-10-17
    python /lab/projects/iris-color/analysis/check_iris_targets.py --input /lab/data/iris-pigment-2026-10-17/human-iris.h5ad --collection /lab/data/iris-pigment-2026-10-17/cellxgene-collection.json --out /lab/projects/iris-color/analysis/new-iris-target-run

The intake uses the existing Regen HTTP/provenance functions. It fetches the identified public CZI collection and Iris dataset, validates the advertised asset size, and records its SHA-256. The 704,151,872-byte matrix stays in ignored local workbench data. Its hash is dc50696b177eb47b5bc5160df69a3ab74aba60dc6a402ad6ebca0e5057c5ec4c.

The prespecified panel is TYR, OCA2, SLC45A2, TPCN2, OPTN, RCHY1, TBK1, MLANA, PMEL, MITF, PTK2 and ITCH. Gene symbols must resolve uniquely. The analysis uses raw counts above zero as a detection indicator, retains author cell labels, and reports the source donor labels without treating overlapping pooled groups as independent donors.

Checks cover finite nonnegative integer values in the selected panel, annotation totals, per-gene denominators, and co-detection bounds. The entire transcriptome was not count-audited. Counts were not depth-normalized; ambient RNA, nuclear capture and dropout may affect detection. No differential-expression test, protein activity, pigmentation response, age/color comparison or turnover estimate is produced.

The iris subset has four individually named donor labels and two overlapping pooled labels. Its six labels must not be presented as six independent donors. Public institutional donor codes are retained only in source-group aggregate summaries.

## Targets and structures

The existing CLI fetched:

    regen uniprot P14679
    regen uniprot Q04671
    regen pdb 7RK7
    regen afdb P14679

7RK7 is an immune complex containing a nine-residue TYR peptide. AF-P14679-F1 is a predicted scaffold. Neither was used to generate docking or affinity scores. Complete coordinates and original fetch receipts remain in local workbench data; the target assessment records IDs and file hashes.

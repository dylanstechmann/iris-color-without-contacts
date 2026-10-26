# Computational exploration of iris drug mechanisms

These are AI-run research calculations on hypothetical balances and existing public data. No drug was administered and no new tissue was obtained.

## Outputs

- [Hue-window exploration](hue-window-run-2026-10-26/MODEL_REPORT.md): 744 hypothetical scatter-plus-absorber cases asking which CIELAB hue windows (blue, orange, purple) the assumed pigment spectra and back-return strengths can reach; standard colorimetry applied to invented iris spectra, not measured iris color.
- [KT-939 and thiamidol comparison](kt939-thiamidol-comparison.md): same-study lysate and cell-pigment IC50 ratios, source-name-transcribed structure checks, calculated descriptors and the missing paired withdrawal comparison.
- [Withdrawal and recovery](withdrawal-and-recovery.md): source-qualified inhibitor withdrawal observations and an exact counterexample showing which pigment mechanisms can share the same curve.
- [Ampyrone numerical readout review](ampyrone-readout-review.md): selected public-workbook values, exact source cells and distinct human-cell, skin and mouse-cell endpoints; no iris or withdrawal inference.
- [Phenolic binding follow-up](phenolic-binding-followup.md): measured paracetamol two-site data and remaining resorcinol/pyrazolone gaps, kept separate from the existing MST panel.
- [Measured binding benchmark and chemical coverage](binding-benchmark-run-2026-10-17/BENCHMARK_REPORT.md): nineteen resolved structures, source-specific binding/release endpoints and 88 probe/reference comparisons; no fitted affinity predictor.
- [Exposure and pigment-feedback model](exposure-run-2026-10-17/MODEL_REPORT.md): separate free/bound pools, membrane escape, gross pigment turnover and production up/down; 32 hypothetical cases.
- [TYR assay audit](tyr-assay-audit-final-2026-10-17/ASSAY_REPORT.md): 870 activity records with explicit species, endpoint and repeated-source qualifications.
- [IP3R2 numerical extraction](ip3r2-data-run-2026-10-17/DATA_REPORT.md): human skin-cell image/protein metrics and a separate mouse-cell energy endpoint from public source workbooks.
- [Model report](feasibility-run-2026-10-17/MODEL_REPORT.md): 720 combinations of production, baseline loss, added loss and persistent pigment.
- [Human iris target-location report](iris-atlas-run-2026-10-17/IRIS_TARGET_REPORT.md): fixed-panel reanalysis of 57,422 existing human iris nuclei.
- [Compound properties](workbench-comparison-2026-10-17/compounds.csv): seven PubChem identities with RDKit descriptors.
- [Target snapshots](target-snapshots-2026-10-17): human TYR/OCA2 sequence and annotation snapshots.
- [Workbench status](WORKBENCH_STATUS.md): actual runtime and check outcomes.

## Reproduce the hue-window exploration

Run from this repository with Python 3.11 or later; only the standard library is used:

    python analysis/simulate_hue_window.py --assumptions analysis/hue_window_assumptions.json --out analysis/new-hue-window-run
    python -m unittest discover -s analysis -p test_hue_window.py -v

The output folder must be new. The model is analytical: bounded Rayleigh-like backscatter, power-law eumelanin and pheomelanin absorbance, and a constant or red-edge return from behind the stroma. Color is CIE 1976 L\*a\*b\* for the CIE 1931 2° observer under illuminant D65, read from [unmodified CIE tables](cie-tables/README.md) whose SHA-256 values are pinned in the assumptions; the script refuses a changed table. Hue windows are ±20° hue-angle ranges centred on declared reference spectra, and a brightness floor is applied separately. Every iris spectrum and threshold is an assumption, no measured iris spectrum is used, and scenario counts are not probabilities. The first changes that could alter the results are measured melanin spectra and a measured back return.

## Reproduce the KT-939 comparison

From this repository in the existing development container, using the source XML already fetched by the withdrawal intake:

    python3 analysis/compare_kt939_thiamidol.py --xml ../regen-workbench/data/literature/iris-withdrawal-2026-10-17/kt939.xml --out analysis/new-kt939-comparison --plot
    python3 analysis/verify_artifacts.py
    python3 -m unittest discover -s analysis -p test_feasibility.py -v

The comparison requires RDKit; the optional figure uses matplotlib and Pillow. The actual run used Python 3.12.3 and RDKit 2023.09.3 in the existing development container. The output directory must be new. The script pins the prior XML hash, checks source identity and parses reported values, checks the two neutral molecular graphs against declared formulas and a shared core, and calculates each assay's IC50 ratio separately. No curves are refitted and no affinity or withdrawal rate is inferred. The database InChIKey is retained as source metadata, not recalculated by this runtime. Output hashes and software versions are recorded in the receipt, and the PNG figure was inspected visually.

If using another source cache, supply its KT-939 XML path. The [original withdrawal source records](withdrawal-evidence-run-2026-10-17/sources.json) identify the public XML URL and required hash. This run reused existing snapshots without a new fetch. Git newline conversion is disabled to preserve exact hashed bytes, including the original CRLF CSV rows. Previously committed artifacts and receipts are unchanged.

## Reproduce the withdrawal analysis

Use the existing research runtime for source intake and the optional scientific figure. With this repository mounted as /lab/projects/iris-color:

    python /lab/projects/iris-color/analysis/intake_withdrawal_sources.py --cache /lab/data/literature/iris-withdrawal-new
    python /lab/projects/iris-color/analysis/extract_withdrawal_evidence.py --cache /lab/data/literature/iris-withdrawal-new --clinical-inputs /lab/projects/iris-color/analysis/withdrawal_clinical_inputs.json --out /lab/projects/iris-color/analysis/new-withdrawal-evidence
    python /lab/projects/iris-color/analysis/demonstrate_recovery_identifiability.py --assumptions /lab/projects/iris-color/analysis/recovery_identifiability_assumptions.json --out /lab/projects/iris-color/analysis/new-recovery-identifiability --plot

Output directories must be new. Intake is bounded to three declared primary records. Available source XML and metadata use Regen's existing HTTP/provenance helpers; a failed publisher download is reported, not replaced by an asserted snapshot. KT-939 text values are parsed from the actual source paragraph. Clinical mean changes are declared manual transcriptions from publisher text inspected through the web tool. They produce descriptive mean contrasts, without significance tests or pharmacokinetic fits. Thiamidol 2018 endpoint qualification uses an explicitly identified rehosted accepted manuscript; no exact curve points are digitized.

The counterexample extends the existing linear pigment balance. Its three parameter sets are intentionally constructed to coincide during action. Old and newly made inventory are tracked separately, assuming no label recycling. Calculation residuals report overlap and accounting. All rates and times are hypothetical. Drug retention and delayed target recovery are excluded from this particular comparison; the earlier exposure model addresses those as separate hypotheses. The plotted example is not a fit to the withdrawal studies or to iris biology.

## Reproduce the ampyrone extraction

Inside the full Regen Workbench image, with this repository mounted as /lab/projects/iris-color:

    python /lab/projects/iris-color/analysis/fetch_ampyrone_sources.py --cache /lab/data/literature/iris-ampyrone-new
    python /lab/projects/iris-color/analysis/extract_ampyrone_data.py --input /lab/data/literature/iris-ampyrone-new/supporting-data.xlsx --out /lab/projects/iris-color/analysis/new-ampyrone-extract --plot

The source workbook is read without editing through Python's standard-library ZIP/XML reader. Its exact snapshot hash is pinned. The output folder must be new. The numerical cells were declared after inspecting source layout and figure mapping, before calculating summaries. Ratios divide matched condition means within each endpoint. Original values, source issues and endpoint-specific replication limits are exported. No sample labels are repaired, donor counts inferred, new significance tests performed, or new kinetic constants fitted. Figure 2 contains means/dispersion rather than replicate-level curves. Scientific plotting uses the existing matplotlib runtime. The original XML/workbook stay in ignored literature storage; source sizes and hashes are exported.

## Reproduce the binding benchmark

Inside the full Regen Workbench image, with this repository mounted as /lab/projects/iris-color:

    python /lab/projects/iris-color/analysis/build_binding_benchmark.py --inputs /lab/projects/iris-color/analysis/binding_benchmark_inputs.json --cache /lab/data/literature/iris-binding-benchmark-new --out /lab/projects/iris-color/analysis/new-binding-benchmark --plot

The runner uses existing Regen HTTP/provenance helpers, public source XML/PDF and PubChem properties, then RDKit 2026.03.6 for the recorded structures. Use a fresh output directory; a fresh cache is appropriate when changing identity queries. Raw XML/PDF stay in ignored literature data. Nineteen public property snapshots are exported with hashes. The eleven manually declared MST estimates/confidence values must match the fetched XML table; other source-specific values are retained as declared transcriptions.

Fingerprint settings are declared before calculation. Parent preparation uses FragmentParent and Uncharger, preserving returned stereochemistry without canonical tautomer enumeration. All returned graphs were unchanged by those operations in this run. Chiral sensitivity concerns the database representations, not verified experimental mixtures or assay-pH species. The outputs include the full 88-pair matrix, three nearest neighbors under each representation, reference-only nearest neighbors and seven separate descriptor-range checks. No predictor, calibrated applicability-domain cutoff or aggregate candidate score is fitted.

## Reproduce the exposure model

The full Regen Workbench image provides scipy 1.17.1, numpy 2.3.5 and matplotlib 3.11.2. With this repository mounted as /lab/projects/iris-color:

    python /lab/projects/iris-color/analysis/simulate_exposure.py --assumptions /lab/projects/iris-color/analysis/exposure_assumptions.json --out /lab/projects/iris-color/analysis/new-exposure-run --plot

The output folder must be new. The saved receipt contains all parameters, software versions, source hash and generated-file hashes. The solver uses an explicit Jacobian and records drug accounting, nonnegativity and capacity bounds. The static scientific SVG is portable; a PNG preview is written beside the output folder and is not part of the hashed run package. No candidate-specific parameters are fitted.

Two comparisons are kept separate: equal initial free concentration with differing preloaded inventories, and equal input histories with differing achieved exposure. Threshold statuses distinguish a crossing from a response already below threshold. Activation and suppression use different mappings from the placeholder target effect to pigment synthesis; a 10% target effect is not universally a 10% source change.

## Repeat the new source checks

Inside the full Regen Workbench image, with this repository mounted as /lab/projects/iris-color:

    python /lab/projects/iris-color/analysis/audit_tyr_assays.py --cache /lab/data/iris-tyr-assays-new --out /lab/projects/iris-color/analysis/new-tyr-audit
    python /lab/projects/iris-color/analysis/qualify_tyr_records.py --input /lab/projects/iris-color/analysis/new-tyr-audit

The first command performs bounded pagination through public target, activity, assay and document endpoints, records actual fetch provenance, and checks identifier/page completeness. Full activity/assay responses stay in workbench data; selected fields are exported. The second command flags a declared partial set of secondary sources and species conflicts. It retains every activity ID and does not pool measurements or rank compounds by potency.

The IP3R2 extraction reads two original public source workbooks obtained through Regen's HTTP/provenance functions:

    python analysis/extract_ip3r2_data.py --input PATH_TO_ORIGINAL_WORKBOOKS --out analysis/new-ip3r2-extract

See the run's source URLs and SHA-256 values in [summary.json](ip3r2-data-run-2026-10-17/summary.json). Output folders for the audit and workbook extraction must be new. The extraction uses Python's standard-library ZIP/XML reader and statistics module; it does not modify Excel files, infer donor independence, or perform significance tests.

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

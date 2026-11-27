# Computational exploration of iris drug mechanisms

These are AI-run research calculations on hypothetical balances and existing public data. No drug was administered and no new tissue was obtained.

## Outputs

- [Hue-window exploration](hue-window-run-2026-10-26-calibrated/MODEL_REPORT.md): 10,872 hypothetical scatter-plus-absorber cases asking which CIELAB hue windows (blue, orange, purple) the assumed pigment spectra, stroma settings and back-return strengths can reach, using only stroma settings that read blue when pigment-free; standard colorimetry and one sourced eumelanin exponent applied to invented iris spectra, not measured iris color.
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
- [KT-939 washout fit](kt939-washout-fit-run-2026-11-09/): published Hou et al. 2025 KT-939 washout series fitted to a washout half-time with bootstrap CI, accumulated-pigment endpoint, and minimum raw-data request for the authors listed.
- [Optics v1 run](optics-v1-run-2026-11-09/): layered forward model per the optics spec, CIELAB with uncertainty, self-consistency checks passing; calibration gate unevaluated pending accessible published iris spectra.
- [Optics v1 measured-melanin run](optics-v1-measured-melanin-run-2026-11-09/): the same layered forward model with the assumed power-law melanin spectra replaced by pinned measured Sarna & Swartz 1988 extinction coefficients (550-normalized shapes); 550 nm magnitudes remain order-of-magnitude assumptions; calibration gate still unevaluated.
- [Hue-window measured-melanin exploration](hue-window-measured-melanin-run-2026-11-09/MODEL_REPORT.md): the hue-window exploration re-run with the same measured melanin spectral shapes instead of the swept pheomelanin exponent; the qualitative finding is unchanged — orange and purple windows stay unreachable over a dark back and still require a strong reddish back return.
- [F5 washout-kinetics pipeline](washout-fit-pipeline-validation-2026-11-10/MODEL_REPORT.md): multi-readout washout fitter separating synthesis flux, old-pigment pool, and free-compound inhibition, validated on synthetic/hypothetical data only; ready to consume Phase-2 paired-washout data when a facility delivers it.
- [Paired generic synthetic G1 design simulation](washout-paired-design-simulation-run-2026-11-15/MODEL_REPORT.md): KT-939/thiamidol-labelled generic arms across four half-time-ratio scenarios and nested full/reduced/minimal designs; mandatory isotope, shared effects/common random numbers, descriptive per-scenario/per-design matched-fit counts and fractions, linearized-CI diagnostics, separately matched no-isotope controls, explicit MNT-1 accounting, and receipted hashes.
- [Phase-1 feasibility-gate evaluator](gate-evaluation-demo-2026-11-10/run/EVALUATION_REPORT.md): mechanical per-gate results on unchanged predeclared criteria, now with fail-closed schema/type/unit/provenance and run-metadata checks plus valid synthetic facility-style fixtures; the linked November 10 output is an archived schema-1.0 artifact, not measured facility evidence.
- [Workbench status](WORKBENCH_STATUS.md): actual runtime and check outcomes.

## Reproduce the hue-window exploration

Run from this repository with Python 3.11 or later; only the standard library is used:

    python analysis/simulate_hue_window.py --assumptions analysis/hue_window_assumptions.json --out analysis/new-hue-window-run
    python -m unittest discover -s analysis -p test_hue_window.py -v

The output folder must be new. The model is analytical: bounded stromal backscatter, power-law eumelanin and pheomelanin absorbance, and a constant or red-edge return from behind the stroma. Color is CIE 1976 L\*a\*b\* for the CIE 1931 2° observer under illuminant D65, read from [unmodified CIE tables](cie-tables/README.md) whose SHA-256 values are pinned in the assumptions; the script refuses a changed table. Hue windows are ±20° hue-angle ranges centred on declared reference spectra, with chroma and luminance floors applied separately. Stroma scattering is swept and then calibrated: only settings whose pigment-free stroma over a dark back reads as blue are used to interpret pigmented cases. The eumelanin wavelength exponent (3.48) comes from a published melanosome absorption law; every other iris input is an assumption, and [the assumptions file](hue_window_assumptions.json) records the provenance and limits of each. No measured iris spectrum is used, and scenario counts are not probabilities. The first changes that could alter the results are a measured pheomelanin visible spectrum and a measured back return.

## Reproduce the measured-melanin runs

Run from this repository with the project virtual environment (Python 3.12.16, NumPy 2.5.4 for the optics model; the hue-window model uses only the standard library):

    .venv/bin/python3 analysis/optics-v1-measured-melanin-run-2026-11-09/simulate_optics_v1.py --assumptions analysis/optics-v1-measured-melanin-run-2026-11-09/assumptions.json --out analysis/new-optics-measured-run
    cd analysis/optics-v1-measured-melanin-run-2026-11-09 && ../../.venv/bin/python3 -m unittest test_optics_v1 -v
    .venv/bin/python3 analysis/simulate_hue_window_measured.py --assumptions analysis/hue_window_assumptions_measured.json --out analysis/new-hue-window-measured-run
    python -m unittest discover -s analysis -p test_hue_window_measured.py -v

Output folders must be new. Both runs replace the previously assumed power-law melanin spectra with the measured Sarna & Swartz 1988 extinction coefficients in [melanin-spectra/](melanin-spectra/README.md), whose SHA-256 values are pinned in the assumptions; the scripts refuse a changed table. The shapes are linearly interpolated and normalized to 1.0 at 550 nm. The 550 nm magnitudes and every other iris input remain order-of-magnitude assumptions; these are hypothetical models, not measured iris color. The optics script, its assumptions and its tests live inside the run directory and read the CIE tables and melanin CSVs through relative paths, mirroring the original optics v1 run. A measured pheomelanin visible spectrum is no longer an outstanding input for these models; a measured back return still is.

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


## Reproduce the F5 washout-kinetics pipeline

Run from this repository with the project virtual environment (NumPy and SciPy required):

    .venv/bin/python3 analysis/fit_washout.py --assumptions analysis/washout_assumptions.json --out analysis/new-washout-fit-run
    .venv/bin/python3 -m unittest discover -s analysis -p test_washout.py -v

The output directory must be new. The assumptions JSON (`analysis/washout_assumptions.json`) declares the synthetic ground-truth parameters, noise levels, and readout flags. The CLI generates synthetic data from those parameters, fits the model, and writes fitted parameters, confidence intervals, per-timepoint residuals, `receipt.json`, and `MODEL_REPORT.md`. Supply `--input PATH.tsv` to fit real data instead of generating synthetic data.

The pipeline is deliberately built to consume Phase-2 paired-washout data the moment a facility delivers it; today it is validated only on clearly labeled synthetic data. The identifiability calculation in `analysis/withdrawal-and-recovery.md` shows that total pigment alone cannot separate a fixed persistent pool, partial production suppression, and added loss — three mechanisms that share one total-inventory curve. The requested readouts in `research/core-facility-quote-request.md` section 3 (heavy/light melanin isotope-ratio, free-compound LC-MS/MS, total melanin, and cell-count normalization) are the minimal set this pipeline needs to break that symmetry. No real washout data are claimed as fitted.

Developed by AI assistant; owner-reviewed before interpretation.


## Reproduce the paired generic synthetic G1 design simulation

Run from this repository with the existing project virtual environment (Python 3.12.16, NumPy 2.5.4, SciPy 1.18.1); no additional dependency is used:

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python3 -m unittest discover -s analysis -p 'test_washout*.py' -v
    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python3 analysis/simulate_washout_design.py --assumptions analysis/washout_design_assumptions.json --out analysis/new-paired-washout-design-run
    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python3 -m unittest discover -s analysis -p 'test_*.py' -v
    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python3 analysis/verify_artifacts.py

The output path must be new; an existing path exits with an error without changing its contents. The receipted November 15 run used `analysis/washout-paired-design-simulation-run-2026-11-15` as the output path. `washout_design_assumptions.json` is the frozen generic/non-calibrated input. Its `ic50` values describe only assumed free-compound synthesis inhibition, not accumulated-pigment IC50. `washout_design.py` reuses the unchanged `simulate_washout`, `fit_washout`, `PARAM_NAMES`, `write_json`, and `build_receipt` primitives.

Full uses nine timepoints, three replicates, and three systems (two generic synthetic donors plus one MNT-1 reference cell-line system). Reduced uses five timepoints, two replicates, one synthetic donor, and MNT-1; minimal uses four timepoints with the same two systems and two replicates. Reduced/minimal records are exact nested subsets of the full observations. System/pair effects are shared across arms and random streams are common across ratios; no donor mixed-effects model is fitted. Every candidate design retains total melanin, free compound, and isotope `old_fraction` readouts. No-isotope fits are labelled diagnostic negative controls only.

**Independent-review correction:** the superseded development output incorrectly used record-level Wilson intervals and scenario-mixed no-isotope aggregates. Those outputs are not valid evidence. Within-system replicates are correlated, scenario copies use common random numbers, and scenario-mixed records have no single probability meaning. The corrected run removes the Wilson utility and every record-level inferential probability interval. Decisions, failures, and CI coverage now contain only descriptive matched-fit counts/fractions within one scenario/design. No primary or control result is pooled across scenarios; each no-isotope comparison is matched on scenario, design, system, replicate, and observations.

The actual run contains 68 primary paired records (136 separate arm fits) as operational run-size accounting, not pooled-scenario evidence, with no primary fit or covariance failures. Descriptive counts of both proposed conditions, reported separately for each scenario/design, were:

| True half-time ratio | Full | Reduced | Minimal |
| ---: | ---: | ---: | ---: |
| 1.00 | 9/9 | 4/4 | 4/4 |
| 1.25 | 9/9 | 4/4 | 4/4 |
| 1.50 | 4/9 | 2/4 | 2/4 |
| 2.00 | 0/9 | 0/4 | 0/4 |

At true ratio 2.00, descriptive both-arm recovery >=0.80 counts were 3/9 full, 1/4 reduced, and 1/4 minimal; mean fitted thiamidol-labelled recovery was 0.792, 0.784, and 0.775 respectively. Separately within each scenario, full-design KT-939-labelled no-isotope old/new median-CI width ratios were 264.85/297.63 with covariance failures 3/9; these common-random-number repetitions are not independent confirmations. Full thiamidol-labelled width ratios and covariance-failure counts were 15.54/16.96 and 1/9 at ratio 1.00, 22.31/24.46 and 7/9 at 1.25, 2.96/2.65 and 5/9 at 1.50, and 4.91/6.07 and 8/9 at 2.00. In every reduced/minimal scenario, no-isotope covariance failed for 4/4 fits per arm and old/new CI width ratios were not evaluable. These are correlated descriptive records, not independent Bernoulli samples, probabilities, or pooled-scenario evidence; they do not select a preferred design.

The ratio `<1.5` and both-arm day-14 recovery `>=0.80` conditions remain proposed, configurable, owner-unapproved metadata, not go/no-go criteria or formal equivalence. Isotope recoverability is an identifiability diagnostic, not an assay LOD measurement. MNT-1 is not a donor. Linearized/delta-method CIs showed imperfect descriptive coverage counts and sometimes large recovery widths in this synthetic run; they are not guaranteed uncertainty intervals. No variance estimator, mixed-effects population model, independence correction, or formal decision probability is supplied. No ocular, clinical, facility-contact, spending, adoption, or gate-passage conclusion follows.

Validation observed after the review correction: focused `test_washout*.py` passed 39/39; full top-level analysis `test_*.py` passed 99/99; measured-melanin optics passed 16/16 with `PYTHONDONTWRITEBYTECODE=1 ../../.venv/bin/python3 -m unittest test_optics_v1 -v` from `analysis/optics-v1-measured-melanin-run-2026-11-09`; no skips were reported. New regressions independently check noiseless forward truths, realized shared arm multipliers, configured true ratios, one-arm failure decisions, every runtime source and assumptions hash, and the saved November 15 receipt/artifacts read-only. The artifact verifier passed 120 selected artifacts with the project `.venv`. The earlier `/usr/bin/python3` 3.12.3 artifact-verifier attempt failed before script execution with `ModuleNotFoundError: No module named 'json'`; the existing `.venv` invocation succeeded. The corrected run was regenerated once after preserving `/tmp/iris-washout-paired-design-simulation-run-2026-11-15-pre-review-backup`; its two output hashes, four runtime-source hashes plus CLI receipt hash, and assumptions hash passed independent read-only verification. An output collision returned exit 2 with unchanged `results.json`. The November 10 archive and legacy washout files remained unchanged.

## Replay the paired synthetic washout archive

Use Python 3.12 with NumPy 2.5.4 and SciPy 1.18.1, as in the [GitHub Actions workflow](../.github/workflows/paired-washout.yml). Run from the repository root:

    python -B -m unittest discover -s analysis -p test_replay_paired_washout.py -v

The check verifies the archived receipt, generates a fresh run in a temporary directory and verifies its receipt. It checks the status, three proposed conditions and fitted half-time ratio for each of the 68 archived primary synthetic fits. Conditions must agree exactly and ratios may differ by up to 0.00001 to allow numerical drift across SciPy builds. This checks whether the synthetic result reproduces in software.

## Targets and structures

The existing CLI fetched:

    regen uniprot P14679
    regen uniprot Q04671
    regen pdb 7RK7
    regen afdb P14679

7RK7 is an immune complex containing a nine-residue TYR peptide. AF-P14679-F1 is a predicted scaffold. Neither was used to generate docking or affinity scores. Complete coordinates and original fetch receipts remain in local workbench data; the target assessment records IDs and file hashes.

## Reproduce the Phase-1 feasibility-gate evaluator

Run from this repository with Python 3.11 or later; only the standard library is used:

    PYTHONDONTWRITEBYTECODE=1 python3 analysis/evaluate_gates.py --report analysis/gate-evaluator-fixtures/valid-synthetic --criteria analysis/gate_criteria.json --out analysis/new-gate-evaluation-run
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s analysis -p 'test_evaluate_gates.py' -v

The output directory must be new. Schema 1.1 rejects malformed JSON, duplicate keys, unknown fields/files, missing compound or readout declarations, wrong/missing units, ambiguous booleans, non-finite numbers, inconsistent provenance, and mismatched gate/run metadata before creating output. A completely missing gate or an explicit null readout is "not evaluable", never silently passed. The evaluator writes `gate_evaluation.json`, `EVALUATION_REPORT.md`, and `receipt.json` with input/output SHA-256 values and the validated shared `data_kind`, `facility_id`, and `run_id`; it does not hardcode synthetic output or accept a measured label without the measured provenance declarations. Provenance references are checked for schema consistency, not authenticated as real facility evidence. See `analysis/README_gates_input_format.md` for the strict contract and `analysis/gate-evaluator-fixtures/valid-synthetic/` for complete fixtures. The archived November 10 schema-1.0 demo is preserved unchanged and is not accepted as new input. Thresholds remain predeclared and unchanged, including PROPOSED status awaiting owner confirmation. Tests exercise synthetic fixtures and hypothetical metadata paths only; no measured facility data, design adoption, feasibility verdict, or biological/clinical validation is claimed.

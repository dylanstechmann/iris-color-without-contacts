# Feasibility-gate report input format

*2026-11-10. AI-assisted drafting; owner-reviewed.*

*Schema 1.1 update, 2026-11-26: AI-assisted drafting; owner review pending before interpretation.*

This document defines the strict JSON contract that `analysis/evaluate_gates.py` accepts in a `--report` directory. It maps to the existing deliverable formats and gate criteria in `research/core-facility-quote-request.md` §4–5; it does not add a wet-lab protocol, select a washout design, or issue a feasibility verdict.

## Files in the report directory

Provide one JSON file per available gate, named either `{gate_id}.json` or `{gate_id}_report.json`. Do not supply both names for the same gate. Unrecognized `*.json` files are rejected so a misspelled gate filename cannot be ignored silently; non-JSON sidecar files are not consumed.

| Gate ID (file stem) | RFQ section | Content |
| --- | --- | --- |
| `gate_1_old_pigment_labeling` | §5 Gate 1 | Isotope-ratio labeling validation |
| `gate_2_free_compound_validation` | §5 Gate 2 | Per-compound LC-MS/MS assay validation |
| `gate_3_ampyrone_solubility` | §5 Gate 3 | Ampyrone solubility and viability |

The three files in `analysis/gate-evaluator-fixtures/valid-synthetic/` are complete valid synthetic examples. The November 10 demo under `analysis/gate-evaluation-demo-2026-11-10/` is an archived schema-1.0 artifact and is not accepted as schema-1.1 input.

## Common top-level fields

Every report must declare the following fields, with no additional top-level fields except the Gate 3 `compound` declaration described below:

```json
{
  "report_version": "1.1",
  "gate_id": "gate_1_old_pigment_labeling",
  "facility_id": "SYNTHETIC-FIXTURE",
  "run_id": "synthetic-phase1-fixture-2026-11-26",
  "data_kind": "synthetic",
  "provenance": {
    "source_kind": "synthetic_fixture",
    "source_reference": "analysis/test_evaluate_gates.py synthetic gate-1 fixture"
  },
  "observations": {}
}
```

- `report_version` — exactly `"1.1"`.
- `gate_id` — exactly the gate ID represented by the filename.
- `facility_id` — non-empty reporting-facility or explicit synthetic-fixture identifier, without surrounding whitespace.
- `run_id` — non-empty identifier for this coordinated Phase-1 evaluation run. All supplied gate reports must use the same value. Per-gate batch details belong in `source_reference`, not in a conflicting `run_id`.
- `data_kind` — `"synthetic"` or `"measured"`; all supplied gate reports must agree.
- `provenance` — exact origin declaration described below.
- `observations` — required for Gates 1 and 3. Gate 2 uses `compounds` instead.

An empty report directory is rejected because there is no validated `data_kind` to propagate. A missing individual gate file is different: that gate's criteria are reported as **not evaluable**, while the other validated reports determine the run metadata.

## Provenance and data kind

`data_kind` is not accepted as a stand-alone label. Its exact provenance requirements are:

| `data_kind` | Required `provenance.source_kind` | Required references |
| --- | --- | --- |
| `synthetic` | `synthetic_fixture` | non-empty `source_reference` |
| `measured` | `facility_measurement` | non-empty `source_reference` and `raw_data_reference` |

No other provenance fields are accepted. In particular, changing only `data_kind` from `synthetic` to `measured` is rejected, as is mixed synthetic/measured metadata within one run.

These checks establish internal schema consistency only. The evaluator does not open or authenticate the referenced facility records, verify that raw files exist, or establish biological or clinical validity. A `measured` value in `gate_evaluation.json` and `receipt.json` means that the supplied reports consistently declared the measured-data provenance contract; it is not independent evidence authentication.

## Observation objects

Every criterion must be present and must be an object with exactly `value` and `unit`:

```json
"c2_old_pool_fraction_lod": {
  "value": 0.05,
  "unit": "fraction_of_total"
}
```

The direct-value shorthand accepted by the archived evaluator is not valid report input. Units must exactly equal the unit declared for that criterion in `analysis/gate_criteria.json`; missing units, substituted percent/fraction units, and extra wrapper fields are rejected.

Boolean observations must be JSON `true` or `false`. Strings such as `"true"`, numbers `0`/`1`, and other truthy/falsy values are not coerced. Numeric observations must be finite JSON numbers, not numeric strings or booleans. `NaN`, `Infinity`, `-Infinity`, and numbers overflowing to infinity are rejected. An explicit `null` value with the correct unit remains allowed and evaluates as **not evaluable**; an absent readout is a malformed report.

## Gate 1 — Old-pigment pre-labeling (`gate_1_old_pigment_labeling`)

Maps to RFQ §5 Gate 1 and deliverable "Isotope-ratio validation report". The isotope old/new separation readouts remain mandatory in this gate evaluator.

| Criterion ID | Expected observation type | Exact unit |
| --- | --- | --- |
| `c1_baseline_separation` | boolean | `boolean` |
| `c2_old_pool_fraction_lod` | finite number or null | `fraction_of_total` |
| `c3_chemical_melanin_agreement` | finite number or null | `%` |

All three declarations are required in a supplied Gate 1 report.

## Gate 2 — Intracellular free-compound assay validation (`gate_2_free_compound_validation`)

Maps to RFQ §5 Gate 2 and deliverable "LC-MS/MS method documentation". `gate_criteria.json` predeclares `required_compounds` as `KT-939`, `Thiamidol`, and `Ampyrone`. The `compounds` object must contain exactly those names; a missing or unknown compound is rejected.

Each compound block must declare every criterion:

| Criterion ID | Expected observation type | Exact unit |
| --- | --- | --- |
| `c1_spike_recovery` | finite number or null | `%` |
| `c2_calibration_r2` | finite number or null | `unitless` |
| `c3_intra_day_cv` | finite number or null | `%` |
| `c4_freeze_thaw_stability` | boolean or null | `boolean` |

Abbreviated example (the real input must also include Thiamidol and Ampyrone):

```json
"compounds": {
  "KT-939": {
    "c1_spike_recovery": {"value": 95.0, "unit": "%"},
    "c2_calibration_r2": {"value": 0.995, "unit": "unitless"},
    "c3_intra_day_cv": {"value": 8.0, "unit": "%"},
    "c4_freeze_thaw_stability": {"value": true, "unit": "boolean"}
  }
}
```

## Gate 3 — Ampyrone solubility window (`gate_3_ampyrone_solubility`)

Maps to RFQ §5 Gate 3 and deliverable "Feasibility-gate pass/fail outcomes". The top-level field `"compound": "Ampyrone"` is required so observations cannot be attached implicitly to another compound.

| Criterion ID | Expected observation type | Exact unit |
| --- | --- | --- |
| `c1_no_visible_precipitate` | boolean or null | `boolean` |
| `c2_concentration_drop` | finite number or null | `%` |
| `c3_cell_viability` | finite number or null | `%` |

## Fail-closed validation rules

Before creating the output directory, the evaluator rejects:

1. Invalid JSON, duplicate object keys, non-object roots, unsupported schema versions, and non-finite numbers anywhere in the JSON input.
2. Missing or unknown top-level, provenance, observation-wrapper, criterion, or compound fields.
3. Missing required compounds or readouts, direct-value shorthand, wrong or missing units, ambiguous booleans, and wrong numeric types.
4. A Gate 3 compound other than `Ampyrone`, or Gate 2 compound sets that differ from `required_compounds`.
5. `data_kind`/provenance mismatches and inconsistent `facility_id`, `run_id`, or `data_kind` across supplied gate reports.
6. Unknown report JSON filenames and simultaneous use of both accepted filenames for one gate.
7. Malformed criteria, including unsupported comparators, non-finite thresholds, missing provenance, and absent per-compound declarations.

The predeclared numerical and boolean gate thresholds are unchanged. Criteria provenance and `CONFIRMED`/`PROPOSED` status remain part of the output.

After validation, a completely missing gate file or an explicit null observation is **not evaluable**, never silently passed. Exit status is `0` when all evaluated criteria pass, `1` when a criterion fails or is not evaluable, and `2` for invocation or malformed-input errors. Per-gate mechanical results are not an overall feasibility verdict.

## Receipt discipline

The evaluator writes:

- `gate_evaluation.json` with the validated `data_kind`, shared `facility_id`/`run_id`, and per-criterion results;
- `EVALUATION_REPORT.md` with mechanical per-gate results and limitations;
- `receipt.json` with the same data/run metadata, SHA-256 of the criteria and each consumed report, output SHA-256/byte sizes, and a normalized command record.

This matches the receipt convention established in `analysis/kt939-washout-fit-run-2026-11-09/` and `analysis/washout-fit-pipeline-validation-2026-11-10/`.

## Mapping to RFQ deliverables

| RFQ §4 deliverable | How it feeds the evaluator |
| --- | --- |
| Raw data (.raw, .wiff, etc.) | Not consumed or authenticated by the evaluator; identify its manifest in `raw_data_reference` for measured input and retain it for audit |
| Processed data files (TSV) | Convert to the strict JSON contract above; identify the processed source in `source_reference` |
| LC-MS/MS method documentation | Reference only; pass/fail targets are predeclared in `gate_criteria.json` |
| Isotope-ratio validation report | Becomes `gate_1_old_pigment_labeling_report.json` |
| Feasibility-gate pass/fail outcomes | **Output** of the evaluator, not input; no overall feasibility verdict is generated |

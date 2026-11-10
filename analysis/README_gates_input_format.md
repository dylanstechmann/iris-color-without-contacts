# Feasibility-gate report input format

*2026-11-10. AI-assisted drafting; owner-reviewed.*

This document defines the JSON schema that `analysis/evaluate_gates.py` expects in a `--report` directory. It maps 1:1 to the deliverable formats and gate criteria in `research/core-facility-quote-request.md` §4–5 so that a facility handoff translates directly into files the evaluator can consume.

## Files in the report directory

The evaluator looks for one JSON file per gate, named either `{gate_id}.json` or `{gate_id}_report.json`. All other files are ignored. Unknown or missing fields are reported as **"not evaluable"**, never silently passed.

| Gate ID (file stem) | RFQ section | Content |
| --- | --- | --- |
| `gate_1_old_pigment_labeling` | §5 Gate 1 | Isotope-ratio labeling validation |
| `gate_2_free_compound_validation` | §5 Gate 2 | Per-compound LC-MS/MS assay validation |
| `gate_3_ampyrone_solubility` | §5 Gate 3 | Ampyrone solubility and viability |

## Common top-level fields

Every report file must contain:

```json
{
  "report_version": "1.0",
  "gate_id": "gate_1_old_pigment_labeling",
  "facility_id": "string",
  "run_id": "string",
  "data_kind": "synthetic",
  "observations": { ... }
}
```

- `report_version` — must be `"1.0"` (future versions may extend).
- `gate_id` — must match the file stem.
- `facility_id` — identifier of the reporting facility.
- `run_id` — facility-internal run or batch identifier.
- `data_kind` — `"synthetic"` for test/validation data; `"measured"` for real facility data.
- `observations` — mapping from criterion ID to observed value (see per-gate tables below).

For `gate_2_free_compound_validation`, the top-level key is `compounds` instead of `observations` (see below).

## Gate 1 — Old-pigment pre-labeling (`gate_1_old_pigment_labeling`)

Maps to RFQ §5 Gate 1 and deliverable "Isotope-ratio validation report".

| Criterion ID | RFQ criterion | Expected observation type | Unit |
| --- | --- | --- | --- |
| `c1_baseline_separation` | Quantifiable heavy/light separation at baseline | boolean | boolean |
| `c2_old_pool_fraction_lod` | Old-pool fraction detectable above LOD after 7-day chase | number (fraction of total) | fraction_of_total |
| `c3_chemical_melanin_agreement` | Agreement with total chemical melanin within tolerance | number | % |

Example `observations`:

```json
"observations": {
  "c1_baseline_separation": {"value": true, "unit": "boolean"},
  "c2_old_pool_fraction_lod": {"value": 0.05, "unit": "fraction_of_total"},
  "c3_chemical_melanin_agreement": {"value": 8.5, "unit": "%"}
}
```

## Gate 2 — Intracellular free-compound assay validation (`gate_2_free_compound_validation`)

Maps to RFQ §5 Gate 2 and deliverable "LC-MS/MS method documentation". Criteria are evaluated **per compound**; each compound gets its own sub-object.

| Criterion ID | RFQ criterion | Expected observation type | Unit |
| --- | --- | --- | --- |
| `c1_spike_recovery` | Spike recovery 80–120 % in cell-lysate matrix | number | % |
| `c2_calibration_r2` | Calibration linearity R² ≥ 0.99 | number | unitless |
| `c3_intra_day_cv` | Intra-day CV < 15 % at the LOQ | number | % |
| `c4_freeze_thaw_stability` | Stability through ≥ 1 freeze-thaw cycle | boolean | boolean |

Example `compounds`:

```json
"compounds": {
  "KT-939": {
    "c1_spike_recovery": {"value": 95.0, "unit": "%"},
    "c2_calibration_r2": {"value": 0.995, "unit": "unitless"},
    "c3_intra_day_cv": {"value": 8.0, "unit": "%"},
    "c4_freeze_thaw_stability": {"value": true, "unit": "boolean"}
  },
  "Thiamidol": { ... }
}
```

The criterion IDs inside each compound block must exactly match the criteria declared in `gate_criteria.json`.

## Gate 3 — Ampyrone solubility window (`gate_3_ampyrone_solubility`)

Maps to RFQ §5 Gate 3 and deliverable "Feasibility-gate pass/fail outcomes".

| Criterion ID | RFQ criterion | Expected observation type | Unit |
| --- | --- | --- | --- |
| `c1_no_visible_precipitate` | No visible precipitate | boolean | boolean |
| `c2_concentration_drop` | ≤ 10 % drop in nominal concentration at 6 days | number | % |
| `c3_cell_viability` | Cell viability ≥ 70 % of vehicle | number | % |

Example `observations`:

```json
"observations": {
  "c1_no_visible_precipitate": {"value": false, "unit": "boolean"},
  "c2_concentration_drop": {"value": 5.0, "unit": "%"},
  "c3_cell_viability": {"value": 85.0, "unit": "%"}
}
```

## Value shorthand

For brevity, the `"value"` may be supplied directly without the wrapper dict:

```json
"observations": {
  "c1_baseline_separation": true
}
```

The evaluator accepts either form.

## Validation rules

1. **Missing criterion**: if an expected criterion ID is absent from the observations (or from a compound block), the result is `"not_evaluable"`.
2. **Missing gate report**: if no JSON file matches a gate ID in the criteria file, all criteria for that gate are `"not evaluable"`.
3. **Unknown extra fields**: ignored; only declared criteria are evaluated.
4. **Unit mismatch**: not checked mechanically; the evaluator trusts the reported unit and compares the numeric value against the threshold. Facilities are expected to declare units explicitly.

## Receipt discipline

The evaluator writes a `receipt.json` in the output directory that records:
- SHA-256 of the criteria JSON
- SHA-256 of every report JSON consumed
- SHA-256 and byte size of `gate_evaluation.json` and `EVALUATION_REPORT.md`
- Exact command line used

This matches the receipt convention established in `analysis/kt939-washout-fit-run-2026-11-09/` and `analysis/washout-fit-pipeline-validation-2026-11-10/`.

## Mapping to RFQ deliverables

| RFQ §4 deliverable | How it feeds the evaluator |
| --- | --- |
| Raw data (.raw, .wiff, etc.) | Not consumed by evaluator; kept for audit trail |
| Processed data files (TSV) | Facility may convert to the JSON schema above, or the evaluator may be extended to read TSV directly |
| LC-MS/MS method documentation | Reference only; pass/fail targets are predeclared in `gate_criteria.json` |
| Isotope-ratio validation report | Becomes `gate_1_old_pigment_labeling_report.json` |
| Feasibility-gate pass/fail outcomes | **Output** of the evaluator, not input; the evaluator produces this from the report JSON |

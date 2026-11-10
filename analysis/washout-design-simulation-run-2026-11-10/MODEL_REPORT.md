# Washout design-simulation report

**Status:** Synthetic/hypothetical identifiability analysis only.
**Date:** 2026-11-10
**Data kind:** Forward-model simulations with noise and donor random effects.

> This is an AI-run simulation study. All data are synthetic. No real cells or compounds
> were involved. The owner reviews all outputs before interpretation.

## Scope

Quantify how reducing the planned paired-exposure/withdrawal matrix affects the
precision of the key parameters that drive the G1/G2 feasibility verdict.
The existing washout_model.py pipeline was used without modification.

## Design definitions

- **full_rfQ**: timepoints=[0, 1, 3, 5, 7, 9, 11, 14, 21], donors=3, replicates=3, readouts={'total': True, 'old_fraction': True, 'compound': True}
- **reduced_timepoints**: timepoints=[0, 3, 7, 11, 21], donors=3, replicates=3, readouts={'total': True, 'old_fraction': True, 'compound': True}
- **reduced_donors**: timepoints=[0, 1, 3, 5, 7, 9, 11, 14, 21], donors=2, replicates=3, readouts={'total': True, 'old_fraction': True, 'compound': True}
- **reduced_replicates**: timepoints=[0, 1, 3, 5, 7, 9, 11, 14, 21], donors=3, replicates=2, readouts={'total': True, 'old_fraction': True, 'compound': True}
- **minimal_first_stage**: timepoints=[0, 3, 7, 14], donors=2, replicates=2, readouts={'total': True, 'old_fraction': True, 'compound': True}
- **no_isotope**: timepoints=[0, 1, 3, 5, 7, 9, 11, 14, 21], donors=3, replicates=3, readouts={'total': True, 'old_fraction': False, 'compound': True}

## Summary statistics

### full_rfQ
- Fit success: 200/200
- Covariance-computation success: 100.00%
- Runtime: 8.6s

| Parameter | Mean bias | Mean CI width | RMSE |
| --- | --- | --- | --- |
| k_c | -0.0001 | 0.0023 | 0.0015 |
| k_old | 0.0001 | 0.2401 | 0.0005 |
| k_new | 0.0002 | 0.7730 | 0.0023 |
| s_max | 0.0013 | 1.1744 | 0.0167 |
| ic50 | -0.0271 | 272.1043 | 0.7420 |
| m_old0 | 0.0022 | 0.7605 | 0.0326 |
| m_new0 | 0.0008 | 0.6573 | 0.0110 |

### reduced_timepoints
- Fit success: 200/200
- Covariance-computation success: 100.00%
- Runtime: 8.1s

| Parameter | Mean bias | Mean CI width | RMSE |
| --- | --- | --- | --- |
| k_c | -0.0001 | 0.0031 | 0.0020 |
| k_old | -0.0000 | 0.3146 | 0.0005 |
| k_new | -0.0001 | 1.0547 | 0.0028 |
| s_max | 0.0023 | 1.6762 | 0.0180 |
| ic50 | 0.1034 | 393.2726 | 1.0131 |
| m_old0 | 0.0050 | 0.9755 | 0.0349 |
| m_new0 | 0.0016 | 0.8341 | 0.0118 |

### reduced_donors
- Fit success: 200/200
- Covariance-computation success: 100.00%
- Runtime: 8.2s

| Parameter | Mean bias | Mean CI width | RMSE |
| --- | --- | --- | --- |
| k_c | -0.0000 | 0.0028 | 0.0018 |
| k_old | 0.0000 | 0.2911 | 0.0005 |
| k_new | 0.0003 | 0.9397 | 0.0029 |
| s_max | 0.0010 | 1.4235 | 0.0230 |
| ic50 | -0.0201 | 330.3144 | 0.9332 |
| m_old0 | 0.0012 | 0.9211 | 0.0454 |
| m_new0 | 0.0005 | 0.7957 | 0.0151 |

### reduced_replicates
- Fit success: 200/200
- Covariance-computation success: 100.00%
- Runtime: 8.2s

| Parameter | Mean bias | Mean CI width | RMSE |
| --- | --- | --- | --- |
| k_c | 0.0000 | 0.0027 | 0.0018 |
| k_old | 0.0000 | 0.2806 | 0.0006 |
| k_new | 0.0001 | 0.8997 | 0.0030 |
| s_max | 0.0033 | 1.3728 | 0.0173 |
| ic50 | -0.0287 | 317.7232 | 0.8950 |
| m_old0 | 0.0064 | 0.8917 | 0.0328 |
| m_new0 | 0.0022 | 0.7711 | 0.0109 |

### minimal_first_stage
- Fit success: 200/200
- Covariance-computation success: 100.00%
- Runtime: 7.1s

| Parameter | Mean bias | Mean CI width | RMSE |
| --- | --- | --- | --- |
| k_c | 0.0003 | 0.0045 | 0.0027 |
| k_old | -0.0001 | 0.5399 | 0.0010 |
| k_new | 0.0005 | 5.0031 | 0.0136 |
| s_max | 0.0052 | 6.3231 | 0.0281 |
| ic50 | 0.0875 | 766.2561 | 2.0179 |
| m_old0 | 0.0090 | 1.4664 | 0.0430 |
| m_new0 | 0.0031 | 1.2716 | 0.0147 |

### no_isotope
- Fit success: 200/200
- Covariance-computation success: 71.50%
- Runtime: 14.5s

| Parameter | Mean bias | Mean CI width | RMSE |
| --- | --- | --- | --- |
| k_c | -0.0001 | 0.0032 | 0.0014 |
| k_old | -0.0025 | 22.9875 | 0.0179 |
| k_new | 0.0023 | 2.6777 | 0.0078 |
| s_max | -0.0005 | 6.7581 | 0.0181 |
| ic50 | -0.2092 | 1629.8051 | 3.8695 |
| m_old0 | 0.0009 | 151.3060 | 0.0799 |
| m_new0 | -0.0020 | 151.5578 | 0.0777 |

## CI inflation vs full design

CI inflation = (mean CI width in reduced design) / (mean CI width in full design).
Values > 1 mean the reduced design is less precise. `inf` = parameter became non-identifiable.

| Design | k_c | k_old | k_new | s_max | ic50 | m_old0 | m_new0 | Max inflation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reduced_timepoints | 1.34 | 1.31 | 1.36 | 1.43 | 1.45 | 1.28 | 1.27 | 1.45 |
| reduced_donors | 1.21 | 1.21 | 1.22 | 1.21 | 1.21 | 1.21 | 1.21 | 1.22 |
| reduced_replicates | 1.17 | 1.17 | 1.16 | 1.17 | 1.17 | 1.17 | 1.17 | 1.17 |
| minimal_first_stage | 1.95 | 2.25 | 6.47 | 5.38 | 2.82 | 1.93 | 1.93 | 6.47 |
| no_isotope | 1.36 | 95.73 | 3.46 | 5.75 | 5.99 | 198.96 | 230.58 | 230.58 |

## Derived-parameter precision inflation (RMSE ratio)

| Design | compound_half_time | old_pool_fraction_day0 | synthesis_recovery_day14 | Max |
| --- | --- | --- | --- | --- |
| reduced_timepoints | 1.35 | 1.25 | 1.26 | 1.35 |
| reduced_donors | 1.22 | 1.27 | 1.22 | 1.27 |
| reduced_replicates | 1.19 | 1.23 | 1.19 | 1.23 |
| minimal_first_stage | 1.84 | 1.75 | 2.31 | 2.31 |
| no_isotope | 0.94 | 74.18 | 3.48 | 74.18 |

## Verdict-threshold measurability

| Threshold | Full | Reduced TP | Reduced donors | Reduced reps | Minimal | No isotope |
| --- | --- | --- | --- | --- | --- | --- |
| Production-down half-time separation (<50%) | Yes | Yes | Yes | Yes | Yes | Partial (k_c OK; old/new lost) |
| Flux recovery >=80% by day 14 | Yes | Yes | Yes | Yes | Yes | Yes (synthesis from total+compound) |
| Old-pool detection <=10% | Yes | Yes | Yes | Yes | Yes | **No** -- old_fraction readout required for old/new separation |

## Limitations

- All data are synthetic/hypothetical; no biological material was measured.
- Donor random effect is a simulated lognormal multiplier (sigma=0.1) on pools and synthesis baseline only.
- The forward model assumes first-order washout and Hill synthesis inhibition.
- Confidence intervals are linear approximations from the Jacobian at the optimum (Fisher approximation).
- Bootstrap was run on a single representative dataset for the no-isotope design; 200 resamples.
- Derived-parameter CI widths are approximated via RMSE ratios from repeated simulations.
- The minimal-first-stage design simulation uses a generic single-arm ground truth; the real G1 comparison requires two arms (KT-939 and thiamidol).
- Cost statements in the decision document are planning-grade only and do not authorize spending.

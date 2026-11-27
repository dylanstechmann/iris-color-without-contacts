# Paired generic synthetic G1 washout-design simulation

**Status:** AI-run synthetic software simulation; not biological validation.
**Date:** 2026-11-15
**Arms:** `KT-939_synthetic` and `thiamidol_synthetic` (generic labels, not calibrated compounds).

The fullest grid was generated first. Reduced and minimal fits reused exact nested observations, common random numbers, and shared system/pair effects. No preferred design is selected.

## Independent-review correction

This run supersedes the earlier development output that incorrectly displayed record-level Wilson intervals and scenario-mixed no-isotope aggregates. Within-system replicates are correlated, scenario copies use common random numbers, and scenario-mixed records have no single probability meaning. The earlier intervals/aggregates are not valid evidence. This corrected run reports only descriptive matched-fit counts/fractions separately for each scenario/design and contains no scenario-pooled primary or control summary.

## Proposed, unapproved decision metadata

The simulated conditions are symmetric half-time ratio **<1.5** and both-arm day-14 synthesis recovery **>=0.80**. They are `proposed_not_owner_approved_not_go_no_go`; neither is a go/no-go criterion or formal equivalence test.

## System and MNT-1 accounting

| Design | Systems | Synthetic donors | Reference cell lines | MNT-1 represented | Replicates/system | Timepoints |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| full | 3 | 2 | 1 | true (1) | 3 | 0, 1, 3, 5, 7, 9, 11, 14, 21 |
| reduced | 2 | 1 | 1 | true (1) | 2 | 0, 3, 7, 14, 21 |
| minimal | 2 | 1 | 1 | true (1) | 2 | 0, 3, 7, 14 |

MNT-1 is a single reference cell-line system, not a donor. Synthetic donor labels and multipliers do not establish donor-population inference.

## Descriptive decision counts and fractions

Each row describes only the matched fits for that one scenario/design. Fractions are observed record fractions, not independent-Bernoulli estimates, decision probabilities, or inferential intervals. `NE` means not evaluable and is never counted as zero or success. No rows are pooled across scenarios.

| True ratio | Design | Pairs | Ratio <1.5 | Both recoveries >=0.80 | Both proposed conditions | Mean fitted ratio |
| ---: | --- | ---: | --- | --- | --- | ---: |
| 1.00 | full | 9 | 9/9 (100.0% descriptive) | 9/9 (100.0% descriptive) | 9/9 (100.0% descriptive) | 1.011 |
| 1.00 | reduced | 4 | 4/4 (100.0% descriptive) | 4/4 (100.0% descriptive) | 4/4 (100.0% descriptive) | 1.006 |
| 1.00 | minimal | 4 | 4/4 (100.0% descriptive) | 4/4 (100.0% descriptive) | 4/4 (100.0% descriptive) | 1.006 |
| 1.25 | full | 9 | 9/9 (100.0% descriptive) | 9/9 (100.0% descriptive) | 9/9 (100.0% descriptive) | 1.253 |
| 1.25 | reduced | 4 | 4/4 (100.0% descriptive) | 4/4 (100.0% descriptive) | 4/4 (100.0% descriptive) | 1.249 |
| 1.25 | minimal | 4 | 4/4 (100.0% descriptive) | 4/4 (100.0% descriptive) | 4/4 (100.0% descriptive) | 1.249 |
| 1.50 | full | 9 | 4/9 (44.4% descriptive) | 9/9 (100.0% descriptive) | 4/9 (44.4% descriptive) | 1.504 |
| 1.50 | reduced | 4 | 2/4 (50.0% descriptive) | 4/4 (100.0% descriptive) | 2/4 (50.0% descriptive) | 1.500 |
| 1.50 | minimal | 4 | 2/4 (50.0% descriptive) | 4/4 (100.0% descriptive) | 2/4 (50.0% descriptive) | 1.500 |
| 2.00 | full | 9 | 0/9 (0.0% descriptive) | 3/9 (33.3% descriptive) | 0/9 (0.0% descriptive) | 2.005 |
| 2.00 | reduced | 4 | 0/4 (0.0% descriptive) | 1/4 (25.0% descriptive) | 0/4 (0.0% descriptive) | 2.003 |
| 2.00 | minimal | 4 | 0/4 (0.0% descriptive) | 1/4 (25.0% descriptive) | 0/4 (0.0% descriptive) | 2.003 |

## Day-14 recovery and fit/covariance failures

| True ratio | Design | Arm | Mean day-14 recovery | Fit failures / pairs | Covariance failures / successful fits |
| ---: | --- | --- | ---: | ---: | ---: |
| 1.00 | full | KT-939_synthetic | 0.981 | 0/9 | 0/9 |
| 1.00 | full | thiamidol_synthetic | 0.988 | 0/9 | 0/9 |
| 1.00 | reduced | KT-939_synthetic | 0.980 | 0/4 | 0/4 |
| 1.00 | reduced | thiamidol_synthetic | 0.989 | 0/4 | 0/4 |
| 1.00 | minimal | KT-939_synthetic | 0.980 | 0/4 | 0/4 |
| 1.00 | minimal | thiamidol_synthetic | 0.988 | 0/4 | 0/4 |
| 1.25 | full | KT-939_synthetic | 0.981 | 0/9 | 0/9 |
| 1.25 | full | thiamidol_synthetic | 0.961 | 0/9 | 0/9 |
| 1.25 | reduced | KT-939_synthetic | 0.980 | 0/4 | 0/4 |
| 1.25 | reduced | thiamidol_synthetic | 0.961 | 0/4 | 0/4 |
| 1.25 | minimal | KT-939_synthetic | 0.980 | 0/4 | 0/4 |
| 1.25 | minimal | thiamidol_synthetic | 0.957 | 0/4 | 0/4 |
| 1.50 | full | KT-939_synthetic | 0.981 | 0/9 | 0/9 |
| 1.50 | full | thiamidol_synthetic | 0.915 | 0/9 | 0/9 |
| 1.50 | reduced | KT-939_synthetic | 0.980 | 0/4 | 0/4 |
| 1.50 | reduced | thiamidol_synthetic | 0.913 | 0/4 | 0/4 |
| 1.50 | minimal | KT-939_synthetic | 0.980 | 0/4 | 0/4 |
| 1.50 | minimal | thiamidol_synthetic | 0.906 | 0/4 | 0/4 |
| 2.00 | full | KT-939_synthetic | 0.981 | 0/9 | 0/9 |
| 2.00 | full | thiamidol_synthetic | 0.792 | 0/9 | 0/9 |
| 2.00 | reduced | KT-939_synthetic | 0.980 | 0/4 | 0/4 |
| 2.00 | reduced | thiamidol_synthetic | 0.784 | 0/4 | 0/4 |
| 2.00 | minimal | KT-939_synthetic | 0.980 | 0/4 | 0/4 |
| 2.00 | minimal | thiamidol_synthetic | 0.775 | 0/4 | 0/4 |

## Linearized CI diagnostics

Coverage is the descriptive count/fraction of intervals containing the known synthetic truth within one scenario/design, including shared system/pair multipliers. It is not an estimated coverage probability or inferential interval. Widths are medians over available finite intervals. `k_c` uses the legacy parameter interval; day-14 recovery uses a delta-method interval. These are local linear approximations.

| True ratio | Design | Arm | k_c coverage | k_c median width | Recovery coverage | Recovery median width |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1.00 | full | KT-939_synthetic | 2/9 | 0.00830 | 9/9 | 0.35898 |
| 1.00 | full | thiamidol_synthetic | 2/9 | 0.01081 | 9/9 | 0.24208 |
| 1.00 | reduced | KT-939_synthetic | 0/4 | 0.00871 | 4/4 | 0.37319 |
| 1.00 | reduced | thiamidol_synthetic | 1/4 | 0.00749 | 4/4 | 0.17863 |
| 1.00 | minimal | KT-939_synthetic | 0/4 | 0.01152 | 4/4 | 0.61891 |
| 1.00 | minimal | thiamidol_synthetic | 2/4 | 0.00948 | 4/4 | 0.34131 |
| 1.25 | full | KT-939_synthetic | 2/9 | 0.00830 | 9/9 | 0.35898 |
| 1.25 | full | thiamidol_synthetic | 2/9 | 0.00775 | 9/9 | 0.87955 |
| 1.25 | reduced | KT-939_synthetic | 0/4 | 0.00871 | 4/4 | 0.37319 |
| 1.25 | reduced | thiamidol_synthetic | 1/4 | 0.00711 | 4/4 | 0.79211 |
| 1.25 | minimal | KT-939_synthetic | 0/4 | 0.01152 | 4/4 | 0.61891 |
| 1.25 | minimal | thiamidol_synthetic | 1/4 | 0.00916 | 4/4 | 1.36167 |
| 1.50 | full | KT-939_synthetic | 2/9 | 0.00830 | 9/9 | 0.35898 |
| 1.50 | full | thiamidol_synthetic | 4/9 | 0.00613 | 9/9 | 1.94768 |
| 1.50 | reduced | KT-939_synthetic | 0/4 | 0.00871 | 4/4 | 0.37319 |
| 1.50 | reduced | thiamidol_synthetic | 2/4 | 0.00588 | 4/4 | 1.75395 |
| 1.50 | minimal | KT-939_synthetic | 0/4 | 0.01152 | 4/4 | 0.61891 |
| 1.50 | minimal | thiamidol_synthetic | 3/4 | 0.00746 | 4/4 | 2.61139 |
| 2.00 | full | KT-939_synthetic | 2/9 | 0.00830 | 9/9 | 0.35898 |
| 2.00 | full | thiamidol_synthetic | 4/9 | 0.00465 | 9/9 | 5.15735 |
| 2.00 | reduced | KT-939_synthetic | 0/4 | 0.00871 | 4/4 | 0.37319 |
| 2.00 | reduced | thiamidol_synthetic | 3/4 | 0.00517 | 4/4 | 4.74009 |
| 2.00 | minimal | KT-939_synthetic | 0/4 | 0.01152 | 4/4 | 0.61891 |
| 2.00 | minimal | thiamidol_synthetic | 3/4 | 0.00566 | 4/4 | 6.05873 |

## Matched no-isotope negative controls by scenario/design

Controls retain the generated isotope array but omit `old_fraction` only from the diagnostic fit. Each row compares primary/control fits matched on scenario, design, system, replicate, and observations. There is no scenario-mixed aggregate. A missing interval or width ratio is `NE`, not zero. This is an identifiability result, never an assay LOD estimate.

| True ratio | Design | Arm | Pool | Isotope median CI width | No-isotope median CI width | Width ratio | No-isotope covariance failures / fits |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 1.00 | full | KT-939_synthetic | m_old0 | 2.51687 | 666.58774 | 264.85 | 3/9 |
| 1.00 | full | KT-939_synthetic | m_new0 | 2.24377 | 667.81112 | 297.63 | 3/9 |
| 1.00 | full | thiamidol_synthetic | m_old0 | 3.00155 | 46.65003 | 15.54 | 1/9 |
| 1.00 | full | thiamidol_synthetic | m_new0 | 2.72481 | 46.20745 | 16.96 | 1/9 |
| 1.00 | reduced | KT-939_synthetic | m_old0 | 2.59589 | NE | NE | 4/4 |
| 1.00 | reduced | KT-939_synthetic | m_new0 | 2.20141 | NE | NE | 4/4 |
| 1.00 | reduced | thiamidol_synthetic | m_old0 | 1.93065 | NE | NE | 4/4 |
| 1.00 | reduced | thiamidol_synthetic | m_new0 | 1.67913 | NE | NE | 4/4 |
| 1.00 | minimal | KT-939_synthetic | m_old0 | 3.60443 | NE | NE | 4/4 |
| 1.00 | minimal | KT-939_synthetic | m_new0 | 3.12055 | NE | NE | 4/4 |
| 1.00 | minimal | thiamidol_synthetic | m_old0 | 2.55722 | NE | NE | 4/4 |
| 1.00 | minimal | thiamidol_synthetic | m_new0 | 2.21809 | NE | NE | 4/4 |
| 1.25 | full | KT-939_synthetic | m_old0 | 2.51687 | 666.58774 | 264.85 | 3/9 |
| 1.25 | full | KT-939_synthetic | m_new0 | 2.24377 | 667.81112 | 297.63 | 3/9 |
| 1.25 | full | thiamidol_synthetic | m_old0 | 2.77852 | 61.99281 | 22.31 | 7/9 |
| 1.25 | full | thiamidol_synthetic | m_new0 | 2.53383 | 61.97261 | 24.46 | 7/9 |
| 1.25 | reduced | KT-939_synthetic | m_old0 | 2.59589 | NE | NE | 4/4 |
| 1.25 | reduced | KT-939_synthetic | m_new0 | 2.20141 | NE | NE | 4/4 |
| 1.25 | reduced | thiamidol_synthetic | m_old0 | 2.53982 | NE | NE | 4/4 |
| 1.25 | reduced | thiamidol_synthetic | m_new0 | 2.24588 | NE | NE | 4/4 |
| 1.25 | minimal | KT-939_synthetic | m_old0 | 3.60443 | NE | NE | 4/4 |
| 1.25 | minimal | KT-939_synthetic | m_new0 | 3.12055 | NE | NE | 4/4 |
| 1.25 | minimal | thiamidol_synthetic | m_old0 | 3.43746 | NE | NE | 4/4 |
| 1.25 | minimal | thiamidol_synthetic | m_new0 | 3.05374 | NE | NE | 4/4 |
| 1.50 | full | KT-939_synthetic | m_old0 | 2.51687 | 666.58774 | 264.85 | 3/9 |
| 1.50 | full | KT-939_synthetic | m_new0 | 2.24377 | 667.81112 | 297.63 | 3/9 |
| 1.50 | full | thiamidol_synthetic | m_old0 | 2.81465 | 8.34237 | 2.96 | 5/9 |
| 1.50 | full | thiamidol_synthetic | m_new0 | 2.60716 | 6.91966 | 2.65 | 5/9 |
| 1.50 | reduced | KT-939_synthetic | m_old0 | 2.59589 | NE | NE | 4/4 |
| 1.50 | reduced | KT-939_synthetic | m_new0 | 2.20141 | NE | NE | 4/4 |
| 1.50 | reduced | thiamidol_synthetic | m_old0 | 2.63752 | NE | NE | 4/4 |
| 1.50 | reduced | thiamidol_synthetic | m_new0 | 2.35076 | NE | NE | 4/4 |
| 1.50 | minimal | KT-939_synthetic | m_old0 | 3.60443 | NE | NE | 4/4 |
| 1.50 | minimal | KT-939_synthetic | m_new0 | 3.12055 | NE | NE | 4/4 |
| 1.50 | minimal | thiamidol_synthetic | m_old0 | 3.51082 | NE | NE | 4/4 |
| 1.50 | minimal | thiamidol_synthetic | m_new0 | 3.13321 | NE | NE | 4/4 |
| 2.00 | full | KT-939_synthetic | m_old0 | 2.51687 | 666.58774 | 264.85 | 3/9 |
| 2.00 | full | KT-939_synthetic | m_new0 | 2.24377 | 667.81112 | 297.63 | 3/9 |
| 2.00 | full | thiamidol_synthetic | m_old0 | 3.13601 | 15.40338 | 4.91 | 8/9 |
| 2.00 | full | thiamidol_synthetic | m_new0 | 2.85578 | 17.33913 | 6.07 | 8/9 |
| 2.00 | reduced | KT-939_synthetic | m_old0 | 2.59589 | NE | NE | 4/4 |
| 2.00 | reduced | KT-939_synthetic | m_new0 | 2.20141 | NE | NE | 4/4 |
| 2.00 | reduced | thiamidol_synthetic | m_old0 | 3.21870 | NE | NE | 4/4 |
| 2.00 | reduced | thiamidol_synthetic | m_new0 | 2.94092 | NE | NE | 4/4 |
| 2.00 | minimal | KT-939_synthetic | m_old0 | 3.60443 | NE | NE | 4/4 |
| 2.00 | minimal | KT-939_synthetic | m_new0 | 3.12055 | NE | NE | 4/4 |
| 2.00 | minimal | thiamidol_synthetic | m_old0 | 3.68419 | NE | NE | 4/4 |
| 2.00 | minimal | thiamidol_synthetic | m_new0 | 3.31995 | NE | NE | 4/4 |

## Limitations

- All ground truths, system effects, pair effects, readouts, and noise are generic synthetic assumptions; neither arm is compound-calibrated.
- The ic50 inputs represent generic free-compound synthesis inhibition, never accumulated-pigment IC50 substitutions.
- The isotope old_fraction readout is mandatory for old/new pool identifiability; its recoverability is not an assay LOD measurement.
- MNT-1 is one represented reference cell-line system, not a donor and not evidence of donor or tissue generalizability.
- Synthetic donor/system multipliers are shared across arms but are not fitted with a donor mixed-effects model; fits are separate arm-level fits.
- Confidence intervals are legacy Jacobian-linearized parameter intervals and delta-method derived intervals; coverage is a descriptive synthetic diagnostic, not a guarantee.
- Within-system replicates are correlated and ratio scenarios/nested designs reuse random streams and observations. Record summaries are descriptive counts/fractions within one scenario/design only, with no independent-Bernoulli assumption, Wilson or other record-level inferential interval, decision probability, or scenario-pooled primary/control aggregate.
- The proposed ratio <1.5 and both-arm day-14 recovery >=0.80 metadata are unapproved simulation conditions, not go/no-go criteria or formal equivalence.
- No-isotope controls diagnose loss of old/new identifiability and never authorize dropping isotope from a candidate design.
- Nested reduced/minimal results share full-design observations; they do not establish biological sufficiency, cost effectiveness, owner adoption, or a preferred design.
- No ocular, clinical, safety, efficacy, procurement, facility-contact, spending, or gate-passage conclusion follows from this run.

## Receipt

`receipt.json` pins the frozen assumptions, CLI and reusable/legacy source hashes, software versions, deterministic seed hierarchy, scenarios, design accounting, proposed metadata, and output hashes. Hashes establish file identity only.

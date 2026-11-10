# F5 washout-kinetics fit report

**Status:** synthetic/hypothetical validation
**Date:** 2026-11-10
**Data kind:** synthetic

This is an AI-run forward-model fit. See washout-and-recovery.md for the identifiability
calculation that motivates the multi-readout design.

## Readout flags

- total: USED
- old_fraction: USED
- compound: USED

## Fitted parameters
- **c0** = 501.598169
- **k_c** = 0.502538
- **m_old0** = 0.597927
- **m_new0** = 0.200578
- **k_old** = 0.050090
- **k_new** = 0.161821
- **s_max** = 0.314918
- **ic50** = 46.898948

## Confidence intervals
- c0: [500.640766, 502.555572]
- k_c: [0.500291, 0.504786]
- m_old0: [-0.128362, 1.324216]
- m_new0: [-0.429648, 0.830804]
- k_old: [-0.180494, 0.280675]
- k_new: [-0.622088, 0.945730]
- s_max: [-0.869663, 1.499499]
- ic50: [-191.772886, 285.570783]

## Identifiability notes
- All declared readouts present: old/new pool separation, compound clearance, and synthesis recovery are jointly identifiable in principle.
- Maximum absolute parameter correlation ≈ 0.982.
- High correlation suggests practical non-identifiability even if the Jacobian is invertible.

## Fit summary
- Cost (SSE): 5.096798
- N observations: 27
- Free parameters: 8
- DOF: 19
- Status: 2
- Message: `ftol` termination condition is satisfied.

## Residuals (first 5 rows)
| time | total_resid | old_frac_resid | compound_resid |
| --- | --- | --- | --- |
| 0.0 | 0.001618 | -0.003073 | 0.158732 |
| 1.0 | -0.009505 | 0.003165 | -0.297931 |
| 3.0 | 0.012084 | -0.000416 | 0.122711 |
| 5.0 | -0.000242 | -0.003084 | -0.973791 |
| 7.0 | -0.008008 | 0.004640 | 2.663578 |

## Limitations
- All values are synthetic/hypothetical unless explicitly labeled otherwise.
- The forward model assumes first-order compound washout and Hill synthesis inhibition.
- Old and new pigment loss rates are allowed to differ; in the identifiability counterexample they coincide.
- Confidence intervals are linear approximations from the Jacobian at the optimum.
- Developed by AI assistant; owner-reviewed before interpretation.

# Hypothetical pigment feasibility sweep

All parameters are assumptions. Inventory percentages do not map to eye colors.

Mobile pigment is normalized to its own starting value. Baseline synthesis equals k0.
During modulation: dm/dt = f*k0 - (k0+a)*m.
After withdrawal: dm/dt = b*k0 - k0*m. Total inventory = p+(1-p)*m.

The source is kept at its original baseline when added loss changes. This prevents an accelerated
loss pathway from silently increasing pigment production.

| Hypothetical case | Inventory at year 7 | Years to 25% inventory | Years after withdrawal to 90%, original source |
| --- | ---: | ---: | ---: |
| slow native loss; suppression alone | 79.5% | 44.96 | 20.66 |
| slow native loss; suppression plus added loss | 16.1% | 5.29 | 61.37 |
| same combined mechanism; persistent pool | 41.3% | not reached | 51.08 |
| added loss alone; synthesis unchanged | 26.6% | 7.47 | 57.52 |
| fast native loss; suppression alone | 5.7% | 2.25 | 3.24 |
| no native loss; new loss pathway | 19.8% | 6.00 | not reached |

A fivefold recovery-source comparison is in the CSV. It is a hypothetical control lever.
Keeping an increased source active could overshoot baseline; this is not a maintenance regimen.

A persistent fraction sets a floor only while it stays persistent. Whole-eye cell renewal is not assumed.
A null native half-life models a stored pool with no baseline flux, not a measured iris state.

Scenarios: 720. The grid is unweighted; counts are not probabilities of success.

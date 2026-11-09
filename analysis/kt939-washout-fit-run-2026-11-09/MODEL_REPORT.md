# KT-939 washout exponential-fit report

Single-exponential fit to published mean inhibition values from Hou et al., 2025.

## Source values

| Concentration | Day post-washout | Inhibition % | Flag |
| --- | ---: | ---: | --- |
| 10 μM | 3 | 66.6 | verified-against-paper |
| 10 μM | 5 | 52.7 | verified-against-paper |
| 10 μM | 7 | 21.3 | verified-against-paper |
| 10 μM | 9 | 20.0 | verified-against-paper |
| 10 μM | 11 | recovery reported (normal levels) | verified-against-paper |
| 1 μM | 3 | 38.0 | verified-against-paper |
| 1 μM | 5 | 28.3 | verified-against-paper |
| 1 μM | 7 | recovery reported (baseline) | verified-against-paper |

Endpoint: bulk melanin absorbance at 405 nm normalized to protein (μg melanin / mg protein); inhibition percent relative to matched vehicle (denominator not explicit).
The 10 μM day-11 and 1 μM day-7 entries are qualitative recovery bounds, not 0% data points, and were excluded from the least-squares objective.

## 10 μM fit: inhibition(t) = I0 · exp(−k · t)

- Fitted I0 = 132.20% (extrapolated inhibition at t = 0, not measured)
- Fitted k = 0.2172 day⁻¹
- Washout half-time = 3.19 days
- SSE = 129.93 (n = 4, DOF = 2)

| Residuals | Observed | Predicted | Residual |
| --- | ---: | ---: | ---: |
| Day 3 | 66.6 | 68.90 | -2.30 |
| Day 5 | 52.7 | 44.63 | 8.07 |
| Day 7 | 21.3 | 28.90 | -7.60 |
| Day 9 | 20.0 | 18.72 | 1.28 |

### Uncertainty estimate (bootstrap, n = 4)

- Bootstrap median half-time: 3.15 days
- Bootstrap 95% percentile CI: [2.43, 9.50] days
- Bootstrap interquartile range: [2.70, 3.63] days

The bootstrap resamples the n = 4 mean points with replacement and reflits; it does not recover replicate-level uncertainty. The CI is wide because the sample is small and the residual at day 5 is large.

## 1 μM series: underdetermined

Only two quantitative points exist (day 3: 38.0%, day 5: 28.3%). These do not determine both I0 and k independently. A forced two-point exponential is not a fit; it is a descriptive line.

- Forced two-point exponential (not recommended): I0 = 59.13%, k = 0.1474 day⁻¹, half-time = 4.70 days

The 1 μM qualitative recovery by day 7 is consistent with a faster washout than the 10 μM series, but a direct half-time comparison is unsupported.

## Limitations

1. **Endpoint is accumulated pigment content, not synthesis flux.** The measured quantity is bulk melanin per protein after six days of exposure and various days after washout. Recovery of this quantity conflates resumption of new pigment synthesis, turnover of existing pigment, possible cell division, and any protein-content change. It does not isolate synthesis flux. See analysis/withdrawal-and-recovery.md for the identifiability problem this creates.

2. **Qualitative recovery bounds are not fitted points.** The paper reports normal levels by day 11 (10 μM) and baseline by day 7 (1 μM). These have not been converted to exact 0% inhibition measurements and are excluded from the SSE. Treating them as 0% would bias the fit downward.

3. **Day-7 to day-9 plateau violates strict exponential decay.** The observed inhibition drops only from 21.3% to 20.0% between days 7 and 9, while the fitted single exponential predicts a drop from 28.85% to 18.65%. This plateau is a source inconsistency: either experimental variability, a persistent low-level inhibition floor, or some other process not captured by the model. The SSE is dominated by this mismatch.

4. **n = 4 fit uncertainty is large.** Four mean points for two nonlinear parameters yields bootstrap 95% CIs spanning roughly a factor of three in half-time. The normal-approximation residual-based CI (not reported here because the small-sample t-distribution with 2 degrees of freedom hits the lower parameter boundary) would be even wider. The half-time should be read as a crude order-of-magnitude estimate, not a precise kinetic constant.

5. **No replicate-level data were used.** Figure 4 shows mean ± SD of three independent experiments, but error bars were not transcribed or digitized. Equal weighting of the mean points is assumed; if the true underlying variance differs across days, the effective uncertainty is larger than reported.

6. **Cell model and tissue transfer limits.** MNT-1 human melanoma cells are a transformed line. The fitted rate describes pigment-content change in that system under the stated culture conditions. It does not transfer to normal human melanocytes, 3D skin equivalents, or iris tissue.

## What this estimate does and does not resolve

This run extracts one crude washout half-time (~3.2 days, 95% CI ~2.4–8.7 days) from published 10 μM mean values. It does **not**:

- Provide a synthesis-flux recovery rate (the endpoint is accumulated pigment, not flux).
- Resolve the KT-939 vs thiamidol comparative-recovery gap, because thiamidol has no washout arm in this study.
- Establish whether KT-939's scaffold confers different retention kinetics from thiamidol's shared resorcinol–thiazole core.
- Quantify free-compound clearance or target-activity recovery after withdrawal.

What it **does** do:

- Quantify the order-of-magnitude speed at which the 10 μM accumulated-pigment inhibition phenotype decays in MNT-1 cells after medium replacement.
- Provide a numerical benchmark that a future paired KT-939/thiamidol washout experiment could exceed or falsify.
- Flag which specific missing raw values would sharpen or overturn the estimate (see Minimum raw-data request below).

## Minimum raw-data request

The following exact values from Hou et al., 2025 would resolve the fit's ambiguity and could be requested from the authors as a free data enquiry:

1. **Replicate-level melanin-content values per timepoint.** The figure caption states three independent experiments. The individual replicate values per day (not just mean ± SD) would allow proper weighting and would support a measurement-error model instead of equal-weighted means.

2. **Exact washout-start definition.** Was the replacement medium changed once at day 6, or was it refreshed repeatedly? What volume was used, and was any residual compound in the extracellular space quantified?

3. **How the percent inhibition was normalized.** Was the denominator the day-matched vehicle control, the pre-exposure baseline, or a single vehicle average across the time course? The answer changes the interpretation of residual inhibition at late timepoints.

4. **Whether a thiamidol washout arm exists in unpublished data.** The paired same-study comparison is the highest-priority gap in the registered evidence. If the authors measured thiamidol washout in the same MNT-1 system, that dataset would immediately resolve the comparative-recovery question without new wet-lab work.

5. **Cell-count and protein-content data per timepoint.** If protein normalization absorbed cell-number changes, the inhibition-percent time course may reflect population dynamics rather than pigment per cell.

6. **Day 0 and day 1 post-washout measurements, if collected.** The fitted I0 is an extrapolation from day 3. An early dense sampling window (days 0, 0.5, 1, 2) would test whether recovery begins immediately or after a lag.

These are minimal requests: they require no new experiments, only disclosed values from completed work.

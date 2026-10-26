# Hypothetical hue-window exploration

The iris spectra, thresholds and windows are assumptions; only the colorimetry tables are standard.

Model: reflectance = B*exp(-2*phi*A) + (1-B)*exp(-2*A)*rho, where B is bounded Rayleigh-like
stromal backscatter, A is the sum of eumelanin and pheomelanin absorbance (power laws), phi is the
fraction of pigment lying above the scattering events, and rho is the return from behind the stroma.
Colour is CIE 1976 L*a*b* from the CIE 1931 2 degree observer under illuminant D65, sampled every
5 nm from 380 to 780 nm. Windows are hue-angle ranges centred on reference spectra: a short-pass, a long-pass and a
bimodal (blue plus red) reflector. A scenario is in a window when its hue is within 20 degrees of
the reference's. It is classified when its chroma is also at least the stated fraction of the reference
chroma and its luminance Y is at least 0.5 of the reference's.

| Back return | Window | Scenarios in hue window | Of those, below luminance floor | Best chroma / reference | Best luminance / reference | Classified at chroma fraction 0.25 / 0.5 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| dark_pigment_epithelium | blue | 6 of 124 | 0 | 0.51 | 2.83 | 6 / 4 |
| dark_pigment_epithelium | orange | 0 of 124 | 0 | 0.00 | 0.00 | 0 / 0 |
| dark_pigment_epithelium | purple | 0 of 124 | 0 | 0.00 | 0.00 | 0 / 0 |
| translucent_red_return_plateau_0.05 | blue | 24 of 124 | 0 | 0.50 | 2.89 | 24 / 0 |
| translucent_red_return_plateau_0.05 | orange | 0 of 124 | 0 | 0.00 | 0.00 | 0 / 0 |
| translucent_red_return_plateau_0.05 | purple | 0 of 124 | 0 | 0.00 | 0.00 | 0 / 0 |
| translucent_red_return_plateau_0.15 | blue | 69 of 124 | 0 | 0.47 | 3.11 | 39 / 0 |
| translucent_red_return_plateau_0.15 | orange | 2 of 124 | 0 | 0.02 | 1.08 | 0 / 0 |
| translucent_red_return_plateau_0.15 | purple | 4 of 124 | 0 | 0.03 | 1.76 | 0 / 0 |
| translucent_red_return_plateau_0.25 | blue | 52 of 124 | 0 | 0.46 | 3.32 | 37 / 0 |
| translucent_red_return_plateau_0.25 | orange | 6 of 124 | 0 | 0.13 | 1.15 | 0 / 0 |
| translucent_red_return_plateau_0.25 | purple | 62 of 124 | 0 | 0.45 | 3.33 | 36 / 0 |
| translucent_red_return_plateau_0.35 | blue | 24 of 124 | 0 | 0.46 | 3.54 | 24 / 0 |
| translucent_red_return_plateau_0.35 | orange | 12 of 124 | 0 | 0.21 | 1.22 | 0 / 0 |
| translucent_red_return_plateau_0.35 | purple | 55 of 124 | 0 | 0.45 | 3.54 | 39 / 0 |
| translucent_red_return_plateau_0.5 | blue | 0 of 124 | 0 | 0.00 | 0.00 | 0 / 0 |
| translucent_red_return_plateau_0.5 | orange | 22 of 124 | 0 | 0.47 | 1.76 | 19 / 0 |
| translucent_red_return_plateau_0.5 | purple | 42 of 124 | 0 | 0.47 | 3.87 | 40 / 0 |

| Reference | Hue angle | Chroma | L* | Luminance Y |
| --- | ---: | ---: | ---: | ---: |
| blue | 294.0 | 70.3 | 36.8 | 0.094 |
| orange | 35.5 | 57.3 | 46.1 | 0.153 |
| purple | 318.7 | 72.1 | 36.8 | 0.094 |

Counts come from an unweighted grid; they are not probabilities and do not rank outcomes.
A scenario that lands in a window shows that the assumed spectra allow it, not that an iris can.
The 5 translucent-return modes assume a reddish return behind a pigment-poor stroma at
different strengths, because the real strength is unknown. Such a state is the transparency route
discussed in the sidequest note and is not a function-preserving target.
Measured melanin spectra and a measured back return are the first changes that could move these results.

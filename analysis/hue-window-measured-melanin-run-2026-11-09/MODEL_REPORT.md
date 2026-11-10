# Hypothetical hue-window exploration with measured melanin spectra

The iris spectra, thresholds and windows are assumptions; the colorimetry tables and the melanin
spectral shapes are the only sourced inputs (see the assumptions file for provenance). The melanin
shapes are the measured Sarna & Swartz 1988 extinction coefficients, linearly interpolated and
normalized to 1.0 at 550 nm; the 550 nm absorbance magnitudes remain assumptions.

Model: reflectance = B*exp(-2*phi*A) + (1-B)*exp(-2*A)*rho, where B is bounded stromal backscatter,
A is the sum of eumelanin and pheomelanin absorbance (measured 550-normalized shapes), phi is the
fraction of pigment above the scattering events, and rho is the return from behind the stroma.
Colour is CIE 1976 L*a*b* for the CIE 1931 2 degree observer under illuminant D65, sampled every
5 nm from 380 to 780 nm. Windows are hue-angle ranges centred on reference spectra: a short-pass, a long-pass and a
bimodal (blue plus red) reflector. A case is in a window when its hue is within 20 degrees of the reference's.
It is classified when its chroma is also at least the stated fraction of the reference chroma and its
luminance Y is at least 0.5 of the reference's.

## Calibration: which stroma settings can represent a blue iris at all

A stroma setting is used for interpretation only if, with no pigment over a dark back, it falls in the blue window
(chroma fraction 0.25). 5 of 12 settings pass.

| Backscatter at 550 nm | Wavelength exponent | Pigment-free hue | Chroma | L* | Calibrated |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0.1 | 2 | 268 | 11.6 | 41 | no |
| 0.1 | 4 | 276 | 25.0 | 41 | yes |
| 0.1 | 6 | 284 | 41.4 | 42 | yes |
| 0.25 | 2 | 268 | 16.7 | 58 | no |
| 0.25 | 4 | 276 | 35.7 | 59 | yes |
| 0.25 | 6 | 282 | 55.4 | 60 | yes |
| 0.4 | 2 | 268 | 19.8 | 70 | no |
| 0.4 | 4 | 274 | 40.4 | 71 | yes |
| 0.4 | 6 | 267 | 47.2 | 71 | no |
| 1 | 2 | 206 | 9.7 | 98 | no |
| 1 | 4 | 206 | 18.1 | 95 | no |
| 1 | 6 | 206 | 25.4 | 94 | no |

## Reachability in blue-calibrated stromas

"Hue" counts cases inside the hue window, which includes near-black cases where hue means little.
"Hue + chroma" also requires chroma of at least 0.25 of the reference. "Classified" also requires the luminance
floor. Ranges describe the classified cases only.

| Back return | Window | Hue | Hue + chroma | Classified | Brightest hue + chroma case (Y / reference, L*) | Pheomelanin share | Absorbance at 550 nm |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| dark_pigment_epithelium | orange | 100 of 255 | 20 | 0 | 0.10, L* 12 | – | – |
| dark_pigment_epithelium | purple | 0 of 255 | 0 | 0 | – | – | – |
| translucent_red_return_0.05 | orange | 99 of 255 | 23 | 0 | 0.10, L* 13 | – | – |
| translucent_red_return_0.05 | purple | 2 of 255 | 0 | 0 | – | – | – |
| translucent_red_return_0.1 | orange | 110 of 255 | 29 | 0 | 0.13, L* 15 | – | – |
| translucent_red_return_0.1 | purple | 6 of 255 | 0 | 0 | – | – | – |
| translucent_red_return_0.2 | orange | 134 of 255 | 59 | 2 | 0.58, L* 36 | 0.8–1 | 0.5 |
| translucent_red_return_0.2 | purple | 9 of 255 | 3 | 3 | 1.75, L* 48 | 0 | 0–0.5 |
| translucent_red_return_0.3 | orange | 152 of 255 | 79 | 13 | 0.82, L* 42 | 0–1 | 0.5 |
| translucent_red_return_0.3 | purple | 13 of 255 | 6 | 6 | 3.56, L* 65 | 0–0.3 | 0–0.5 |
| translucent_red_return_0.4 | orange | 166 of 255 | 98 | 28 | 1.28, L* 51 | 0–1 | 0.5–1 |
| translucent_red_return_0.4 | purple | 9 of 255 | 5 | 5 | 3.78, L* 66 | 0–0.3 | 0–0.5 |

Over the dark back, the 7 stroma settings that do not read blue when pigment-free
classify 0 orange and 0 purple cases. They are not used: a stroma that is already
whitish before any pigment is added cannot be taken as evidence for what a pigmented iris does.

## Return strength needed behind the stroma

- **purple:** reached in 4 of 5 calibrated stroma settings, at a smallest red return of 0.2 to 0.3 on the swept grid. A round trip behind a perfect reflector implies one-way red transmission of 0.45 to 0.55.
- **orange:** reached in 5 of 5 calibrated stroma settings, at a smallest red return of 0.2 to 0.4 on the swept grid. A round trip behind a perfect reflector implies one-way red transmission of 0.45 to 0.63.

Measured anchor: For a light-blue eye effective transmission of the iris was 1% for red and 0.2% for green light (van den Berg, IJspeert and de Waard 1991, Vision Research 31:1361-1367, PMID 1891824; abstract read, full text not; psychophysical). It concerns a non-albino iris and a
different geometry from the model's, so it is an order-of-magnitude comparison, not a calibration.

## Reference spectra

| Reference | Hue angle | Chroma | L* | Luminance Y |
| --- | ---: | ---: | ---: | ---: |
| blue | 294.0 | 70.3 | 36.8 | 0.094 |
| orange | 35.5 | 57.3 | 46.1 | 0.153 |
| purple | 318.7 | 72.1 | 36.8 | 0.094 |

Counts come from an unweighted grid; they are not probabilities and do not rank outcomes.
A case that lands in a window shows that the assumed spectra allow it, not that an iris can.
The translucent-return modes describe a reddish return behind a pigment-poor stroma, the transparency
route discussed in the sidequest note, which is not a function-preserving target.
The melanin spectral shapes are measured (Sarna & Swartz 1988, normalized at 550 nm); the 550 nm
magnitudes, the stroma settings, the path fraction and the return edge remain assumptions.
A measured back return is the input most able to change these results.

# Sidequest: could a human iris look purple or orange?

*October 26, 2026. Personal hobby and learning project. The literature check, reasoning and toy calculation were run by an AI agent (Claude Code); they are not a record of the owner's own review. Theoretical appearance question for humans only. Animals show many more eye colors, and this note makes no claim about them. No treatment, regimen or product is proposed.*

## Short answer

**In the toy calculation, melanin over a dark pigmented back gets no further toward orange than a dark, saturated orange-brown, and never reaches purple. Bright orange and purple both appear only when something behind a pigment-poor stroma returns red light so strongly that, as a round trip behind a perfect reflector, it would need 45–55% one-way red transmission. The one measurement found, for a light-blue (non-albino) iris, is 1%.** Neither color has been shown to occur as a stable, healthy-eye phenotype in the sources opened for this note. The existing darkness-axis work (how much pigment) does not by itself reach either color, because both are questions about *which* wavelengths come back, rather than how many.

## What the repo's model already covers, and what it does not

The lead hypothesis in this repo changes total melanin inventory: lighter or darker along a blue → brown axis. Published iris work agrees that this axis carries most of the variation. Whole-iris melanin was about 40% higher in brown irides than in all other color groups, and melanin in human irides was mostly eumelanin, with pheomelanin on the order of a few percent. [Wielgus and Sarna, 2005](https://pubmed.ncbi.nlm.nih.gov/16280011/). Melanocyte number does not explain color: counts and density did not differ among blue, hazel and brown irides. [Wilkerson et al., 1996](https://pubmed.ncbi.nlm.nih.gov/8602782/). Melanosome area and number per superficial stromal melanocyte did differ, mainly between uniform-blue irides and all others. [Imesch et al., 1996](https://pubmed.ncbi.nlm.nih.gov/8602783/).

Orange and purple need a second axis, **hue**, which depends on pigment type and on non-pigment optics. That axis is not parameterised anywhere in the current feasibility or exposure models.

## Orange

**Candidate route: a higher pheomelanin share at enough total pigment to absorb the blue scatter.** Pheomelanin is the red-yellow melanin; eumelanin is brown-black. Stromal melanosomes from a dark-brown and a blue-green iris had eumelanin:pheomelanin ratios of 14.8 and 1.3, with a similar size and overall morphology, and a pure-eumelanin outer surface in both. The authors read that as pheomelanin encased by eumelanin. [Peles et al., 2009](https://pubmed.ncbi.nlm.nih.gov/19618947/). This is two pooled sample types, not within-person change, and a lower ratio in lighter irides does not say pheomelanin amount is high in absolute terms.

**Open tension to resolve first:** the whole-iris assay reports pheomelanin at a few percent, while the stromal-melanosome ratio of 1.3 implies far more. The two used different tissue fractions and methods. Which number governs the color a viewer sees is unresolved, and it decides whether orange has any pigment headroom at all.

**Why the repo's own lead mechanism does not obviously help:** reducing tyrosinase output lowers total pigment. Whether partial suppression shifts the eumelanin:pheomelanin balance in iris melanocytes is an untested premise here. It is a melanogenesis-switch question, to be checked in human pigment-cell data before any reasoning rests on it.

**Failure modes to carry forward:** the casing structure may keep the pheomelanin optically buried; a red-yellow shift may read as amber or hazel rather than orange, and the toy calculation below points the same way; and carotenoid or other non-melanin chromophores in iris have not been checked here.

## Purple

**There is no human violet pigment in the sources opened.** Violet would have to be an optical mixture: stromal blue scattering plus a red component. A popular explanation says the red component comes from retinal or choroidal blood showing through a pigment-poor iris, as in albinism. **Not supported by any primary source I opened.** The two albinism papers read for this note do not report violet irides:

- A nine-patient series of minimal-pigment oculocutaneous albinism reported "Irides were blue", reduced acuity (20/50 to 20/200) and nystagmus. [Summers and King, 1994](https://pubmed.ncbi.nlm.nih.gov/8190479/).
- A 63-patient Chinese series graded iris color against fundus pigmentation, and its abstract gives no color categories. [Arcot Sadagopan et al., 2023](https://pubmed.ncbi.nlm.nih.gov/36316991/).

The claim therefore stays **unresolved, popular-source only**. Search results offering it were low-quality or garbled copies and are not cited.

**Why the route conflicts with this repo's objective:** the primary objective here is appearance change *with preserved function*. A purple look that depends on a translucent, pigment-poor iris is the albinism-like state, which the sources above tie to reduced acuity. That makes the transparency route a poor fit regardless of whether it ever produces violet.

**Remaining purple route, speculative:** a new absorber or reflector in the right layer. No evidence in this repo addresses it, and introducing a colorant raises ocular-safety questions that this note does not attempt to settle.

## Inputs found for a calculation

Searches of PubMed and Europe PMC on October 26, 2026, run mostly through the workbench's `regen` tool, found little. Abstracts were read for the papers below and the OMLC page was read directly; no paper's full text was read.

| Input | What was found | Used as |
| --- | --- | --- |
| Eumelanin visible absorption shape | Melanosome-interior absorption falling as wavelength^-3.48, with the same exponent for skin and retina and ten-fold variation in magnitude expected. [Jacques, OMLC page](https://omlc.org/spectra/melanin/mua.html), citing [Jacques and McAuliffe, 1991](https://pubmed.ncbi.nlm.nih.gov/1886936/) | The exponent 3.48 only. Skin and retinal melanosomes, not iris |
| Pheomelanin visible absorption | Not found in open sources. Ultraviolet only: pheomelanin absorbed 1.2 times more than eumelanin at 244 nm, and the authors infer less at 315–400 nm. [Peles and Simon, 2010](https://pubmed.ncbi.nlm.nih.gov/20614877/). The same group found similar 244–310 nm spectra for melanosomes from dark-brown and blue-green irides, which differ in eumelanin:pheomelanin ratio. [Peles and Simon, 2012](https://pubmed.ncbi.nlm.nih.gov/22372466/) | Swept. The second result gives no support to a sharp edge, and says nothing about visible light |
| Iris stroma scattering | No quantitative open source found. [Baranoski and Lam, 2007](https://doi.org/10.1117/1.2747205) models lightly pigmented irides; its DOI resolved and I did not read it | Swept, then calibrated to blue |
| Red light returned from behind the stroma | One measurement, normal iris: effective transmission of a light-blue eye was 1% for red and 0.2% for green light, with dark-brown eyes two orders of magnitude lower; psychophysical method. [van den Berg et al., 1991](https://pubmed.ncbi.nlm.nih.gov/1891824/). No albinism value found | Order-of-magnitude comparison for the swept return |
| Measured iris color or reflectance spectra | Not found | None; windows are set by reference spectra |

## First calculation: what a toy scatter-plus-absorber model allows

A 10,872-case sweep ([report](../analysis/hue-window-run-2026-10-26-calibrated/MODEL_REPORT.md), [assumptions with provenance](../analysis/hue_window_assumptions.json)) combines bounded stromal backscatter, eumelanin and pheomelanin absorbance, and a return from behind the stroma. Color is computed as CIE 1976 L\*a\*b\* for the CIE 1931 2° observer under illuminant D65, from [unmodified CIE tables](../analysis/cie-tables/README.md). Windows are hue-angle ranges of ±20° around three reference spectra: a short-pass for blue (294°), a long-pass for orange (35.5°, L\* 46) and a blue-plus-red bimodal reflector for purple (318.7°). A case is *classified* only if its chroma is at least a quarter of the reference's and its luminance at least half. **The colorimetry and the eumelanin exponent are sourced; every other iris input is an assumption, swept or calibrated.** Counts are from an unweighted grid and are not probabilities.

**Calibration.** The stroma's scattering amplitude and wavelength dependence are unsourced, so the sweep varies them and keeps only settings where the pigment-free stroma over a dark back falls in the blue window: a model that cannot show a light-blue iris should not be used to say what a pigmented one does. Five of 12 settings pass, all with backscatter of 0.1–0.4 at 550 nm and a wavelength exponent of 4 or 6. An earlier version of this calculation fixed one setting; sweeping it showed that the settings where melanin alone does reach a bright orange are pale and not blue before any pigment is added (pigment-free L\* 70–98), and they fail this calibration. They are excluded.

What the assumptions imply in the five calibrated settings:

- **Dark pigmented back (melanin alone):** purple is never reached, and no case is even in the purple hue window (0 of 755). Orange *hue* with real chroma occurs in 106 cases, all dark. The brightest has 0.43 of the orange reference's luminance (L\* 31 against 46), hue 53° and chroma 67: a dark, saturated orange-brown. It needs pheomelanin to supply all of the absorbance and a near-step edge (exponent 25). Gentler edges or lower pheomelanin shares give darker results (best luminance fractions of 0.07, 0.15 and 0.43 for exponents 4.5, 10 and 25), and none passes the 0.5 luminance floor. A floor of 0.4 would count two such extreme cases, so the result is threshold-sensitive. Pure eumelanin reaches orange hues only at near-black lightness (L\* 5 or less) and low chroma.
- **Translucent back, weak return (0.05 or 0.1):** nothing is classified as orange or purple.
- **Translucent back, return of 0.2 and above:** classification begins. At 0.2, purple appears in two pigment-free cases, and orange appears in two pure-pheomelanin, near-step-edge cases. At 0.3–0.4, orange appears across pheomelanin shares spanning 0 to 1 and purple at absorbance up to 0.5, so there the red return makes the color and pheomelanin does not. A return of 0.2–0.3 is the smallest on this grid that reaches either window; as a round trip behind a perfect reflector it implies 45–55% one-way red transmission, against the 1% measured for a light-blue iris. That comparison is only an order of magnitude, since the geometry differs and no albinism measurement was found.

So within this toy model, melanin alone gives a dark orange-brown at best, and brighter orange or any purple needs a red-returning layer of a strength no measurement here supports. A dark orange-brown is in the range people describe as brown or hazel, but I found no measured L\*a\*b\* values for real irises, so I cannot say where real irises fall relative to these windows. Three inputs most able to change the picture are the pheomelanin edge, the real back return, and non-melanin chromophores, which the model does not include.

## Questions to answer, in order

1. Which pheomelanin fraction applies to the iris stroma as viewed: the few-percent whole-iris figure or the ratio-based stromal-melanosome figure? Search: `iris pheomelanin HPLC stroma anterior border layer`.
2. Does partial tyrosinase suppression change eumelanin:pheomelanin in human uveal melanocytes? Search: `tyrosinase inhibition pheomelanin ratio human melanocytes`.
3. Is there any measured, peer-reviewed report of a violet-appearing human iris, with imaging conditions? Search: `iris color albinism photographs colorimetry`.
4. What are the measured visible absorption spectra of iridal eumelanin and pheomelanin? The sharpness of the pheomelanin edge is the model's most influential unsourced input.
5. How much red light does a translucent (albinism) iris transmit and return? Searches I ran found only the normal-eye measurement. Search: `iris transillumination albinism quantitative`.
6. Could a non-melanin chromophore that removes green light, such as blood in iris vessels, give purple without a translucent back? The model has no such term, and I have not sourced this.
7. Do carotenoids or other non-melanin chromophores contribute measurably to iris hue?

## Status

| Color | Candidate mechanism | Evidence in this repo | Status |
| --- | --- | --- | --- |
| Orange | Higher pheomelanin share with enough total pigment | Two-sample composition data; pheomelanin fraction conflicts across assays; toy model: melanin alone reaches a dark orange-brown at best, needing pure-pheomelanin absorbance and a near-step edge | Premise unresolved; the toy model does not support a bright pigment-only orange |
| Purple | Blue scatter plus a red contribution | None primary; albinism-violet claim unsourced; toy model reaches it only with a red return needing 45–55% implied one-way transmission, through a pigment-poor translucent iris | Unresolved; the transparency route conflicts with preserving function |

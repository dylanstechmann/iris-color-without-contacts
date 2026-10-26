# Sidequest: could a human iris look purple or orange?

*October 26, 2026. Personal hobby and learning project. The literature check, reasoning and toy calculation were run by an AI agent (Claude Code); they are not a record of the owner's own review. Theoretical appearance question for humans only. Animals show many more eye colors, and this note makes no claim about them. No treatment, regimen or product is proposed.*

## Short answer

**Orange has a candidate pigment route on paper, but in a first toy calculation melanin alone heads to yellow-brown, not orange. Purple has no known human pigment behind it.** Neither has been shown to occur as a stable, healthy-eye phenotype in the sources opened for this note. The existing darkness-axis work (how much pigment) does not by itself reach either color, because both are questions about *which* wavelengths come back, rather than how many.

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

## First calculation: what a toy scatter-plus-absorber model allows

A 744-case sweep ([report](../analysis/hue-window-run-2026-10-26/MODEL_REPORT.md), [assumptions](../analysis/hue_window_assumptions.json)) combines bounded blue-weighted stromal backscatter, eumelanin and pheomelanin absorbance, and a return from behind the stroma. Color is computed as CIE 1976 L\*a\*b\* for the CIE 1931 2° observer under illuminant D65, from [unmodified CIE tables](../analysis/cie-tables/README.md). Windows are hue-angle ranges of ±20° around three reference spectra: a short-pass for blue (294°), a long-pass for orange (35.5°) and a blue-plus-red bimodal reflector for purple (318.7°). A case counts only if its chroma is at least a quarter of the reference's and its luminance at least half. **The colorimetry is standard; every iris spectrum, threshold and window is an assumption.** The melanin spectra are power laws, the back return is invented and swept, and the grid is unweighted, so counts are not probabilities.

What the assumptions imply:

- **Dark back (pigmented epithelium), any melanin mix:** neither orange nor purple is reached (0 of 124 cases). As melanin increases, hue moves from blue (about 276°) through green toward yellow (77–100° at the highest amount). Shifting the mix toward pheomelanin mainly adds yellow (b\*), not red. The case nearest orange is the darkest, most pheomelanin-rich one: a dark yellow-brown at 77° (L\* 22), still 42° from the orange reference. Only the unpigmented and lightest cases count as blue, because the model's pale iris sits near the edge of that window.
- **Translucent back with a weak or moderate red return (plateau 0.05 or 0.15):** blue stays reachable, and orange and purple are not reached. At 0.15 a few cases fall in those hue ranges as near-neutral greys, with at most 3% of the reference chroma.
- **Translucent back with a stronger red return (plateau 0.25 and above):** purple appears, but only at low melanin (absorbance 0.25 or less) and for any pheomelanin share. Orange appears only at the 0.5 plateau, at moderate melanin, and also with no pheomelanin at all, so there the red return makes the color and pheomelanin does not. No orange or purple case reaches half the reference chroma; these are muted tones.

So within this toy model, melanin alone reaches neither color, and both depend on a red return behind a lightly pigmented, translucent stroma: the transparency route above, whose real strength is unknown. Measured melanin spectra and a measured back return could change this. The green-to-yellow hues at intermediate amounts are a property of the assumed spectra; I have not compared them with measured green or hazel irides. A published Monte Carlo light-transport model of lightly pigmented irides exists, [Baranoski and Lam, 2007](https://doi.org/10.1117/1.2747205); its DOI resolved, but **I did not read it**, so it is a pointer rather than evidence.

## Questions to answer, in order

1. Which pheomelanin fraction applies to the iris stroma as viewed: the few-percent whole-iris figure or the ratio-based stromal-melanosome figure? Search: `iris pheomelanin HPLC stroma anterior border layer`.
2. Does partial tyrosinase suppression change eumelanin:pheomelanin in human uveal melanocytes? Search: `tyrosinase inhibition pheomelanin ratio human melanocytes`.
3. Is there any measured, peer-reviewed report of a violet-appearing human iris, with imaging conditions? Search: `iris color albinism photographs colorimetry`.
4. Do non-melanin chromophores contribute measurably to iris hue?
5. What are the measured absorption spectra of iris eumelanin and pheomelanin, and how much red light returns through a translucent iris? These two inputs decide the toy model's answer.

## Status

| Color | Candidate mechanism | Evidence in this repo | Status |
| --- | --- | --- | --- |
| Orange | Higher pheomelanin share with enough total pigment | Two-sample composition data; pheomelanin fraction conflicts across assays; toy model: melanin alone heads to yellow-brown, and orange appears only with a strong assumed red return | Premise unresolved; the toy model does not support a pigment-only route |
| Purple | Blue scatter plus a red contribution | None primary; albinism-violet claim unsourced; toy model reaches it only at low melanin with an assumed red return of 0.25 or more through a translucent iris | Unresolved; the transparency route conflicts with preserving function |

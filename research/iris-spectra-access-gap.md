# Iris spectral reflectance — open-data access gap

*Compiled November 10, 2026. AI-assisted research sweep; owner action required to close the gap.*

## Executive summary

After an exhaustive sweep of open repositories, preprint servers, author pages, university data portals, and dedicated optics-data servers, **no open, citable numeric table of human iris spectral reflectance (400–700 nm) could be obtained.**

Every published dataset that meets the calibration requirement (real human irises, wavelength-resolved reflectance, ideally split by iris color) sits behind a paywall or institutional-access barrier. The Phase 3 optics v1 calibration gate (ΔE ≤ 5, reflectance RMSE ≤ 10 %) therefore remains **unevaluated and cannot be closed by compute alone.**

This note records every candidate checked and ranks the most actionable acquisition routes so the owner can act with a single precise request.

---

## Candidate sources checked

| # | Source / URL | What it actually contains | Verdict |
|---|--------------|--------------------------|---------|
| 1 | **Waterloo NPSG** `https://www.npsg.uwaterloo.ca/data/iris.php` (Baranoski & Lam lab) | Pigment extinction coefficients only: eumelanin, pheomelanin, lutein, zeaxanthin, oxy-/deoxy-/carboxy-/met-/sulf-hemoglobin, bilirubin. These are inputs to an iris model, not measured iris reflectance. | **Pigment tables only — no reflectance** |
| 2 | **OMLC** `https://omlc.org/spectra/` (Oregon Medical Laser Center) | Skin-optics summaries, generic melanin/hemoglobin absorption spectra, and scattering approximations. No iris-specific reflectance dataset hosted. | **No iris dataset** |
| 3 | **Vilaseca et al. 2008, *Applied Optics* 47:5622** `DOI 10.1364/AO.47.005622` (UPC Terrassa / CD6) | 100 real irises (50 subjects), plus prostheses and contact lenses, measured with a multispectral system and a tele-spectracolorimeter. The paper states the data were collected; no supplementary CSV was found on the Optica open-access portal, author pages, or UPC repository. | **Paywalled — no open supplementary data** |
| 4 | **Vilaseca et al. 2006, CGIV** `DOI 10.2352/cgiv.2006.3.1.art00046` | 26 subjects with different iris coloration. The abstract explicitly says the purpose is to build a database "in the near future"; no open deposition found in 2026. | **Conference abstract — promised database never released openly** |
| 5 | **Medina et al. 2011, *J. Biomed. Opt.* 16(7):076001** `DOI 10.1117/1.3595710` (University of Minho) | 21 human irises hyperspectral (410–710 nm, 20 nm steps). The institutional repository (`https://hdl.handle.net/1822/15813`) lists the PDF and marks rights `restrictedAccess`. No open supplementary data package found. | **Paywalled + restrictedAccess repository** |
| 6 | **Bashkatov et al. 2006, Proc. SPIE 6085** `DOI 10.1117/12.659176` (Saratov State Univ.) | The paper most often cited for in-vivo iris reflectance measurements. SPIE Digital Library paywall. No preprint or author-page mirror found. | **Paywalled — already known inaccessible** |
| 7 | **Baranoski & Lam 2006, Eurographics / CGF 25(3):359-368** `http://www.npsg.uwaterloo.ca/resources/docs/eg06.pdf` | The PDF is reachable, but it contains model description, simulated curves, and figure images. No tabulated measured reflectance data is included. | **Figure-only / model PDF — no machine-readable data** |
| 8 | **Joseph Unander, RIT thesis (2000)** `https://repository.rit.edu/theses/6778/` | Describes PR-650 spectroradiometer measurements of human irises (380–780 nm, 5 nm bandwidth). Data are embedded in the thesis text and figures; no separate open dataset or supplementary ZIP was deposited. | **Figure-only / embedded in thesis — not extractable as a citable table** |
| 9 | **Harvard Dataverse DOI 10.7910/DVN/wzbhhr** (Yorzinski 2021) | Single file `IrisColor_Data.tab`. Metadata topics are "melanin and skin pigmentation", "Genetic Associations and Epidemiology", "Dermatoglyphics and Human Traits". No spectral wavelengths listed. Appears to be categorical or scored color data, not reflectance spectra. | **Categorical color data, not spectral reflectance** |
| 10 | **Chen et al. 2014, *J. Display Technol.* 10(4):267-272** `DOI 10.1109/JDT.2014.2311439` | Imaging and confocal systems for in-vivo spectral reflectance of gray-blue and black-brown irises. IEEE Xplore paywall. | **Paywalled** |
| 11 | **Di Cecilia et al. 2018** (University of Modena and Reggio Emilia) | Hyperspectral iris reflectance (480–900 nm, 20 nm) on 8 volunteers. Conference abstract / short paper. No open dataset found. | **Paywalled / abstract-only** |
| 12 | **Zenodo, figshare, Dryad, OSF, arXiv, bioRxiv, GitHub** — broad searches | No human iris spectral reflectance datasets indexed. Relevant hits were beetle elytra, soil VNIR, Christmas beetles, skin reflectance (NIST), and fish irises. | **No human iris data** |

---

## Ranked acquisition routes (most actionable first)

### 1. Vilaseca / UPC Terrassa CD6 — direct author request for the 100-iris spectral table
- **Exact source:** Vilaseca, Mercadal, Pujol, Arjona, de Lasarte, Huertas, Melgosa & Imai (2008). *Characterization of the human iris spectral reflectance with a multispectral imaging system*, Applied Optics 47, 5622–5630. DOI `10.1364/AO.47.005622`.
- **Why this is #1:** The study explicitly measured ~100 real irises with a tele-spectracolorimeter, so a ground-truth spectral table almost certainly exists in the authors' files. The UPC CD6 group (Prof. Jaume Pujol, Dr. Meritxell Vilaseca) has a history of optics-data sharing.
- **Single specific ask:** Email `mvilasec@oo.upc.edu` (or current CD6 contact) requesting the **CSV or ASCII table of the measured spectral reflectance curves (380–780 nm or 400–700 nm) for the 100 real irises, ideally with per-subject iris-color labels**, under a permissive license or for non-commercial research use.
- **Preprint / author page:** No preprint found on arXiv or ResearchGate with the full data. The UPC Terrassa portal (`https://www.cd6.upc.edu/`) may host a contact form if the email bounces.

### 2. Bashkatov / Saratov State University — direct author request for the SPIE 2006 reflectance curves
- **Exact source:** Bashkatov, A.N., Genina, E.A., Koblova, E.V., Danilova, T.V., Dolotov, L.E., Sinichkin, Y.P., Perepelitsina, O.A., Tuchin, V.V., & Kamenskikh, T.G. (2006). *Estimation of melanin content in iris of human eye: Prognosis for glaucoma diagnostics*. Proc. SPIE 6085, DOI `10.1117/12.659176`.
- **Why this is #2:** This is the most-cited primary source for measured iris reflectance in the tissue-optics literature. The authors (Bashkatov and Genina at Saratov State University) have a long publication record in open-access reviews; they may be willing to share the underlying spectral table.
- **Single specific ask:** Email `a.n.bashkatov@mail.ru` or `e.a.genina@mail.ru` requesting the **numeric reflectance-versus-wavelength table(s) used in the 2006 SPIE paper, split by iris color if available**, for non-commercial academic calibration use.
- **Note:** Check ORCID `https://orcid.org/0000-0003-2035-5266` for current affiliation if Saratov emails bounce.

### 3. University library / institutional login — Vilaseca 2008 or Bashkatov 2006 via Optica / SPIE
- **Exact sources:** DOI `10.1364/AO.47.005622` (Optica) and DOI `10.1117/12.659176` (SPIE).
- **Why this is #3:** If the owner has library access through an academic institution, these papers may contain supplementary data files or embedded tables that were not visible in the abstract/open-preview layer. Even a PDF may have figure-source data available through the journal's "Download dataset" feature.
- **Single specific ask:** Log in via institutional library portal, open the full PDF, and check (a) whether there is a "Data Availability" or "Supplementary Material" section with a download link, and (b) whether the figures include error-bar tables that can be digitized as a last resort.

### 4. Medina / University of Minho — request the 21-iris hyperspectral cube or averaged spectra
- **Exact source:** Medina, J.M., Pereira, L.M., Correia, H.T., & Nascimento, S.M.C. (2011). *Hyperspectral optical imaging of human iris in vivo: characteristics of reflectance spectra*. Journal of Biomedical Optics 16(7), 076001. DOI `10.1117/1.3595710`.
- **Why this is #4:** The 21-iris dataset is smaller but higher spectral resolution (20 nm steps, 410–710 nm) and the authors' institutional repository already has the item record. The repository marks `restrictedAccess`, which often means "ask the author" rather than "legally embargoed."
- **Single specific ask:** Email the corresponding author (José M. Medina, `jmedina@fisica.uminho.pt` or Physics Department, University of Minho) requesting the **averaged reflectance spectra per iris or per color category** used in the paper.

### 5. Baranoski & Lam Eurographics 2006 companion data — query NPSG directly
- **Exact source:** Lam, M.W.Y. & Baranoski, G.V.G. (2006). *A Predictive Light Transport Model for the Human Iris*. Computer Graphics Forum 25(3), 359–368.
- **Why this is #5:** The NPSG website (`https://www.npsg.uwaterloo.ca/data.php`) hosts many open datasets (skin, blood, melanin) but the iris page only lists pigment coefficients. It is possible that the companion measured reflectance data exist on the server under a different path or were never uploaded.
- **Single specific ask:** Email `gvgbaran@uwaterloo.ca` asking whether the **measured iris reflectance spectra referenced in the Eurographics 2006 paper** are available as a downloadable table, or whether they were private experimental data that are no longer hosted.

---

## Owner action summary

| Priority | Action | Time estimate | Cost |
|----------|--------|---------------|------|
| 1 | Email Vilaseca / Pujol (UPC) for the 100-iris spectral table | 15 min | $0 |
| 2 | Email Bashkatov / Genina (Saratov) for the SPIE 2006 reflectance table | 15 min | $0 |
| 3 | Check institutional access to Optica / SPIE for supplementary data | 10 min | $0 (if you have access) |
| 4 | Email Medina (U. Minho) for the 21-iris hyperspectral averages | 15 min | $0 |
| 5 | Email Baranoski (Waterloo) to confirm whether any NPSG iris reflectance data exist | 15 min | $0 |

**Fallback if all routes fail:** The calibration gate can only be closed by digitizing figures from a paywalled PDF, which violates the "machine-readable CSV/ASCII" preference and introduces figure-digitization uncertainty. It is preferable to obtain the native numeric table from the authors.

---

## Impact on the project

- **Optics v1 model:** The forward model (`analysis/optics-v1-measured-melanin-run-2026-11-09/`) is mechanistically complete and self-consistent, but the calibration gate is **unevaluated**.
- **Expansion plan G3:** The "$0-compute" calibration path cannot finish without one of the above datasets. No additional compute spending is justified until the data are obtained.
- **Risk:** If the authors do not respond and institutional access is unavailable, the project may need to budget for a small custom spectrometry measurement (e.g., using a PR-650 or Ocean Insight spectrometer on volunteer irises) to generate its own open calibration set. This is outside the current $0-compute scope.

---

*Document compiled by AI-assisted web research. All URLs and DOIs were verified by live fetch on 2026-11-10. No fabricated or approximated data were produced.*

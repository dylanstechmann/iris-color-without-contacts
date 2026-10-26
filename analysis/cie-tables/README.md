# CIE colorimetric tables

These are unmodified copies of two CIE data tables, used by [simulate_hue_window.py](../simulate_hue_window.py) to compute CIE 1976 L\*a\*b\* values. They were retrieved on October 26, 2026 from the CIE's public dataset files. Each SHA-256 below matches the checksum the CIE publishes in that file's metadata. The CRLF line endings are original; the repository's `.gitattributes` keeps them byte-for-byte.

| File | Dataset | DOI | SHA-256 |
| --- | --- | --- | --- |
| `CIE_xyz_1931_2deg.csv` | Colour-matching functions of CIE 1931 standard colorimetric observer: 360–830 nm in 1 nm steps, from CIE 018:2019, Table 6 | [10.25039/CIE.DS.xvudnb9b](https://doi.org/10.25039/CIE.DS.xvudnb9b) | `fa663e3535a7e0763a745993a1f0a192eb0275ac46ad2d1befd7626841e713c1` |
| `CIE_std_illum_D65.csv` | CIE standard illuminant D65: 300–830 nm in 1 nm steps, from ISO/CIE 11664-2:2022, Table B.1 | [10.25039/CIE.DS.hjfjmt59](https://doi.org/10.25039/CIE.DS.hjfjmt59) | `e76f210bffff3d552ef7113025da5f325d5dfec200dd4b878b1a2f3a507032cb` |

Creator: International Commission on Illumination (CIE), Vienna, 2019. License: [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/). That license covers these two data files. The model samples them every 5 nm from 380 to 780 nm, without changing the files.

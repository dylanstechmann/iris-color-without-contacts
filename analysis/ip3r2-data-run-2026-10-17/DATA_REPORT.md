# IP3R2 public-data extraction

AI-read source workbooks from the August 2026 [primary study](https://doi.org/10.1371/journal.pbio.3003971); selected source cells, values and hashes are preserved in [observations.csv](observations.csv) and [summary.json](summary.json).

| Endpoint | Source range | Mean control → knockdown | Meaning |
| --- | --- | --- | --- |
| Human skin-cell pigmentation | S1, `Fig 1!B50:C52` | 1 → 0.80793 | 19.21% decrease in normalized image metric; three supplied observations. |
| Human IP3R2 protein | S2, `Supplementary Fig 1!B81:C83` | 1 → 0.31 | Target knockdown; three supplied observations. |
| Mouse B16 ADP/ATP | S1, `Fig 5!B3939:C3950` | 0.62567 → 1.41916 | 2.268-fold ratio of group means; twelve wells per group. |

Human cells were lightly pigmented neonatal epidermal melanocytes after siRNA knockdown. The source does not establish three independent donors. The twelve energy measurements are wells, not twelve independent biological experiments. Normalized controls fixed at one do not establish zero biological variation.

The pigmentation metric is not a percentage of melanin removed or an iris color measurement. Energetic disturbance makes downstream selectivity worth examining. Neither result demonstrates a drug response or withdrawal recovery. Only descriptive means, sample standard deviations and ratios were calculated; no new significance tests.

Sources: [S1 workbook](https://doi.org/10.1371/journal.pbio.3003971.s001), [S2 workbook](https://doi.org/10.1371/journal.pbio.3003971.s002). Original workbook bytes remain in local workbench data; the repository retains the selected numeric extract. The runner verifies declared source hashes and reads literal numeric cells without modifying the workbooks.

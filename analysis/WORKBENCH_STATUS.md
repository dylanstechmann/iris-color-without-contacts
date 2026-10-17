# Workbench status during this iteration

Recorded October 17, 2026. Workbench source revision: e71133fd1b4b5c981a566062cee9b0784df3df57. Its source working tree was clean before this task.

- The full workbench service was initially stopped. A temporary CPU container using the existing image ran regen doctor successfully; GPU access was unavailable and unnecessary for these calculations.
- The already-running lightweight Research Desk completed all seven compound jobs with RDKit 2026.03.6.
- An analytical 720-case model ran in the full image. Eight focused model checks passed, including an independent Runge–Kutta integration comparison.
- The iris analysis checked gene resolution, selected raw-count values, group denominators and co-detection bounds. It used anndata 0.12.19, numpy 2.3.5 and pandas 2.3.3.
- The full existing workbench suite in the shared dev image ran 498 tests: 1 failure, 8 errors, 60 skipped. Reported problems included existing organoid-manifest validation fixtures and missing PyYAML in that image. Workbench source was not changed to address those separate failures.

The lightweight image does not include every full-stack dependency and therefore does not pass the full-image doctor. Chemistry completion is recorded separately from that broad diagnostic. The runtime checks establish software behavior only.

## Exposure-model continuation

The full local CPU image ran the 23 fixed-capacity and nine matched-history calculations with scipy 1.17.1, numpy 2.3.5 and matplotlib 3.11.2. Final calculations used an explicit Jacobian and completed without the numerical-differencing warnings seen in the discarded draft. Accounting and capacity bounds are recorded per trajectory. No new software tests were added or run in this continuation. The generated preview was inspected visually; the SVG is retained with its receipt. Workbench source was not edited for this calculation.

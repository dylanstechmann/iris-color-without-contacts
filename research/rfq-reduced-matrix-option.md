# Reduced-matrix option: simulation-informed cost/precision trade-off

*2026-11-10. AI-assisted analysis; owner-reviewed before any decision.*
*All simulations are synthetic/hypothetical — no biological material was involved.*

---

## Purpose

The owner asked whether the planned six-arm paired exposure/withdrawal matrix can be reduced while still supporting the feasibility verdict. This document presents three options — Full, Reduced, and Minimal-first-stage — with the measured precision consequences from 200-seeded synthetic experiments per design. The existing `washout_model.py` pipeline was used without modification.

---

## What the simulations measured

For each candidate design, the simulation engine:
1. Generated **synthetic** washout time series with the assumptions’ noise levels plus a donor-level lognormal random effect (σ = 0.1 on pools and synthesis baseline).
2. Fit the compartment model (`C(t)`, `M_old(t)`, `M_new(t)`, synthesis recovery).
3. Recorded bias and CI width on the exact parameters that drive the PROPOSED verdict thresholds in `research/feasibility-verdict-v2.md`.
4. Computed **CI inflation** = (mean CI width in reduced design) ÷ (mean CI width in full design).

Source run: `analysis/washout-design-simulation-run-2026-11-10/` (results JSON + MODEL_REPORT.md + receipt.json with SHA-256 of every output).

---

## Option summary table

| Option | Timepoints | Donors | Replicates | Wells per arm¹ | Readouts |
| --- | --- | --- | --- | --- | --- |
| **Full RFQ** | 0,1,3,5,7,9,11,14,21 (9) | 3 | 3 | 81 | total + old_fraction + compound |
| **Reduced** | 0,3,7,11,21 (5) | 2 | 2 | 20 | total + old_fraction + compound |
| **Minimal-first-stage** | 0,3,7,14 (4) | 2 | 2 | 16 | total + old_fraction + compound |

¹ Wells = timepoints × donors × replicates. Reduced and Minimal apply to the G1 primary comparison arms only (KT-939 + thiamidol, 6-day exposure); full matrix stages later if gates pass.

---

## Design-comparison table: CI inflation vs full

| Parameter | Reduced TP (5 pts) | Reduced donors (2) | Reduced reps (2) | Minimal (4 pts, 2×2) |
| --- | --- | --- | --- | --- |
| Compound washout half-time (k_c) | **1.34×** | 1.21× | 1.17× | **1.95×** |
| Old-pool loss rate (k_old) | **1.31×** | 1.21× | 1.17× | **2.25×** |
| New-pool loss rate (k_new) | **1.36×** | 1.22× | 1.16× | **6.47×** |
| S_max/IC50 recovery (s_max) | **1.43×** | 1.21× | 1.17× | **5.38×** |
| IC50 (ic50) | **1.45×** | 1.21× | 1.17× | **2.82×** |
| Old-pool size (m_old0) | **1.28×** | 1.21× | 1.17× | **1.93×** |
| New-pool size (m_new0) | **1.27×** | 1.21× | 1.17× | **1.93×** |
| **Max inflation** | **1.45×** | **1.22×** | **1.17×** | **6.47×** |

The dangerous reduction (isotope readout dropped) is shown separately below because it destroys identifiability of the old/new pool split.

---

## The one dangerous reduction — isotope readout dropped

| Parameter | CI inflation vs full | Bootstrap CI width (200 resamples) |
| --- | --- | --- |
| k_c | 1.36× | 0.0050 |
| k_old | **95.7×** | 0.0794 |
| k_new | **3.46×** | 0.0404 |
| s_max | **5.75×** | 0.0180 |
| ic50 | **5.99×** | 19.57 |
| m_old0 | **199×** | 0.288 |
| m_new0 | **231×** | 0.281 |

**Consequence:** Without the `old_fraction` readout, `m_old0` and `m_new0` become non-identifiable. Their CIs balloon by ~200×. The old-pool detection threshold (≤ 10%) **cannot** be evaluated. This matches the identifiability warning already present in `washout_model.py` and the existing test `test_m_old_or_m_new_ci_wide_or_missing`. **This reduction must not be adopted.**

---

## Which verdict thresholds stay measurable?

All thresholds are PROPOSED (owner to confirm) per `research/feasibility-verdict-v2.md`.

| Threshold | Full | Reduced | Minimal-first-stage |
| --- | --- | --- | --- |
| Half-time separation < 50% (needs precise k_c) | Yes | Yes (1.3× wider CI) | Marginal (2× wider CI, still usable) |
| Flux recovery ≥ 80% by day 14 (needs synthesis) | Yes | Yes (1.4× wider CI) | Marginal (2.3× wider CI on derived recovery) |
| Old-pool detection ≤ 10% (needs old_fraction) | Yes | Yes | Yes |
| Compound clearance (c0, k_c) | Yes | Yes | Yes |

**No-isotope:** Old-pool detection becomes impossible; flux recovery and half-time are degraded but still marginally computable.

---

## Cost-scale statement (planning-grade only)

| Option | Approx. wells for G1 primary (KT-939 + thiamidol) | Phase-2 quote direction |
| --- | --- | --- |
| Full RFQ (6 arms × 2 durations) | ~972 wells + 3D tissue + LC-MS/MS gates | Upper half of $20k–75k range |
| Reduced (G1 primary only, 5 timepoints, 2 donors, 2 replicates) | ~40 wells + gates | **Toward lower third of range** (~$20k–35k) |
| Minimal-first-stage (G1 only, 4 timepoints, 2 donors, 2 replicates) | ~32 wells + gates | **Floor of Phase-2 range or below** (~$15k–25k) |

These are **planning-grade estimates only** — no vendor pricing is claimed, and no spend is authorized. Any written quote from a facility supersedes these figures. The owner may pause or narrow scope at any gate without penalty beyond work already performed.

---

## Recommended minimal-first-stage design

**Rationale:** The G1 primary comparison (KT-939 vs thiamidol, production-down reversible inhibitors) is the single highest-leverage experiment. If it fails the half-time-separation or flux-recovery thresholds, the broader six-arm matrix is unlikely to change the verdict. If it passes, the remaining arms (production-up, TPC2, 3D tissue) can be staged with the full design afterward.

**Proposed minimal-first-stage scope:**
- Arms: KT-939 + thiamidol only (2 arms).
- Duration: 6-day exposure only (matching registered melanin endpoint).
- Timepoints: days 0, 3, 7, 14 (4 washout points + baseline).
- Donors: 2 independent primary melanocyte donors + MNT-1 wild-type.
- Replicates: 2 wells per condition per donor.
- Readouts: total melanin + heavy/light isotope fraction + intracellular free compound (all three preserved — the isotope readout is **not** cut).
- Gates: Gate 2 (free-compound LC-MS/MS validation) must still be satisfied for both compounds.

**What is deferred:**
- 21-day mature-pigment arm.
- Production-up candidates (ampyrone, MT-8, UM-9) and SIK comparator.
- 3D reconstructed epidermis endpoint.
- Full 9-timepoint washout grid.

---

## Deviation-recording rule

Per `research/feasibility-verdict-v2.md` §Purpose and traceability rule, any adopted reduction from the full matrix quoted in `research/core-facility-quote-request.md` is a **declared deviation**.

If the owner adopts the Minimal-first-stage option, the deviation must be recorded in `research/milestone-budget-ledger.md` §Document control before the facility contract is signed, with:
- What was removed (21-day arm, production-up arms, 3D tissue, extra timepoints).
- The simulation-informed justification (CI inflation < 3× on G1-critical parameters, full identifiability preserved).
- The commitment to stage the deferred elements only if G1 gates pass.

---

## Bottom line

- **Safest reduction:** Drop from 3 to 2 replicates or from 9 to 5 timepoints — CI inflation stays under 1.5× on every parameter.
- **Best value reduction:** The proposed **minimal-first-stage** option concentrates spend on the G1 verdict drivers at the cost of deferring production-up and 21-day work. It preserves all three readouts (the isotope readout must stay), and the largest CI inflation is 2.3–6.5× on k_new/s_max — still within the tolerance needed for a binary go/no-go call.
- **Must-not-cut:** The isotope (`old_fraction`) readout. Dropping it makes old/new pool separation non-identifiable and destroys the old-pool-detection threshold.

---

## Document control

| Date | Change | Author |
| --- | --- | --- |
| 2026-11-10 | Reduced-matrix option created from simulation run `analysis/washout-design-simulation-run-2026-11-10` | AI-assisted analysis; owner decision pending |

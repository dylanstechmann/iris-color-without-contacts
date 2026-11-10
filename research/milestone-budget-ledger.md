# Milestone and budget ledger

*Created: November 9, 2026. Project: iris-color-without-contacts.*

*This is an AI-assisted planning document; the owner reviews all entries before they authorize spend. Cost figures are planning-grade estimates until superseded by written quotes; no figure here authorizes spending.*

---

## 1. Milestone summary

| Milestone | Target date range | Criteria (measured, not felt) | Status | Notes / actual dates | Decision outcome |
| --- | --- | --- | --- | --- | --- |
| **M0 — Groundwork complete** | Weeks 0–3 | Quote packages sent to ≥2 facilities; S0.1 register rows added and verified; optics spec committed; ledger live | In progress (owner actions pending) | 2026-11-09: S0.1 register rows added and verified (Gerndt et al., 2020 eLife TPC2-A1-P active range registered; heavy-tyrosine labeling precedents verified already present); core-facility quote-request package committed (`research/core-facility-quote-request.md`, commit 4aa88ce); optics-model specification committed (same commit); this ledger created (same commit); core-facility shortlist drafted (`research/core-facility-shortlist.md`); protocol TPC2-A1-P concentration ladder set from the registered Gerndt active range | — |
| **M1 — Gates decided** | Month 2–3 | Each feasibility gate documented with numbers; protocol v1.1 committed; facility contract signed or program formally paused | Not started | — | — |
| **M2 — Primary comparison landed** | Month 5 | Six-day-arm data ingested; KT-939 vs thiamidol washout fits with CIs from ≥3 lines; scaffold-retention gate outcome recorded | Not started | — | — |
| **M3 — Production-up cycle measured** | Month 8 | 21-day arm plus at least one production-up on/off cycle (ampyrone or SIK) with free-compound accounting | Not started | — | — |
| **M4 — Optics v1 calibrated** | Month 10 | Inventory→appearance model reproduces published calibration spectra within stated tolerance; residuals documented | Not started | — | — |
| **M5 — Iris-cell foundation documented** | Month 12 | Native iris-melanocyte study registered or sourced-line decision recorded with cost | Not started | 2026-11-09: literature-first G5 sweep complete — 7 primary studies registered; sourcing note drafted (`research/iris-cell-sourcing-note.md`); no commercial iris stromal melanocyte line exists; Option A (registered evidence) vs Option B (academic/eye-bank isolation) pending owner decision. | — |
| **M6 — Integrated verdict v2** | Month 14–15 | Bidirectional feasibility verdict published in-repo; all five branches re-ranked on data; go/no-go for any pre-ocular phase recorded | Not started | 2026-11-10: G7 verdict v2 thresholds pre-proposed by agent in `research/feasibility-verdict-v2.md`; owner confirmation pending before M6 review. No go/no-go decisions recorded. | — |

**Slippage rule:** A milestone that slips two consecutive reviews triggers a scope decision (drop a feature, narrow a phase, or pause), recorded below — never a silent extension.

---

## 2. Budget envelope

| Phase | Planning estimate | Actual quote received | Quote source | Committed spend | Variance | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Phase 0 — Groundwork | $0–100 | — | — | — | — | Agent/API costs only |
| Phase 1 — Feasibility gates | $8k–30k | — | — | — | — | Method development and validation at core-facility rates; separately quoted first stage |
| Phase 2 — Paired washout matrix | $20k–75k | — | — | — | — | Scales with arms × timepoints × donors; KT-939/thiamidol pairing lands first |
| Phase 3 — Optics module | $0–500 compute; $5k–20k if donor-eye | — | — | — | — | Donor-eye range reflects tissue-acquisition and analysis variance |
| Phase 4 — Iris-cell foundation | $1k–5k or $0 | — | — | — | — | Literature-first policy |
| Contingency | +25–30% | — | — | — | — | Standard for planning-grade estimates |

*Stages are severable: each phase produces standalone value, and the program is designed to pause cleanly at any gate if budget or interest ends.*

---

## 3. Quote-and-spend log

| Date | Vendor / facility | Item / service | Quote amount | Currency | Quote expiry | Decision (accepted / declined / pending) | Commitment date | Amount spent to date | Invoice reference | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| — | — | — | — | — | — | — | — | — | — | — |

---

## 4. Go / no-go review record

| Phase | Review date | Go / No-go / Pause | Owner initials | Criteria checked (yes/no) | Reason if no-go | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| Phase 0 exit | — | — | — | — | — | — |
| Phase 1 exit | — | — | — | — | — | — |
| Phase 2 exit | — | — | — | — | — | — |
| Phase 3 exit | — | — | — | — | — | — |
| Phase 4 exit | — | — | — | — | — | — |
| Phase 5 exit | — | — | — | — | — | — |

*Exit gates (from expansion plan):*
- *Phase 0:* Quotes requested from at least two facilities; S0.1 rows verified in the register.
- *Phase 1:* Each of the three gates documented pass/fail with numbers; revised protocol committed.
- *Phase 2:* G1 delivered — comparative washout fits with CIs; scaffold-retention gate answered with data.
- *Phase 3:* G3 delivered — calibration residuals stated; limitations documented.
- *Phase 4:* G5 delivered — either registered evidence or a sourced-line decision recorded.
- *Phase 5:* G7 delivered — verdict doc with every re-ranking traceable to a dataset or registered source.

**Slippage rule reminder:** A milestone that slips two consecutive reviews triggers a scope decision (drop, narrow, or pause), recorded here — never a silent extension.

---

## 5. Phase 0 immediate owner actions

| Action | Owner | Status | Target date | Notes |
| --- | --- | --- | --- | --- |
| Send quote requests to ≥2 academic core facilities | Owner | Pending owner action | This week | Shortlist: `research/core-facility-shortlist.md`. RFQ package (`research/core-facility-quote-request.md`, commit 4aa88ce) ready to attach. Quote requests NOT yet sent. |
| Open budget ledger (this document) | Owner | Pending owner action | This week | — |
| Set milestone review cadence | Owner | Pending owner action | This week | Roughly weekly during active phases; monthly between phases |
| Decide Phase-1 budget ceiling and record it here | Owner | Pending owner action | This month | Ceiling limits committed spend; quotes may reveal a narrower feasible band |

---

## 6. Document control

| Date | Change | Author |
| --- | --- | --- |
| November 9, 2026 | Initial draft created from expansion-plan.md Feature F6 | AI-assisted, owner-reviewed |
| 2026-11-09 | M0 agent-side groundwork recorded as complete; shortlist and protocol ladder updates noted | AI agent (owner review pending) |
| 2026-11-10 | G7 feasibility-verdict-v2.md thresholds pre-proposed by agent; owner confirmation pending before M6 review | AI-assisted (thresholds) |
| 2026-11-09 | M5 notes: G5 literature sweep and sourcing options recorded; KT-939 washout fit and optics v1 runs added to analysis | AI agent (owner review pending) |
| 2026-11-10 | Reduced-matrix option prepared by agent (`research/rfq-reduced-matrix-option.md`) citing simulation run `analysis/washout-design-simulation-run-2026-11-10`; owner decision pending before any contract or spend | AI agent (owner review pending) |

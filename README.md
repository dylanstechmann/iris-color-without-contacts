# Reversible cosmetic iris pigmentation through drugs

A theoretical research project about cosmetic iris-color change without contacts or surgery. The lead question is whether sustained, reversible drug modulation of melanin production could gradually lighten an iris over months or years, and permit repigmentation after stopping.

The earlier bidirectional goal remains: **blue → dark brown → the same person's original blue**. Lightening a naturally brown iris and reversing a drug-induced darkening are related questions with potentially different kinetics.

## Latest completed exploration

The optics model melanin spectral shapes now use pinned measured Sarna & Swartz 1988 extinction coefficients (see [analysis/optics-v1-measured-melanin-run-2026-11-09/](analysis/optics-v1-measured-melanin-run-2026-11-09/) and [analysis/hue-window-measured-melanin-run-2026-11-09/](analysis/hue-window-measured-melanin-run-2026-11-09/)). The qualitative finding from the hue-window re-run is unchanged versus the earlier power-law assumption: orange and purple CIELAB windows remain unreachable over a dark pigment-epithelium back, and a strong translucent-red back return is still required.

The [KT-939 and thiamidol comparison](analysis/kt939-thiamidol-comparison.md) now extracts paired measurements from one study and checks the compounds' related structures. KT-939 has a lower reported IC50 in both the lysate and six-day cell-pigment assays. Its withdrawal study has no thiamidol arm, so comparative recovery remains unresolved. The comparison adds reproducible tables, a figure and source hashes. The earlier [withdrawal analysis](analysis/withdrawal-and-recovery.md) explains why pigment recovery alone cannot identify drug washout or old-pigment loss; the [mechanism shortlist](research/mechanism-shortlist.md) connects these findings to the reversible-color goal.

The November 9, 2026 mechanism-shortlist refresh swept all five prioritized branches for new or missed evidence, verified every added citation against publisher or PubMed records, and appended twenty rows to the [pigment evidence register](research/pigment-evidence-register.md). The sweep confirms the paired KT-939/thiamidol exposure-and-withdrawal study does not exist in the accessible literature, and elevates melanosomal pH (OCA2–TPC2) as the strongest alternative production controller after new digenic-genetics, small-molecule, human-cell, and ocular-phenotype evidence.

## Current research direction

Start with **pigment production, pigment persistence, and optics**. Build explicit hypotheses, calculate their consequences, and use targeted searches to check the assumptions that matter most. Slow change and maintenance over years are within scope.

The lead hypothesis is simple: reduce new melanin production while existing pigment undergoes net loss. That can lower the pigment inventory without replacing cells. It depends on loss continuing at a useful rate. A persistent pigment fraction, incomplete suppression, or a different optical response could limit the change.

The [reasoning and drug-modulation note](research/chronic-pharmacologic-modulation.md) contains:

- foundations, assumptions, and alternative mechanism combinations;
- hypothetical models for synthesis, pigment loss, persistent stores, and withdrawal;
- specific questions and search strings for each missing link;
- existing drug evidence as checks on those premises.

The models do not predict a seven-year biological renewal interval or a compulsory brown → green → blue sequence. Drug activity, color change, and recovery may follow different timescales.

## Next

Seek paired KT-939/thiamidol exposure and withdrawal observations in one human pigment-cell system, with free active compound, target activity and cell-population accounting. The November 9, 2026 sweep confirms no such study exists yet; new 2024–2026 analog work adds potency, not withdrawal data. Ampyrone still has no washout experiment anywhere, and its enzyme-product identity question stands, while SIK inhibitors and forskolin supply measured reversible production-up precedent in mice. The OCA2–TPC2 branch gained bidirectional small-molecule control and a human ocular phenotype, making TPC2 modulators named candidates for the same paired exposure/withdrawal design. Their structural difference motivates measuring retention; calculated properties do not establish it. Pair new synthesis with stored-pigment tracking before fitting recovery rates. The [identifiability calculation](analysis/withdrawal-and-recovery.md#which-added-observations-answer-which-question) explains which added observations are informative; the [analysis methods](analysis/README.md) document completed runs. A concrete proposed design for the paired series is drafted in the [paired exposure/withdrawal protocol](research/paired-exposure-withdrawal-protocol.md).

The primary cosmetic objective is repeatable living-eye appearance change with preserved function and recovery. A noninvasive color measure can track appearance; chemistry addresses pigment mechanisms. Archived records, cell models, donor-eye calibration, and automation are supporting options chosen for a defined question.

## Research map

- [Expansion plan](research/expansion-plan.md) — goals, phases, resources, budget ranges and milestones from evidence gaps to a bidirectional feasibility verdict.
- [Feasibility verdict v2 (skeleton)](research/feasibility-verdict-v2.md) — predeclared G7 re-ranking structure and go/no-go criteria; no verdicts recorded.
- [Milestone and budget ledger](research/milestone-budget-ledger.md) — living milestone tracker, quote-and-spend log, and go/no-go review record.
- [Mechanism shortlist](research/mechanism-shortlist.md) — current prioritization, completed computation and next discriminating questions.
- [Computational analysis](analysis/README.md) — reproducible models, human iris data checks and workbench runs.
- [Chronic drug modulation](research/chronic-pharmacologic-modulation.md) — lead track: foundations, hypothetical combinations, sensitivity models, and targeted questions.
- [Bidirectional iris reversibility](research/bidirectional-reversibility.md) — blue-to-brown-to-baseline goal and evidence requirements.
- [Paired exposure/withdrawal protocol](research/paired-exposure-withdrawal-protocol.md) — proposed discriminating cell study across the named candidates.
- [Optics-model specification](research/optics-model-specification.md) — inventory→appearance model architecture, calibration data requirements, and tolerances.
- [Pigment evidence register](research/pigment-evidence-register.md) — study models, outcomes, and limits.
- [Core-facility quote-request package](research/core-facility-quote-request.md) — RFQ package for the paired exposure/withdrawal study, with separately quoted feasibility gates.
- [Core-facility shortlist](research/core-facility-shortlist.md) — researched candidate facilities with confirmed/VERIFY capability markers, pending owner verification and contact.
- [Tissue pigment atlas](research/tissue-pigment-atlas.md) — broader background for eyes, skin, gums, hair, and other compartments.
- [Selective-clearance framework](research/selective-clearance-framework.md) — pigment-fate concepts across tissues.
- [Donor-eye measurement proposal](research/iris-measurement-validation-proposal.md) — optional optical/chemical calibration study.
- [Iris-cell sourcing note](research/iris-cell-sourcing-note.md) — G5 literature-first outcome: seven registered iris-melanocyte studies and the finding that no commercial iris stromal melanocyte line exists.
- [Automated lab concept](research/automated-lab-operating-model.md) — optional logistics and cost planning for tissue work.
- [Hair scope](research/hair-scope.md) — separate question for follicle pigmentation.
- [Sidequest: purple or orange human irises](research/sidequest-purple-orange-eyes.md) — hue question beyond the light-to-dark axis, with a toy CIELAB calculation; in that model melanin over a dark back reaches at best a dark orange-brown and never purple.

## Scope

Literature review and conceptual analysis for cosmetic pharmacology. The repository does not provide a treatment regimen or establish clinical suitability. Evidence from existing medicines, cell culture, animal studies, and patents is labeled by type.

*Latest focused comparison: October 22, 2026. Latest mechanism-shortlist refresh: November 9, 2026. Personal hobby and learning project; AI-assisted synthesis.*

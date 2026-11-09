# Iris-cell sourcing note: G5 literature-first sweep outcome

*2026-11-09. AI-assisted literature sweep and vendor search; owner-reviewed. Personal hobby/learning project document.*

## (i) Native iris-melanocyte evidence now registered

The Phase-4 literature-first sweep (2000–2026) added **7 verified primary-study rows** to the "Anterior iris and uveal melanocytes" table in `pigment-evidence-register.md`:

1. **Hu et al., 2000** — cultured human iridal melanocytes; prostaglandin A₂/E₁/F₂α and latanoprost pharmacology. PGA₂/E₁ stimulated melanogenesis; PGF₂α/latanoprost did not directly stimulate iridal melanocytes in monoculture.
2. **Hu et al., 2001** — cultured human iridal melanocytes; receptor-selective prostanoid agonist/antagonist pharmacology. EP₂ agonist and thromboxane mimetic stimulated melanogenesis; DP/IP/TP/EP₄ agonists did not.
3. **Stjernschantz et al., 2000** — monkey in vivo (in situ hybridization) plus human iridial melanocyte in vitro (Northern blot). Latanoprost increased tyrosinase transcription in monkey iridal melanocytes and in at least one human donor (heterochromic iris), but not in blue-iris melanocytes.
4. **Wentzel et al., 2003** — cultivated human iridial melanocytes from blue/hazel eyes; RT-PCR survey of prostanoid receptor and COX genes. FP most consistently transcribed; DP/EP2/TP absent. No transcriptional difference between latanoprost-treated and untreated donors.
5. **Li et al., 2006** — cultured human uveal (iridal + choroidal) melanocytes; α-MSH dose–response. **No** proliferation, melanin, or melanogenic-enzyme response to α-MSH; MC1-R not detectable. Negative result in pure culture contradicts the α-MSH responsiveness reported in Smith-Thomas et al., 2001 co-culture model.
6. **Sharif & Crider, 2011** — human iridial fibroblasts and melanocytes; intracellular signaling. HIM cells lacked functionally active FP receptors but expressed ETB and cAMP responses to PGE₂/isoproterenol. Supports FP-mediated pigmentation being fibroblast-dependent.
7. **Draper et al., 2026** — single-cell transcriptomic atlas of human **fetal** uveal tract (81,603 cells, 8 eyes, 12–20 PCW), including 5,142 melanocytes across four subpopulations. Developmental atlas, not adult iris; no drug-response or washout data.

**Negative findings (sweep reported as empty):**
- **Zero** primary studies report drug washout or withdrawal recovery in cultured human iris-derived melanocytes.
- **Zero** primary studies examine TPC2 or OCA2 channel/transporter function specifically in iris-derived melanocytes (all TPC2/OCA2 pharmacology to date uses skin/mouse melanoma or human epidermal melanocyte lines).
- **Zero** newer (2024–2026) adult human iris single-cell atlases with OCA2/TPCN2/TYR coverage beyond the fixed CZI 57,422-nucleus panel (Makovoz et al., 2025) already analyzed. The Draper 2026 atlas is fetal, not adult, and does not focus on OCA2/TPCN2/TYR machinery.

## (ii) Sourcing options found

### Commercial / vendor landscape

A systematic vendor search (ATCC, ScienCell, Innoprot, 3H Biomedical, AcceGen, Creative Bioarray, Cloud-Clone, Cells Online, Gentaur, AstralCell, CliniSciences) found **no commercial source of human iris stromal melanocytes**. The available products are:

| Product | Vendor examples | Price (approx.) | Notes |
| --- | --- | --- | --- |
| Human Iris Pigment Epithelial Cells (HIPEpiC) | Innoprot | €920 / vial (5×10⁵ cells) | Posterior IPE, not anterior stromal melanocytes. Shares RPE-like properties (phagocytosis, trophic-factor secretion). |
| Human Iris Pigment Epithelial Cells (HIPEpiC) | 3H Biomedical | €2,981 / vial | Same as above; special-order item. |
| Human Iris Pigment Epithelial Cells (HIPEpiC) | ScienCell | ~$871 / vial (live); $273 pellet (5×10⁶ cells) | Same as above; passage-one cryopreserved. |
| Human Iris Pigment Epithelial Cells (HIPEpiC) | Cells Online | $1,425 / vial | Same as above. |
| Human Iris Pigment Epithelial Cells (HIPEpiC) | AcceGen / Creative Bioarray / Cloud-Clone / Gentaur / AstralCell | Quote on request | All are IPE; none are iris stromal melanocytes. |
| Human Iris Fibroblasts (HIrF) | Innoprot / ScienCell | €795 / $871 per vial | Stromal fibroblasts, not melanocytes. Useful for co-culture models (cf. Smith-Thomas et al., 2003/2004) but do not replace melanocytes. |
| Primary Epidermal / Dermal Melanocytes | ATCC (e.g., PCS-200-013, CRL-4059) | $641–$6,670 | Skin-derived, not iris. |

**Key sourcing gap:** Human anterior iris stromal melanocytes (the cells that determine visible iris color) are not offered by any surveyed commercial cell bank or vendor catalog ( searchable as of November 2026). The IPE cells that are sold are from the posterior pigmented epithelium, a different embryonic origin and functional compartment.

### Academic / non-commercial routes

- **Eye-bank primary isolation:** The canonical human uveal melanocyte isolation method (Hu et al., 1992–2001 series) uses postmortem donor eyes. This is the route used by most registered primary studies. The mechanism-shortlist notes the owner may need to contact eye banks for research tissue access.
- **Declared atlas extension:** The expansion-plan F3 calls for a declared extension of the fixed 57,422-nucleus atlas panel to OCA2/TPC2 machinery checks. Draper 2026 supplies fetal uveal melanocyte transcriptomes but does not replace an adult iris stromal panel. Performing this extension would require either:
  1. New scRNA-seq on primary iris stromal melanocytes isolated from donor tissue, or
  2. Collaboration with a lab already holding such cells (e.g., groups that published Hu, Smith-Thomas, Lindsey, or Makovoz atlas work).

## (iii) Recommendation on G5 decision

**Registered evidence now covers prostaglandin/cAMP/tyrosinase mechanistic pharmacology in human iridal melanocytes.** The new rows establish that:
- Iridal melanocyte monocultures respond to cAMP-elevating agents and specific EP agonists;
- Latanoprost’s direct effect on iridal melanocytes is minimal in monoculture but transcriptionally detectable in some donors;
- FP-receptor signaling appears fibroblast-dependent;
- α-MSH does not directly stimulate pure uveal melanocytes, implying co-culture/medium dependencies for that response.

**However, the OCA2/TPC2 machinery gap in iris cells remains entirely open.** No registered study examines melanosomal pH regulation or TPC2/OCA2 function in iris-derived melanocytes, and no washout data exist for any drug in this cell type. The fixed CZI atlas panel already has raw detection fractions for TYR, OCA2, OPTN, RCHY1 and TBK1 in adult iris nuclei, but an atlas extension checking OCA2/TPC2/TYR *machinery* (e.g., pharmacological TPC2 modulation followed by melanosomal pH/pigment readouts) requires a living iris-melanocyte system.

**Owner-decision input:**
- **Option A — "Registered evidence suffices for now":** Accept that the prostaglandin/cAMP branch now has a solid iridal-melanocyte literature foundation, and keep the OCA2/TPC2 iris-specific question on the backlog pending new publications or an academic collaboration. Cost: $0.
- **Option B — "Sourced line warranted":** Commission or collaborate on primary isolation of human iris stromal melanocytes from eye-bank donors, followed by the declared OCA2/TPC2/TYR extension assay. No commercial off-the-shelf product exists; this would require a custom academic core-facility or collaborator effort. Estimated cost range from the expansion plan: $1k–5k if a collaborator already has a line; substantially more if de novo isolation and characterization are required.

**Suggested leaning:** Option A is defensible for the immediate G5 milestone because primary iridal-melanocyte pharmacology is now registered. Option B becomes compelling only if the owner wants the OCA2/TPC2 branch to have iris-specific cellular data before a broader feasibility verdict. If Option B is chosen, the first step should be an academic inquiry to eye banks or to labs with existing iridal melanocyte cultures (e.g., authors of Hu, Smith-Thomas, Lindsey, or Makovoz papers), not a commercial purchase, because no vendor sells the required cell type.

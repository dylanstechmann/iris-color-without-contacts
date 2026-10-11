# Tissue pigment atlas: what exists and what remains theoretical

*Literature and official-source review: October 11, 2026. Personal learning project; AI-assisted synthesis.*

The broader research question is whether stored pigment can be reduced to a chosen level in a chosen tissue while preserving its cells and function. The original [reversible iris-color goal](bidirectional-reversibility.md) is one application. DNA editing is not a prerequisite: production, transfer, degradation, and excretion are distinct mechanisms to evaluate.

This atlas groups the major pigment-bearing compartments across the body. It is **not an exhaustive inventory of every cell type or every marketed treatment**. A coverage gap is labeled explicitly. Availability is described for the stated indication and jurisdiction; an experimental result is not a treatment listing.

## Reading the diagrams

| Label | Meaning |
| --- | --- |
| **C — Clinical** | Established clinical use or an official approval for a specified condition. This does not imply approval for general cosmetic use. |
| **H — Human research** | A human study, with its design and limitations stated. This may be a small trial, observational work, or a case report. |
| **P — Preclinical** | Cultured cells, isolated tissue, or animals. Human cells in a dish are still preclinical evidence. |
| **G — Gap** | The reviewed sources do not establish the requested selective, predictable capability. |
| **X — Procedure / comparison** | Surgery, ablation, injections, or another procedure; distinguished from noninvasive biological modulation. |

Solid arrows show an observed relationship, established biology, or an evidence classification. Dashed arrows show a proposed research transition. The diagrams are conceptual maps, not treatment pathways or protocols.

## 1. Body-wide overview

```mermaid
flowchart TD
    A["Pigment identity + tissue compartment"]
    A --> B["Skin, gums, hair and nails<br/>Melanin"]
    A --> C["Eye compartments<br/>Melanin and retinal bisretinoids"]
    A --> D["Brain and visceral cells<br/>Neuromelanin or lipofuscin"]
    A --> E["Disease-related deposits<br/>Iron, bilirubin or ochronotic pigment"]
    A --> F["Other coloration<br/>External pigments, tooth stains, blood"]
    A --> G["Inner ear / cochlea<br/>Strial melanin"]
    A --> H["Leptomeninges<br/>Melanin-bearing melanocytes"]
    A --> I["Heart / pulmonary veins<br/>DCT-positive melanocyte-like cells"]
    A --> J["Other mucosal surfaces<br/>Site-specific pigment"]
    A --> K["Adipose tissue<br/>carotenoids; candidate melanocyte progenitors"]
    B --> B1["Skin: C for specific disorders<br/>Gums: limited H<br/>Hair/nail biological control: G"]
    C --> C1["Iris reversal: G<br/>RPE clearance mechanisms: P"]
    D --> D1["Mechanistic studies: P / human tissue<br/>General selective clearance: G"]
    G --> G1["H tissue mapping; P mouse function data<br/>Selective reduction: G"]
    H --> H1["H normal anatomy / imaging<br/>Selective clearance: G"]
    I --> I1["H human cell identity; P mouse function data<br/>Pigment clearance: G"]
    J --> J1["Nasal / laryngeal: localized H findings<br/>Many mucosal sites remain gaps"]
    E --> E1["C for certain diagnosed diseases<br/>Different chemistry and mechanisms"]
    F --> F1["Separate targets and methods<br/>No universal pigment-clearing system established"]
```

### Comparison by tissue

| Tissue / compartment | Relevant pigment or color source | What is available or demonstrated | What remains unestablished |
| --- | --- | --- | --- |
| **Epidermal skin** | Melanin in melanocytes and keratinocytes | **C:** facial melasma treatment and vitiligo repigmentation; **C + X:** afamelanotide implant increases skin eumelanin for adult EPP. **P:** transfer modulation and melanosome degradation in cell/skin models; a 2026 human-keratinocyte model reported lower intracellular melanin absorbance after uptake of mouse melanoma-derived melanosomes. | A programmable healthy-skin shade cycle or selective removal of all stored melanin; the 2026 model does not establish an intact-tissue or human clearance route. |
| **Dermis** | Native melanin, tattoo ink, and deposited metals are different targets | **H:** ashy-dermatosis biopsies identify melanosome-retaining fibroblasts and macrophages. **X:** FDA-cleared tattoo-removal lasers; human biopsies document pigment fragmentation and cell injury. | Selective nonprocedural clearance of native melanin or proof that a deposit left the body. |
| **Gums** | Physiologic epithelial melanin, among other causes of discoloration | **H:** small topical ascorbic-acid trial; stronger early response in an injection comparison arm. **X:** epithelial depigmentation procedures. | A routinely established topical, selective, reversible gum-color controller. |
| **Lips and other oral mucosa** | Melanocytic and nonmelanocytic pigmentation | **H:** human pathology evidence identifies different causes and compartments. | Transfer of gum-study results to all oral surfaces or other mucosa. |
| **Hair follicles / hair shaft** | Pigment deposited during fiber growth | Marketed shaft dyes/bleaches exist; **P/H:** follicle biology and observational human repigmentation. | Selectable reversible control of living human follicles; clearing a shaft is different from changing future growth. |
| **Nail matrix / plate** | Melanin can be deposited into the nail plate | Human anatomy evidence; isolated procedural case reports for specific causes. | A validated general topical cosmetic modulator or stored-pigment clearance system. |
| **Anterior iris / stroma** | Melanin in stromal melanocytes plus tissue optics | Drug-associated darkening is documented; **X:** cosmetic photoablative laser cases report pigment dispersion and secondary glaucoma. | Controlled blue → brown → original blue; selective nondestructive clearance. |
| **Posterior iris pigment epithelium** | Dense pigment, chemically distinguishable from the stroma | Human anatomical and chemical mapping. | Selective cosmetic clearing; this is not interchangeable with the visible anterior target. |
| **Retinal pigment epithelium (RPE)** | Functional melanin plus lipofuscin/bisretinoids | **P:** reduction of selected bisretinoids and model-specific lipofuscin degradation. | General human retinal pigment clearance or cosmetic iris-color application. |
| **Choroid / ciliary body** | Uveal melanocytes and pigmented epithelial compartments | Human/anatomical mapping. | A demonstrated selective cosmetic clearing method in the reviewed sources. |
| **Inner ear / cochlea** | Melanin in stria-vascularis intermediate melanocytes and Rosenthal's canal | **H:** human temporal-bone mapping. **P:** matched pigmented/albino mice show an age-related endocochlear-potential difference. | Selective pigment reduction with preserved cochlear homeostasis or hearing; human pigment amount was not associated with thresholds in the studied sample. |
| **Conjunctiva / episclera** | Surface or deeper melanocytic lesions and other deposits | Human clinical/pathological evidence; a postburn laser case report. | A general reversible molecular color modulator. |
| **Brain neurons** | Neuromelanin; lipofuscin is a separate residual-material class | Human tissue studies characterize neuromelanin organelles. | Safe selective clinical clearance, preservation of bound substances, or a cosmetic application. |
| **Leptomeninges** | Melanin in non-neuronal meningeal melanocytes | **H:** human histology places most cells over the ventrolateral medulla; normal pigment can be visible on T2 MRI. | Selective removal, safe disposition, or extrapolation to neuronal neuromelanin. |
| **Heart / liver / adrenal cells** | Lipofuscin | Human tissue studies document accumulation; **P:** cardiac clearance research in old rats. | A selective human visceral lipofuscin-removal treatment demonstrated by this source set. |
| **Heart / pulmonary-vein melanocyte-like cells** | Human DCT-positive cells; cardiac melanosomes demonstrated in mice | **H:** melanocyte-like cells identified in human atria and pulmonary veins. **P:** mouse cell/pathway models show rhythm effects with DCT deficiency or cell loss. | A quantified human cardiac melanin store, causal link between pigment amount and human arrhythmia, or any clearance method. |
| **Liver Kupffer cells (tattoo-ink comparison)** | Exogenous tattoo particles, separate from endogenous liver pigments | **P:** a one-year mouse study detected black/red tattoo particles in Kupffer cells; other sampled internal organs were negative by light microscopy. | Human internal-organ distribution, whole-body elimination, or an endogenous pigment-clearance route. |
| **Draining lymph nodes (tattoo ink)** | Exogenous ink particles in phagocytes, separate from endogenous pigment | **H:** postmortem human skin/node study and human node biopsies document ink; **P:** human-cell macrophage and mouse studies show possible cell injury/inflammation. | Human clinical consequences, safe whole-body elimination, or relevance to endogenous melanin. |
| **Liver / heart / pancreas and other iron-overload sites** | Excess stored iron, including ferritin/hemosiderin pools | **C:** iron depletion or chelation for diagnosed overload. | Arbitrary tissue-by-tissue cosmetic targeting or guaranteed reversal of prior damage. |
| **Cartilage / connective tissue in alkaptonuria** | Homogentisic-acid-derived ochronotic pigment | **C/H:** precursor lowering, slower disease progression, and partial pigment regression in human studies. | Complete clearing of every deposit or a mechanism transferable to normal melanin. |
| **Skin / mucosa / whites of eyes in jaundice** | Excess bilirubin | Cause-specific clinical management. | A melanosome-based explanation or an iris-color treatment. |
| **Teeth** | Extrinsic stains and intrinsic chromogens | Dental cleaning/whitening methods exist. | Evidence that tooth whitening demonstrates clearance of living-tissue melanin. |
| **Skeletal muscle** | Age-associated lipofuscin | **H:** human muscle biopsies identify lipofuscin as an aging-associated pigment. | Selective clearance of native muscle lipofuscin while preserving function. |
| **Adipose tissue** | Dietary carotenoids; possible melanocyte-lineage progenitors are a separate question | **H:** carotenoids measured in healthy human fat; concentrations vary by anatomical site and correlate with diet. **P:** human adipose-derived cells expressed melanocyte markers and formed melanin in a UVB-exposed 3D epidermal model after culture/differentiation. | The cell-culture result does not establish a melanin store in intact adipose tissue, or a tissue-selective clearance route. |
| **Bone** | Bone-associated iron in overload; marrow hemosiderin is a separate compartment | **H:** stainable iron at the bone surface is uncommon in routine biopsies and more frequent in verified iron overload. | Selective removal of bone-associated pigment; other bone deposits need separate review. |
| **Tendon** | Ochronotic homogentisic-acid-derived pigment in alkaptonuria | **H:** human case reports document pigmented, damaged tendons; disease-directed precursor lowering does not establish tendon-specific reversal. | Targeted clearance of established tendon pigment. |
| **Pancreatic islets** | Lipofuscin in insulin-producing β-cells; age-associated residual material | **H:** electron-microscopy morphometry of human donors finds age-correlated lipofuscin and supports long β-cell lifespan. | Clearance or selective β-cell pigment reduction with preserved insulin function. |
| **Kidney tubules** | Lipofuscin in proximal tubular epithelial cells | **H:** one incidental human biopsy with ultrastructural confirmation; case-level observation. | General prevalence, tissue-selective clearance, and functional outcomes. |
| **Spleen** | Ferritin and hemosiderin iron stores; lipofuscin reports are a separate target | **H:** iron-storage material characterized in spleens from patients with transfusion-related secondary overload. | Selective splenic clearance independent of systemic iron management. |
| **Airways / lung-draining lymph nodes** | Inhaled carbon and other particles within macrophages | **H:** human bronchoscopy, biopsy, and node studies document anthracotic macrophages. | Safe selective extraction; visible deposits do not measure the full particle burden or associated fibrosis. |
| **Colon mucosa** | Lipofuscin-like pigment in lamina-propria macrophages in melanosis coli; the name does not mean ordinary melanin | **H:** human histology identifies pigment-laden macrophages; observational cases document endoscopic disappearance after the inducing anthraquinone exposure ends. | Direct pigment mass/export after resolution, a selective intervention, or transfer to other pigments and organs. |
| **Esophageal mucosa** | Rare melanocytic proliferation with melanin deposition in squamous mucosa | **H:** human case reports/series document esophageal melanocytosis and distinguish it from melanoma. | Natural history, selective clearance, or generalization to other mucosal surfaces. |
| **Other mucosa** | Site-specific melanin in melanocytes or epithelial cells; many different surfaces | **H:** oral, nasal, laryngeal, vulvar, cervical, anorectal, and rare esophageal findings have been described, but study designs and compartments differ. | No selective clearance assessment; normal vaginal distribution and many other mucosal sites remain underassessed. |

### Additional tissues contain different pigment targets

```mermaid
flowchart LR
    M["Skeletal muscle"] --> ML["H: age-associated lipofuscin<br/>observed in human muscle"]
    A["Adipose tissue"] --> AC["H: dietary carotenoids measured;<br/>concentrations vary by site"]
    B["Bone"] --> BI["H: stainable iron is more evident<br/>in iron-overload cases"]
    T["Tendon"] --> TO["H: ochronotic pigment<br/>documented in alkaptonuria"]
    ML -.-> G["G: general, tissue-selective<br/>cosmetic clearance"]
    AC -.-> G
    BI -.-> G
    TO -.-> G
```

These findings identify different stored materials, not a shared pigment pool: lipofuscin, carotenoids, iron, and ochronotic polymer need separate measurement and disposition models. Clinical management of diagnosed iron overload or alkaptonuria is disease-directed; it does not establish cosmetic, tissue-specific clearance. [Human muscle study](https://pubmed.ncbi.nlm.nih.gov/17376148/), [human adipose carotenoid study](https://pubmed.ncbi.nlm.nih.gov/19587090/), [human bone iron study](https://pubmed.ncbi.nlm.nih.gov/3282446/), [Achilles tendon ochronosis case report](https://pubmed.ncbi.nlm.nih.gov/39027761/).

### Pancreas, kidney, spleen, and airways: distinct internal deposits

```mermaid
flowchart LR
    P["Pancreatic beta cells"] --> PL["H: age-associated<br/>lipofuscin in human islets"]
    K["Proximal kidney tubules"] --> KL["H: lipofuscin in<br/>one human biopsy"]
    S["Spleen in transfusion-related overload"] --> SI["H: ferritin and hemosiderin<br/>characterized in human samples"]
    A["Airways and draining nodes"] --> AP["H: inhaled particles<br/>inside macrophages"]
    PL -.-> G["G: selective, function-preserving<br/>cosmetic clearance"]
    KL -.-> G
    SI -.-> G
    AP -.-> G
```

These observations represent different substrates and evidence strengths. Human beta-cell lipofuscin is an age-associated intracellular residue, and the human study used morphometry to estimate cell longevity; it did not test clearance. The kidney finding is an incidental, single-biopsy observation. Splenic ferritin and hemosiderin were characterized in patients with transfusion-related iron overload. Anthracotic carbon is inhaled particulate material in macrophages, not endogenous melanin. None establishes a general-purpose pigment-removal route. [Cnop et al., 2010](https://pubmed.ncbi.nlm.nih.gov/19855953/), [human kidney biopsy report](https://pmc.ncbi.nlm.nih.gov/articles/PMC11093538/), [Weir et al., 1985](https://pubmed.ncbi.nlm.nih.gov/4031104/), [human nodal anthracosis case series](https://pmc.ncbi.nlm.nih.gov/articles/PMC3920429/), [NEJM bronchial case](https://www.nejm.org/doi/full/10.1056/NEJMicm2516602).

### Colon mucosa: a natural-history example with limits

```mermaid
flowchart LR
    X["Anthraquinone exposure"] --> A["H: apoptotic epithelial bodies<br/>in human biopsies"]
    A --> M["H: pigment-laden macrophages<br/>in lamina propria"]
    M --> P["H: lipofuscin identified<br/>in a histopathology study"]
    P --> C["Visible melanosis-coli<br/>appearance on colonoscopy"]
    X -.-> S["Exposure cessation"]
    S -.-> R["H: endoscopic disappearance<br/>reported in selected cases"]
    R -.-> G["G: pigment mass, cell fate,<br/>and net export not measured"]
```

The condition's name is misleading for this project: a human histopathology study identified the colonic macrophage pigment as lipofuscin, not melanin. A retrospective colonoscopy review identified 10 disappearance cases among 216 melanosis-coli cases; 4 of the 10 had stopped anthranoid use before disappearance was observed. A separate single-patient report documented endoscopic disappearance seven months after senna cessation, without follow-up biopsy to measure the pigment or trace its fate. This is evidence of cause-associated appearance resolution in one colonic condition, not proof of a selective pigment-clearing mechanism or a result transferable to iris, skin, or other pigments. [Human histopathology study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4581826/), [longitudinal clinical course study](https://pubmed.ncbi.nlm.nih.gov/36849146/), [single-case endoscopic follow-up](https://pmc.ncbi.nlm.nih.gov/articles/PMC11402352/).

Sources and model details are linked in the sections below and in the [evidence register](pigment-evidence-register.md). The shared criteria for evaluating a tissue-specific clearance claim are in the [selective clearance framework](selective-clearance-framework.md).

### Cell renewal is not the same measurement as pigment clearance

```mermaid
flowchart LR
    subgraph surfaces["Renewing epithelial surfaces"]
        Skin["Skin epidermis"] --> SkinEvidence["H: melanin measured in outer<br/>stratum corneum / corneocytes"]
        Skin --> SkinProxy["H: UVA-pigment fading proxy<br/>small human study, n = 6"]
        Oral["Gingiva / buccal mucosa"] --> OralEvidence["H: melanin in gingival keratinocytes;<br/>oral proliferation is site-dependent"]
    end
    subgraph iris["Adult iris"]
        Iris["Adult iris tissue"] --> IrisEvidence["H: no PCNA / Ki-67-positive nuclei<br/>in examined adult samples"]
    end
    SkinEvidence -.-> SkinGap
    SkinProxy -.-> SkinGap["G: complete source-to-surface mass balance<br/>or selective clearance controller"]
    OralEvidence -.-> OralGap["G: pigment in shed oral cells<br/>not quantified"]
    IrisEvidence -.-> IrisGap["G: long-term iris pigment fate<br/>and return route"]
```

Cell renewal can carry pigment-bearing cells out of a surface layer, but calling that selective pigment clearance remains an inference. Human studies have imaged melanin granules in superficial corneocytes and chemically quantified eumelanin and pheomelanin in tape-sampled outer stratum corneum. This establishes a measurable pigment pool at the skin surface, compatible with epidermal desquamation, but does not provide a complete source-to-surface mass balance for native pigment or demonstrate a selective-clearance intervention. A separate six-person human study used fading of UVA-induced forearm pigmentation as an epidermal-turnover proxy. Normal human gingiva ultrastructure identified melanin granules in keratinocytes, and oral biopsies showed site-dependent epithelial S-phase labeling; neither tracked pigment into exfoliated oral cells. A human iris histology study found no PCNA- or Ki-67-positive nuclei in the adult iris samples examined; this is a snapshot, not proof of zero lifetime turnover or a pigment-export route. [Lu et al., 1996](https://pubmed.ncbi.nlm.nih.gov/8881670/), [Matsunaka et al., 2017](https://doi.org/10.1111/srt.12309), [Maeda, 2017](https://www.mdpi.com/2079-9284/4/4/47), [Squier and Waterhouse, 1967](https://doi.org/10.1016/0003-9969(67)90148-3), [Thomson et al., 1999](https://pubmed.ncbi.nlm.nih.gov/10577752/), [Thomson et al., 2001](https://pubmed.ncbi.nlm.nih.gov/11684035/), [Pfeiffer et al., 2001](https://jamanetwork.com/journals/jamaophthalmology/fullarticle/265260).

## 2. Skin: production, transfer, clearance, and repigmentation

```mermaid
flowchart TD
    M["Melanocyte makes melanin"] --> O["Melanosomes"]
    O --> K["Transfer to keratinocytes"]
    K --> V["Visible epidermal pigmentation"]
    M --> C["C: synthesis modulation in<br/>specified pigmentation disorders"]
    M --> E["C + X: afamelanotide implant<br/>increases skin eumelanin for adult EPP"]
    E --> E2["Disease-specific photoprotection<br/>not cosmetic or reversible shade control"]
    K --> T["P + H: transfer modulation<br/>mechanistic and human appearance endpoints"]
    O --> P["P: melanosome degradation<br/>in human cells / 3D skin equivalents"]
    P -.-> R["G: controlled stored-melanin clearance<br/>in intact healthy human tissue"]
    D["Vitiligo-associated pigment loss"] --> I["C: disease-specific repigmentation"]
    I -.-> W["G: arbitrary healthy-skin<br/>increase / decrease / baseline cycle"]
```

TRI-LUMA is a prescription combination for short-term moderate-to-severe **facial melasma**; its label identifies hydroquinone as a synthesis inhibitor. That indication does not cover every tissue or every form of pigmentation. Ruxolitinib cream has a separate FDA approval for nonsegmental vitiligo. These clinical examples address particular disorders. [Melasma label](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=a35fa709-5eb5-4429-b38f-f1e0019bf0ee), [vitiligo approval](https://www.fda.gov/drugs/news-events-human-drugs/fda-approves-topical-treatment-addressing-repigmentation-vitiligo-patients-aged-12-and-older). For an increase in skin pigmentation, afamelanotide (SCENESSE) is an FDA-labeled MC1-R agonist for increasing pain-free light exposure in adults with erythropoietic protoporphyria; the EMA describes its action as stimulating skin eumelanin. It is administered as a subcutaneous implant by a trained clinician. This is a disease-specific, procedural skin example, not cosmetic use, iris selectivity, a chosen shade, or a reversible color cycle. [Current U.S. label](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=94f53286-11dd-7fbb-e053-2a95a90a7c48&version=11), [EMA assessment](https://www.ema.europa.eu/en/medicines/human/EPAR/scenesse).

A primary niacinamide study combined transfer experiments with human facial-pigmentation outcomes. Separately, human skin-cell cultures showed autophagy-associated melanosome degradation and lighter cell pellets. The 2024 melanophagy study identified selective melanosome-autophagy machinery, mainly in a mouse melanoma-cell model; the same effect was not reproduced in its transferred-melanosome keratinocyte model. This makes cell compartment an evidence requirement. [Transfer study](https://pubmed.ncbi.nlm.nih.gov/12100180/), [human-cell degradation study](https://doi.org/10.1111/pcmr.12838), [melanophagy study](https://pmc.ncbi.nlm.nih.gov/articles/PMC10998605/). A 2025 preclinical study also reported reduced melanin accumulation and increased autophagy in normal human melanocytes and 3D MelanoDerm skin equivalents; mechanistic work also used melanoma cells. The work was industry-sponsored and did not test a treatment in people. [Geyfman et al., 2025](https://pubmed.ncbi.nlm.nih.gov/39305105/).

```mermaid
flowchart TD
    B["B16 mouse melanoma cells"] --> F["Isolated melanosome-enriched fraction"]
    F --> K["P: loaded into normal human epidermal keratinocytes"]
    K --> H["Hydrolyzed conchiolin protein treatment<br/>lowered cell-normalized melanin absorbance at 72 h"]
    H --> M["Authors' proposed sequence:<br/>lysosomal proteolysis → oxidative modification"]
    X["Separate cell-free chemical model"] --> R["Hydroxyl-radical conditions<br/>reduced melanin absorbance"]
    M --> L["P: no intact skin, iris, or human treatment;<br/>no metabolite or export mass balance"]
    R --> L
    L --> G["G: tissue-selective, function-preserving<br/>pigment clearance remains unestablished"]
```

A 2026 in-vitro study loaded normal human epidermal keratinocytes with melanosome-enriched fractions isolated from B16 mouse melanoma cells. Hydrolyzed conchiolin protein (HCP) treatment lowered cell-normalized intracellular melanin absorbance after 72 hours, and the authors proposed lysosomal proteolysis followed by hydroxyl-radical oxidative modification. A separate cell-free oxidation system also reduced absorbance. The experiment isolates post-transfer pigment handling, but it did not test intact skin or a person, identify breakdown products, or account for pigment export; lower optical absorbance does not provide a whole-tissue mass balance. The paper also reports opposite pH directions in its results and discussion, leaving that aspect of the mechanism unresolved. It was funded by Osman Biological Co. These findings are a preclinical human-cell foothold, not evidence of safe cosmetic skin treatment or a transferable iris mechanism. [Zhao et al., 2026](https://doi.org/10.1111/jocd.70770).

**Measurement distinction:** degradation of melanosome-associated proteins can occur without a reduction in melanin itself, as a mouse keratinocyte study demonstrated. A lower organelle-marker signal alone cannot establish pigment clearance. [Primary study](https://pmc.ncbi.nlm.nih.gov/articles/PMC10739166/).

**Appearance versus pigment mass:** In a small human in-situ comparison designed to produce comparable visible tanning, UVA alone did not significantly increase measured melanin, whereas UVB-containing exposures did. This shows that visible skin color can change without a corresponding increase in pigment mass. It is skin-specific evidence; it does not establish the same optical mechanism or a clearance route in the iris. [Choi et al., 2010](https://pubmed.ncbi.nlm.nih.gov/20147966/).

**Critical storage context:** cultured human keratinocytes show donor-dependent melanosome turnover, and autophagy manipulation changed measured melanin in cultured and ex-vivo human skin models. Other cultured-cell uptake studies and human skin electron microscopy found melanin in compartments that were not highly acidic or degradative. This is context-dependent evidence, not a settled universal clearance route. In human skin explants, supranuclear melanin caps correlated with fewer UV-induced DNA photoproducts; an experimental melanocore-disruption model found weaker protection from disrupted cores. Thus a color change alone would not establish safe, selective clearance. [Donor-dependent turnover](https://pubmed.ncbi.nlm.nih.gov/21326292/), [ex-vivo skin model](https://doi.org/10.1038/jid.2013.165), [nondegradative compartments](https://pubmed.ncbi.nlm.nih.gov/29074272/), [in-situ human skin](https://pubmed.ncbi.nlm.nih.gov/29054596/), [human skin explants](https://pubmed.ncbi.nlm.nih.gov/9579550/), [melanocore model](https://pmc.ncbi.nlm.nih.gov/articles/PMC6056223/).

A 2026 human-biopsy study of 14 people with ashy dermatosis found greater melanosome uptake in dermal fibroblasts than in macrophages. In a seven-case marker subset, increased macrophage p62 was interpreted as evidence consistent with impaired autophagic degradation. This disease-specific pathology suggests that persistent dermal melanosomes can involve multiple cell types; it does not establish a treatment or generalize to normal dermis. [Hada et al., 2026](https://pubmed.ncbi.nlm.nih.gov/42410740/).

### Dermal pigment procedures: local fading and body fate are separate

```mermaid
flowchart LR
    T["Tattoo ink in dermal cells"] --> X["X: pulsed laser"]
    X --> F["H: particles fragment;<br/>pigment-cell injury and inflammation"]
    F --> R["H: tattoo pigment again intracellular<br/>11 days after exposure"]
    D["Tattoo pigment removed by dermabrasion"] --> N["H: pigment present in regional<br/>lymph nodes three years later"]
    H["Human postmortem samples"] --> N2["H: matching tattoo pigments in skin and nodes<br/>in 2 of 4 tattooed donors"]
    N2 -.-> P2["P: macrophage apoptosis in human-cell culture<br/>and inflammation in mouse nodes"]
    P2 -.-> G
    P["P: mouse tattoo-ink study"] --> L["Ink particles in liver Kupffer cells<br/>after one year"]
    L -.-> G
    A["Silver deposits in argyria"] --> Y["X: laser in one human case"]
    Y --> S["H: smaller particles and lower<br/>silver signal in treated-skin biopsy"]
    S --> M["H: silver also found<br/>inside macrophages"]
    S -.-> G["G: no whole-body balance<br/>or excretion measured"]
    N -.-> G
    R -.-> G
```

Human tattoo biopsies show that laser-associated lightening can involve disruption of pigment-containing cells, smaller particles, and inflammation; pigment was again intracellular 11 days later. A postmortem human tissue study detected matching tattoo-pigment species in skin and regional nodes in two of four tattooed donors. A separate human case found tattoo pigment in regional lymph nodes three years after the tattoo had been removed by dermabrasion; surface removal therefore did not ensure pigment left the body. A 2026 pathology review of 90 lymph nodes already selected for tattoo-ink deposition found no unifying histologic pattern beyond the ink; 11 specimens came from patients with hematologic neoplasms, but this selected series cannot estimate risk or establish causation. These human findings are small-sample or case evidence and concern ink, not melanin. [Human tattoo biopsy study](https://doi.org/10.1111/1523-1747.ep12478570), [human skin-and-node study](https://doi.org/10.1038/s41598-017-11721-z), [regional lymph-node case](https://pubmed.ncbi.nlm.nih.gov/32650854/).

A separate one-year mouse biodistribution study detected tattoo particles in liver Kupffer cells; it did not detect particles in other sampled internal organs by light microscopy. This is preclinical distribution evidence, not human pharmacokinetics or clearance. [Sepehri et al., 2017](https://pubmed.ncbi.nlm.nih.gov/28486229/).

A 2025 study found persistent inflammation in mouse draining lymph nodes after tattooing and macrophage apoptosis in both mouse experiments and human monocyte-derived macrophage culture; it also reported vaccine-specific immune effects in mice. A 2026 letter questioned how closely the extensive mouse-footpad exposure represents ordinary tattooing. The authors replied that human macrophage and lymph-node observations support mechanistic relevance but agreed clinical effects need further study. This is a preclinical signal about heterogeneous foreign inks, not evidence that native melanin clearance would have the same effects. [Capucetti et al., 2025](https://doi.org/10.1073/pnas.2510392122), [Kluger, 2026](https://doi.org/10.1073/pnas.2611211123), [Gonzalez reply, 2026](https://doi.org/10.1073/pnas.2613440123).

A single generalized-argyria case provides stronger local tissue measurements: after laser treatment, a treated-skin biopsy showed smaller silver-containing particles and markedly lower silver signals, while some residual silver was found in macrophages and on elastic fibers. The authors proposed partial macrophage clearance; the patient had long-lasting visible improvement, but no whole-body silver accounting. It is a metal-deposit case report using a procedure, not evidence for melanin or iris reversal. [Fukayama et al., 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC9309704/). A separate human case reported recurrence after Q-switched laser treatment. The 2020 authors proposed that ultraviolet exposure might re-darken residual silver through a chemical-state change, but this explanation remains speculative; it illustrates that visible color can shift while metal remains. [Krase et al., 2017](https://pubmed.ncbi.nlm.nih.gov/28296792/).

## 3. Gums and oral mucosa

```mermaid
flowchart TD
    A["Oral color / pigmentation"] --> B["Physiologic gingival melanin"]
    A --> C["Other causes<br/>Inflammation, drugs, external deposits or lesions"]
    B --> V["H: oral melanin detection varies<br/>among six sampled sites"]
    V --> X["Do not generalize gum findings<br/>to every oral mucosa"]
    B --> T["H: topical ascorbic-acid gel alone<br/>small trial; clinical index not significant at 1 month"]
    T -.-> G["G: predictable topical-only<br/>selective pigment clearance"]
    B --> I["H + X: intramucosal injections<br/>Invasive despite nonsurgical terminology"]
    B --> L["H + X: 2026 trial, n = 20<br/>topical AS-G added after diode laser"]
    L --> D9["9-month clinical pigmentation score<br/>favored adjunct; laser in both groups"]
    D9 -.-> C9["Repigmentation/follow-up appearance<br/>not a pigment-mass or export measure"]
    B --> S["X: scalpel / ablative laser<br/>Pigmented epithelium removed"]
    S --> R["Healing and possible repigmentation"]
    C --> O["Cause-specific assessment<br/>Not automatically a melanin-clearance target"]
```

In a 20-person randomized study, topical ascorbic-acid gel alone did not significantly improve the pigmentation index at one month, whereas the injection arm had an earlier response; both groups showed lower melanin-stained area fraction at six months. The study was small and had no placebo arm. A 2026 randomized study of 20 participants found a lower nine-month clinical pigmentation score when topical ascorbyl glucoside was added after diode-laser depigmentation than after laser alone. Both arms received laser, and the study assessed a clinical score rather than pigment mass or fate. It therefore does not establish topical-only depigmentation or a pigment-export route. These are **human-research** findings, not proof of a routinely available, predictable gum-color controller. [El-Mofty et al.](https://pubmed.ncbi.nlm.nih.gov/33966113/), [Gudur et al.](https://pubmed.ncbi.nlm.nih.gov/42147661/).

Scalpel and ablative-laser studies concern removal of pigmented epithelium; recurrence is a relevant outcome. These are procedural comparisons, distinct from preservation of the existing tissue through molecular modulation. Oral pathology also distinguishes melanocytic pigmentation from deposits such as amalgam tattoos. [Procedure trial](https://pubmed.ncbi.nlm.nih.gov/31983845/), [oral pathology series](https://pmc.ncbi.nlm.nih.gov/articles/PMC8141314/). Red, swollen, bleeding gums belong to an inflammatory branch. [NIDCR](https://www.nidcr.nih.gov/health-info/gum-disease).

Ultrastructural examination of normal human gingiva found melanin granules in keratinocytes. This identifies an epithelial pigment pool, but does not quantify pigment in exfoliated cells or establish a selective export mechanism. [Squier and Waterhouse, 1967](https://doi.org/10.1016/0003-9969(67)90148-3).

A histochemical study of 95 autopsies sampled six oral sites and found marked site variation: melanin was detected in 28.4% of mandibular gingival samples and 51.6% of labial samples; 24.2% of subjects had no detectable pigment at any sampled oral site. This supports treating gingiva as a distinct compartment rather than assuming one oral-mucosa baseline. The study measured presence, not pigment export or function. [Barrett and Beynon, 1991](https://pubmed.ncbi.nlm.nih.gov/1747076/).

## 4. Eyes: separate compartments

```mermaid
flowchart TD
    E["Eye pigment is compartment-specific"]
    E --> A["Anterior iris / stroma<br/>Visible color target"]
    E --> B["Posterior iris epithelium<br/>Separate dense pigment"]
    E --> C["RPE<br/>Melanin + lipofuscin / bisretinoids"]
    E --> D["Choroid and ciliary body<br/>Separate functional tissues"]
    E --> F["Conjunctiva / episclera<br/>Cause-dependent surface pigmentation"]
    E --> Y["Yellow whites of eyes<br/>Bilirubin branch"]
    A --> A1["Darkening side effect documented<br/>Selective reversible clearance: G"]
    B --> B1["Cosmetic clearance: G"]
    B --> P["P: pathological pigment release<br/>from posterior iris epithelium"]
    P --> Q["Pigment enters aqueous pathways"]
    Q --> T["Trabecular meshwork<br/>receives pigment"]
    T --> T1["Outflow impairment in models;<br/>secondary glaucoma reported after cosmetic laser"]
    L["X: cosmetic photoablative iris laser"] --> Q
    L --> L1["H: case reports of serious<br/>pigmentary glaucoma"]
    C --> C1["Selected stored-substrate reduction: P<br/>General clinical clearance: G"]
    D --> D1["Cosmetic clearance: G"]
    F --> F1["Human pathology and procedural reports<br/>General molecular modulation: G"]
    Y --> Y1["Cause-specific clinical management"]
```

Human iris microscopy and chemical microdissection distinguish anterior/stromal pigmentation from the posterior pigment epithelium. These compartments cannot be combined into one clearance target. [Microscopy](https://pubmed.ncbi.nlm.nih.gov/8602783/), [pigment chemistry](https://pubmed.ncbi.nlm.nih.gov/9778410/).

Cosmetic photoablative iris-laser treatment is a procedural comparator, not a selective biological modulator. Case reports document pigment dispersion and secondary pigmentary glaucoma; after four sessions, one bilateral case had intraocular pressures of 50 and 42 mmHg, with visual-field defects and glare still present at follow-up despite urgent treatment. These case reports establish possible severe harm, not its frequency. [Ning et al.](https://pubmed.ncbi.nlm.nih.gov/33449587/), [Swampillai et al.](https://pubmed.ncbi.nlm.nih.gov/36175318/), [Liu et al.](https://pubmed.ncbi.nlm.nih.gov/37771388/).

**Pigment fate is part of the eye constraint.** In pigment-dispersion disease, granules released from the posterior iris pigment epithelium can travel through aqueous pathways and accumulate in the trabecular meshwork. Porcine models show impaired meshwork-cell phagocytosis/migration and reduced outflow after pigment exposure. A small human follow-up cohort found that meshwork pigmentation can attenuate over time after treatment for this disease; it does not establish a nonprocedural cosmetic clearance route. This pathology involves the posterior epithelium, distinct from the anterior stromal color target. [Human PDS cohort](https://pubmed.ncbi.nlm.nih.gov/34397796/), [trabecular-meshwork cell model](https://pmc.ncbi.nlm.nih.gov/articles/PMC7847180/), [porcine outflow model](https://pmc.ncbi.nlm.nih.gov/articles/PMC5915754/).

For the RPE, a 2014 cell/mouse study reduced **selected bisretinoids**, with substrate-specific limitations. A 2023 mouse study reported lipofuscin degradation involving melanin; subsequent scientific discussion addressed alternative pathways and the limits of a universal melanin-required interpretation. These are retinal research mechanisms, not evidence of iris-color reversal. [2014 study](https://pmc.ncbi.nlm.nih.gov/articles/PMC3986126/), [2023 study](https://pmc.ncbi.nlm.nih.gov/articles/PMC10194005/), [comment](https://pmc.ncbi.nlm.nih.gov/articles/PMC10622903/), [reply](https://pmc.ncbi.nlm.nih.gov/articles/PMC10622899/).

Human fetal RPE cultures provide evidence concerning melanin's photoprotective role. Choroid mapping, epithelial anatomy, and ocular-surface pathology are separate evidence categories. [RPE study](https://pmc.ncbi.nlm.nih.gov/articles/PMC1157035/), [human choroid study](https://pmc.ncbi.nlm.nih.gov/articles/PMC6901595/), [NLM epithelial definition](https://www.ncbi.nlm.nih.gov/mesh/D010857), [conjunctival case report](https://pmc.ncbi.nlm.nih.gov/articles/PMC4251888/).

## 5. The original iris cycle

Human iris chemistry found very low pigment content in blue irides and variation in melanin type across color groups. Histology found no significant difference in stromal melanocyte counts among blue, hazel, and brown irides. **Inference:** a return-to-blue claim should measure the visible anterior-stromal pigment state and standardized optical appearance; melanocyte counts or a whole-eye pigment measure alone are inadequate endpoints. [Iris histology](https://pubmed.ncbi.nlm.nih.gov/8602782/), [human iris pigment chemistry](https://pubmed.ncbi.nlm.nih.gov/9778410/).


```mermaid
flowchart LR
    A["Original blue iris"]
    B["Chosen dark-brown iris"]
    C["Original blue restored"]
    A -.->|"G: controlled increase<br/>in a uniformly blue iris"| B
    B -.->|"G: selective removal<br/>of added pigment"| C
    C -.->|"G: repeatable cycle"| A
    D["Documented glaucoma-drug darkening<br/>Some susceptible / mixed-color irides"]
    D --> E["Pigment may persist after stopping"]
```

The dashed arrows are the goal, not demonstrated clinical transitions. Official Xalatan information reports no observed color change in uniformly blue eyes in its cited studies. U.S. labeling describes increased iris pigmentation as likely permanent. Human follow-up reported no fading over two years after stopping, and a separate one-person photographic case found no appreciable change over five years. In contrast, one case of periocular-skin darkening visibly improved within a month and was significantly lighter by two months after stopping; epidermis is a renewing surface tissue, so this is not an iris reversal result. FDA states that there are no approved eye drops for changing eye color. [UK product information](https://www.medicines.org.uk/emc/product/1616/smpc), [U.S. label](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=f4e73059-5ba0-4d73-9ea1-09d8d654e844), [Wistrand et al.](https://pubmed.ncbi.nlm.nih.gov/9154289/), [Camras et al.](https://pubmed.ncbi.nlm.nih.gov/10708238/), [periocular-skin case](https://jamanetwork.com/journals/jamaophthalmology/fullarticle/265847), [FDA](https://www.fda.gov/drugs/buying-using-medicine-safely/what-you-should-know-about-eye-drops).

## 6. Hair and nails: living producers versus existing keratin

```mermaid
flowchart TD
    H["Living hair follicle"] --> HP["Pigment production during growth"]
    HP --> HS["Pigmented hair shaft"]
    HS --> HC["Marketed shaft dye / bleach<br/>Existing fiber chemistry"]
    H -.-> HG["G: selectable reversible<br/>human follicle controller"]
    N["Nail matrix melanocytes"] --> NP["Pigment in nail plate"]
    NP --> NG["G: general selective<br/>topical clearance"]
    N --> ND["Cause-dependent human biology<br/>Procedural case reports are limited evidence"]
```

Human-hair experiments show that bleaching can degrade melanin while also damaging fiber proteins. That does not demonstrate clearance in living tissue. Mouse follicle stem-cell research and observational human hair repigmentation concern a different biological system. Hair remains a candidate for the [separate project proposed earlier](hair-scope.md). [FDA hair cosmetics](https://www.fda.gov/cosmetics/cosmetic-products/hair-dyes), [ex vivo fiber study](https://doi.org/10.1111/ics.12495), [mouse follicle study](https://www.nature.com/articles/s41586-023-05960-6), [human observational study](https://elifesciences.org/articles/67437).

Human nail-matrix studies document melanocytes; a drug-induced melanonychia laser report is a case report. Neither establishes a general cosmetic pigment-removal controller. [Nail anatomy study](https://pubmed.ncbi.nlm.nih.gov/8040399/), [case report](https://pubmed.ncbi.nlm.nih.gov/31220366/).

## 7. Brain and visceral lipofuscin: clearance is more than autophagy

```mermaid
flowchart TD
    B["Brain neuromelanin"] --> BO["Long-lived autolysosome-like organelle"]
    BO --> NM["Pigment compartment<br/>Al, Ca, Fe mapped in human LC"]
    BO --> PM["Protein matrix"]
    BO --> LB["Lipid bodies"]
    BO --> BG["G: selective clinical clearance"]
    L["Lipofuscin in long-lived cells<br/>Heart, liver, adrenal and neural compartments"]
    L --> R["P: lower cardiac burden in old rats"]
    L --> A["Delivery toward degradative compartments"]
    A --> S["Successful substrate breakdown / disposal"]
    A --> F["Processing failure<br/>Accumulation can increase"]
    S -.-> G["G: selective human tissue clearance<br/>with function preserved"]
```

Human brain research characterizes neuromelanin-containing organelles; this is not a demonstrated clinical clearance intervention. A 2026 elemental-mapping study of seven postmortem locus-coeruleus samples localized several metals mainly to the pigment compartment, alongside a protein matrix and lipid bodies. The sample is small and observational; it sharpens the cargo map but cannot predict a clearance intervention. Human tissue studies also document lipofuscin in cardiac, hepatic and adrenal cells. A cardiac study reported reduced burden in old rats. Separately, stressed human fibroblast cultures accumulated more lipofuscin when autophagy was activated under impaired processing. **Increasing autophagy is not sufficient evidence that every pigment will be cleared.** [Neuromelanin organelle study](https://pubmed.ncbi.nlm.nih.gov/29900402/), [human locus-coeruleus elemental map](https://pmc.ncbi.nlm.nih.gov/articles/PMC13408184/), [human visceral-tissue study](https://pubmed.ncbi.nlm.nih.gov/7206299/), [old-rat cardiac study](https://www.sciencedirect.com/science/article/pii/S0014482721001178), [human fibroblast study](https://pubmed.ncbi.nlm.nih.gov/37438887/).

## 8. Iron deposits: an existing disease-treatment example

```mermaid
flowchart TD
    I["Diagnosed systemic iron overload"] --> O["Excess stores in affected organs<br/>Liver, heart, pancreas and others"]
    O --> C["C: medical iron depletion / chelation"]
    C --> L["Lower excess body iron burden"]
    L --> U["Prior tissue damage may persist"]
    L -.-> G["G: arbitrary cosmetic targeting<br/>of individual tissue color"]
```

Iron-overload treatment is a real example of reducing an accumulated chemical burden. Its purpose is disease management; iron is also essential to normal physiology. Phlebotomy is a procedure, and chelation is a medical therapy for particular circumstances. Neither is a melanin-clearance mechanism. [NIDDK treatment information](https://www.niddk.nih.gov/health-information/liver-disease/hemochromatosis/treatment).

## 9. Ochronosis: precursor reduction with partial human pigment regression

```mermaid
flowchart TD
    A["Alkaptonuria<br/>Excess homogentisic acid"] --> P["Ochronotic tissue deposits<br/>Cartilage and other connective tissues"]
    A --> N["C: nitisinone lowers precursor"]
    N --> H["Less homogentisic acid"]
    H --> R["H: partial pigment regression<br/>at measured eye / ear sites"]
    R -.-> G["G: complete clearing of all deposits"]
    H --> D["Human trial: slower disease progression"]
```

A human observational study reported partial regression in photographed eye/ear pigmentation and a reduction in ear-cartilage biopsy pigment. A randomized trial also found slower disease progression. This is a useful example of existing pigment decreasing after precursor reduction, with incomplete reversal and disease-specific chemistry. It does **not** demonstrate the same behavior for adult iris melanin. FDA's Harliku approval concerns reducing urinary homogentisic acid in adult alkaptonuria. [Pigment study](https://pubmed.ncbi.nlm.nih.gov/32904992/), [SONIA 2 trial](https://pubmed.ncbi.nlm.nih.gov/32822600/), [FDA approval record](https://www.accessdata.fda.gov/scripts/opdlisting/oopd/detailedIndex.cfm?cfgridkey=942723).

## 10. Bilirubin and other color changes

```mermaid
flowchart TD
    H["Heme turnover"] --> B["Unconjugated bilirubin"]
    B --> U["H: UGT1A1 in human liver<br/>conjugates bilirubin"]
    U --> C["Conjugated bilirubin"]
    C --> L["Hepatic elimination into bile"]
    L --> G["Gut metabolism"]
    G --> F["Fecal products"]
    B --> T["H: tracer study in 13 healthy adults"]
    T --> R["96% mean recovery of injected tracer<br/>in feces + urine over 7 days"]
    B --> J["Excess bilirubin"]
    J --> Y["Jaundice: yellow skin, mucosa<br/>and eye whites"]
    Y --> M["Cause-specific medical management"]
    R --> S["Substrate-specific metabolic route<br/>and human tracer accounting"]
    S --> X["Does not establish clearance of stored<br/>melanin or lipofuscin"]
    O["Other visible color"] --> D["Tooth stains / chromogens<br/>Dental cleaning or whitening"]
    O --> P["External dermal tattoo pigment<br/>X: cleared laser devices"]
    O --> V["Blood / vascular coloration<br/>Different chromophores"]
    D --> X
    P --> X
    V --> X
```

Bilirubin is a useful narrow comparator because both hepatic handling and whole-body tracer recovery have been measured in people. In 13 healthy adults, an injected unconjugated-bilirubin tracer was followed for seven days; mean cumulative radioactivity recovered in feces and urine was 96% of the dose. A separate human donor-liver and primary-hepatocyte study linked UGT1A1 abundance with bilirubin-conjugating activity and documented substantial donor variation. These studies describe a specialized route for bilirubin. They do not show selective clearance of stored melanin or lipofuscin, or a way to change skin, gum, or iris color. Tooth whitening and removal of external tattoo ink remain different capabilities; FDA states that it has not approved tattoo-removal creams. [Berk et al., human tracer study](https://www.jci.org/articles/view/106184), [Ritter et al., human liver UGT1A1 study](https://pubmed.ncbi.nlm.nih.gov/10421657/), [NIH jaundice information](https://newsinhealth.nih.gov/2022/10/recognizing-jaundice), [ADA tooth whitening](https://www.ada.org/resources/ada-library/oral-health-topics/whitening), [FDA tattoo removal](https://www.fda.gov/consumers/consumer-updates/tattoo-removal-options-and-results), [NHLBI hemoglobin and red cells](https://www.nhlbi.nih.gov/health/anemia/causes).

## 11. Systemic exposures can affect several tissues

```mermaid
flowchart TD
    A["Systemic exposure or metabolic precursor"] --> B["Visible change at one or more sites"]
    B --> C["H: separate medication-related reports<br/>skin, oral mucosa, sclera, nails, teeth"]
    B --> D["C: porphyrin disorders<br/>precursors can build up in liver or bone marrow"]
    C --> E["Tissue chemistry may differ<br/>melanin, iron-containing or drug-derived material"]
    D --> F["Effects can show in skin<br/>or the nervous system"]
    C --> G["Stopping an initiating drug"]
    G --> H["Some human cases: gradual change over years"]
    G --> I["Other sites / cases: pigment may persist"]
    C --> X["X: limited laser reports for<br/>specific skin deposits"]
    E -.-> U["G: no demonstrated single method<br/>to clear all affected tissues"]
```

Separate human reports document minocycline-associated discoloration in skin, oral mucosa (including gums), sclera, nails, teeth and other tissues. Tissue analyses show why a shared cause does not guarantee one shared pigment: particular skin and nail deposits have contained iron and calcium, while different patterns can involve melanin. In one case with broad skin and scleral involvement, color slowly moved toward normal over several years after the drug was stopped; a scleral case series reports that pigmentation can also persist. These are adverse-effect observations and case reports, not a controlled or selectable cosmetic color cycle. [Multi-tissue case reports](https://pubmed.ncbi.nlm.nih.gov/9512163/), [skin/gum/nail/sclera case](https://pubmed.ncbi.nlm.nih.gov/36158857/), [skin and nail tissue analysis](https://pubmed.ncbi.nlm.nih.gov/3158285/), [scleral follow-up series](https://pubmed.ncbi.nlm.nih.gov/9186432/).

Porphyria gives a different systems map: depending on type, porphyrins or precursors may accumulate in liver or bone marrow while symptoms affect skin, nervous system, or both. Its disease-specific management is not an example of selectively clearing visible melanin. [NIDDK overview](https://www.niddk.nih.gov/health-information/liver-disease/porphyria).

Silver deposition in argyria is another distinct substrate. Published skin-laser reports are limited clinical case reports; they do not establish a noninvasive whole-body clearance system. [Systematic review](https://pubmed.ncbi.nlm.nih.gov/25845405/).

## 12. Inner ear: melanin in a hearing-critical compartment

```mermaid
flowchart TD
    S["Cochlear stria vascularis"] --> I["Melanocyte-like intermediate cells<br/>contribute to endocochlear potential"]
    I --> M["Cells produce and export melanin"]
    H["H: human temporal bones, n = 46"] --> HD["Melanin in stria + Rosenthal's canal;<br/>age/group differences, no threshold association"]
    P["P: genetically matched mouse comparison"] --> PD["In mice over 2 years, absent melanin<br/>coincided with more EP decline / cell loss"]
    M -.-> R["Melanin's own protective role<br/>remains unresolved"]
    HD -.-> G["G: selective pigment reduction<br/>with hearing function preserved"]
    PD -.-> G
    R -.-> G
```

The cochlear stria vascularis contains melanin-producing intermediate cells, and human temporal-bone studies also identify pigment in Rosenthal's canal. In one 46-specimen study, pigmentation differed between the study's African-American and Caucasian donor groups and strial pigment increased with age; pigment amount was not associated with hearing thresholds in that sample. A genetically matched mouse comparison found that, after two years of age, endocochlear-potential decline and marginal-cell loss were more common in albino mice. This does not prove that melanin itself is essential or that changing pigment would alter human hearing. It does make cochlear cell function and pigment burden separate endpoints. No selective cochlear pigment-reduction method is established here. [Sun et al., 2014](https://pubmed.ncbi.nlm.nih.gov/25166018/), [Ohlemiller et al., 2009](https://pubmed.ncbi.nlm.nih.gov/19141317/).

## 13. Leptomeninges: normal melanin outside neurons

```mermaid
flowchart LR
    L["Leptomeninges"] --> M["H: melanin-containing dendritic cells<br/>confirmed as melanocytes"]
    M --> D["Most concentrated over ventrolateral medulla;<br/>isolated cells elsewhere in sampled brains"]
    M --> I["Normal melanin can produce<br/>T2 MRI hypointensity"]
    I --> C["May resemble a pigmented<br/>meningeal abnormality"]
    M -.-> G["G: selective removal and safe disposition<br/>with CNS function preserved"]
    N["Neuronal neuromelanin"] --> X["Different cell and storage compartment;<br/>do not treat as one pigment pool"]
```

Human histology and ultrastructure identified leptomeningeal pigment cells as melanocytes, based on their dendritic morphology and melanosomes. In 15 brains, they were concentrated over the ventrolateral medulla; a small subset averaged 325 cells/mm² there. A separate imaging study found that normal meningeal melanin can create T2-weighted hypointensity that resembles disease. The studies establish a non-neuronal CNS pigment compartment, not its normal physiological role or a selective clearance route. That compartment is distinct from neuronal neuromelanin. [Goldgeier et al., 1984](https://pubmed.ncbi.nlm.nih.gov/6699426/), [Gebarski and Blaivas, 1996](https://pubmed.ncbi.nlm.nih.gov/8770250/).

## 14. Heart and pulmonary veins: melanocyte-like cells with uncertain human pigment burden

```mermaid
flowchart TD
    H["Human atria / pulmonary veins"] --> HC["H: DCT-positive<br/>melanocyte-like cells identified"]
    M["Mouse cardiac melanocyte-like cells"] --> MM["P: melanosomes and pigmented cells observed"]
    M --> D["P: DCT deficiency or loss of these cells<br/>changes arrhythmia susceptibility in mice"]
    D --> U["Mechanism is not proof that<br/>melanin amount drives the phenotype"]
    HC --> G["G: human pigment burden, clinical role,<br/>and selective clearance unresolved"]
    MM --> G
    U --> G
```

A primary study identified DCT-positive melanocyte-like cells in human pulmonary veins and atria; ultrastructural melanosomes and pigmented cardiac cells were shown in mice. Mouse DCT-deficient or cell-deficient models had altered susceptibility to atrial arrhythmias. Because DCT also participates in calcium and reactive-species regulation, these results do not show that reducing melanin itself causes arrhythmia, and the contribution of these cells to clinical human arrhythmias remains undetermined. No human cardiac pigment-reduction or clearance method is established. [Levin et al., 2009](https://pubmed.ncbi.nlm.nih.gov/19855129/).

## 15. Esophageal mucosa: rare melanocytosis is site-specific

```mermaid
flowchart TD
    E["Esophageal squamous mucosa"] --> M["H: rare melanocytic proliferation<br/>with melanin deposition"]
    M --> D["Histology helps distinguish<br/>melanocytosis from melanoma"]
    M -.-> G["G: natural history and selective<br/>clearance not established"]
    C["Colon melanosis coli"] --> L["H: lipofuscin-like pigment<br/>in macrophages"]
    L --> X["Different pigment and cell compartment;<br/>do not generalize by name"]
```

Esophageal melanocytosis is a rare human mucosal finding described as non-atypical melanocytic proliferation with melanin deposits. Case reports and small series emphasize its distinction from primary esophageal melanoma; they do not establish a predictable natural history or a selective pigment-clearance method. It is chemically distinct from colon melanosis coli, whose macrophage pigment has been identified as lipofuscin-like material. [Dubail et al., 2022](https://pubmed.ncbi.nlm.nih.gov/35709783/), [Ohnuma et al., 2017](https://pubmed.ncbi.nlm.nih.gov/28445275/), [colon histopathology](https://pmc.ncbi.nlm.nih.gov/articles/PMC4581826/).

## 16. Candidate melanocyte-lineage signals are not evidence of pigment stores

```mermaid
flowchart LR
    O["Normal human organ samples"] --> R["H: tyrosinase transcripts detected by RT-PCR<br/>in several organs"]
    R --> U["Cell identity unresolved;<br/>transcript assay did not measure melanin"]
    A["Human subcutaneous adipose-derived cells"] --> C["P: melanocyte markers in cultured cells"]
    C --> D["Melanocyte-specific culture + 3D epidermis + UVB<br/>produced melanin deposits in the model"]
    D --> V["Shows cell differentiation potential;<br/>not a pigmented adipose store in vivo"]
    U --> G["G: organ-specific pigment burden<br/>and selective clearance remain unestablished"]
    V --> G
```

A sensitive 1993 RT-PCR study detected tyrosinase transcripts in normal samples of skin, lymph nodes, stomach antrum, colon, kidney, lung, testis, ovary, breast, and peripheral nerve. The authors said the expressing cells still needed identification; the assay did not localize cells or quantify tissue melanin. A later human adipose-derived stem-cell study found melanocyte markers in cultured cells and generated melanin after differentiation in a three-dimensional epidermal model with UVB exposure. That supports progenitor potential under model conditions, not a native melanin deposit in adipose tissue. These findings justify candidate-tissue research, not a claim that all marker-positive organs contain accumulated melanin. [Battyani et al., 1993](https://pubmed.ncbi.nlm.nih.gov/7511806/), [Ikeda et al., 2021](https://pubmed.ncbi.nlm.nih.gov/34432824/).

## 17. Nasal and laryngeal mucosa: localized, sample-dependent evidence

```mermaid
flowchart LR
    N["Nasal / paranasal mucosa"] --> NH["H: melanocytes in 21 of 99<br/>autopsy specimens in one Japanese series"]
    NH --> NS["Mostly subepithelial stroma near<br/>glands and sinuses"]
    NS --> NG["Site and sampling matter;<br/>no clearance endpoint"]
    L["Laryngeal mucosa"] --> LB["H: melanocytes in a vocal-cord biopsy;<br/>none in 15 whole-larynx autopsies"]
    L --> LC["H: 4 melanosis cases had more<br/>melanocytes than 16 controls"]
    LB --> LG["Small, differing samples;<br/>no clearance endpoint"]
    LC --> LG
    NG --> G["G: tissue-selective pigment reduction<br/>not established"]
    LG --> G
```

A Japanese pathology series found stromal melanocytes in 21 of 99 autopsy specimens of nasal cavity/paranasal sinus, commonly around glands and sinuses; intraepithelial dendritic melanocytes were seen in 2 of the 21 positive cases. The series also included 79 surgical specimens from chronic sinusitis or nasal-polyps cases, so its result is a histology observation, not a population estimate. [Uehara et al., 1987](https://pubmed.ncbi.nlm.nih.gov/3661192/).

Laryngeal findings are sparse and sampling-dependent. A 1976 report found melanocytes in a vocal-cord biopsy but none in extensive sections from 15 larynges at autopsy. A 1997 retrospective series described four laryngeal-melanosis cases; the melanosis samples had more melanocytes than 16 controls, with a small, nonsignificant trend between smoking and control groups. These reports do not establish a general laryngeal pigment burden, health role, or clearance capability. [Busuttil, 1976](https://doi.org/10.1001/archotol.1976.00780060089012), [Gonzalez-Vela et al., 1997](https://pubmed.ncbi.nlm.nih.gov/9419104/).

## 18. Genital mucosa: different sites, different evidence

```mermaid
flowchart TD
    G["Genital mucosa"] --> V["Vulvar melanosis cohort<br/>129 patients; long follow-up"]
    V --> VN["About 30% changed in size/color,<br/>then stabilized"]
    VN --> VE["Natural history of appearance;<br/>not a clearance intervention"]
    G --> C["Cervix: visible pigmented lesions"]
    C --> CN["33 of 2,118; mostly blue nevi;<br/>one melanotic macule"]
    G --> A["Anorectal mucosa"]
    A --> AN["Low baseline melanocyte density<br/>measured in surgical controls"]
    G --> E["Endocervix"]
    E --> EN["Melanin-confirmed cells<br/>in two case specimens"]
    G --> X["Vaginal normal-pigment distribution"]
    X --> XN["Dedicated prevalence data<br/>remain limited in this review"]
    VE --> N["Different lesions and cell compartments;<br/>no general pigment-clearance route"]
    CN --> N
    AN --> N
    EN --> N
    XN --> N
```

A 20-year single-center cohort followed 129 patients with vulvar melanosis for 5–20 years. About 30% of lesions enlarged or changed color before stabilizing; no malignant evolution was documented. This is natural history of visible lesions, not a test of deliberate removal or pigment mass. A prospective cervical series found visible pigmented lesions in 33 of 2,118 cervices; most were blue nevi, and one was a melanotic macule. A two-case endocervical report confirmed melanin-containing cells but found no pigment in the endocervical epithelium. [Vulvar cohort](https://pubmed.ncbi.nlm.nih.gov/32785609/), [cervical lesions](https://pubmed.ncbi.nlm.nih.gov/24300541/), [endocervical cases](https://pubmed.ncbi.nlm.nih.gov/7405906/).

In a surgical-pathology anorectal series, 24 control specimens had low densities of melanocytes that varied by glandular versus squamous compartment and by stain; controls included some hemorrhoids and other pathology, so they are not a population survey. These data identify a local cell population and support compartment-specific diagnosis, not a healthy-tissue color treatment. Dedicated normal vaginal-pigment prevalence was not established by the sources reviewed here. [Nazarian et al., 2016](https://pubmed.ncbi.nlm.nih.gov/27247367/).

## Research requirements shared across tissues

A future selective-clearance claim would need to identify the pigment chemically; locate it in the relevant cells or extracellular compartment; measure actual pigment loss separately from reduced synthesis or marker loss; account for breakdown products; and show preservation of tissue function.

A reversible system would additionally need evidence for return to the original appearance, spatial uniformity, and repeat cycles. The reviewed literature offers several tissue-specific footholds. It does not establish selective pigment removal across all bodily tissues.

# Automated, remote operating model for iris measurement

*Concept for planning and literature review; not an experimental protocol. Reviewed October 2026.*

## Design goal

Automate the repeatable parts of a donor-eye measurement study while keeping fragile, not-yet-validated tissue decisions visible to trained staff. The data chain should link one coded donor eye to its receipt record, condition sensors, intact-eye images, separated tissue fractions, assay results, and quality-control decision.

A cloud laboratory can provide remote scheduling, sample processing, automated instruments, and data capture. That does not mean every provider accepts intact human donor eyes or can perform a custom iris dissection. Confirm sample acceptance, biosafety classification, cold-storage window, processing capability, turnaround, and all fees before shipping anything.

## Staged workflow

1. **Source and approve.** A research partner checks availability with an ARVO/EBAA EyeFind-listed bank and specifies a whole globe or iris-containing anterior segment, research-use consent, donor metadata, preservation, and postmortem interval. The bank and receiving institution determine local IRB, biosafety, shipping, and use requirements. See the specimen details in the [measurement-validation proposal](iris-measurement-validation-proposal.md#1-sample-and-scope).
2. **Receive and accession.** Use scheduled delivery to a staffed, approved receiving location. Record tracking and arrival times; scan a coded identifier; photograph the outer package and specimen container; capture a validated temperature logger; weigh the package if useful for shipping QC. A trained person checks identity, seal, temperature/time limits, and visible damage before releasing a specimen. Flag and quarantine exceptions rather than automatically treating a sensor alert as an acceptable sample.
3. **Image before dissection.** Capture standardized visible images with a color reference and controlled geometry, plus the proposed OCT measurements. Use a fixed camera and OCT first. Add 3D surface imaging only if it improves a prespecified measurement. LiDAR is not a first-stage requirement: it does not measure melanin, and no reviewed evidence shows it improves this iris endpoint.
4. **Separate and document fractions.** Begin with trained, documented human dissection and image-assisted orientation. Record the anatomical boundary and operator for each stromal and IPE fraction. Keep machine-vision guidance and a second-person or histology-based check in the loop until fraction purity and between-operator repeatability are demonstrated. Robotic dissection would be a later engineering project, not an assumed capability of a general-purpose liquid handler.
5. **Run validated analytical chemistry.** Barcode each fraction and use an existing lab or cloud provider for automated sample preparation and HPLC where its validated instruments and accepted sample types fit. Include the blanks, references, recovery checks, precision checks, and limits defined in the assay-feasibility gate. Preserve donor-level identity; batch samples to save instrument time, but do not pool different donors.
6. **Review and report.** Join sensor, image, dissection, instrument, reagent-lot, and assay-QC records in one LIMS/ELN or provider data system. Human review approves any exclusion, rerun, or interpretation. Keep appearance, marker abundance, converted pigment estimate, and tissue function as separate outcomes.

## Which parts are ready to automate?

| Stage | Good early automation target | Keep human review for |
| --- | --- | --- |
| Parcel and sample intake | Barcode/QR scanning, timestamps, temperature-logger import, package images, alerts | Consent/source match, broken seals, excursions, identity and release decision |
| Imaging | Fixed illumination, camera positioning, color target, file naming, OCT capture and repeat scans | Iris orientation, segmentation quality, corneal opacity, pathology and image exclusion |
| Fraction handling | Coded tubes, electronic chain of custody, instrument setup reminders | Tissue boundary identification and dissection until method repeatability is proven |
| Chemistry | Liquid dispensing, plate/tube tracking, HPLC sequence, chromatogram capture, QC flags | Method suitability, out-of-range samples, marker interpretation and any pigment-mass conversion |
| Data | Automatic metadata linking, audit trail, analysis scripts, versioned reports | Final QC and interpretation |

The goal is automated evidence collection, not a “lights-out” decision about whether a donor specimen is usable. Postmortem tissue condition can vary; an unattended receiver should not release a sample solely because a parcel barcode scanned.

## Delivery model and cost logic

Three delivery models should be quoted against the same pilot and the same output: **cost per quality-control-passing donor eye**, including failed or unusable specimens.

| Model | Best fit | Main cost or limitation |
| --- | --- | --- |
| **Academic eye-research core** | First feasibility work when an ophthalmology or pathology partner already has imaging, tissue-handling, and analytical facilities | Requires a local collaborator and scheduled staff time; access and fees vary by institution |
| **Remote cloud lab** | Remote access to automated instruments, data systems, and common analytical workflows without buying a lab | Usually quote-based; sample intake, unusual tissue handling, cold storage, materials, shipping, instrument time, storage, waste, and custom workflow support can all add cost |
| **Own robot / dedicated lab** | Repeated, stable, high-throughput work with trained staff and facility support | Hardware is only one part of cost: installation, modules, validation, maintenance, facility, consumables, and staff remain |

Emerald Cloud Lab publicly describes remote sample shipment and automated access to HPLC and other instruments. Its terms list materials/stocking, shipping and handling, waste, instrument time, sample storage, and software/data fees; estimates are not a fixed all-in price. Its public materials do not establish acceptance of intact donor globes or a custom iris workflow, so that must be confirmed directly. [ECL workflow](https://www.emeraldcloudlab.com/how-it-works/run/), [ECL terms](https://www.emeraldcloudlab.com/ecl-terms-of-service/).

For context, Opentrons currently lists Flex configurations starting around $24,950–$26,400; the configured product page also shows a $38,125 setup, with required on-site installation and optional modules or services. Flex is a liquid-handling robot, not an iris-dissection system, and the manufacturer says it is not a sterile environment. Those prices exclude the facility, method validation, staffing, consumables, service, and integration. It is a cost reference, not a recommendation to buy. [Opentrons pricing and product options](https://opentrons.com/robots/flex), [Flex product details](https://opentrons.com/products/opentrons-flex-robot).

## Cost controls without weakening the evidence

- Start with a small, prespecified feasibility run through an existing academic core or a cloud-lab quote. Do not build or buy a dedicated lab before the required throughput is known.
- Request quotes from more than one eligible provider, using the same specimen, sample count, metadata, turnaround, imaging, assay, storage, and waste requirements. Ask for an itemized estimate and per-sample pricing at pilot and scaled volumes.
- Prefer a nearby eye bank and laboratory to reduce transit time and cold-chain risk. Coordinate delivery to staffed hours; shipping savings are not useful if tissue quality is lost.
- Use postmortem animal byproducts or repository specimens only for method development when a specific species is scientifically suitable and the institution approves the source. This can reduce new animal use, but it cannot replace human iris calibration.
- Batch instrument runs and automate aliquoting after the method is validated. Maintain separate donor IDs so batching does not erase biological replicates.
- Use standard, interoperable labware and nonproprietary consumables where the provider allows them and equivalence is validated. Negotiate academic/core-facility or volume pricing. Buy stable, commonly used consumables in planned quantities only after the assay and demand forecast are stable; avoid bulk stockpiling of expiring or specialized reagents.
- Keep quality controls and repeatability measurements intact. Cut idle capacity, duplicated software, custom hardware, and unnecessary shipping—not the checks needed to know whether the measurement is trustworthy.

## Immediate next step

Before any equipment purchase or specimen shipment, prepare one matched request for an eye bank and a candidate academic core/cloud lab. Ask:

- Can they supply and accept coded, research-consented whole globes or iris-containing anterior segments?
- What donor metadata, postmortem interval, preservation, packaging, and cold-chain record can they provide?
- Can intact-eye visible imaging/OCT happen before dissection, and who performs or validates the separation?
- Can their analytical workflow measure the proposed melanin markers in iris fractions, or would the assay need a separate method-development phase?
- What are the itemized costs for tissue recovery/handling, shipping, receipt, storage, imaging, dissection, assay, controls, waste, and data access at pilot and later volumes?
- What IRB, biosafety, IACUC determination (if animal material is considered), provider review, and sample-transfer documents are required?

The go/no-go decision is whether one partnered site can handle the postmortem window and specimen form while meeting the purity and assay-QC requirements at a defensible cost. If not, revise the source/model or stop before building automation.

## Evidence and limits

A 2025 EBAA statistical report records 23,213 ocular tissues supplied by U.S. eye banks for research and training, but that does not guarantee this project’s exact specimen or metadata needs. ARVO/EBAA guidance recommends discussing specimen type, donor age, time from death, preservation, consent, transport, and cost with the bank. [EBAA 2025 statistics](https://restoresight.org/members/publications/statistical-report/), [ARVO/EBAA best practices](https://integration.arvo.org/globalassets/arvo/journals-and-publications/eye-bank/best-practices-for-using-human-eye-tissue-in-research.pdf).

Animal tissue sharing from existing dead animals or slaughterhouse sources may be a useful reduction strategy where scientifically appropriate. NIH OLAW says the PHS Policy generally does not cover dead animal tissue unless animals are killed for the tissue or undergo project-specific premortem manipulation; institutions may have broader policies and must make the applicable determination. [OLAW FAQ](https://olaw.nih.gov/policies-laws/21st-century-cures-act/Activities-Exempt-From-Protocol-Review), [OLAW/USDA shared-tissue guidance](https://olaw.nih.gov/guidance/articles/laba97v26n3p21.htm).

Species substitution needs restraint. Comparative work documents species- and strain-associated differences in ocular melanin, but measured sclera, choroid/RPE, and retina rather than iris. It supports caution about extrapolation, not a particular animal iris as a human surrogate. [Comparative ocular melanin study](https://pmc.ncbi.nlm.nih.gov/articles/PMC3358346/).

*This is a workflow and procurement-planning concept only. It does not establish that a provider will accept donor eye tissue, that robotic dissection will work, or that an iris melanin assay is validated.*

"""Compare source-defined structures and two paired, distinct IC50 endpoints."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

from rdkit import Chem, DataStructs, rdBase
from rdkit.Chem import Crippen, Descriptors, Draw, Lipinski, rdFingerprintGenerator, rdMolDescriptors


XML_SHA256 = "73d032625e98b25239a823f46676c465fb98044e96fc178aa4c986c158cace23"
DOI = "10.1111/jocd.70510"
KT939_SMILES = "CC1(COC1)C(=O)Nc1nc(-c2ccc(O)cc2O)cs1"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalized(element):
    value = unicodedata.normalize("NFKC", "".join(element.itertext()))
    return " ".join(value.replace("µ", "μ").replace("‐", "-").split())


def unique_paragraph(root, prefix):
    found = [normalized(p) for p in root.findall(".//body//p") if normalized(p).startswith(prefix)]
    if len(found) != 1:
        raise ValueError(f"Expected one paragraph starting {prefix!r}; got {len(found)}")
    return found[0]


def numeric(pattern, text):
    matches = re.findall(pattern, text)
    if len(matches) != 1:
        raise ValueError(f"Expected one numeric match for {pattern!r}; got {matches}")
    return float(matches[0])


def structure_row(name, smiles, origin, expected_formula):
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        raise ValueError("Invalid transcribed graph: " + name)
    formula = rdMolDescriptors.CalcMolFormula(molecule)
    if formula != expected_formula:
        raise ValueError("Unexpected formula: " + name)
    core = Chem.MolFromSmiles("Nc1nc(-c2ccc(O)cc2O)cs1")
    if not molecule.HasSubstructMatch(core):
        raise ValueError("Missing declared resorcinol/thiazole core: " + name)
    row = {"compound": name, "identity_origin": origin,
           "canonical_smiles": Chem.MolToSmiles(molecule), "formula": formula,
           "database_inchikey": None,
           "molecular_weight_g_mol": Descriptors.MolWt(molecule),
           "exact_neutral_mass_Da": Descriptors.ExactMolWt(molecule),
           "calculated_logP": Crippen.MolLogP(molecule),
           "TPSA_A2": rdMolDescriptors.CalcTPSA(molecule),
           "hydrogen_bond_donors": Lipinski.NumHDonors(molecule),
           "hydrogen_bond_acceptors": Lipinski.NumHAcceptors(molecule),
           "ring_count": rdMolDescriptors.CalcNumRings(molecule),
           "formal_charge": Chem.GetFormalCharge(molecule),
           "shared_resorcinol_thiazole_core": True}
    return molecule, row


def make_figure(molecules, structures, assays, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "svg.hashsalt": "kt939-thiamidol-2026-10-22"})
    figure, axes = plt.subplots(2, 2, figsize=(10.8, 7.3), layout="constrained")
    for ax, molecule, row in zip(axes[0], molecules, structures):
        ax.imshow(Draw.MolToImage(molecule, size=(750, 360)))
        ax.axis("off")
        ax.set_title(row["compound"] + " | " + row["formula"], weight="bold")
        ax.text(.5, -.02, f"Calculated logP {row['calculated_logP']:.2f} | TPSA {row['TPSA_A2']:.2f} Å²",
                ha="center", transform=ax.transAxes)
    for ax, row in zip(axes[1], assays):
        values = [row["kt939_IC50_uM"], row["thiamidol_IC50_uM"]]
        bars = ax.barh(["KT-939", "Thiamidol"], values, color=["#137f85", "#d28b38"])
        ax.invert_yaxis()
        ax.set_xlim(0, max(values) * 1.27)
        ax.bar_label(bars, labels=[f"{value:g}" for value in values], padding=4)
        ax.set_title(row["short_label"] + f"\nThiamidol / KT-939 IC50 = {row['thiamidol_over_kt939_IC50_ratio']:.2f}")
        ax.set_xlabel("Reported IC50 (μM); lower means more potent in this assay")
        ax.spines[["top", "right"]].set_visible(False)
    figure.suptitle("KT-939 and thiamidol: related structures, separate endpoints", weight="bold")
    figure.supxlabel("One source study. Neutral structures and calculated properties. No paired withdrawal comparison or iris measurements.", fontsize=9)
    figure.savefig(out / "comparison.svg", metadata={"Date": None})
    svg = out / "comparison.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    figure.savefig(out / "comparison.png", dpi=170)
    plt.close(figure)


def run(xml_path, reference_path, out, plot):
    if digest(xml_path) != XML_SHA256:
        raise ValueError("Primary XML does not match the previously qualified source snapshot")
    root = ET.parse(xml_path).getroot()
    if not any(x.text == DOI for x in root.findall(".//article-id")):
        raise ValueError("Unexpected source DOI")
    titles = [normalized(x).lower() for x in root.findall(".//sec/title")]
    if not any("3-methyloxetane-3-carboxamide" in title and "dihydroxyphenyl" in title for title in titles):
        raise ValueError("Source compound name was not found")
    lysate = unique_paragraph(root, "Tyrosinase functions as a key catalytic enzyme")
    cells = unique_paragraph(root, "To investigate the impact of tyrosinase inhibitors")
    assays = [
        {"endpoint": "MNT-1 crude-lysate L-DOPA oxidation", "short_label": "Lysate enzyme activity | Figure 1",
         "source_location": "Results 3.1, Figure 1; Methods 2.3",
         "kt939_IC50_uM": numeric(r"IC50 of ([0-9.]+) μM", lysate),
         "thiamidol_IC50_uM": numeric(r"IC50 values of Thiamidol,.*?were ([0-9.]+),", lysate),
         "meaning": "475-nm optical activity endpoint; IC50 derived from reported Vmax curves"},
        {"endpoint": "Six-day MNT-1 accumulated melanin normalized to protein", "short_label": "Cell pigment / protein | Figure 3",
         "source_location": "Results 3.3, Figure 3; Methods 2.4",
         "kt939_IC50_uM": numeric(r"IC50 of ([0-9.]+) μM", cells),
         "thiamidol_IC50_uM": numeric(r"Thiamidol \(IC50: ([0-9.]+) μM\)", cells),
         "meaning": "405-nm bulk pigment/protein endpoint; not a direct new-synthesis flux"},
    ]
    for row in assays:
        row["thiamidol_over_kt939_IC50_ratio"] = row["thiamidol_IC50_uM"] / row["kt939_IC50_uM"]
    reference = json.loads(reference_path.read_text(encoding="utf-8"))["PropertyTable"]["Properties"]
    if len(reference) != 1 or reference[0]["CID"] != 71543007:
        raise ValueError("Unexpected thiamidol reference")
    thiamidol = reference[0]
    th_mol, th_row = structure_row("Thiamidol", thiamidol["SMILES"], "Existing PubChem CID 71543007 snapshot", "C13H14N2O3S")
    named_thiamidol = Chem.MolFromSmiles("CC(C)C(=O)Nc1nc(-c2ccc(O)cc2O)cs1")
    if th_row["canonical_smiles"] != Chem.MolToSmiles(named_thiamidol):
        raise ValueError("Reference graph does not match named thiamidol")
    th_row["database_inchikey"] = thiamidol["InChIKey"]
    kt_mol, kt_row = structure_row("KT-939", KT939_SMILES, "Manual transcription of Methods 2.1 compound name", "C14H14N2O4S")
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048, includeChirality=False)
    similarity = DataStructs.TanimotoSimilarity(generator.GetFingerprint(kt_mol), generator.GetFingerprint(th_mol))
    lc_ms = numeric(r"LCMS\(\[M\+H\]\+\): ([0-9]+(?:\.[0-9]+)?)", normalized(root.find("body")))
    structures = [th_row, kt_row]
    out.mkdir(parents=True, exist_ok=False)
    write_csv(out / "paired_assays.csv", assays)
    write_csv(out / "structures.csv", structures)
    summary = {
        "activity": "Source-qualified paired IC50 and structure comparison; no new experiments",
        "doi": DOI, "assays": assays,
        "structural_difference": "Oxetane-containing acyl substituent in KT-939 versus isopropyl acyl substituent in thiamidol; net +CO",
        "descriptor_difference_kt939_minus_thiamidol": {key: kt_row[key] - th_row[key] for key in [
            "molecular_weight_g_mol", "calculated_logP", "TPSA_A2", "hydrogen_bond_donors", "hydrogen_bond_acceptors", "ring_count"]},
        "morgan_radius2_2048bit_nochirality_tanimoto": similarity,
        "mass_identity_qualification": {"source_reported_LCMS_M_plus_H": lc_ms,
            "calculated_exact_M_plus_H": kt_row["exact_neutral_mass_Da"] + 1.007276466621,
            "interpretation": "Source precision/calibration is unspecified; not an asserted exact-mass match or independent material identity verification"},
        "limits": [
            "Two endpoint-specific ratios from rounded published point estimates; no raw curve refit, confidence interval or new significance test",
            "Figure 4 tests KT-939 withdrawal only, so no paired recovery superiority is established",
            "Cell pigment normalized to protein does not distinguish new synthesis, old pigment, cell division or loss",
            "72-hour viability does not account for the full six-day pigment exposure or subsequent recovery",
            "Figure 1 specifies three independent experiments; Figure 3 caption does not state n",
            "One developer-affiliated study; underlying datasets available on request, not independently reproduced here",
            "Neutral graph calculations do not measure pH speciation, solubility, free exposure, melanin binding or iris delivery",
            "Morgan similarity is a representation-specific structural comparison, not an affinity or performance prediction",
            "Docking is not measured affinity; skin formulation before/after observations are not a paired compound or iris comparison",
        ],
    }
    write_json(out / "summary.json", summary)
    sources = [
        {"role": "Primary KT-939 study XML", "url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12569736/fullTextXML",
         "bytes": xml_path.stat().st_size, "sha256": digest(xml_path), "status": "Reused prior actual fetch; no new fetch claimed; raw XML outside repository"},
        {"role": "Thiamidol structure snapshot", "url": "https://pubchem.ncbi.nlm.nih.gov/compound/71543007",
         "repository_file": "analysis/binding-benchmark-run-2026-10-17/pubchem/thiamidol.pubchem.json",
         "bytes": reference_path.stat().st_size, "sha256": digest(reference_path), "status": "Reused existing public-identity snapshot"},
    ]
    write_json(out / "sources.json", sources)
    if plot:
        make_figure([th_mol, kt_mol], structures, assays, out)
    outputs = {p.name: {"bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(out.iterdir())}
    write_json(out / "receipt.json", {"created_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": digest(Path(__file__)), "python_version": platform.python_version(),
        "rdkit_version": rdBase.rdkitVersion, "source_xml_sha256": digest(xml_path),
        "reference_sha256": digest(reference_path), "outputs": outputs})
    print(json.dumps({"out": str(out), "assay_ratios": [r["thiamidol_over_kt939_IC50_ratio"] for r in assays],
                      "structures": structures, "limits": "No paired withdrawal or iris inference"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml", type=Path, required=True)
    parser.add_argument("--thiamidol", type=Path, default=Path(__file__).parent / "binding-benchmark-run-2026-10-17/pubchem/thiamidol.pubchem.json")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    run(args.xml, args.thiamidol, args.out, args.plot)

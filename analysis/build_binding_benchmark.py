"""Build a source-specific binding benchmark and inspect structural coverage."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import time
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree as ET

sys.path.insert(0, "/lab/workbench/tools")
import regen
from rdkit import Chem, DataStructs, rdBase
from rdkit.Chem import Crippen, Descriptors, Lipinski, rdFingerprintGenerator, rdMolDescriptors
from rdkit.Chem.MolStandardize import rdMolStandardize


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cached_fetch(cache, name, url, kind, provenance):
    path = cache / name
    if not path.exists():
        if kind == "json":
            write_json(path, regen.http_json(url))
        elif kind == "text":
            path.write_text(regen.http_text(url), encoding="utf-8")
        else:
            path.write_bytes(regen.http_bytes(url))
        regen.record("iris-binding-benchmark", {"url": url}, [path])
    provenance.append({"url": url, "cache_file": str(path), "bytes": path.stat().st_size,
                       "sha256": file_hash(path), "raw_snapshot_in_repository": kind == "json"})
    return path


def tables(xml_path):
    root = ET.fromstring(xml_path.read_text(encoding="utf-8"))
    for element in root.iter():
        element.tag = element.tag.rsplit("}", 1)[-1]
    result = {}
    for table in root.iter("table-wrap"):
        label = table.findtext("label", default="").strip().rstrip(".")
        rows = [[" ".join("".join(cell.itertext()).split()) for cell in row if cell.tag in {"td", "th"}]
                for row in table.findall(".//tbody/tr")]
        result[label] = rows
    return result


def identifier(value):
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def fingerprint(mol, method):
    if method == "rdkit_path":
        return Chem.RDKFingerprint(mol, fpSize=2048, minPath=1, maxPath=7)
    return rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048,
               includeChirality=method == "morgan_chiral").GetFingerprint(mol)


def plot(probes, refs, comparisons, nearest, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({"font.size": 9, "svg.hashsalt": "iris-binding-coverage"})
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 6.4), gridspec_kw={"width_ratios": [2.3, 1]}, layout="constrained")
    by_pair = {(r["probe"], r["reference"]): r for r in comparisons}
    matrix = np.array([[by_pair[p["id"], r["id"]]["morgan_tanimoto"] for r in refs] for p in probes])
    mesh = axes[0].imshow(matrix, cmap="cividis", vmin=0, vmax=1, aspect="auto")
    axes[0].set_xticks(range(len(refs)), [r["name"] for r in refs], rotation=55, ha="right")
    axes[0].set_yticks(range(len(probes)), [p["name"] for p in probes])
    axes[0].set_title("Morgan structural similarity to measured comparators")
    for i in range(len(probes)):
        for j in range(len(refs)):
            axes[0].text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center", fontsize=7,
                         color="white" if matrix[i,j] < .45 else "black")
    fig.colorbar(mesh, ax=axes[0], shrink=.6, label="Tanimoto similarity; 0–1")
    y = np.arange(len(probes))
    for method, offset, color, label in [("morgan", -.16, "#168083", "Morgan"), ("rdkit_path", .16, "#c86928", "Path")]:
        values = [next(n["similarity"] for n in nearest if n["probe"] == p["id"] and n["method"] == method and n["rank"] == 1) for p in probes]
        axes[1].barh(y+offset, values, height=.29, color=color, label=label)
    axes[1].set_yticks(y, [p["name"] for p in probes])
    axes[1].invert_yaxis()
    axes[1].set(xlim=(0, 1), xlabel="Nearest-reference similarity", title="Representation sensitivity")
    axes[1].legend()
    axes[1].grid(axis="x", alpha=.15)
    fig.suptitle("Chemical coverage of eleven numeric binding comparators\nSimilarity is not binding affinity, exposure, or efficacy", fontsize=13)
    fig.savefig(out / "structural_coverage.svg", metadata={"Date": None})
    fig.savefig(out.parent / "binding-coverage-preview.png", dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.inputs.read_text(encoding="utf-8"))
    args.cache.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "pubchem").mkdir()
    provenance = []
    xml = cached_fetch(args.cache, "hellinen2020.xml", config["sources"]["hellinen2020"]["xml_url"], "text", provenance)
    selected = tables(xml)
    if not all(label in selected for label in ["Table 1", "Table 2", "Table 4"]):
        raise ValueError("Expected source tables were not found.")
    rows = {identifier(row[0]): row for row in selected["Table 2"]}
    for ref in config["reference_2020"]:
        source = rows[ref["id"]]
        numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", source[1].replace(",", ""))]
        if numbers[:2] != [ref["mst_kd_uM"], ref["mst_68pct_confidence_value_uM"]]:
            raise ValueError("Manual input differs from numeric source row: " + ref["id"])
    write_json(args.out / "source_table_rows.json", selected)
    cached_fetch(args.cache, "bahrpeyma2022.pdf", config["sources"]["bahrpeyma2022"]["pdf_url"], "bytes", provenance)
    shutil.copyfile(args.inputs, args.out / "inputs.json")
    binding_rows = []
    for ref in config["reference_2020"]:
        sips = ref["sips"] or [None]*6
        binding_rows.append({"id": ref["id"], "name": ref["name"], "vendor_catalog": ref["vendor_catalog"],
            "mst_kd_uM": ref["mst_kd_uM"], "mst_68pct_confidence_value_uM": ref["mst_68pct_confidence_value_uM"],
            "mst_mode": ref["mst_mode"], "mst_uncertainty_exceeds_estimate": ref["mst_68pct_confidence_value_uM"] > ref["mst_kd_uM"],
            **dict(zip(["sips_kd_uM", "sips_kd_se_uM", "sips_bmax_nmol_per_mg", "sips_bmax_se_nmol_per_mg", "sips_n", "sips_n_se"], sips)),
            "sips_origin": ref["sips_origin"], "source_doi": config["sources"]["hellinen2020"]["doi"]})
    write_csv(args.out / "binding_2020.csv", binding_rows)
    release_rows = []
    for ref in config["release_2022"]:
        release_rows.append({"id": ref["id"], **dict(zip(["reused_sips_kd_uM", "reused_sips_kd_se_uM", "reused_sips_bmax_nmol_per_mg", "reused_sips_bmax_se_nmol_per_mg", "reused_sips_n", "reused_sips_n_se"], ref["sips"])),
            "melanin_koff_per_h": ref["melanin_koff_per_h"], "apparent_melanosome_koff_per_h": ref["apparent_melanosome_koff_per_h"],
            "particle_to_organelle_rate_ratio": ref["melanin_koff_per_h"]/ref["apparent_melanosome_koff_per_h"],
            "rate_uncertainty": "not_tabulated", "binding_is_reused": True, "source_doi": config["sources"]["bahrpeyma2022"]["doi"]})
    write_csv(args.out / "release_2022.csv", release_rows)
    write_csv(args.out / "calculated_fu_2020.csv", [{"id": r[0], "calculated_in_vitro_fu_percent": r[1], "predicted_human_rpe_choroid_fu_percent": r[2],
              "method": r[3], "measured_human_exposure": False} for r in config["calculated_fu_2020"]])
    identities, molecules = [], {}
    entries = [("reference", r) for r in config["reference_2020"]] + [("probe", p) for p in config["probes"]]
    for role, item in entries:
        query = f"cid/{item['cid']}" if "cid" in item else "name/"+quote(item["name"], safe="")
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/{query}/property/SMILES,ConnectivitySMILES,InChIKey,Title,MolecularFormula/JSON"
        path = cached_fetch(args.cache, item["id"]+".pubchem.json", url, "json", provenance)
        properties = json.loads(path.read_text())["PropertyTable"]["Properties"]
        if len(properties) != 1:
            raise ValueError("Ambiguous structure resolution: " + item["id"])
        prop = properties[0]
        if "cid" in item and prop["CID"] != item["cid"]:
            raise ValueError("Unexpected CID.")
        original = Chem.MolFromSmiles(prop["SMILES"])
        if original is None:
            raise ValueError("Invalid source SMILES.")
        parent = rdMolStandardize.Uncharger().uncharge(rdMolStandardize.FragmentParent(original))
        original_smiles = Chem.MolToSmiles(original, isomericSmiles=True)
        parent_smiles = Chem.MolToSmiles(parent, isomericSmiles=True)
        molecules[item["id"]] = parent
        row = {"id": item["id"], "role": role, "name": item["name"], "cid": prop["CID"], "resolved_title": prop["Title"],
               "pubchem_inchikey": prop["InChIKey"], "pubchem_formula": prop["MolecularFormula"], "original_smiles": original_smiles,
               "parent_smiles": parent_smiles, "parent_graph_changed": parent_smiles != original_smiles,
               "original_fragments": len(Chem.GetMolFrags(original)), "original_charge": Chem.GetFormalCharge(original), "parent_charge": Chem.GetFormalCharge(parent),
               "unspecified_stereocenters": sum(label == "?" for _, label in Chem.FindMolChiralCenters(parent, includeUnassigned=True)),
               "mw": Descriptors.MolWt(parent), "neutral_crippen_logp": Crippen.MolLogP(parent), "tpsa": rdMolDescriptors.CalcTPSA(parent),
               "hbd": Lipinski.NumHDonors(parent), "hba": Lipinski.NumHAcceptors(parent), "rotatable_bonds": Lipinski.NumRotatableBonds(parent),
               "aromatic_rings": rdMolDescriptors.CalcNumAromaticRings(parent), "source_url": url,
               "identity_limit": "Named parent structure; purchased salt/mixture and assay-pH species not established"}
        identities.append(row)
        shutil.copyfile(path, args.out / "pubchem" / path.name)
        print(f"{item['id']}: CID {prop['CID']}", flush=True)
        time.sleep(.25)
    write_csv(args.out / "identities.csv", identities)
    methods = ["morgan", "morgan_chiral", "rdkit_path"]
    fingerprints = {method: {key: fingerprint(mol, method) for key, mol in molecules.items()} for method in methods}
    comparisons, nearest, loo = [], [], []
    for probe in config["probes"]:
        for ref in config["reference_2020"]:
            comparisons.append({"probe": probe["id"], "reference": ref["id"],
                **{method+"_tanimoto": DataStructs.TanimotoSimilarity(fingerprints[method][probe["id"]], fingerprints[method][ref["id"]]) for method in methods}})
        for method in methods:
            ordered = sorted((r for r in comparisons if r["probe"] == probe["id"]), key=lambda r: (-r[method+"_tanimoto"], r["reference"]))
            nearest.extend({"probe": probe["id"], "method": method, "rank": i+1, "reference": r["reference"], "similarity": r[method+"_tanimoto"],
                            "candidate_affinity_predicted": False} for i, r in enumerate(ordered[:3]))
    for ref in config["reference_2020"]:
        for method in methods:
            candidates = [(r["id"], DataStructs.TanimotoSimilarity(fingerprints[method][ref["id"]], fingerprints[method][r["id"]]))
                          for r in config["reference_2020"] if r["id"] != ref["id"]]
            winner = sorted(candidates, key=lambda r: (-r[1], r[0]))[0]
            loo.append({"reference": ref["id"], "method": method, "nearest_other_reference": winner[0], "similarity": winner[1]})
    write_csv(args.out / "similarities.csv", comparisons)
    write_csv(args.out / "nearest_neighbors.csv", nearest)
    write_csv(args.out / "reference_leave_one_out_neighbors.csv", loo)
    descriptors = ["mw", "neutral_crippen_logp", "tpsa", "hbd", "hba", "rotatable_bonds", "aromatic_rings"]
    coverage = []
    for probe in (r for r in identities if r["role"] == "probe"):
        for descriptor in descriptors:
            values = [r[descriptor] for r in identities if r["role"] == "reference"]
            coverage.append({"probe": probe["id"], "descriptor": descriptor, "value": probe[descriptor], "reference_min": min(values), "reference_max": max(values),
                             "position": "below" if probe[descriptor] < min(values) else "above" if probe[descriptor] > max(values) else "within_marginal_range"})
    write_csv(args.out / "descriptor_coverage.csv", coverage)
    summary = {"numeric_mst_reference_structures": len(config["reference_2020"]), "probe_structures": len(config["probes"]),
               "pairwise_probe_reference_comparisons": len(comparisons), "release_compounds": len(release_rows),
               "source_table1_rows": len(selected["Table 1"]), "source_table2_rows": len(selected["Table 2"]),
               "mst_uncertainty_exceeds_estimate_count": sum(r["mst_uncertainty_exceeds_estimate"] for r in binding_rows),
               "excluded_numeric_mst": config["excluded_numeric_mst"], "nearest_by_method": [r for r in nearest if r["rank"] == 1],
               "outside_descriptor_ranges": [r for r in coverage if r["position"] != "within_marginal_range"],
               "rdkit_version": rdBase.rdkitVersion, "limits": config["limits"], "binding_predictor_fitted": False,
               "source_snapshots": provenance}
    write_json(args.out / "summary.json", summary)
    if args.plot:
        plot(config["probes"], config["reference_2020"], comparisons, nearest, args.out)
    outputs = {p.relative_to(args.out).as_posix(): {"bytes": p.stat().st_size, "sha256": file_hash(p)} for p in sorted(args.out.rglob("*")) if p.is_file()}
    write_json(args.out / "receipt.json", {"script_sha256": file_hash(Path(__file__)), "input_sha256": file_hash(args.inputs),
               "created_utc": regen.now(), "rdkit_version": rdBase.rdkitVersion, "outputs": outputs})
    print(json.dumps({"output": str(args.out), "references": len(config["reference_2020"]), "probes": len(config["probes"]), "comparisons": len(comparisons)}, indent=2))


if __name__ == "__main__":
    main()

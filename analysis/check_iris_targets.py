"""Describe a preselected target panel in the existing public adult human iris atlas."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

import anndata
import numpy as np
import pandas as pd
from scipy import sparse

PANEL = ["TYR", "OCA2", "SLC45A2", "TPCN2", "OPTN", "RCHY1", "TBK1", "MLANA", "PMEL", "MITF", "PTK2", "ITCH"]
PIGMENT = ["TYR", "OCA2", "SLC45A2", "TPCN2"]
DISPOSAL = ["OPTN", "RCHY1", "TBK1", "PTK2", "ITCH"]


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def analyze(source, collection_path, out):
    out.mkdir(parents=True, exist_ok=False)
    adata = anndata.read_h5ad(source, backed="r")
    if adata.raw is None:
        raise ValueError("The prespecified raw-count layer is unavailable.")
    for column in ["author_cell_type", "donor_id", "is_primary_data"]:
        if column not in adata.obs:
            raise ValueError("Required annotation missing: " + column)
    var = adata.raw.var
    if "feature_name" not in var:
        raise ValueError("Gene symbols unavailable.")
    features, indexes, genes = [], [], []
    for gene in PANEL:
        matches = np.flatnonzero(var["feature_name"].astype(str).to_numpy() == gene)
        entry = {"gene": gene, "n_matching_features": int(len(matches)), "status": "resolved" if len(matches) == 1 else "unresolved"}
        if len(matches) == 1:
            i = int(matches[0])
            entry.update(feature_id=str(var.index[i]), feature_is_filtered=bool(var.iloc[i].get("feature_is_filtered", False)))
            indexes.append(i)
            genes.append(gene)
        features.append(entry)
    if not indexes:
        raise ValueError("No uniquely resolved targets.")
    selected = adata.raw.X[:, indexes]
    values = selected.toarray() if sparse.issparse(selected) else np.asarray(selected)
    if values.shape != (adata.n_obs, len(genes)):
        raise ValueError("Unexpected matrix shape.")
    if not np.isfinite(values).all() or (values < 0).any() or not np.allclose(values, np.round(values), atol=1e-8):
        raise ValueError("Selected raw panel is not finite nonnegative integer counts.")
    primary = adata.obs["is_primary_data"].to_numpy() == True
    obs = adata.obs.loc[primary].copy()
    values = values[primary]
    positive = values > 0
    positions = {gene: i for i, gene in enumerate(genes)}
    rows = []
    for labels in [["author_cell_type"], ["author_cell_type", "donor_id"]]:
        for keys, indices in obs.groupby(labels, observed=True).indices.items():
            keys = (keys,) if not isinstance(keys, tuple) else keys
            context = dict(zip(labels, map(str, keys)))
            for gene, column in positions.items():
                detected = int(positive[indices, column].sum())
                rows.append({**context, "gene": gene, "n_nuclei": len(indices), "n_detected": detected,
                             "detected_fraction": detected / len(indices), "selected_raw_count_sum": int(values[indices, column].sum()),
                             "aggregation": "cell_type" if len(labels) == 1 else "cell_type_by_source_donor_label"})
    table = pd.DataFrame(rows)
    table.to_csv(out / "target_detection.csv", index=False)
    co = []
    for cell_type, indices in obs.groupby("author_cell_type", observed=True).indices.items():
        for first, second in itertools.product(PIGMENT, DISPOSAL):
            if first not in positions or second not in positions:
                continue
            both = int((positive[indices, positions[first]] & positive[indices, positions[second]]).sum())
            n_first = int(positive[indices, positions[first]].sum())
            n_second = int(positive[indices, positions[second]].sum())
            if both > min(n_first, n_second):
                raise ValueError("Co-detection exceeds marginal detection.")
            co.append({"author_cell_type": str(cell_type), "pigment_gene": first, "disposal_gene": second,
                       "n_nuclei": len(indices), "n_both_detected": both, "both_detected_fraction": both / len(indices)})
    pd.DataFrame(co).to_csv(out / "target_codetection.csv", index=False)
    cell_counts = {str(k): int(v) for k, v in obs["author_cell_type"].value_counts().items()}
    donor_counts = {str(k): int(v) for k, v in obs["donor_id"].value_counts().items()}
    if sum(cell_counts.values()) != len(obs) or sum(donor_counts.values()) != len(obs):
        raise ValueError("Annotation totals fail to reconcile.")
    by_type = table.loc[table["aggregation"] == "cell_type"]
    for gene in genes:
        if int(by_type.loc[by_type["gene"] == gene, "n_nuclei"].sum()) != len(obs):
            raise ValueError("Gene-summary denominator mismatch.")
    summary = {
        "source_accession": "GSE199013",
        "cellxgene_collection": "63d03351-06be-478e-a0db-f7a653b6b19b",
        "cellxgene_dataset": "9a281de7-cee5-4e80-8584-1929f46f152f",
        "source_bytes": source.stat().st_size,
        "source_sha256": hashlib.file_digest(source.open("rb"), "sha256").hexdigest(),
        "source_shape": list(adata.shape), "n_primary_nuclei_analyzed": len(obs),
        "n_nonprimary_excluded": int((~primary).sum()), "cell_type_counts": cell_counts,
        "source_donor_label_counts": donor_counts, "fixed_panel": features,
        "selected_count_validation": "All selected values finite, nonnegative and integer; whole transcriptome counts not audited.",
        "normalization": "Detection above zero in raw counts; no expression normalization, significance test or causal estimate.",
        "independence": "Pooled labels overlap individually named donors; source labels are not independent biological replicates.",
        "interpretation": "Transcript detection and co-detection only; no protein, activity, pigment turnover, drug response or cell-selectivity prediction.",
        "software": {"anndata": anndata.__version__, "numpy": np.__version__, "pandas": pd.__version__},
    }
    save_json(out / "summary.json", summary)
    collection = json.loads(collection_path.read_text())
    dataset = next(d for d in collection["datasets"] if d["dataset_id"] == summary["cellxgene_dataset"])
    save_json(out / "source_metadata.json", {"collection_id": summary["cellxgene_collection"],
        "collection_name": collection.get("name"), "links": collection.get("links"),
        "dataset": dataset})
    lines = ["# Adult human iris target-location check", "",
             "AI-run reanalysis of an existing public atlas. The fixed target panel preceded matrix inspection.",
             "Detection is not activity, absence of detection is not proof of absence, and nuclei are not independent people.", "",
             f"Primary nuclei analyzed: {len(obs):,}; excluded nonprimary rows: {int((~primary).sum()):,}.",
             "Raw counts were used only to distinguish detected from undetected transcripts.",
             "No donor-level significance, intervention effect, or pigment-loss rate was calculated.", "",
             "| Author cell type | Nuclei | TYR detected | OCA2 detected | OPTN detected | RCHY1 detected | TBK1 detected |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for cell_type, n in cell_counts.items():
        entries = by_type.loc[by_type["author_cell_type"] == cell_type].set_index("gene")
        cells = []
        for gene in ["TYR", "OCA2", "OPTN", "RCHY1", "TBK1"]:
            cells.append("unresolved" if gene not in entries.index else f"{100*entries.loc[gene,'detected_fraction']:.1f}%")
        lines.append("| " + cell_type + " | " + str(n) + " | " + " | ".join(cells) + " |")
    lines.extend(["", "## Source grouping", "",
                  "Individual and pooled donor labels below overlap. The six labels must not be treated as six independent donors.", ""])
    lines.extend("- " + k + ": " + str(v) + " nuclei" for k, v in donor_counts.items())
    lines.extend(["", "These results locate candidate machinery at the transcript level. They do not show that it degrades mature iris melanin.",
                  "Shared transcript detection in stromal and posterior pigment cells would make tissue selectivity a separate requirement."])
    (out / "IRIS_TARGET_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    outputs = {p.name: {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
               for p in out.iterdir() if p.is_file()}
    save_json(out / "receipt.json", {"activity": "fixed-panel human-iris raw-count detection",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "input_sha256": summary["source_sha256"], "outputs": outputs,
        "checks": ["selected count values", "gene resolution", "annotation totals", "co-detection bounds"],
        "biological_efficacy_established": False})
    adata.file.close()
    print((out / "IRIS_TARGET_REPORT.md").read_text())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--collection", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    analyze(args.input, args.collection, args.out)

"""Audit TYR assay provenance before interpreting potency; no treatment ranking."""
import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, "/lab/workbench/tools")
import regen

BASE = "https://www.ebi.ac.uk/chembl/api/data/"
TARGET = "CHEMBL1973"


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fetch_pages(endpoint, key, cache, sources):
    url = BASE + endpoint + ".json?" + urlencode({"target_chembl_id": TARGET, "limit": 1000})
    rows = []
    page = 0
    while url:
        if page >= 20:
            raise ValueError("Pagination exceeded declared bound.")
        result = regen.http_json(url)
        path = cache / f"{endpoint}-{page}.json"
        write_json(path, result)
        regen.record("iris-tyr-assay-audit", {"url": url}, [path])
        sources.append({"url": url, "path": str(path), "sha256": regen.sha256_file(path),
                        "bytes": path.stat().st_size, "included_in_repository": False})
        rows.extend(result[key])
        following = result["page_meta"]["next"]
        url = "https://www.ebi.ac.uk" + following if following else None
        page += 1
    if len(rows) != result["page_meta"]["total_count"]:
        raise ValueError("Page totals changed during retrieval.")
    return rows


def provenance_class(description, organism):
    text = description.lower()
    nonhuman = bool(re.search(r"mushroom|agaricus|b16|murine|\bmouse\b|\bmice\b|\brat\b|\bfungal\b", text))
    human = bool(re.search(r"\bhuman\b|\bhomo sapiens\b|\bhtyr\b", text))
    if nonhuman:
        return "explicit_nonhuman_or_mixed_description"
    if organism and organism != "Homo sapiens":
        return "nonhuman_assay_organism"
    if human:
        return "explicit_human_description_review_needed"
    if organism == "Homo sapiens":
        return "human_metadata_only_review_needed"
    return "species_unresolved"


def csv_file(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=False)
    sources = []
    target_url = BASE + f"target/{TARGET}.json"
    target = regen.http_json(target_url)
    target_path = args.out / "target.json"
    write_json(target_path, target)
    regen.record("iris-tyr-assay-audit", {"url": target_url}, [target_path])
    sources.append({"url": target_url, "path": "target.json", "sha256": regen.sha256_file(target_path),
                    "bytes": target_path.stat().st_size, "included_in_repository": True})
    if target["organism"] != "Homo sapiens" or not any(c["accession"] == "P14679" for c in target["target_components"]):
        raise ValueError("Unexpected target identity.")
    activities = fetch_pages("activity", "activities", args.cache, sources)
    assays = fetch_pages("assay", "assays", args.cache, sources)
    by_assay = {a["assay_chembl_id"]: a for a in assays}
    if len(by_assay) != len(assays) or len({a["activity_id"] for a in activities}) != len(activities):
        raise ValueError("Duplicate source identifiers.")
    output_rows = []
    for a in activities:
        assay = by_assay[a["assay_chembl_id"]]
        row = {k: a.get(k) for k in ["activity_id", "assay_chembl_id", "document_chembl_id", "document_year",
                "molecule_chembl_id", "molecule_pref_name", "standard_type", "standard_relation", "standard_value",
                "standard_units", "pchembl_value", "data_validity_comment", "potential_duplicate", "activity_comment"]}
        row["provenance_class"] = provenance_class(assay.get("description") or a.get("assay_description") or "", assay.get("assay_organism"))
        output_rows.append(row)
    fields = list(output_rows[0])
    csv_file(args.out / "activities.csv", fields, output_rows)
    assay_fields = ["assay_chembl_id", "document_chembl_id", "assay_type", "assay_organism", "assay_tax_id",
                    "assay_cell_type", "assay_tissue", "assay_subcellular_fraction", "bao_format", "confidence_score",
                    "relationship_type", "description", "provenance_class", "activity_count"]
    counts = Counter(a["assay_chembl_id"] for a in activities)
    for a in assays:
        a["provenance_class"] = provenance_class(a.get("description") or "", a.get("assay_organism"))
        a["activity_count"] = counts[a["assay_chembl_id"]]
    csv_file(args.out / "assays.csv", assay_fields, assays)
    human_ids = {a["assay_chembl_id"] for a in assays if a["provenance_class"] == "explicit_human_description_review_needed"}
    candidates = [a for a in activities if a["assay_chembl_id"] in human_ids]
    candidate_path = args.cache / "explicit-human-records.json"
    write_json(candidate_path, candidates)
    doc_ids = sorted({a["document_chembl_id"] for a in activities})
    doc_url = BASE + "document.json?" + urlencode({"document_chembl_id__in": ",".join(doc_ids), "limit": 1000})
    documents = regen.http_json(doc_url)
    if documents["page_meta"]["next"] or len(documents["documents"]) != len(doc_ids):
        raise ValueError("Incomplete document metadata.")
    doc_path = args.out / "documents.json"
    write_json(doc_path, documents)
    regen.record("iris-tyr-assay-audit", {"url": doc_url}, [doc_path])
    sources.append({"url": doc_url, "path": "documents.json", "sha256": regen.sha256_file(doc_path),
                    "bytes": doc_path.stat().st_size, "included_in_repository": True})
    summary = {"target": TARGET, "accession": "P14679", "retrieved_utc": regen.now(),
               "activities": len(activities), "assays": len(assays), "documents": len(doc_ids),
               "unique_molecules": len({a["molecule_chembl_id"] for a in activities}),
               "activity_provenance_classes": dict(Counter(a["provenance_class"] for a in output_rows)),
               "assay_provenance_classes": dict(Counter(a["provenance_class"] for a in assays)),
               "endpoint_types": dict(Counter(a["standard_type"] for a in activities)),
               "human_description_documents": sorted({a["document_chembl_id"] for a in candidates}),
               "human_description_assays": sorted(human_ids),
               "classification": "Conservative text/metadata triage only; human labels require manual source review. Mixed descriptions go to nonhuman/mixed.",
               "raw_snapshots": sources}
    write_json(args.out / "summary.json", summary)
    outputs = [p for p in args.out.iterdir() if p.is_file()]
    receipt = {"created_utc": regen.now(), "source_script_sha256": regen.sha256_file(Path(__file__)),
               "files": [{"path": p.name, "bytes": p.stat().st_size, "sha256": regen.sha256_file(p)} for p in sorted(outputs)]}
    write_json(args.out / "receipt.json", receipt)
    print(json.dumps({k: v for k, v in summary.items() if k != "raw_snapshots"}, indent=2))


if __name__ == "__main__":
    main()

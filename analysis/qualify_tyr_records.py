"""Attach source-review flags to the frozen TYR export without pooling potencies."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

# Classification follows these records' own title and abstract in documents.json.
# This is a declared partial source review, not an exhaustive document classifier.
KNOWN_SECONDARY = {
    "CHEMBL4411257": "Perspective/review: Inhibitors of Melanogenesis: An Updated Review",
    "CHEMBL4715852": "Review: Advances in the Design of Genuine Human Tyrosinase Inhibitors",
    "CHEMBL5241093": "Review: Recent advances in the design and discovery of synthetic tyrosinase inhibitors",
    "CHEMBL5331042": "Review: Azole inhibitors of mushroom and human tyrosinases",
    "CHEMBL5523717": "Review: Pyrrole-containing hybrids as potential anticancer agents",
}


def load_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    folder = args.input
    records = load_csv(folder / "activities.csv")
    assays = {a["assay_chembl_id"]: a for a in load_csv(folder / "assays.csv")}
    docs = {d["document_chembl_id"]: d for d in json.loads((folder / "documents.json").read_text())["documents"]}
    output = []
    for r in records:
        assay = assays[r["assay_chembl_id"]]
        doc = docs[r["document_chembl_id"]]
        r["known_secondary_source"] = r["document_chembl_id"] in KNOWN_SECONDARY
        r["description_metadata_species_conflict"] = (
            "human" in assay["description"].lower()
            and assay["assay_organism"] not in {"", "Homo sapiens"}
        )
        r["document_doi"] = doc["doi"]
        r["assay_description"] = assay["description"]
        r["assay_organism"] = assay["assay_organism"]
        output.append(r)
    path = folder / "record_flags.csv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["activity_id", "known_secondary_source", "description_metadata_species_conflict"], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(output)
    human = [r for r in output if r["provenance_class"] == "explicit_human_description_review_needed"]
    summary = {
        "records": len(output), "explicit_human_description_records": len(human),
        "explicit_human_records_in_five_known_secondary_sources": sum(r["known_secondary_source"] for r in human),
        "explicit_human_records_flagged_potential_duplicate_by_chembl": sum(r["potential_duplicate"] == "1" for r in human),
        "all_records_flagged_potential_duplicate_by_chembl": sum(r["potential_duplicate"] == "1" for r in output),
        "description_metadata_species_conflict_records": sum(r["description_metadata_species_conflict"] for r in output),
        "conflicting_assay_ids": sorted({r["assay_chembl_id"] for r in output if r["description_metadata_species_conflict"]}),
        "known_secondary_sources": KNOWN_SECONDARY,
        "known_secondary_is_exhaustive": False,
        "flags_overlap": True,
        "potencies_pooled": False,
        "meaning": "Source triage, not independent experimental counts or a qualified-eye-drug shortlist.",
    }
    (folder / "qualification_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    receipt = {"source_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "files": {p.name: {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in [folder / "activities.csv", folder / "assays.csv", folder / "documents.json",
                                   path, folder / "qualification_summary.json"]}}
    (folder / "qualification_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

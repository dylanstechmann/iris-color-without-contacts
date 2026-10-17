"""Read declared public XLSX ranges; preserve source units and replication limits."""
import argparse
import csv
import hashlib
import json
import statistics
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
SOURCES = {
    "s001": {"file": "journal.pbio.3003971.s001.xlsx", "sha256": "3c318f362f508aef8e3b2f72daefbf13010f35ce9fdd4f3fbb4f7982593ca0f4"},
    "s002": {"file": "journal.pbio.3003971.s002.xlsx", "sha256": "ce078bb7886bbf20674f5031e40c15f86d5b887d3205af7c95be1a1fe60d2f77"},
}
PANELS = [
    {"panel": "human_pigmentation_1K", "source": "s001", "sheet": "Fig 1", "start": 50, "end": 52,
     "metric": "authors_normalized_pellet_pixel_intensity", "population": "primary_neonatal_human_epidermal_melanocytes", "replication": "N=3 as supplied; independent donor count not established"},
    {"panel": "human_target_protein_S1R", "source": "s002", "sheet": "Supplementary Fig 1", "start": 81, "end": 83,
     "metric": "normalized_IP3R2_protein_signal", "population": "primary_neonatal_human_epidermal_melanocytes", "replication": "N=3 as supplied; independent donor count not established"},
    {"panel": "B16_energy_5K", "source": "s001", "sheet": "Fig 5", "start": 3939, "end": 3950,
     "metric": "ADP_ATP_ratio", "population": "B16_mouse_melanoma_cells", "replication": "12 wells per group; biological experiment independence not established"},
]


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def worksheet(path, name):
    with zipfile.ZipFile(path) as archive:
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = book.find("s:sheets", NS)
        sheet = next(s for s in sheets if s.attrib["name"] == name)
        relation = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        links = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        target = next(r.attrib["Target"] for r in links if r.attrib["Id"] == relation)
        member = target.lstrip("/") if target.startswith("/") else "xl/" + target
        tree = ET.fromstring(archive.read(member))
        return {c.attrib["r"]: c for c in tree.findall(".//s:sheetData/s:row/s:c", NS)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    for spec in SOURCES.values():
        path = args.input / spec["file"]
        if hash_file(path) != spec["sha256"]:
            raise ValueError("Source differs from declared workbook snapshot.")
        spec["bytes"] = path.stat().st_size
        spec["url"] = "https://doi.org/10.1371/journal.pbio.3003971." + path.stem.rsplit(".", 1)[1]
    observations, summaries = [], []
    for panel in PANELS:
        cells = worksheet(args.input / SOURCES[panel["source"]]["file"], panel["sheet"])
        groups = {}
        for column, group in [("B", "control"), ("C", "siIP3R2")]:
            values = []
            for row in range(panel["start"], panel["end"] + 1):
                coordinate = f"{column}{row}"
                cell = cells[coordinate]
                if cell.find("s:f", NS) is not None or cell.attrib.get("t", "n") != "n":
                    raise ValueError("Expected literal source number.")
                value = float(cell.find("s:v", NS).text)
                values.append(value)
                observations.append({"panel": panel["panel"], "source": panel["source"], "sheet": panel["sheet"],
                                     "cell": coordinate, "group": group, "value": value, "metric": panel["metric"]})
            groups[group] = {"n_observations": len(values), "mean": statistics.mean(values), "sample_sd": statistics.stdev(values)}
        summaries.append({**panel, "groups": groups,
                          "ratio_of_group_means": groups["siIP3R2"]["mean"] / groups["control"]["mean"]})
    with (args.out / "observations.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(observations[0]))
        writer.writeheader()
        writer.writerows(observations)
    summary = {"source_doi": "10.1371/journal.pbio.3003971", "sources": SOURCES, "panels": summaries,
               "limits": ["Descriptive arithmetic only; no new significance tests.", "Normalized controls equal to one do not establish zero biological variation.",
                          "Pellet image intensity is not mature melanin mass, optical eye color, or a pigment-loss rate.",
                          "siRNA knockdown is not an ocular drug response or a withdrawal/recovery experiment."]}
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    receipt = {"source_script_sha256": hash_file(Path(__file__)),
               "files": {p.name: {"bytes": p.stat().st_size, "sha256": hash_file(p)} for p in sorted(args.out.iterdir())}}
    (args.out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({p["panel"]: p["ratio_of_group_means"] for p in summaries}, indent=2))


if __name__ == "__main__":
    main()

"""Fetch the declared primary ampyrone sources using Regen provenance helpers."""
import argparse
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, "/lab/workbench/tools")
import regen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    sources = {
        "main.xml": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13502167/fullTextXML",
        "supporting-data.xlsx": "https://df6sxcketz7bb.cloudfront.net/manuscripts/202000/202947/jci.insight.202947.sdval.xlsx",
    }
    receipt = []
    for name, url in sources.items():
        path = args.cache / name
        if not path.exists():
            data = regen.http_bytes(url)
            if name.endswith(".xlsx") and not data.startswith(b"PK"):
                raise ValueError(f"Not an XLSX response: {url}")
            path.write_bytes(data)
            regen.record("iris_ampyrone_source_fetch", {"url": url}, [path])
        receipt.append({"file": name, "url": url, "bytes": path.stat().st_size,
                        "sha256": regen.sha256_file(path)})
    (args.cache / "source_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    tree = ET.parse(args.cache / "main.xml")
    print(json.dumps({"sources": receipt, "supplement_links": [s.attrib for s in tree.findall(".//supplementary-material//media")]}, indent=2))
    with zipfile.ZipFile(args.cache / "supporting-data.xlsx") as archive:
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        print([s.attrib["name"] for s in book.find("{*}sheets")])


if __name__ == "__main__":
    main()

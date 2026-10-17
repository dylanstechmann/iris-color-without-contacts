"""Retrieve a bounded set of primary withdrawal sources through Regen."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree as ET

sys.path.insert(0, "/lab/workbench/tools")
import regen


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    sources = []
    for name, query in [("thiamidol2018", 'DOI:"10.1016/j.jid.2018.01.019"'),
                        ("thiamidol2021", 'DOI:"10.1111/1346-8138.16080"'),
                        ("kt939", "EXT_ID:41159291 AND SRC:MED")]:
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=" + quote(query) + "&format=json&resultType=core"
        path = args.cache / (name + ".metadata.json")
        if not path.exists():
            path.write_text(json.dumps(regen.http_json(url), indent=2) + "\n", encoding="utf-8")
            regen.record("iris_withdrawal_metadata_fetch", {"url": url}, [path])
        data = json.loads(path.read_text())
        sources.append({"file": path.name, "url": url, "bytes": path.stat().st_size,
                        "sha256": digest(path), "representation": "serialized API JSON, not wire bytes"})
        results = data.get("resultList", {}).get("result", [])
        if len(results) != 1:
            raise ValueError(f"Expected exactly one source for {name}; found {len(results)}")
        record = results[0]
        print(json.dumps({"name": name, "pmid": record.get("id"), "pmcid": record.get("pmcid"),
                          "doi": record.get("doi"), "title": record.get("title")}))
        if record.get("pmcid"):
            xmlpath = args.cache / (name + ".xml")
            xmlurl = "https://www.ebi.ac.uk/europepmc/webservices/rest/" + record["pmcid"] + "/fullTextXML"
            if not xmlpath.exists():
                raw = regen.http_bytes(xmlurl)
                ET.fromstring(raw)
                xmlpath.write_bytes(raw)
                regen.record("iris_withdrawal_fulltext_fetch", {"url": xmlurl}, [xmlpath])
            sources.append({"file": xmlpath.name, "url": xmlurl, "bytes": xmlpath.stat().st_size,
                            "sha256": digest(xmlpath), "representation": "XML response bytes"})
    publisher_url = "https://onlinelibrary.wiley.com/doi/10.1111/1346-8138.16080"
    htmlpath = args.cache / "thiamidol2021.publisher.html"
    if not htmlpath.exists():
        try:
            raw = regen.http_bytes(publisher_url)
            if b"16.2" not in raw or b"regression" not in raw:
                raise ValueError("Response did not expose expected source content")
            htmlpath.write_bytes(raw)
            regen.record("iris_withdrawal_publisher_fetch", {"url": publisher_url}, [htmlpath])
        except Exception as exc:
            print(json.dumps({"publisher_snapshot_unavailable": type(exc).__name__,
                              "use": "verified web tool primary full text; no downloaded snapshot asserted"}))
    if htmlpath.exists():
        sources.append({"file": htmlpath.name, "url": publisher_url, "bytes": htmlpath.stat().st_size,
                        "sha256": digest(htmlpath), "representation": "publisher HTML response bytes"})
    (args.cache / "source_receipt.json").write_text(json.dumps(sources, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

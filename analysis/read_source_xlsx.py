"""Read XLSX values and coordinates without editing the source workbook."""
import argparse
import json
import posixpath
import zipfile
from xml.etree import ElementTree as ET

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def read_book(path):
    result = {}
    with zipfile.ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = ["".join(t.itertext()) for t in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        links = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relations = {r.attrib["Id"]: r.attrib["Target"] for r in links}
        for sheet in book.find("s:sheets", NS):
            rel = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target = relations[rel]
            member = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            tree = ET.fromstring(archive.read(member))
            cells = {}
            for cell in tree.findall(".//s:sheetData/s:row/s:c", NS):
                raw = cell.find("s:v", NS)
                typ = cell.attrib.get("t", "n")
                value = raw.text if raw is not None else None
                if typ == "s" and value is not None:
                    value = strings[int(value)]
                elif typ == "inlineStr":
                    value = "".join(cell.find("s:is", NS).itertext())
                elif typ == "n" and value is not None:
                    value = float(value)
                if value is not None:
                    cells[cell.attrib["r"]] = {"value": value, "type": typ,
                        "formula": cell.findtext("s:f", default=None, namespaces=NS)}
            result[sheet.attrib["name"]] = cells
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file")
    parser.add_argument("--sheets", nargs="*")
    parser.add_argument("--max-rows", type=int, default=80)
    args = parser.parse_args()
    for name, cells in read_book(args.file).items():
        if args.sheets and name not in args.sheets:
            continue
        rows = {}
        for coord, cell in cells.items():
            row = int("".join(c for c in coord if c.isdigit()))
            rows.setdefault(row, []).append(f"{coord}={cell['value']}")
        print(name, len(cells), "nonempty cells", len(rows), "rows")
        for row in list(rows)[:args.max_rows]:
            print(" | ".join(rows[row])[:1200])

"""Extract reported withdrawal points and retain their endpoint limitations."""
import argparse
import csv
import hashlib
import json
import platform
import re
from pathlib import Path
from xml.etree import ElementTree as ET


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--clinical-inputs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    sources = json.loads((args.cache / "source_receipt.json").read_text())
    xmlpath = args.cache / "kt939.xml"
    spec = next(s for s in sources if s["file"] == xmlpath.name)
    if digest(xmlpath) != spec["sha256"]:
        raise ValueError("Source does not match intake receipt")
    tree = ET.parse(xmlpath)
    paragraphs = [" ".join(" ".join(p.itertext()).split()) for p in tree.findall(".//p")]
    paragraph = next(p for p in paragraphs if "melanin inhibition rate was" in p and "drug withdrawal" in p)
    lower = re.search(r"rate was ([\d.]+)% on day 3 and ([\d.]+)% on day 5, returning to baseline after (\w+) days", paragraph)
    higher = re.search(r"inhibition rates were ([\d.]+)% and ([\d.]+)% on days 3 and 5, and ([\d.]+)% and ([\d.]+)% on days 7 and 9", paragraph)
    end = re.search(r"normal levels after (\d+) days of drug withdrawal", paragraph)
    if not lower or not higher or not end or lower.group(3) != "seven" or end.group(1) != "11":
        raise ValueError("Source narrative changed; inspect before extracting")
    rows = []
    for condition, concentration, days, values in [
        ("lower_prior_cell_exposure", 1, [3, 5], lower.groups()[:2]),
        ("higher_prior_cell_exposure", 10, [3, 5, 7, 9], higher.groups())]:
        for day, value in zip(days, values):
            rows.append({"compound": "KT-939", "condition": condition,
                         "prior_cell_culture_concentration_uM": concentration,
                         "days_after_withdrawal": day, "authors_reported_inhibition_percent": float(value),
                         "endpoint": "bulk_A405_pigment_per_protein; inhibition_denominator_not_explicit",
                         "population": "human_MNT1_melanoma_cells", "source": "10.1111/jocd.70510 Results 3.3 and Figure 4"})
    clinical = json.loads(args.clinical_inputs.read_text())
    clinical_rows = [{"phase": "active", "weeks_since_start": week,
        "thiamidol_regimen_MASI_change": active, "vehicle_regimen_MASI_change": vehicle,
        "difference_of_mean_changes": active - vehicle}
        for week, active, vehicle in zip(clinical["active_weeks"], clinical["thiamidol_regimen_mean_changes"], clinical["vehicle_regimen_mean_changes"])]
    follow = clinical["followup"]
    follow_gap = follow["thiamidol_regimen_mean_change_from_baseline"] - follow["vehicle_regimen_mean_change_from_baseline"]
    args.out.mkdir(parents=True, exist_ok=False)
    for name, data in [("kt939_reported_points.csv", rows), ("clinical_descriptive_contrasts.csv", clinical_rows)]:
        with (args.out / name).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    write_json(args.out / "sources.json", sources)
    write_json(args.out / "clinical_inputs.json", clinical)
    summary = {"kt939": {"doi": "10.1111/jocd.70510", "pmcid": "PMC12569736", "pre_exposure_days": 6,
        "numeric_points_extracted": len(rows), "population": "human_MNT1_melanoma_cells",
        "qualitative_recovery_reports": [
            {"condition": "lower_prior_cell_exposure", "days_after_withdrawal": 7, "authors_wording": "returning to baseline", "numeric_inhibition_percent": None},
            {"condition": "higher_prior_cell_exposure", "days_after_withdrawal": 11, "authors_wording": "fully returned to normal levels", "numeric_inhibition_percent": None}],
        "limits": ["Bulk content per protein is not new synthesis flux or mature-polymer chemical mass balance.",
                   "Inhibition denominator is not explicit; percentages were not converted to recovered mass fractions.",
                   "Normal primary human melanocytes and iris cells were not used for this withdrawal experiment.",
                   "No paired free-compound, TYR-activity, old-pigment tracking or cell-division measurements during withdrawal are supplied.",
                   "Separate 72-hour viability measurement does not cover the full six-day exposure plus withdrawal sequence.",
                   "hTYR inhibition in this paper uses MNT1 crude lysate, not purified recombinant human enzyme.",
                   "Raw data are available on request; the parsed narrative supplies no point-specific uncertainties."]},
        "clinical": {"doi": clinical["source_doi"], "endpoint": clinical["endpoint"],
            "week24_difference_of_mean_MASI_changes": clinical_rows[-1]["difference_of_mean_changes"],
            "variable_time_followup_difference_of_mean_MASI_changes": follow_gap,
            "followup_weeks_after_cessation": [13, 20], "limits": clinical["limits"]},
        "fit_status": "No PK, source-recovery, pigment-loss or iris time constants fitted."}
    write_json(args.out / "summary.json", summary)
    receipt = {"script_sha256": digest(Path(__file__)), "clinical_inputs_sha256": digest(args.clinical_inputs),
               "python": platform.python_version(), "kt939_source_xml_sha256": spec["sha256"],
               "selected_source_paragraph_sha256": hashlib.sha256(paragraph.encode()).hexdigest(),
               "outputs": {p.name: {"bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(args.out.iterdir())}}
    write_json(args.out / "receipt.json", receipt)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

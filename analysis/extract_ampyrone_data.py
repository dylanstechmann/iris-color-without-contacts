"""Extract declared ampyrone readouts without changing their endpoint meanings."""
import argparse
import csv
import hashlib
import json
import platform
import statistics
from pathlib import Path

from read_source_xlsx import read_book

SOURCE_SHA256 = "91ead86457a85cbfda800548b583e07ad18755e6fad7c11e35a71ba44363782f"
SOURCE_URL = "https://df6sxcketz7bb.cloudfront.net/manuscripts/202000/202947/jci.insight.202947.sdval.xlsx"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot(groups, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "svg.hashsalt": "iris-ampyrone-readouts"})
    fig, axes = plt.subplots(1, 3, figsize=(13.3, 5.2), layout="constrained")
    for ax, ids, title, ylabel in [
        (axes[0], ["human_C4_scatter", "human_1125_scatter"], "Human melanocyte lines", "Mean 355-nm scatter / matched control mean"),
        (axes[1], ["skin_TYRP1", "skin_FM"], "Reconstructed human epidermis", "Image metric / negative-control mean"),
    ]:
        for x, gid in enumerate(ids):
            spec = next(g for g in groups if g["id"] == gid)
            control = spec["groups"]["control"]["mean"]
            for shift, name, color in [(-.12, "control", "#63758b"), (.12, "ampyrone", "#bb5a2f")]:
                values = [v / control for v in spec["groups"][name]["values"]]
                ax.scatter([x + shift] * len(values), values, color=color, s=27, alpha=.8,
                           label=name if x == 0 else None)
                mean = statistics.mean(values)
                ax.plot([x + shift - .08, x + shift + .08], [mean, mean], color=color, lw=2)
        ax.set_xticks(range(len(ids)), [next(g for g in groups if g["id"] == i)["plot_label"] for i in ids])
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.axhline(1, color="#aaa", ls="--", lw=.8)
        ax.set_ylim(bottom=0)
        ax.spines[["top", "right"]].set_visible(False)
    for metabolite, color in [("tyrosine", "#63758b"), ("DHICA", "#bb5a2f"), ("DHI", "#376a52")]:
        subset = [g for g in groups if g["id"].startswith("mouse_" + metabolite + "_")]
        axes[2].plot([g["time_min"] for g in subset], [g["ratio_of_means"] for g in subset],
                     "o-", label=metabolite, color=color)
    axes[2].set(title="Mouse-cell isotope tracing", xlabel="Time (minutes)",
                ylabel="Labeled metabolite ion count / control mean")
    axes[2].axhline(1, color="#aaa", ls="--", lw=.8)
    axes[2].set_ylim(bottom=0)
    axes[2].spines[["top", "right"]].set_visible(False)
    axes[0].legend(frameon=False, fontsize=8)
    axes[2].legend(frameon=False, fontsize=8)
    fig.suptitle("Ampyrone: human-cell, skin and mouse-cell readouts", fontsize=15)
    fig.supxlabel("Points in left/center panels are supplied values, not independent donors. No panel measures iris color or withdrawal recovery.", fontsize=9)
    fig.savefig(out / "ampyrone_readouts.svg", metadata={"Date": None})
    fig.savefig(out.parent / "ampyrone-readouts-preview.png", dpi=145)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    if digest(args.input) != SOURCE_SHA256:
        raise ValueError("Workbook differs from declared source snapshot.")
    args.out.mkdir(parents=True, exist_ok=False)
    book = read_book(args.input)
    observations, groups = [], []

    def number(sheet, coord):
        cell = book[sheet][coord]
        if cell["formula"] is not None or cell["type"] != "n":
            raise ValueError(f"Expected literal numeric source value: {sheet}!{coord}")
        return cell["value"]

    def group(gid, sheet, mapping, metric, population, replication, **extra):
        result = {"id": gid, "sheet": sheet, "metric": metric, "population": population,
                  "replication": replication, **extra, "groups": {}}
        for name, coords in mapping.items():
            values = [number(sheet, c) for c in coords if c in book[sheet]]
            actual = [c for c in coords if c in book[sheet]]
            for coord, value in zip(actual, values):
                observations.append({"id": gid, "sheet": sheet, "cell": coord, "group": name,
                                     "value": value, "metric": metric, "population": population})
            result["groups"][name] = {"cells": actual, "n_supplied_values": len(values),
                "n_unique_values": len(set(values)), "values": values, "mean": statistics.mean(values),
                "sample_sd_of_supplied_values": statistics.stdev(values) if len(values) > 1 else None}
        result["ratio_of_means"] = result["groups"]["ampyrone"]["mean"] / result["groups"]["control"]["mean"]
        groups.append(result)

    for metabolite, controlcols, ampcols in [("tyrosine", ["C", "D", "E", "F"], ["G", "H", "I", "J"]),
            ("DHICA", ["M", "N", "O", "P"], ["Q", "R", "S", "T"]),
            ("DHI", ["W", "X", "Y", "Z"], ["AA", "AB", "AC", "AD"])]:
        for row, time in [(3, 20), (4, 60), (5, 180)]:
            group(f"mouse_{metabolite}_{time}", "Figure 5",
                  {"control": [f"{c}{row}" for c in controlcols], "ampyrone": [f"{c}{row}" for c in ampcols]},
                  "13C_labeled_ion_counts", "mouse_melan_ink4a_null_melanocytes",
                  "3 or 4 supplied values per condition; exact biological independence not assigned in workbook",
                  time_min=time, metabolite=metabolite)
    for gid, control, amp, label in [("human_C4_scatter", "AK", "AL", "WT C4"),
                                     ("human_1125_scatter", "AR", "AS", "OCA1B 1125")]:
        group(gid, "Figure 5", {"control": [f"{control}{r}" for r in [2, 3]],
                                  "ampyrone": [f"{amp}{r}" for r in [2, 3]]},
              "mean_355nm_scatter", "human_epidermal_melanocyte_line",
              "2 supplied mean-scatter values per condition; cells/events are not independent replicates",
              plot_label=label)
    for gid, cols, metric, label in [("skin_TYRP1", ["B", "C", "A"], "authors_TYRP1_image_metric", "TYRP1"),
            ("skin_FM", ["E", "F", "D"], "Fontana_Masson_area_percent", "FM area")]:
        group(gid, "Figure 6", {name: [f"{c}{r}" for r in range(3, 9)]
              for name, c in zip(["control", "ampyrone", "positive"], cols)}, metric,
              "reconstructed_human_epidermis", "6 supplied values; legend: duplicates, 3 replicates; nesting and donor independence unassigned",
              plot_label=label)

    curves = []
    for panel, variant, xcol, ccol, acol, end in [("diphenolase", "WT", "A", "B", "D", 9),
            ("diphenolase", "P406L", "F", "G", "I", 9),
            ("monophenolase", "WT", "K", "L", "N", 8),
            ("monophenolase", "P406L", "P", "Q", "S", 8)]:
        for row in range(3, end + 1):
            c, a = number("Figure 2", f"{ccol}{row}"), number("Figure 2", f"{acol}{row}")
            curves.append({"reaction": panel, "variant": variant, "substrate_mM": number("Figure 2", f"{xcol}{row}"),
                           "control_source_mean": c, "ampyrone_source_mean": a, "ratio_of_means": a / c,
                           "source_cells": f"Figure 2!{xcol}{row},{ccol}{row},{acol}{row}",
                           "endpoint": "authors_absorbance_derived_rate; not independently identified product"})
    issues = [
        {"issue": "exactly_duplicated_DHI_values", "cells": "Figure 5!Y4=Z4; AC4=AD4; Y5=Z5; AC5=AD5",
         "handling": "retained verbatim; cannot establish whether repeated observations, processing or transcription"},
        {"issue": "duplicated_histogram_label", "cells": "Figure 5!AG2,AH2 both control 2",
         "handling": "no relabeling; selected supplied mean-scatter values separately"},
        {"issue": "S12_numeric_scope", "cells": "Figure S12!A1:G1025",
         "handling": "only one histogram block; no separately labeled means for supplemental panels B/C. No reconstructed extra-cell-line results"},
        {"issue": "isotope_timepoint_conflict", "cells": "Figure 5!B3:B5,L3:L5,V3:V5",
         "handling": "workbook and figure show 20/60/180 minutes, whereas Methods states 20/40/60; follow explicit workbook labels and retain discrepancy"},
        {"issue": "Figure2_mean_SD_only", "cells": "Figure 2!A1:T9",
         "handling": "means and adjacent dispersion values supplied, not replicate-level curves; no new kinetic fit or uncertainty inference"},
    ]
    write_csv(args.out / "observations.csv", observations)
    write_csv(args.out / "enzyme_curve_means.csv", curves)
    write_json(args.out / "source_issues.json", issues)
    write_json(args.out / "sources.json", json.loads(args.input.with_name("source_receipt.json").read_text()))
    summary = {"source_doi": "10.1172/jci.insight.202947", "source_url": SOURCE_URL,
               "source_sha256": SOURCE_SHA256, "source_bytes": args.input.stat().st_size,
               "sheets": {name: {"nonempty_cells": len(cells)} for name, cells in book.items()},
               "groups": groups, "limits": ["Descriptive arithmetic only; no new significance tests.",
               "Ratios compare matched means within an endpoint. Ratios across endpoints are not interchangeable.",
               "Neither scatter, TYRP1 nor labeled intermediate abundance directly measures mature melanin mass.",
               "No iris efficacy, withdrawal recovery or repeated pigmentation cycle in the source."]}
    write_json(args.out / "summary.json", summary)
    if args.plot:
        plot(groups, args.out)
    receipt = {"python": platform.python_version(), "source_workbook_sha256": SOURCE_SHA256,
               "analysis_scripts": {p.name: digest(p) for p in [Path(__file__), Path(__file__).with_name("read_source_xlsx.py")]},
               "outputs": {p.name: {"bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(args.out.iterdir())}}
    write_json(args.out / "receipt.json", receipt)
    print(json.dumps({g["id"]: g["ratio_of_means"] for g in groups}, indent=2))


if __name__ == "__main__":
    main()

"""Explore production, added loss, persistent pigment, and recovery as hypotheses."""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import platform
from pathlib import Path


def loss_rate(half_life):
    if half_life is None:
        return 0.0
    if not math.isfinite(half_life) or half_life <= 0:
        raise ValueError("Half-life must be positive and finite, or null.")
    return math.log(2) / half_life


def mobile_at(t, f, k0, a):
    rate = k0 + a
    if rate == 0:
        return 1.0
    equilibrium = f * k0 / rate
    return equilibrium + (1 - equilibrium) * math.exp(-rate * t)


def total_at(t, f, k0, a, p):
    return p + (1 - p) * mobile_at(t, f, k0, a)


def target_time(target, f, k0, a, p):
    if target >= 1:
        return 0.0
    rate = k0 + a
    if p == 1 or rate == 0:
        return None
    equilibrium = f * k0 / rate
    goal = (target - p) / (1 - p)
    if goal <= equilibrium or equilibrium >= 1:
        return None
    return math.log((1 - equilibrium) / (goal - equilibrium)) / rate


def recovery_time(target, mobile_start, k0, p, synthesis_factor=1):
    if p + (1 - p) * mobile_start >= target:
        return 0.0
    if p == 1 or k0 == 0:
        return None
    goal = (target - p) / (1 - p)
    if goal >= synthesis_factor:
        return None
    return math.log((synthesis_factor - mobile_start) / (synthesis_factor - goal)) / k0


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def run(config, out, make_plot):
    out.mkdir(parents=True, exist_ok=False)
    grid = itertools.product(
        config["baseline_pigment_half_life_years"],
        config["synthesis_remaining_fraction"],
        config["added_loss_half_life_years"],
        config["persistent_fraction"],
    )
    rows = []
    for h, f, added_h, p in grid:
        if not 0 <= f <= 1 or not 0 <= p <= 1:
            raise ValueError("Production and persistent fractions must be in [0,1].")
        k0, a = loss_rate(h), loss_rate(added_h)
        row = {"baseline_half_life_years": h, "synthesis_remaining_fraction": f,
               "added_loss_half_life_years": added_h, "persistent_fraction": p,
               "baseline_loss_rate_per_year": k0, "added_loss_rate_per_year": a,
               "limiting_inventory_fraction_if_assumptions_persist":
                   p + (1 - p) * f * k0 / (k0 + a) if k0 + a else 1.0}
        for t in config["observation_years"]:
            row["inventory_fraction_year_" + str(t)] = total_at(t, f, k0, a, p)
        for target in config["pigment_inventory_targets"]:
            row["years_to_inventory_" + str(round(100 * target)) + "pct"] = target_time(target, f, k0, a, p)
        start = mobile_at(config["withdrawal_after_years"], f, k0, a)
        for factor in config["recovery_synthesis_factors"]:
            row["withdrawal_years_to_90pct_at_source_factor_" + str(factor)] = recovery_time(
                config["recovery_inventory_target"], start, k0, p, factor)
        rows.append(row)
    with (out / "scenario_sweep.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    examples = []
    for label, h, f, added_h, p in [
        ("slow native loss; suppression alone", 20, .05, None, 0),
        ("slow native loss; suppression plus added loss", 20, .05, 3, 0),
        ("same combined mechanism; persistent pool", 20, .05, 3, .3),
        ("added loss alone; synthesis unchanged", 20, 1, 3, 0),
        ("fast native loss; suppression alone", 1, .05, None, 0),
        ("no native loss; new loss pathway", None, .05, 3, 0),
    ]:
        found = next(r for r in rows if r["baseline_half_life_years"] == h
                     and r["synthesis_remaining_fraction"] == f
                     and r["added_loss_half_life_years"] == added_h and r["persistent_fraction"] == p)
        examples.append({"label": label, **found})
    write_json(out / "summary.json", {
        "activity": "Analytical hypothetical pigment balance",
        "scenario_count": len(rows), "examples": examples,
        "null_time_means": "Threshold is not reached in finite time under the stated continuing assumptions.",
        "interpretation": "No measured iris rates, drug-to-rate mapping, efficacy probability, tissue delivery or eye-color prediction.",
    })
    lines = ["# Hypothetical pigment feasibility sweep", "",
             "All parameters are assumptions. Inventory percentages do not map to eye colors.", "",
             "Mobile pigment is normalized to its own starting value. Baseline synthesis equals k0.",
             "During modulation: dm/dt = f*k0 - (k0+a)*m.",
             "After withdrawal: dm/dt = b*k0 - k0*m. Total inventory = p+(1-p)*m.", "",
             "The source is kept at its original baseline when added loss changes. This prevents an accelerated",
             "loss pathway from silently increasing pigment production.", "",
             "| Hypothetical case | Inventory at year 7 | Years to 25% inventory | Years after withdrawal to 90%, original source |",
             "| --- | ---: | ---: | ---: |"]
    for ex in examples:
        fmt = lambda x: "not reached" if x is None else f"{x:.2f}"
        lines.append(f"| {ex['label']} | {100*ex['inventory_fraction_year_7']:.1f}% | "
                     f"{fmt(ex['years_to_inventory_25pct'])} | {fmt(ex['withdrawal_years_to_90pct_at_source_factor_1'])} |")
    lines.extend(["", "A fivefold recovery-source comparison is in the CSV. It is a hypothetical control lever.",
                  "Keeping an increased source active could overshoot baseline; this is not a maintenance regimen.", "",
                  "A persistent fraction sets a floor only while it stays persistent. Whole-eye cell renewal is not assumed.",
                  "A null native half-life models a stored pool with no baseline flux, not a measured iris state.", "",
                  f"Scenarios: {len(rows)}. The grid is unweighted; counts are not probabilities of success."])
    (out / "MODEL_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if make_plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.6), layout="constrained")
        hs, fs = [1, 3, 7, 20, 100], [0, .05, .1, .25, .5, 1]
        for ax, added_h, title in zip(axes, [None, 3], ["Synthesis control only", "Same source + hypothetical added loss"]):
            data = np.array([[100 * total_at(7, f, loss_rate(h), loss_rate(added_h), 0) for f in fs] for h in hs])
            image = ax.imshow(data, vmin=0, vmax=100, cmap="cividis", aspect="auto")
            ax.set_xticks(range(len(fs)), [str(round(f*100)) for f in fs])
            ax.set_yticks(range(len(hs)), [str(h) for h in hs])
            ax.set_xlabel("Synthesis remaining (% of baseline)")
            ax.set_ylabel("Assumed native pigment half-life (years)")
            ax.set_title(title)
            for i in range(len(hs)):
                for j in range(len(fs)):
                    ax.text(j, i, f"{data[i,j]:.0f}", ha="center", va="center",
                            color="white" if data[i,j] < 45 else "black")
        fig.colorbar(image, ax=axes, label="Inventory remaining after 7 years (%)")
        fig.suptitle("Hypothetical pigment balance; no persistent pool\nAdded pathway half-life = 3 years in right panel; no eye-color prediction")
        fig.savefig(out / "hypothetical_balance.svg")
        plt.close(fig)
    files = {}
    for path in sorted(out.iterdir()):
        if path.is_file():
            blob = path.read_bytes()
            files[path.name] = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
    source = Path(__file__).resolve()
    write_json(out / "receipt.json", {
        "model_status": "hypothetical", "python": platform.python_version(),
        "assumptions": config, "script_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "scenario_count": len(rows), "outputs": files,
    })
    print(json.dumps({"scenarios": len(rows), "output": str(out), "measured_iris_parameters": False}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assumptions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    run(json.loads(args.assumptions.read_text(encoding="utf-8")), args.out, args.plot)

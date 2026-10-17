"""Calculate an exact counterexample to inferring pigment mechanisms from curves."""
import argparse
import csv
import hashlib
import json
import math
import platform
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def calculate(case, lam, duration, time, phase):
    p = case["persistent_fraction"]
    k = lam * case["native_loss_fraction_of_lambda"]
    a = lam * case["added_loss_fraction_of_lambda"]
    f = case["synthesis_fraction"]
    rate = k + a
    eq = f * k / rate
    active_time = time if phase == "active" else duration
    mobile = eq + (1 - eq) * math.exp(-rate * active_time)
    old_mobile = math.exp(-rate * active_time)
    if phase == "withdrawal":
        mobile = mobile * math.exp(-k * time) - math.expm1(-k * time)
        old_mobile *= math.exp(-k * time)
    return {"case": case["id"], "phase": phase, "time_in_phase_hypothetical_years": time,
            "total_inventory": p + (1 - p) * mobile,
            "old_inventory": p + (1 - p) * old_mobile,
            "persistent_old_inventory": p,
            "mobile_old_inventory": (1 - p) * old_mobile,
            "new_inventory": (1 - p) * (mobile - old_mobile),
            "new_source_relative_to_own_baseline": f if phase == "active" else 1,
            "absolute_new_source_in_total_baseline_units_per_hypothetical_year": (1 - p) * k * (f if phase == "active" else 1),
            "native_loss_per_hypothetical_year": k,
            "added_loss_per_hypothetical_year": a if phase == "active" else 0}


def plot(rows, config, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "svg.hashsalt": "iris-recovery-identifiability"})
    fig, axes = plt.subplots(1, 3, figsize=(13.7, 5.2), layout="constrained")
    active = [r for r in rows if r["case"] == "A" and r["phase"] == "active"]
    axes[0].plot([r["time_in_phase_hypothetical_years"] for r in active],
                 [r["total_inventory"] for r in active], color="#29394c", lw=2.6)
    axes[0].text(.97, .9, "A, B and C coincide exactly", ha="right", transform=axes[0].transAxes)
    axes[0].set(title="Same inventory during drug action", xlabel="Hypothetical years of action", ylabel="Total pigment / initial pigment")
    for case, label, color in [("A", "A and B coincide", "#29394c"), ("C", "C: slower native recovery", "#298065")]:
        after = [r for r in rows if r["case"] == case and r["phase"] == "withdrawal"]
        axes[1].plot([r["time_in_phase_hypothetical_years"] for r in after],
                     [r["total_inventory"] for r in after], label=label, color=color, lw=2.5)
    axes[1].set(title="Withdrawal separates only some causes", xlabel="Hypothetical years after withdrawal", ylabel="Total pigment / initial pigment")
    axes[1].legend(frameon=False, loc="lower right", fontsize=9)
    endpoints = [next(r for r in rows if r["case"] == c["id"] and r["phase"] == "withdrawal"
                     and r["time_in_phase_hypothetical_years"] == 0) for c in config["cases"]]
    base = [0., 0., 0.]
    for field, label, color in [("persistent_old_inventory", "Persistent old", "#63758b"),
                              ("mobile_old_inventory", "Mobile old", "#c17b39"),
                              ("new_inventory", "Made during action", "#298065")]:
        values = [r[field] for r in endpoints]
        axes[2].bar(range(3), values, bottom=base, label=label, color=color, width=.6)
        base = [b + v for b, v in zip(base, values)]
    axes[2].set(title="Same endpoint, different pigment age", ylabel="Inventory at withdrawal / initial", xticks=range(3),
                xticklabels=["A\nFixed pool", "B\nPartial source", "C\nAdded loss"])
    axes[2].legend(frameon=False, fontsize=8, loc="upper right")
    for ax in axes:
        ax.set_ylim(0, 1.06)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Which cause can a pigment curve actually identify?", fontsize=15)
    fig.supxlabel("Constructed mathematical example. All rates and times are hypothetical; no iris rates, drug doses or eye colors are fitted.", fontsize=9)
    fig.savefig(out / "recovery_identifiability.svg", metadata={"Date": None})
    fig.savefig(out.parent / "recovery-identifiability-preview.png", dpi=145)
    plt.close(fig)
    return matplotlib.__version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assumptions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.assumptions.read_text())
    lam = math.log(2) / config["reference_active_loss_half_life_hypothetical_years"]
    duration = config["active_duration_hypothetical_years"]
    step = config["sample_step_hypothetical_years"]
    rows = []
    for c in config["cases"]:
        for phase, end in [("active", duration), ("withdrawal", config["withdrawal_observation_hypothetical_years"])]:
            n = round(end / step)
            if not math.isclose(n * step, end):
                raise ValueError("Sampling must end at the exact declared horizon")
            rows.extend(calculate(c, lam, duration, i * step, phase) for i in range(n + 1))
    args.out.mkdir(parents=True, exist_ok=False)
    write_json(args.out / "assumptions.json", config)
    with (args.out / "trajectories.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    maps = {c["id"]: {(r["phase"], r["time_in_phase_hypothetical_years"]): r for r in rows if r["case"] == c["id"]}
            for c in config["cases"]}
    overlap = max(abs(maps["A"][key]["total_inventory"] - maps[c][key]["total_inventory"])
                  for key in maps["A"] if key[0] == "active" for c in ["B", "C"])
    withdrawal_overlap = max(abs(maps["A"][key]["total_inventory"] - maps["B"][key]["total_inventory"])
                             for key in maps["A"] if key[0] == "withdrawal")
    accounting = max(abs(r["total_inventory"] - r["old_inventory"] - r["new_inventory"]) for r in rows)
    nonnegative_min = min(r[k] for r in rows for k in ["total_inventory", "old_inventory", "new_inventory"])
    seven = {c: maps[c][("withdrawal", 7.0)]["total_inventory"] for c in ["A", "B", "C"]}
    summary = {"kind": "exact constructed mathematical counterexample", "lambda_per_hypothetical_year": lam,
               "on_action_total_equation": "P(t)=0.2+0.8*exp(-lambda*t)",
               "withdrawal_equation": "P(T+s)=1-(1-P(T))*exp(-k0*s)",
               "inventory_at_withdrawal": maps["A"][("withdrawal", 0.0)]["total_inventory"],
               "inventory_seven_hypothetical_years_after_withdrawal": seven,
               "calculation_residuals": {"active_curve_max_difference": overlap, "A_B_withdrawal_max_difference": withdrawal_overlap,
                                         "old_plus_new_max_residual": accounting, "minimum_inventory_component": nonnegative_min},
               "conclusion": "A and B cannot be distinguished by total inventory under these on/off settings. C differs in withdrawal. Relative synthesis and old-pigment observations supply additional information.",
               "not_established": "No measured iris mechanism, turnover, pharmacology, appearance mapping or treatment schedule"}
    write_json(args.out / "summary.json", summary)
    version = plot(rows, config, args.out) if args.plot else None
    receipt = {"script_sha256": digest(Path(__file__)), "assumptions_sha256": digest(args.assumptions),
               "python": platform.python_version(), "matplotlib": version,
               "outputs": {p.name: {"bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(args.out.iterdir())}}
    write_json(args.out / "receipt.json", receipt)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

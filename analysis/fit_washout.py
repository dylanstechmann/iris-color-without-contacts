
"""CLI washout fitter: reads assumptions + input TSV, writes fitted parameters,
residuals, and receipt into a fresh output directory.

Usage:
    .venv/bin/python3 analysis/fit_washout.py \\
        --assumptions analysis/washout_assumptions.json \\
        --input analysis/washout-fit-pipeline-validation-2026-11-10/synthetic_data.tsv \\
        --out analysis/washout-fit-pipeline-validation-2026-11-10/
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path

import numpy as np

from washout_model import fit_washout, simulate_washout, write_json, build_receipt


def write_tsv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def generate_synthetic_data(assumptions: dict) -> dict:
    """Generate synthetic/hypothetical time series from assumptions."""
    cfg = assumptions["synthetic_ground_truth"]
    t = np.array(assumptions["timepoints_days"], dtype=float)
    rng = np.random.default_rng(assumptions["noise_seed"])

    sim = simulate_washout(t, **cfg, hill=1.0)

    noise = assumptions["noise_levels"]
    total = sim["total"] + rng.normal(0.0, noise["total_sd"], size=t.shape)
    old_frac = sim["old_fraction"] + rng.normal(0.0, noise["old_fraction_sd"], size=t.shape)
    compound = sim["compound"] + rng.normal(0.0, noise["compound_sd"], size=t.shape)
    cell_count = np.ones_like(t) + rng.normal(0.0, noise["cell_count_sd"], size=t.shape)

    # Enforce physical bounds
    total = np.clip(total, 0.0, None)
    old_frac = np.clip(old_frac, 0.0, 1.0)
    compound = np.clip(compound, 0.0, None)
    cell_count = np.clip(cell_count, 0.01, None)

    return {
        "time": t,
        "total": total,
        "old_fraction": old_frac,
        "compound": compound,
        "cell_count": cell_count,
        "ground_truth_sim": sim,
    }


def run(assumptions_path: Path, input_path: Path | None, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=False)
    assumptions = json.loads(assumptions_path.read_text(encoding="utf-8"))

    if input_path is None:
        # Synthetic run: generate data from assumptions
        data_bundle = generate_synthetic_data(assumptions)
        rows = []
        for i in range(len(data_bundle["time"])):
            rows.append({
                "time_days": f"{data_bundle['time'][i]:.1f}",
                "total_melanin_au": f"{data_bundle['total'][i]:.6f}",
                "old_fraction": f"{data_bundle['old_fraction'][i]:.6f}",
                "free_compound_nM": f"{data_bundle['compound'][i]:.6f}",
                "cell_count": f"{data_bundle['cell_count'][i]:.6f}",
            })
        write_tsv(out / "synthetic_data.tsv", rows, [
            "time_days", "total_melanin_au", "old_fraction",
            "free_compound_nM", "cell_count",
        ])
        data = {
            "time": data_bundle["time"],
            "total": data_bundle["total"] / data_bundle["cell_count"],
            "old_fraction": data_bundle["old_fraction"],
            "compound": data_bundle["compound"],
        }
    else:
        # Parse external TSV
        with input_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            raw = list(reader)
        time = np.array([float(r["time_days"]) for r in raw])
        total = np.array([float(r["total_melanin_au"]) for r in raw])
        old_frac = np.array([float(r["old_fraction"]) for r in raw])
        compound = np.array([float(r["free_compound_nM"]) for r in raw])
        cell_count = np.array([float(r["cell_count"]) for r in raw])
        data = {
            "time": time,
            "total": total / cell_count,
            "old_fraction": old_frac,
            "compound": compound,
        }

    readout_flags = assumptions["readout_flags"]
    weights = assumptions.get("fit_weights", {"total": 1.0, "old_fraction": 1.0, "compound": 1.0})
    guess = assumptions.get("initial_guess")
    bounds = assumptions.get("fit_bounds")

    result = fit_washout(data, readout_flags, initial_guess=guess, bounds=bounds, weights=weights)

    # Write fitted parameters + CIs
    fitted = {
        "activity": "F5 washout-kinetics fit",
        "data_kind": assumptions.get("data_kind", "unknown"),
        "readout_flags": readout_flags,
        "parameters": result["params"],
        "confidence_intervals": result["confidence_intervals"],
        "fit_summary": result["fit_summary"],
        "identifiability_notes": result["identifiability_notes"],
        "residuals_rmse": result["residuals_rmse"],
    }
    write_json(out / "fitted_params.json", fitted)

    # Write per-timepoint residuals TSV
    sim = result["simulated"]
    res_rows = []
    for i in range(len(data["time"])):
        res_rows.append({
            "time_days": f"{data['time'][i]:.1f}",
            "observed_total": f"{data['total'][i]:.6f}",
            "predicted_total": f"{sim['total'][i]:.6f}",
            "residual_total": f"{data['total'][i] - sim['total'][i]:.6f}",
            "observed_old_fraction": f"{data['old_fraction'][i]:.6f}",
            "predicted_old_fraction": f"{sim['old_fraction'][i]:.6f}",
            "residual_old_fraction": f"{data['old_fraction'][i] - sim['old_fraction'][i]:.6f}",
            "observed_compound": f"{data['compound'][i]:.6f}",
            "predicted_compound": f"{sim['compound'][i]:.6f}",
            "residual_compound": f"{data['compound'][i] - sim['compound'][i]:.6f}",
        })
    write_tsv(out / "residuals.tsv", res_rows, [
        "time_days",
        "observed_total", "predicted_total", "residual_total",
        "observed_old_fraction", "predicted_old_fraction", "residual_old_fraction",
        "observed_compound", "predicted_compound", "residual_compound",
    ])

    # Build MODEL_REPORT.md
    lines = [
        "# F5 washout-kinetics fit report",
        "",
        "**Status:** " + ("synthetic/hypothetical validation" if input_path is None else "real-data fit"),
        "**Date:** " + assumptions.get("date", "unknown"),
        "**Data kind:** " + assumptions.get("data_kind", "unknown"),
        "",
        "This is an AI-run forward-model fit. See washout-and-recovery.md for the identifiability",
        "calculation that motivates the multi-readout design.",
        "",
        "## Readout flags",
        "",
    ]
    for k, v in readout_flags.items():
        flag = "USED" if v else "OMITTED"
        lines.append(f"- {k}: {flag}")
    lines.extend(["", "## Fitted parameters"])
    for n, v in result["params"].items():
        lines.append(f"- **{n}** = {v:.6f}")
    lines.extend(["", "## Confidence intervals"])
    if result["cov_success"]:
        for n in result["params"]:
            lo = result["confidence_intervals"].get(f"{n}_95_lower")
            hi = result["confidence_intervals"].get(f"{n}_95_upper")
            if lo is not None and hi is not None:
                lines.append(f"- {n}: [{lo:.6f}, {hi:.6f}]")
    else:
        note = result["confidence_intervals"].get("note", "Unavailable.")
        lines.append(f"- {note}")
    lines.extend(["", "## Identifiability notes"])
    for note in result["identifiability_notes"]:
        lines.append(f"- {note}")
    lines.extend(["", "## Fit summary"])
    lines.append(f"- Cost (SSE): {result['fit_summary']['cost']:.6f}")
    lines.append(f"- N observations: {result['fit_summary']['n_obs']}")
    lines.append(f"- Free parameters: {result['fit_summary']['n_param_free']}")
    lines.append(f"- DOF: {result['fit_summary']['dof']}")
    lines.append(f"- Status: {result['fit_summary']['status']}")
    lines.append(f"- Message: {result['fit_summary']['message']}")
    lines.extend(["", "## Residuals (first 5 rows)"])
    lines.append("| time | total_resid | old_frac_resid | compound_resid |")
    lines.append("| --- | --- | --- | --- |")
    for r in res_rows[:5]:
        lines.append(f"| {r['time_days']} | {r['residual_total']} | {r['residual_old_fraction']} | {r['residual_compound']} |")
    lines.extend(["", "## Limitations"])
    lines.append("- All values are synthetic/hypothetical unless explicitly labeled otherwise.")
    lines.append("- The forward model assumes first-order compound washout and Hill synthesis inhibition.")
    lines.append("- Old and new pigment loss rates are allowed to differ; in the identifiability counterexample they coincide.")
    lines.append("- Confidence intervals are linear approximations from the Jacobian at the optimum.")
    lines.append("- Developed by AI assistant; owner-reviewed before interpretation.")

    (out / "MODEL_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Receipt
    receipt = build_receipt(out, assumptions_path, Path(__file__), extra={
        "data_kind": assumptions.get("data_kind", "unknown"),
        "readout_flags": readout_flags,
        "fit_success": result["fit_summary"]["success"],
    })
    write_json(out / "receipt.json", receipt)

    print(json.dumps({
        "output": str(out),
        "fit_success": result["fit_summary"]["success"],
        "cost": result["fit_summary"]["cost"],
    }))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assumptions", type=Path, required=True)
    parser.add_argument("--input", type=Path, default=None,
                        help="External TSV input. If omitted, synthetic data are generated from assumptions.")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args.assumptions, args.input, args.out)

#!/usr/bin/env python3
"""Washout design-simulation engine: quantify CI inflation vs the full matrix.

All data are synthetic/hypothetical. No real cells or compounds were involved.
Uses the existing F5 pipeline (washout_model.py, fit_washout.py) without
modification. Run from the repo root or from analysis/.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

# ---------------------------------------------------------------------------
# Import existing pipeline without edits
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent))
from washout_model import simulate_washout, fit_washout, PARAM_NAMES, write_json


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SEED_OFFSETS = {
    "full_rfQ": 0,
    "reduced_timepoints": 10000,
    "reduced_donors": 20000,
    "reduced_replicates": 30000,
    "minimal_first_stage": 40000,
    "no_isotope": 50000,
}

N_SIM = 200  # independent synthetic experiments per design

# Which readouts the designs carry
READOUT_ALL = {"total": True, "old_fraction": True, "compound": True}
READOUT_NO_ISO = {"total": True, "old_fraction": False, "compound": True}

# ---------------------------------------------------------------------------
# Data generation
# ---------------------------------------------------------------------------

def generate_experiment_data(
    design: dict,
    ground_truth: dict,
    noise: dict,
    rng: np.random.Generator,
) -> dict:
    """Generate one averaged dataset for a design (donors x replicates -> one time series).
    
    Averages across replicates within donor, then across donors, producing a single
    observation per unique timepoint. This avoids duplicate timepoints that violate
    solve_ivp t_eval requirements, while preserving donor-level variance in the mean.
    """
    t = np.array(design["timepoints"], dtype=float)
    donor_totals: List[np.ndarray] = []
    donor_olds: List[np.ndarray] = []
    donor_comps: List[np.ndarray] = []

    for d in range(design["donors"]):
        # Donor-level random effect: multiplicative lognormal on pools & synthesis
        factor = float(rng.lognormal(0.0, 0.1))
        donor_gt = dict(ground_truth)
        donor_gt["m_old0"] *= factor
        donor_gt["m_new0"] *= factor
        donor_gt["s_max"] *= factor

        sim = simulate_washout(t, **donor_gt, hill=1.0)

        # Replicate noise, then average
        total_reps = []
        old_reps = []
        comp_reps = []
        for _ in range(design["replicates"]):
            total_reps.append(
                sim["total"] + rng.normal(0.0, noise["total_sd"], size=t.shape)
            )
            old_reps.append(
                sim["old_fraction"]
                + rng.normal(0.0, noise["old_fraction_sd"], size=t.shape)
            )
            comp_reps.append(
                sim["compound"] + rng.normal(0.0, noise["compound_sd"], size=t.shape)
            )

        total_avg = np.clip(np.mean(total_reps, axis=0), 0.0, None)
        old_avg = np.clip(np.mean(old_reps, axis=0), 0.0, 1.0)
        comp_avg = np.clip(np.mean(comp_reps, axis=0), 0.0, None)

        donor_totals.append(total_avg)
        donor_olds.append(old_avg)
        donor_comps.append(comp_avg)

    # Average across donors; donor random effects create extra variance in the mean
    data: dict = {
        "time": t,
        "total": np.mean(donor_totals, axis=0),
        "old_fraction": np.mean(donor_olds, axis=0),
        "compound": np.mean(donor_comps, axis=0),
    }

    # Drop readouts not requested by design
    for key in ("total", "old_fraction", "compound"):
        if not design["readout_flags"].get(key):
            data.pop(key, None)

    return data


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def bootstrap_ci(
    data: dict,
    readout_flags: dict,
    guess: dict,
    bounds: dict,
    weights: dict,
    n_boot: int = 200,
    seed: int = 99,
) -> dict:
    """Residual bootstrap CI widths and parameter distributions."""
    base_fit = fit_washout(
        data, readout_flags, initial_guess=guess, bounds=bounds, weights=weights
    )
    sim = base_fit["simulated"]

    # Extract residuals
    resid: Dict[str, np.ndarray] = {}
    for key in ("total", "old_fraction", "compound"):
        if readout_flags.get(key) and key in data:
            resid[key] = data[key] - sim[key]

    boot_params: Dict[str, List[float]] = {name: [] for name in PARAM_NAMES}
    rng = np.random.default_rng(seed)

    for b in range(n_boot):
        boot_data = dict(data)
        for key in ("total", "old_fraction", "compound"):
            if readout_flags.get(key) and key in data:
                r = resid[key]
                idx = rng.integers(0, len(r), size=len(r))
                boot_data[key] = sim[key] + r[idx]
                if key == "total" or key == "compound":
                    boot_data[key] = np.clip(boot_data[key], 0.0, None)
                elif key == "old_fraction":
                    boot_data[key] = np.clip(boot_data[key], 0.0, 1.0)

        try:
            bfit = fit_washout(
                boot_data,
                readout_flags,
                initial_guess=guess,
                bounds=bounds,
                weights=weights,
            )
            if bfit["fit_summary"]["success"]:
                for name in PARAM_NAMES:
                    boot_params[name].append(bfit["params"][name])
        except Exception:
            pass

    widths: Dict[str, float] = {}
    for name in PARAM_NAMES:
        vals = boot_params[name]
        if len(vals) >= 100:
            widths[name] = float(np.percentile(vals, 97.5) - np.percentile(vals, 2.5))
        else:
            widths[name] = float("inf")
    return widths, boot_params


# ---------------------------------------------------------------------------
# Derived-parameter helpers
# ---------------------------------------------------------------------------

def derived_from_params(params: dict) -> dict:
    """Compute biologically meaningful derived quantities from fitted parameters."""
    k_c = params["k_c"]
    ht = np.log(2) / k_c if k_c > 1e-12 else float("inf")
    total0 = params["m_old0"] + params["m_new0"]
    old_frac0 = params["m_old0"] / total0 if total0 > 1e-12 else float("nan")
    # Synthesis recovery at day 14
    C14 = params["c0"] * np.exp(-params["k_c"] * 14.0) if params["c0"] > 0 else 0.0
    if params["ic50"] > 1e-12:
        S14 = params["s_max"] / (1.0 + (C14 / params["ic50"]))
    else:
        S14 = 0.0
    syn_rec = S14 / params["s_max"] if params["s_max"] > 1e-12 else float("nan")
    return {
        "compound_half_time": float(ht),
        "old_pool_fraction_day0": float(old_frac0),
        "synthesis_recovery_day14": float(syn_rec),
    }


def ci_widths_from_fit(fit_result: dict) -> dict:
    """Extract CI width for each named parameter."""
    widths: Dict[str, float] = {}
    for name in PARAM_NAMES:
        lo = fit_result["confidence_intervals"].get(f"{name}_95_lower")
        hi = fit_result["confidence_intervals"].get(f"{name}_95_upper")
        if lo is not None and hi is not None:
            widths[name] = float(hi - lo)
        else:
            widths[name] = float("inf")
    return widths


# ---------------------------------------------------------------------------
# Design runner
# ---------------------------------------------------------------------------

def run_design(design: dict, assumptions: dict) -> dict:
    gt = assumptions["synthetic_ground_truth"]
    noise = assumptions["noise_levels"]
    base_guess = assumptions["initial_guess"]
    base_bounds = assumptions["fit_bounds"]
    weights = assumptions.get("fit_weights", {"total": 1.0, "old_fraction": 1.0, "compound": 1.0})

    records: List[dict] = []
    cov_successes = 0
    n_success = 0

    t0 = time.time()
    for i in range(N_SIM):
        seed = assumptions["noise_seed"] + SEED_OFFSETS[design["name"]] + i
        rng = np.random.default_rng(seed)
        data = generate_experiment_data(design, gt, noise, rng)

        # Jittered initial guess (prevents all simulations starting identically)
        guess = {
            k: max(base_bounds[k][0], min(base_bounds[k][1], v * (1 + float(rng.normal(0, 0.05)))))
            for k, v in base_guess.items()
        }

        fit = fit_washout(
            data, design["readout_flags"], initial_guess=guess, bounds=base_bounds, weights=weights
        )
        success = bool(fit["fit_summary"]["success"])
        n_success += int(success)
        cov_successes += int(fit["cov_success"])

        bias = {name: fit["params"][name] - gt[name] for name in PARAM_NAMES}
        widths = ci_widths_from_fit(fit)
        derived = derived_from_params(fit["params"])

        records.append(
            {
                "params": fit["params"],
                "bias": bias,
                "ci_width": widths,
                "derived": derived,
                "cov_success": fit["cov_success"],
                "fit_success": success,
                "max_corr_note": next(
                    (n for n in fit["identifiability_notes"] if "correlation" in n),
                    "",
                ),
            }
        )

    elapsed = time.time() - t0

    # Summarise
    mean_bias: Dict[str, float] = {}
    mean_width: Dict[str, float] = {}
    rmse: Dict[str, float] = {}
    for name in PARAM_NAMES:
        biases = [r["bias"][name] for r in records if r["fit_success"]]
        widths_ok = [r["ci_width"][name] for r in records if r["fit_success"] and r["ci_width"][name] != float("inf")]
        vals = [r["params"][name] for r in records if r["fit_success"]]
        mean_bias[name] = float(np.mean(biases)) if biases else float("nan")
        mean_width[name] = float(np.mean(widths_ok)) if widths_ok else float("inf")
        rmse[name] = float(np.sqrt(np.mean([(v - gt[name]) ** 2 for v in vals]))) if vals else float("inf")

    # Derived statistics
    derived_names = ["compound_half_time", "old_pool_fraction_day0", "synthesis_recovery_day14"]
    derived_mean: Dict[str, float] = {}
    derived_rmse: Dict[str, float] = {}
    true_derived = derived_from_params(gt)
    for dname in derived_names:
        dvals = [r["derived"][dname] for r in records if r["fit_success"]]
        derived_mean[dname] = float(np.mean(dvals)) if dvals else float("nan")
        derived_rmse[dname] = float(np.sqrt(np.mean([(v - true_derived[dname]) ** 2 for v in dvals]))) if dvals else float("inf")

    return {
        "design": design["name"],
        "config": {k: v for k, v in design.items() if k != "name"},
        "n_sim": N_SIM,
        "n_success": n_success,
        "cov_success_rate": cov_successes / N_SIM,
        "mean_bias": mean_bias,
        "mean_ci_width": mean_width,
        "rmse": rmse,
        "derived_mean": derived_mean,
        "derived_rmse": derived_rmse,
        "elapsed_seconds": elapsed,
        # Stash raw records so caller can compute inflation
        "records": records,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    assumptions_path = Path(__file__).parent.parent / "washout_assumptions.json"
    assumptions = json.loads(assumptions_path.read_text(encoding="utf-8"))

    designs = [
        {
            "name": "full_rfQ",
            "timepoints": [0, 1, 3, 5, 7, 9, 11, 14, 21],
            "donors": 3,
            "replicates": 3,
            "readout_flags": READOUT_ALL,
        },
        {
            "name": "reduced_timepoints",
            "timepoints": [0, 3, 7, 11, 21],
            "donors": 3,
            "replicates": 3,
            "readout_flags": READOUT_ALL,
        },
        {
            "name": "reduced_donors",
            "timepoints": [0, 1, 3, 5, 7, 9, 11, 14, 21],
            "donors": 2,
            "replicates": 3,
            "readout_flags": READOUT_ALL,
        },
        {
            "name": "reduced_replicates",
            "timepoints": [0, 1, 3, 5, 7, 9, 11, 14, 21],
            "donors": 3,
            "replicates": 2,
            "readout_flags": READOUT_ALL,
        },
        {
            "name": "minimal_first_stage",
            "timepoints": [0, 3, 7, 14],
            "donors": 2,
            "replicates": 2,
            "readout_flags": READOUT_ALL,
        },
        {
            "name": "no_isotope",
            "timepoints": [0, 1, 3, 5, 7, 9, 11, 14, 21],
            "donors": 3,
            "replicates": 3,
            "readout_flags": READOUT_NO_ISO,
        },
    ]

    results: Dict[str, dict] = {}
    for design in designs:
        print(f"[{time.strftime('%H:%M:%S')}] Running {design['name']} ...", flush=True)
        res = run_design(design, assumptions)
        results[design["name"]] = res
        print(
            f"  success={res['n_success']}/{N_SIM}  cov={res['cov_success_rate']:.2f}  "
            f"time={res['elapsed_seconds']:.1f}s",
            flush=True,
        )

    # Bootstrap the no-isotope design
    print(f"[{time.strftime('%H:%M:%S')}] Bootstrap for no_isotope ...", flush=True)
    rng = np.random.default_rng(assumptions["noise_seed"] + 99999)
    no_iso_design = [d for d in designs if d["name"] == "no_isotope"][0]
    data_no_iso = generate_experiment_data(
        no_iso_design, assumptions["synthetic_ground_truth"], assumptions["noise_levels"], rng
    )
    guess = assumptions["initial_guess"]
    bounds = assumptions["fit_bounds"]
    weights = assumptions.get("fit_weights", {"total": 1.0, "old_fraction": 1.0, "compound": 1.0})
    boot_widths, boot_params = bootstrap_ci(
        data_no_iso, no_iso_design["readout_flags"], guess, bounds, weights, n_boot=200
    )
    results["no_isotope"]["bootstrap_ci_width"] = boot_widths
    results["no_isotope"]["bootstrap_params"] = {
        k: v for k, v in boot_params.items()
    }
    print("  done.", flush=True)

    # -----------------------------------------------------------------------
    # Inflation calculations
    # -----------------------------------------------------------------------
    full = results["full_rfQ"]
    key_params = ["k_c", "k_old", "k_new", "s_max", "ic50", "m_old0", "m_new0"]

    inflation: Dict[str, Dict[str, float]] = {}
    for dname, res in results.items():
        if dname == "full_rfQ":
            continue
        row: Dict[str, float] = {}
        for name in key_params:
            full_w = full["mean_ci_width"].get(name, float("inf"))
            red_w = res["mean_ci_width"].get(name, float("inf"))
            if full_w > 0 and full_w != float("inf"):
                row[name] = red_w / full_w if red_w != float("inf") else float("inf")
            else:
                row[name] = float("inf")
        inflation[dname] = row

    # Derived-parameter inflation (using RMSE as proxy for precision loss
    # when CI width is unavailable for derived quantities)
    derived_keys = ["compound_half_time", "old_pool_fraction_day0", "synthesis_recovery_day14"]
    derived_inflation: Dict[str, Dict[str, float]] = {}
    for dname, res in results.items():
        if dname == "full_rfQ":
            continue
        row: Dict[str, float] = {}
        for dk in derived_keys:
            full_rmse = full["derived_rmse"].get(dk, float("inf"))
            red_rmse = res["derived_rmse"].get(dk, float("inf"))
            if full_rmse > 0 and full_rmse != float("inf"):
                row[dk] = red_rmse / full_rmse if red_rmse != float("inf") else float("inf")
            else:
                row[dk] = float("inf")
        derived_inflation[dname] = row

    # -----------------------------------------------------------------------
    # Write results JSON (trim raw records to avoid multi-MB file)
    # -----------------------------------------------------------------------
    out = Path(__file__).parent
    # Keep only summary stats for JSON; raw records are huge
    json_out = {"assumptions_sha256": hashlib.sha256(assumptions_path.read_bytes()).hexdigest()}
    for dname, res in results.items():
        json_out[dname] = {
            k: v for k, v in res.items() if k != "records"
        }
    json_out["ci_inflation_vs_full"] = inflation
    json_out["derived_precision_inflation_vs_full"] = derived_inflation
    json_out["synthetic_label"] = "All values are synthetic/hypothetical. No biological samples were used."
    json_out["n_sim_per_design"] = N_SIM
    json_out["python"] = platform.python_version()

    write_json(out / "results.json", json_out)

    # -----------------------------------------------------------------------
    # MODEL_REPORT.md
    # -----------------------------------------------------------------------
    lines = [
        "# Washout design-simulation report",
        "",
        "**Status:** Synthetic/hypothetical identifiability analysis only.",
        "**Date:** 2026-11-10",
        "**Data kind:** Forward-model simulations with noise and donor random effects.",
        "",
        "> This is an AI-run simulation study. All data are synthetic. No real cells or compounds",
        "> were involved. The owner reviews all outputs before interpretation.",
        "",
        "## Scope",
        "",
        "Quantify how reducing the planned paired-exposure/withdrawal matrix affects the",
        "precision of the key parameters that drive the G1/G2 feasibility verdict.",
        "The existing washout_model.py pipeline was used without modification.",
        "",
        "## Design definitions",
        "",
    ]
    for design in designs:
        lines.append(
            f"- **{design['name']}**: timepoints={design['timepoints']}, "
            f"donors={design['donors']}, replicates={design['replicates']}, "
            f"readouts={design['readout_flags']}"
        )
    lines.extend(["", "## Summary statistics", ""])

    for dname, res in results.items():
        lines.append(f"### {dname}")
        lines.append(f"- Fit success: {res['n_success']}/{N_SIM}")
        lines.append(f"- Covariance-computation success: {res['cov_success_rate']:.2%}")
        lines.append(f"- Runtime: {res['elapsed_seconds']:.1f}s")
        lines.append("")
        lines.append("| Parameter | Mean bias | Mean CI width | RMSE |")
        lines.append("| --- | --- | --- | --- |")
        for name in key_params:
            mb = res["mean_bias"].get(name, float("nan"))
            mw = res["mean_ci_width"].get(name, float("inf"))
            r = res["rmse"].get(name, float("inf"))
            mw_str = f"{mw:.4f}" if mw != float("inf") else "inf"
            r_str = f"{r:.4f}" if r != float("inf") else "inf"
            lines.append(f"| {name} | {mb:.4f} | {mw_str} | {r_str} |")
        lines.append("")

    lines.extend(["## CI inflation vs full design", ""])
    lines.append("CI inflation = (mean CI width in reduced design) / (mean CI width in full design).")
    lines.append("Values > 1 mean the reduced design is less precise. `inf` = parameter became non-identifiable.")
    lines.append("")
    lines.append("| Design | k_c | k_old | k_new | s_max | ic50 | m_old0 | m_new0 | Max inflation |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for dname in inflation:
        row = inflation[dname]
        vals = [f"{row.get(p, float('inf')):.2f}" if row.get(p, float("inf")) != float("inf") else "inf" for p in key_params]
        max_inf = max(row.get(p, 0.0) for p in key_params if row.get(p, 0.0) != float("inf"))
        any_inf = any(row.get(p, 0.0) == float("inf") for p in key_params)
        max_str = "inf" if any_inf else f"{max_inf:.2f}"
        lines.append(f"| {dname} | {' | '.join(vals)} | {max_str} |")
    lines.append("")

    lines.extend(["## Derived-parameter precision inflation (RMSE ratio)", ""])
    lines.append("| Design | compound_half_time | old_pool_fraction_day0 | synthesis_recovery_day14 | Max |")
    lines.append("| --- | --- | --- | --- | --- |")
    for dname in derived_inflation:
        row = derived_inflation[dname]
        vals = [f"{row.get(p, float('inf')):.2f}" if row.get(p, float("inf")) != float("inf") else "inf" for p in derived_keys]
        max_inf = max(row.get(p, 0.0) for p in derived_keys if row.get(p, 0.0) != float("inf"))
        any_inf = any(row.get(p, 0.0) == float("inf") for p in derived_keys)
        max_str = "inf" if any_inf else f"{max_inf:.2f}"
        lines.append(f"| {dname} | {' | '.join(vals)} | {max_str} |")
    lines.append("")

    lines.extend(["## Verdict-threshold measurability", ""])
    lines.append("| Threshold | Full | Reduced TP | Reduced donors | Reduced reps | Minimal | No isotope |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    # Threshold 1: half-time separation < 50%
    # Need precise k_c; half-time derived precision
    th1 = []
    for dname in ["full_rfQ", "reduced_timepoints", "reduced_donors", "reduced_replicates", "minimal_first_stage", "no_isotope"]:
        if dname == "full_rfQ":
            th1.append("Yes")
        elif dname == "no_isotope":
            # no_isotope still has total+compound, so k_c is still somewhat identifiable
            # but m_old0/m_new0 are lost
            th1.append("Partial (k_c OK; old/new lost)")
        elif derived_inflation[dname]["compound_half_time"] < 3.0:
            th1.append("Yes")
        else:
            th1.append("Marginal")
    lines.append(f"| Production-down half-time separation (<50%) | {' | '.join(th1)} |")

    # Threshold 2: flux recovery >= 80% by day 14
    th2 = []
    for dname in ["full_rfQ", "reduced_timepoints", "reduced_donors", "reduced_replicates", "minimal_first_stage", "no_isotope"]:
        if dname == "full_rfQ":
            th2.append("Yes")
        elif dname == "no_isotope":
            # no_isotope affects old/new, not synthesis directly
            th2.append("Yes (synthesis from total+compound)")
        elif derived_inflation[dname]["synthesis_recovery_day14"] < 3.0:
            th2.append("Yes")
        else:
            th2.append("Marginal")
    lines.append(f"| Flux recovery >=80% by day 14 | {' | '.join(th2)} |")

    # Threshold 3: old-pool detection <= 10%
    th3 = []
    for dname in ["full_rfQ", "reduced_timepoints", "reduced_donors", "reduced_replicates", "minimal_first_stage", "no_isotope"]:
        if dname == "full_rfQ":
            th3.append("Yes")
        elif dname == "no_isotope":
            th3.append("**No** -- old_fraction readout required for old/new separation")
        elif derived_inflation[dname]["old_pool_fraction_day0"] < 3.0:
            th3.append("Yes")
        else:
            th3.append("Marginal")
    lines.append(f"| Old-pool detection <=10% | {' | '.join(th3)} |")
    lines.append("")

    lines.extend(["## Limitations", ""])
    lines.append("- All data are synthetic/hypothetical; no biological material was measured.")
    lines.append("- Donor random effect is a simulated lognormal multiplier (sigma=0.1) on pools and synthesis baseline only.")
    lines.append("- The forward model assumes first-order washout and Hill synthesis inhibition.")
    lines.append("- Confidence intervals are linear approximations from the Jacobian at the optimum (Fisher approximation).")
    lines.append("- Bootstrap was run on a single representative dataset for the no-isotope design; 200 resamples.")
    lines.append("- Derived-parameter CI widths are approximated via RMSE ratios from repeated simulations.")
    lines.append("- The minimal-first-stage design simulation uses a generic single-arm ground truth; the real G1 comparison requires two arms (KT-939 and thiamidol).")
    lines.append("- Cost statements in the decision document are planning-grade only and do not authorize spending.")

    (out / "MODEL_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # -----------------------------------------------------------------------
    # Receipt
    # -----------------------------------------------------------------------
    files: Dict[str, dict] = {}
    for p in sorted(out.iterdir()):
        if p.is_file():
            files[p.name] = {
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "bytes": p.stat().st_size,
            }
    receipt = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "assumptions_sha256": hashlib.sha256(assumptions_path.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "outputs": files,
        "n_sim_per_design": N_SIM,
        "synthetic_only": True,
        "command": f"{sys.executable} {Path(__file__).relative_to(Path(__file__).parent.parent)}",
    }
    write_json(out / "receipt.json", receipt)

    print("\nOutputs written to", out)


if __name__ == "__main__":
    main()

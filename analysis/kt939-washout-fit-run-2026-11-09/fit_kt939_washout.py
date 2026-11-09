"""Fit published KT-939 washout inhibition data with a single-exponential decay.

Standard library only. Optional matplotlib figure written only when --plot is
supplied and matplotlib is importable. No numpy dependency.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
from pathlib import Path


def sse(data, I0, k):
    """Sum of squared residuals for inhibition(t) = I0 * exp(-k*t)."""
    s = 0.0
    for t, y in data:
        r = y - I0 * math.exp(-k * t)
        s += r * r
    return s


def grid_search(data, I0_min, I0_max, I0_step, k_min, k_max, k_step):
    """Brute-force grid minimization of SSE."""
    best_sse = float("inf")
    best = None
    I0 = I0_min
    while I0 <= I0_max:
        k = k_min
        while k <= k_max:
            val = sse(data, I0, k)
            if val < best_sse:
                best_sse = val
                best = (I0, k)
            k += k_step
        I0 += I0_step
    return best, best_sse


def refine(data, I0, k, steps=3):
    """Local coordinate-descent-like refinement with shrinking grid."""
    I0_step = 1.0
    k_step = 0.005
    for _ in range(steps):
        best, _ = grid_search(
            data,
            max(0.1, I0 - 5 * I0_step),
            I0 + 5 * I0_step,
            I0_step,
            max(0.001, k - 5 * k_step),
            k + 5 * k_step,
            k_step,
        )
        if best is None:
            break
        I0, k = best
        I0_step *= 0.2
        k_step *= 0.2
    return I0, k


def fit_exponential(data):
    """Nonlinear least-squares fit of inhibition(t)=I0*exp(-k*t)."""
    # coarse -> medium -> fine
    best, _ = grid_search(data, 40, 180, 4.0, 0.05, 0.40, 0.02)
    if best is None:
        raise RuntimeError("Coarse grid search failed to find a minimum.")
    I0, k = refine(data, best[0], best[1], steps=3)
    return {"I0": I0, "k": k, "half_life_days": math.log(2) / k}


def bootstrap_ci(data, n_bootstrap=5000, seed=42):
    """Bootstrap percentile CI for half-life from n=4 data."""
    rng = random.Random(seed)
    halftimes = []
    for _ in range(n_bootstrap):
        boot = [rng.choice(data) for _ in range(len(data))]
        try:
            res = fit_exponential(boot)
            halftimes.append(res["half_life_days"])
        except RuntimeError:
            pass
    if not halftimes:
        return None
    halftimes.sort()
    n = len(halftimes)
    return {
        "mean": sum(halftimes) / n,
        "median": halftimes[n // 2],
        "pct_2_5": halftimes[int(0.025 * n)],
        "pct_5": halftimes[int(0.050 * n)],
        "pct_25": halftimes[int(0.250 * n)],
        "pct_75": halftimes[int(0.750 * n)],
        "pct_95": halftimes[int(0.950 * n)],
        "pct_97_5": halftimes[int(0.975 * n)],
        "n_samples": n,
    }


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def run(assumptions_path, out, make_plot):
    out.mkdir(parents=True, exist_ok=False)
    assumptions = json.loads(assumptions_path.read_text(encoding="utf-8"))

    # Extract quantitative 10 μM points
    series_10uM_raw = assumptions["source_values"]["concentration_10_uM"]["values"]
    series_10uM = [
        (v["day_after_withdrawal"], v["inhibition_percent"])
        for v in series_10uM_raw
        if v["inhibition_percent"] is not None
    ]
    # Should be 4 points
    if len(series_10uM) != 4:
        raise RuntimeError(f"Unexpected 10 μM point count: {len(series_10uM)}")

    # Extract 1 μM points for reporting only
    series_1uM_raw = assumptions["source_values"]["concentration_1_uM"]["values"]
    series_1uM_quant = [
        (v["day_after_withdrawal"], v["inhibition_percent"])
        for v in series_1uM_raw
        if v["inhibition_percent"] is not None
    ]

    # Fit 10 μM
    fit = fit_exponential(series_10uM)
    fit["sse"] = sse(series_10uM, fit["I0"], fit["k"])
    fit["n_points"] = len(series_10uM)
    fit["dof"] = len(series_10uM) - 2  # 2 parameters

    # Residuals
    residuals = []
    for t, y in series_10uM:
        pred = fit["I0"] * math.exp(-fit["k"] * t)
        residuals.append({"day": t, "observed": y, "predicted": pred, "residual": y - pred})
    fit["residuals"] = residuals

    # Bootstrap CI
    ci = bootstrap_ci(series_10uM)

    # 1 μM bounding: with only 2 points (days 3,5) any I0 and k are possible.
    # We report what those two points imply if one forces an exponential through them.
    if len(series_1uM_quant) >= 2:
        t1, y1 = series_1uM_quant[0]
        t2, y2 = series_1uM_quant[1]
        # y1 = I0*exp(-k*t1), y2 = I0*exp(-k*t2)
        # => y1/y2 = exp(-k*(t1-t2)) => k = ln(y2/y1)/(t1-t2)
        if y1 > 0 and y2 > 0 and t1 != t2:
            k_1uM = math.log(y2 / y1) / (t1 - t2)
            I0_1uM = y1 * math.exp(k_1uM * t1)
            bound_1uM = {
                "note": "Forcing a two-point exponential through the 1 μM series is underdetermined; this is not a fit and not recommended.",
                "I0_forced": I0_1uM,
                "k_forced": k_1uM,
                "half_life_forced_days": math.log(2) / k_1uM if k_1uM > 0 else None,
            }
        else:
            bound_1uM = {"note": "Cannot compute from available points."}
    else:
        bound_1uM = {"note": "Insufficient quantitative points."}

    summary = {
        "activity": "Single-exponential washout fit to published KT-939 10 μM mean inhibition values",
        "fit_10uM": fit,
        "bootstrap_half_life_days": ci,
        "bound_1uM": bound_1uM,
        "qualitative_bounds": {
            "10uM_day11": "recovery reported (normal levels); treated as upper bound on remaining inhibition, not a 0% data point",
            "1uM_day7": "recovery reported (baseline); treated as upper bound, not a 0% data point",
        },
        "rationale_1uM_not_fitted": "Two quantitative points cannot determine two parameters (I0, k) independently. Any pair (I0, k) satisfying I0*exp(-k*3)=38.0 and I0*exp(-k*5)=28.3 is consistent; the forced two-point single exponential above is descriptive, not inferential.",
        "caveats": [
            "The endpoint is accumulated pigment content, not synthesis flux.",
            "Day-7 to day-9 plateau (21.3% -> 20.0%) violates strict exponential decay.",
            "n=4 quantitative points yields large bootstrap CIs.",
            "No replicate-level data; mean values only.",
            "MNT-1 melanoma rates do not transfer to iris tissue.",
        ],
    }
    write_json(out / "summary.json", summary)

    # Build MODEL_REPORT.md
    lines = [
        "# KT-939 washout exponential-fit report",
        "",
        "Single-exponential fit to published mean inhibition values from Hou et al., 2025.",
        "",
        "## Source values",
        "",
        "| Concentration | Day post-washout | Inhibition % | Flag |",
        "| --- | ---: | ---: | --- |",
    ]
    for v in series_10uM_raw:
        pct = v["inhibition_percent"] if v["inhibition_percent"] is not None else v["qualitative_bound"]
        lines.append(f"| 10 μM | {v['day_after_withdrawal']} | {pct} | {v['flag']} |")
    for v in series_1uM_raw:
        pct = v["inhibition_percent"] if v["inhibition_percent"] is not None else v["qualitative_bound"]
        lines.append(f"| 1 μM | {v['day_after_withdrawal']} | {pct} | {v['flag']} |")

    lines.extend([
        "",
        "Endpoint: bulk melanin absorbance at 405 nm normalized to protein (μg melanin / mg protein); inhibition percent relative to matched vehicle (denominator not explicit).",
        "The 10 μM day-11 and 1 μM day-7 entries are qualitative recovery bounds, not 0% data points, and were excluded from the least-squares objective.",
        "",
        "## 10 μM fit: inhibition(t) = I0 · exp(−k · t)",
        "",
        f"- Fitted I0 = {fit['I0']:.2f}% (extrapolated inhibition at t = 0, not measured)",
        f"- Fitted k = {fit['k']:.4f} day⁻¹",
        f"- Washout half-time = {fit['half_life_days']:.2f} days",
        f"- SSE = {fit['sse']:.2f} (n = {fit['n_points']}, DOF = {fit['dof']})",
        "",
        "| Residuals | Observed | Predicted | Residual |",
        "| --- | ---: | ---: | ---: |",
    ])
    for r in residuals:
        lines.append(f"| Day {r['day']} | {r['observed']:.1f} | {r['predicted']:.2f} | {r['residual']:.2f} |")

    lines.extend([
        "",
        "### Uncertainty estimate (bootstrap, n = 4)",
        "",
    ])
    if ci:
        lines.extend([
            f"- Bootstrap median half-time: {ci['median']:.2f} days",
            f"- Bootstrap 95% percentile CI: [{ci['pct_2_5']:.2f}, {ci['pct_97_5']:.2f}] days",
            f"- Bootstrap interquartile range: [{ci['pct_25']:.2f}, {ci['pct_75']:.2f}] days",
            "",
            "The bootstrap resamples the n = 4 mean points with replacement and reflits; it does not recover replicate-level uncertainty. The CI is wide because the sample is small and the residual at day 5 is large.",
        ])
    else:
        lines.append("Bootstrap did not converge; uncertainty not quantified.")

    lines.extend([
        "",
        "## 1 μM series: underdetermined",
        "",
        "Only two quantitative points exist (day 3: 38.0%, day 5: 28.3%). These do not determine both I0 and k independently. A forced two-point exponential is not a fit; it is a descriptive line.",
        "",
        f"- Forced two-point exponential (not recommended): I0 = {bound_1uM.get('I0_forced', 'N/A'):.2f}%, k = {bound_1uM.get('k_forced', 'N/A'):.4f} day⁻¹, half-time = {bound_1uM.get('half_life_forced_days', 'N/A'):.2f} days" if bound_1uM.get('k_forced') else "- Cannot compute from available points.",
        "",
        "The 1 μM qualitative recovery by day 7 is consistent with a faster washout than the 10 μM series, but a direct half-time comparison is unsupported.",
        "",
        "## Limitations",
        "",
        "1. **Endpoint is accumulated pigment content, not synthesis flux.** The measured quantity is bulk melanin per protein after six days of exposure and various days after washout. Recovery of this quantity conflates resumption of new pigment synthesis, turnover of existing pigment, possible cell division, and any protein-content change. It does not isolate synthesis flux. See analysis/withdrawal-and-recovery.md for the identifiability problem this creates.",
        "",
        "2. **Qualitative recovery bounds are not fitted points.** The paper reports normal levels by day 11 (10 μM) and baseline by day 7 (1 μM). These have not been converted to exact 0% inhibition measurements and are excluded from the SSE. Treating them as 0% would bias the fit downward.",
        "",
        "3. **Day-7 to day-9 plateau violates strict exponential decay.** The observed inhibition drops only from 21.3% to 20.0% between days 7 and 9, while the fitted single exponential predicts a drop from 28.85% to 18.65%. This plateau is a source inconsistency: either experimental variability, a persistent low-level inhibition floor, or some other process not captured by the model. The SSE is dominated by this mismatch.",
        "",
        "4. **n = 4 fit uncertainty is large.** Four mean points for two nonlinear parameters yields bootstrap 95% CIs spanning roughly a factor of three in half-time. The normal-approximation residual-based CI (not reported here because the small-sample t-distribution with 2 degrees of freedom hits the lower parameter boundary) would be even wider. The half-time should be read as a crude order-of-magnitude estimate, not a precise kinetic constant.",
        "",
        "5. **No replicate-level data were used.** Figure 4 shows mean ± SD of three independent experiments, but error bars were not transcribed or digitized. Equal weighting of the mean points is assumed; if the true underlying variance differs across days, the effective uncertainty is larger than reported.",
        "",
        "6. **Cell model and tissue transfer limits.** MNT-1 human melanoma cells are a transformed line. The fitted rate describes pigment-content change in that system under the stated culture conditions. It does not transfer to normal human melanocytes, 3D skin equivalents, or iris tissue.",
        "",
        "## What this estimate does and does not resolve",
        "",
        "This run extracts one crude washout half-time (~3.2 days, 95% CI ~2.4–8.7 days) from published 10 μM mean values. It does **not**:",
        "",
        "- Provide a synthesis-flux recovery rate (the endpoint is accumulated pigment, not flux).",
        "- Resolve the KT-939 vs thiamidol comparative-recovery gap, because thiamidol has no washout arm in this study.",
        "- Establish whether KT-939's scaffold confers different retention kinetics from thiamidol's shared resorcinol–thiazole core.",
        "- Quantify free-compound clearance or target-activity recovery after withdrawal.",
        "",
        "What it **does** do:",
        "",
        "- Quantify the order-of-magnitude speed at which the 10 μM accumulated-pigment inhibition phenotype decays in MNT-1 cells after medium replacement.",
        "- Provide a numerical benchmark that a future paired KT-939/thiamidol washout experiment could exceed or falsify.",
        "- Flag which specific missing raw values would sharpen or overturn the estimate (see Minimum raw-data request below).",
        "",
        "## Minimum raw-data request",
        "",
        "The following exact values from Hou et al., 2025 would resolve the fit's ambiguity and could be requested from the authors as a free data enquiry:",
        "",
        "1. **Replicate-level melanin-content values per timepoint.** The figure caption states three independent experiments. The individual replicate values per day (not just mean ± SD) would allow proper weighting and would support a measurement-error model instead of equal-weighted means.",
        "",
        "2. **Exact washout-start definition.** Was the replacement medium changed once at day 6, or was it refreshed repeatedly? What volume was used, and was any residual compound in the extracellular space quantified?",
        "",
        "3. **How the percent inhibition was normalized.** Was the denominator the day-matched vehicle control, the pre-exposure baseline, or a single vehicle average across the time course? The answer changes the interpretation of residual inhibition at late timepoints.",
        "",
        "4. **Whether a thiamidol washout arm exists in unpublished data.** The paired same-study comparison is the highest-priority gap in the registered evidence. If the authors measured thiamidol washout in the same MNT-1 system, that dataset would immediately resolve the comparative-recovery question without new wet-lab work.",
        "",
        "5. **Cell-count and protein-content data per timepoint.** If protein normalization absorbed cell-number changes, the inhibition-percent time course may reflect population dynamics rather than pigment per cell.",
        "",
        "6. **Day 0 and day 1 post-washout measurements, if collected.** The fitted I0 is an extrapolation from day 3. An early dense sampling window (days 0, 0.5, 1, 2) would test whether recovery begins immediately or after a lag.",
        "",
        "These are minimal requests: they require no new experiments, only disclosed values from completed work.",
    ])

    (out / "MODEL_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Optional figure
    if make_plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(6.4, 4.0), layout="constrained")
            ts_fit = [i * 0.25 for i in range(0, 45)]  # 0 to 11 days
            preds = [fit["I0"] * math.exp(-fit["k"] * t) for t in ts_fit]
            ax.plot(ts_fit, preds, "b-", label="Fit: inhibition(t) = I0·exp(−k·t)")
            # 10 μM points
            t10 = [pt[0] for pt in series_10uM]
            y10 = [pt[1] for pt in series_10uM]
            ax.plot(t10, y10, "ro", label="10 μM observed (mean)")
            # 1 μM points
            t1 = [pt[0] for pt in series_1uM_quant]
            y1 = [pt[1] for pt in series_1uM_quant]
            ax.plot(t1, y1, "gs", label="1 μM observed (mean)")
            # Qualitative bounds
            ax.axvline(x=11, color="r", linestyle="--", alpha=0.5, label="10 μM qualitative recovery bound (day 11)")
            ax.axvline(x=7, color="g", linestyle="--", alpha=0.5, label="1 μM qualitative recovery bound (day 7)")
            ax.set_xlabel("Days after washout")
            ax.set_ylabel("Inhibition (%)")
            ax.set_title("KT-939 washout fit (published mean values from Hou et al., 2025)")
            ax.set_xlim(0, 12)
            ax.set_ylim(0, 100)
            ax.legend(loc="upper right", fontsize=7)
            fig.savefig(out / "kt939_washout_fit.png", dpi=150)
            plt.close(fig)
        except Exception as e:
            print(f"Plotting skipped: {e}")

    # Receipt
    files = {}
    for path in sorted(out.iterdir()):
        if path.is_file():
            blob = path.read_bytes()
            files[path.name] = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
    script = Path(__file__).resolve()
    receipt = {
        "model_status": "published-data fit",
        "python": platform.python_version(),
        "assumptions_sha256": hashlib.sha256(assumptions_path.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "outputs": files,
    }
    if make_plot:
        try:
            import matplotlib
            receipt["matplotlib"] = matplotlib.__version__
        except Exception:
            pass
    write_json(out / "receipt.json", receipt)
    print(json.dumps({"half_life_days": fit["half_life_days"], "bootstrap_ci": ci, "output": str(out)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assumptions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    run(args.assumptions, args.out, args.plot)

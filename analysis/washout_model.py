
"""Washout kinetics forward model and fitter (F5 pipeline).

Separates three terms that total-pigment-alone washout data cannot distinguish:
1. synthesis flux / production (new_pool),
2. old (pre-existing) pigment pool,
3. free intracellular compound driving inhibition.

All rates are per day. Concentrations are in nM. Pigment pools are arbitrary
absorbance or mass units per cell (already divided by cell_count when passed).
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
from scipy import integrate, optimize


# ---------------------------------------------------------------------------
# Forward model
# ---------------------------------------------------------------------------

def compound_concentration(t: np.ndarray, c0: float, k_c: float) -> np.ndarray:
    """Free compound concentration after withdrawal: C(t)=C0*exp(-k_c*t)."""
    t = np.asarray(t, dtype=float)
    return c0 * np.exp(-k_c * t)


def synthesis_rate(C: float | np.ndarray, s_max: float, ic50: float, hill: float = 1.0):
    """Hill-type inhibition of synthesis by free compound.

    S(C) = s_max / (1 + (C/ic50)^hill)

    At C=0  -> S = s_max (fully recovered).
    At C>>ic50 -> S -> 0 (fully inhibited).
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        out = s_max / (1.0 + (C / ic50) ** hill)
    if isinstance(out, float):
        if math.isnan(out):
            out = 0.0
    else:
        out = np.nan_to_num(out, nan=0.0, posinf=0.0)
    return out


def simulate_washout(
    t: np.ndarray,
    *,
    c0: float,
    k_c: float,
    m_old0: float,
    m_new0: float,
    k_old: float,
    k_new: float,
    s_max: float,
    ic50: float,
    hill: float = 1.0,
) -> Dict[str, np.ndarray]:
    """Simulate washout multi-readout time series.

    Returns dict with keys:
        time, compound, old, new, total, old_fraction, new_fraction,
        synthesis, new_source_relative_to_baseline.
    """
    t = np.asarray(t, dtype=float)
    if t.size == 0:
        return {k: np.array([]) for k in (
            "time", "compound", "old", "new", "total",
            "old_fraction", "new_fraction", "synthesis", "new_source_relative_to_baseline"
        )}

    # Free compound washout (analytical)
    C = compound_concentration(t, c0, k_c)

    # Old (pre-existing) pigment pool: pure exponential loss
    M_old = m_old0 * np.exp(-k_old * t)

    # New pigment: integrate dM_new/dt = S(C(t)) - k_new * M_new
    def _rhs(t_, y):
        C_ = c0 * math.exp(-k_c * t_)
        S_ = synthesis_rate(C_, s_max, ic50, hill)
        return [S_ - k_new * y[0]]

    sol = integrate.solve_ivp(
        _rhs,
        [0.0, float(t.max())],
        [float(m_new0)],
        t_eval=t,
        method="RK45",
    )
    if not sol.success:
        raise RuntimeError(f"solve_ivp failed: {sol.message}")
    M_new = sol.y[0]

    total = M_old + M_new
    old_fraction = np.zeros_like(total)
    mask = total > 1e-12
    old_fraction[mask] = M_old[mask] / total[mask]
    new_fraction = 1.0 - old_fraction

    S_arr = synthesis_rate(C, s_max, ic50, hill)

    return {
        "time": t,
        "compound": C,
        "old": M_old,
        "new": M_new,
        "total": total,
        "old_fraction": old_fraction,
        "new_fraction": new_fraction,
        "synthesis": S_arr,
        "new_source_relative_to_baseline": S_arr / s_max if s_max > 0 else np.zeros_like(S_arr),
    }


# ---------------------------------------------------------------------------
# Fitting
# ---------------------------------------------------------------------------

PARAM_NAMES = (
    "c0", "k_c", "m_old0", "m_new0", "k_old", "k_new", "s_max", "ic50",
)

DEFAULT_BOUNDS: Dict[str, Tuple[float, float]] = {
    "c0": (0.0, 1e6),
    "k_c": (0.0, 10.0),
    "m_old0": (0.0, 1e6),
    "m_new0": (0.0, 1e6),
    "k_old": (0.0, 10.0),
    "k_new": (0.0, 10.0),
    "s_max": (0.0, 1e6),
    "ic50": (1e-3, 1e6),
}


def _pack(params: Dict[str, float]) -> np.ndarray:
    return np.array([params[n] for n in PARAM_NAMES], dtype=float)


def _unpack(vec: np.ndarray) -> Dict[str, float]:
    return {n: float(v) for n, v in zip(PARAM_NAMES, vec)}


def _residuals(
    vec: np.ndarray,
    t: np.ndarray,
    data: Dict[str, np.ndarray],
    flags: Dict[str, bool],
    weights: Dict[str, float],
) -> np.ndarray:
    """Return concatenated weighted residuals for least_squares."""
    p = _unpack(vec)
    try:
        sim = simulate_washout(t, **p, hill=1.0)
    except RuntimeError:
        n = sum(data[k].size for k in ("total", "old_fraction", "compound") if flags.get(k))
        return np.full(n, 1e6)

    resid = []
    if flags.get("total"):
        r = (data["total"] - sim["total"]) * weights.get("total", 1.0)
        resid.append(r)
    if flags.get("old_fraction"):
        r = (data["old_fraction"] - sim["old_fraction"]) * weights.get("old_fraction", 1.0)
        resid.append(r)
    if flags.get("compound"):
        r = (data["compound"] - sim["compound"]) * weights.get("compound", 1.0)
        resid.append(r)

    return np.concatenate(resid)


def fit_washout(
    data: Dict[str, np.ndarray],
    readout_flags: Dict[str, bool],
    initial_guess: Optional[Dict[str, float]] = None,
    bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    weights: Optional[Dict[str, float]] = None,
    method: str = "trf",
) -> Dict:
    """Fit washout model to time-series data.

    Parameters
    ----------
    data : dict
        Must contain 'time'. Optional keys: 'total', 'old_fraction',
        'compound'. All arrays must match length.
    readout_flags : dict
        Keys 'total', 'old_fraction', 'compound'. Boolean toggles.
    initial_guess : dict
        Starting values for parameters.
    bounds : dict
        Per-param (low, high) bounds.
    weights : dict
        Per-readout scales in SSE objective.
    method : str
        scipy.optimize.least_squares method (trf, lm, dogbox).

    Returns
    -------
    dict with keys:
        params, cov, cov_success, residuals, fit_summary, readout_flags,
        identifiability_notes
    """
    if bounds is None:
        bounds = {k: tuple(v) for k, v in DEFAULT_BOUNDS.items()}
    else:
        bounds = {k: tuple(v) for k, v in bounds.items()}
    if initial_guess is None:
        initial_guess = {
            "c0": 100.0, "k_c": 0.5,
            "m_old0": 0.5, "m_new0": 0.3,
            "k_old": 0.1, "k_new": 0.1,
            "s_max": 1.0, "ic50": 50.0,
        }
    if weights is None:
        weights = {"total": 1.0, "old_fraction": 1.0, "compound": 1.0}

    # Adjust guess if a readout is missing so we do not start far off
    if not readout_flags.get("compound"):
        initial_guess["c0"] = 0.0
        initial_guess["k_c"] = 0.0
        bounds["c0"] = (0.0, 1e-12)
        bounds["k_c"] = (0.0, 1e-12)

    lb = np.array([bounds[n][0] for n in PARAM_NAMES], dtype=float)
    ub = np.array([bounds[n][1] for n in PARAM_NAMES], dtype=float)
    x0 = _pack(initial_guess)

    x0 = np.clip(x0, lb, ub)

    t = np.asarray(data["time"], dtype=float)

    result = optimize.least_squares(
        lambda x: _residuals(x, t, data, readout_flags, weights),
        x0,
        bounds=(lb, ub),
        method=method,
        max_nfev=5000,
        jac="2-point",
    )

    p_fit = _unpack(result.x)
    n_obs = sum(data[k].size for k in ("total", "old_fraction", "compound") if readout_flags.get(k))
    n_param = sum(1 for n in PARAM_NAMES if bounds[n][0] != bounds[n][1])
    dof = max(1, n_obs - n_param)

    cov_success = False
    cov = None
    ci = {}
    if result.jac is not None and result.cost > 0:
        try:
            J = result.jac
            s2 = result.cost / dof
            JTJ = J.T @ J
            cond = np.linalg.cond(JTJ)
            if cond < 1e12:
                inv_JTJ = np.linalg.inv(JTJ)
                cov = s2 * inv_JTJ
                stderr = np.sqrt(np.diag(cov))
                for idx, n in enumerate(PARAM_NAMES):
                    ci[f"{n}_95_lower"] = float(p_fit[n] - 1.96 * stderr[idx])
                    ci[f"{n}_95_upper"] = float(p_fit[n] + 1.96 * stderr[idx])
                cov_success = True
            else:
                ci["note"] = f"Jacobian condition number {cond:.2e} too high; CIs unreliable (non-identifiable)."
        except np.linalg.LinAlgError:
            ci["note"] = "Jacobian singular; parameters non-identifiable with current readouts."

    sim = simulate_washout(t, **p_fit, hill=1.0)
    per_readout = {}
    for key in ("total", "old_fraction", "compound"):
        if readout_flags.get(key) and key in data:
            per_readout[key] = {
                "sse": float(np.sum((data[key] - sim[key]) ** 2)),
                "rmse": float(np.sqrt(np.mean((data[key] - sim[key]) ** 2))),
            }

    id_notes = []
    if not readout_flags.get("old_fraction"):
        id_notes.append(
            "old_fraction readout MISSING: m_old0 and m_new0 cannot be separated; "
            "k_old and k_new are jointly confounded with the synthesis term."
        )
    if not readout_flags.get("compound"):
        id_notes.append(
            "compound readout MISSING: c0, k_c, s_max, and ic50 are confounded. "
            "Multiple (clearance, potency, baseline) combinations reproduce the same total curve."
        )
    if readout_flags.get("old_fraction") and readout_flags.get("compound"):
        id_notes.append(
            "All declared readouts present: old/new pool separation, compound clearance, "
            "and synthesis recovery are jointly identifiable in principle."
        )

    if cov is not None:
        corr = cov / (np.sqrt(np.diag(cov))[:, None] * np.sqrt(np.diag(cov))[None, :])
        max_corr = np.max(np.abs(corr[np.triu_indices_from(corr, k=1)]))
        id_notes.append(f"Maximum absolute parameter correlation ≈ {max_corr:.3f}.")
        if max_corr > 0.95:
            id_notes.append("High correlation suggests practical non-identifiability even if the Jacobian is invertible.")

    return {
        "params": p_fit,
        "cov": cov.tolist() if cov is not None else None,
        "cov_success": cov_success,
        "confidence_intervals": ci,
        "residuals_rmse": per_readout,
        "fit_summary": {
            "cost": float(result.cost),
            "nfev": int(result.nfev),
            "njev": int(result.njev) if result.njev is not None else None,
            "status": int(result.status),
            "message": str(result.message),
            "success": bool(result.success),
            "n_obs": n_obs,
            "n_param_free": n_param,
            "dof": dof,
        },
        "readout_flags": dict(readout_flags),
        "identifiability_notes": id_notes,
        "simulated": sim,
    }


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def build_receipt(
    out_dir: Path,
    assumptions_path: Path,
    script_path: Path,
    extra: Optional[Dict] = None,
) -> Dict:
    files = {}
    for p in sorted(out_dir.iterdir()):
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
        "script_sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
        "outputs": files,
    }
    if extra:
        receipt.update(extra)
    return receipt

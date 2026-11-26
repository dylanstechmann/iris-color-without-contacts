"""Paired generic synthetic washout-design generation, fitting, and summaries.

The two arm labels are placeholders, not compound-calibrated models.  Every
record retains the mandatory isotope old/new readout; explicit negative-control
fits may omit that readout only to demonstrate the resulting identifiability
failure.  No assay LOD, donor population, ocular, or clinical inference is made.

Random streams use SeedSequence([master, stream, system_index, replicate_index]).
Scenarios are deliberately absent from the hierarchy, so all ratio scenarios
and nested design subsets use common random numbers and shared system effects.
"""
from __future__ import annotations

import copy
import math
from typing import Iterable

import numpy as np

from washout_model import PARAM_NAMES, fit_washout, simulate_washout

ARM_NAMES = ("KT-939_synthetic", "thiamidol_synthetic")
READOUT_NAMES = ("total", "old_fraction", "compound")
STREAM_SYSTEM = 10
STREAM_PAIR = 20
STREAM_SHARED_NOISE = 30
STREAM_ARM_NOISE = {ARM_NAMES[0]: 40, ARM_NAMES[1]: 41}
Z_95 = 1.959963984540054
DEFAULT_PROPOSED_DECISIONS = {
    "approval_status": "proposed_not_owner_approved_not_go_no_go",
    "symmetric_half_time_ratio": {"operator": "<", "threshold": 1.5},
    "both_arms_day14_synthesis_recovery": {"operator": ">=", "threshold": 0.8},
    "formal_equivalence": False,
}


def _finite_number(value, label: str, *, minimum=None, positive=False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    if positive and value <= 0:
        raise ValueError(f"{label} must be > 0")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be >= {minimum}")
    return value


def _positive_int(value, label: str, *, allow_zero=False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    if value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f"{label} must be {'>= 0' if allow_zero else '> 0'}")
    return value


def _assert_finite_tree(value, path="config") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _assert_finite_tree(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _assert_finite_tree(item, f"{path}[{index}]")
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{path} must be finite")


def validate_design_assumptions(config: dict) -> None:
    """Validate frozen synthetic, nested, isotope-mandatory design assumptions."""
    if not isinstance(config, dict):
        raise ValueError("config must be an object")
    _assert_finite_tree(config)
    if config.get("data_kind") != "synthetic":
        raise ValueError("data_kind must be synthetic")
    if config.get("calibration_status") != "generic_non_calibrated":
        raise ValueError("ground truths must be generic_non_calibrated")
    semantics = config.get("ground_truth_semantics", {})
    if semantics.get("arms_are_generic_labels_not_calibrated_compounds") is not True:
        raise ValueError("both arms must be declared generic and non-calibrated")
    if semantics.get("ic50") != "free_compound_synthesis_inhibition_generic":
        raise ValueError("ic50 must denote generic free-compound synthesis inhibition")
    if semantics.get("accumulated_pigment_ic50_substitution") is not False:
        raise ValueError("accumulated-pigment IC50 substitution is forbidden")
    if semantics.get("ocular_or_clinical_claims") is not False:
        raise ValueError("ocular/clinical claims must be disabled")

    truths = config.get("synthetic_ground_truths")
    if not isinstance(truths, dict) or set(truths) != set(ARM_NAMES):
        raise ValueError("both generic synthetic ground truths are required")
    for arm in ARM_NAMES:
        if set(truths[arm]) != set(PARAM_NAMES):
            raise ValueError(f"{arm} ground truth must contain exactly PARAM_NAMES")
        for name in PARAM_NAMES:
            _finite_number(truths[arm][name], f"ground_truth.{arm}.{name}", minimum=0.0)
        for name in ("k_c", "s_max", "ic50"):
            if truths[arm][name] <= 0:
                raise ValueError(f"ground_truth.{arm}.{name} must be > 0")

    scenarios = config.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("ratio scenarios are required")
    ratios = []
    names = []
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict) or not isinstance(scenario.get("name"), str) or not scenario["name"]:
            raise ValueError(f"scenario {index} needs a name")
        ratios.append(_finite_number(scenario.get("half_time_ratio"), f"scenario {index} ratio", positive=True))
        names.append(scenario["name"])
    if len(set(names)) != len(names) or set(ratios) != {1.0, 1.25, 1.5, 2.0}:
        raise ValueError("ratio scenarios must be uniquely named and exactly 1.0, 1.25, 1.5, 2.0")

    isotope = config.get("isotope_readout", {})
    if isotope.get("required") is not True or isotope.get("fit_field") != "old_fraction":
        raise ValueError("isotope old_fraction readout is mandatory")
    if isotope.get("interpretation") != "old_new_pool_identifiability_only_not_an_assay_lod_measurement":
        raise ValueError("isotope interpretation must be identifiability, not assay LOD")

    designs = config.get("designs")
    if not isinstance(designs, dict) or set(designs) != {"full", "reduced", "minimal"}:
        raise ValueError("full, reduced, and minimal designs are required")
    system_kinds = config.get("system_kinds", {})
    for name, design in designs.items():
        times = design.get("timepoints_days")
        if not isinstance(times, list) or len(times) < 3:
            raise ValueError(f"{name} needs at least three timepoints")
        checked_times = [_finite_number(t, f"{name} timepoint", minimum=0.0) for t in times]
        if any(b <= a for a, b in zip(checked_times, checked_times[1:])) or 0.0 not in checked_times or 14.0 not in checked_times:
            raise ValueError(f"{name} timepoints must increase and include days 0 and 14")
        _positive_int(design.get("replicates"), f"{name} replicates")
        systems = design.get("systems")
        if not isinstance(systems, list) or not systems or len(set(systems)) != len(systems):
            raise ValueError(f"{name} systems must be a nonempty unique list")
        if any(system not in system_kinds for system in systems):
            raise ValueError(f"{name} has a system without an explicit kind")
        accounting = design.get("system_accounting", {})
        donor_count = sum("donor" in system_kinds[system] and system_kinds[system] != "reference_cell_line_not_a_donor" for system in systems)
        reference_count = sum(system_kinds[system] == "reference_cell_line_not_a_donor" for system in systems)
        mnt_count = systems.count("MNT-1")
        expected = {
            "system_count": len(systems), "donor_count": donor_count,
            "reference_cell_line_count": reference_count,
            "mnt1_represented": mnt_count > 0, "mnt1_count": mnt_count,
        }
        for key, value in expected.items():
            if accounting.get(key) != value:
                raise ValueError(f"{name} system accounting mismatch, including MNT-1: {key}")
        flags = design.get("readout_flags")
        if not isinstance(flags, dict) or set(flags) != set(READOUT_NAMES):
            raise ValueError(f"{name} readout flags are incomplete")
        if any(flags.get(readout) is not True for readout in READOUT_NAMES):
            raise ValueError(f"{name} cannot omit isotope or another required readout")
    for child, parent in (("minimal", "reduced"), ("reduced", "full")):
        if not set(designs[child]["timepoints_days"]).issubset(designs[parent]["timepoints_days"]):
            raise ValueError(f"{child} timepoints must be nested in {parent}")
        if not set(designs[child]["systems"]).issubset(designs[parent]["systems"]):
            raise ValueError(f"{child} systems must be nested in {parent}")
        if designs[child]["replicates"] > designs[parent]["replicates"]:
            raise ValueError(f"{child} replicates must be nested in {parent}")

    controls = config.get("negative_controls", {})
    if controls.get("no_isotope") is not True or controls.get("diagnostic_only") is not True:
        raise ValueError("no-isotope negative control must be explicitly diagnostic")
    if set(controls.get("designs", [])) != set(designs):
        raise ValueError("no-isotope controls must cover full, reduced, and minimal designs")

    seeds = config.get("seeds", {})
    _positive_int(seeds.get("master"), "master seed", allow_zero=True)
    if not isinstance(seeds.get("hierarchy"), str) or "SeedSequence" not in seeds["hierarchy"]:
        raise ValueError("deterministic SeedSequence hierarchy must be documented")
    noise = config.get("noise_levels", {})
    for key in ("total_sd", "old_fraction_sd", "compound_sd", "cell_count_sd"):
        _finite_number(noise.get(key), f"noise {key}", minimum=0.0)
    correlation = _finite_number(noise.get("pair_correlation"), "pair_correlation", minimum=0.0)
    if correlation > 1:
        raise ValueError("pair_correlation must be <= 1")
    for effect in ("system_log_sd", "pair_log_sd"):
        values = noise.get(effect, {})
        if not isinstance(values, dict) or not values or any(key not in PARAM_NAMES for key in values):
            raise ValueError(f"{effect} has invalid parameters")
        for key, value in values.items():
            _finite_number(value, f"{effect}.{key}", minimum=0.0)

    weights = config.get("fit_weights", {})
    if set(weights) != set(READOUT_NAMES):
        raise ValueError("fit weights must cover all readouts")
    for key in READOUT_NAMES:
        _finite_number(weights[key], f"fit weight {key}", positive=True)
    bounds = config.get("fit_bounds", {})
    guess = config.get("initial_guess", {})
    if set(bounds) != set(PARAM_NAMES) or set(guess) != set(PARAM_NAMES):
        raise ValueError("fit bounds and initial guess must cover PARAM_NAMES")
    for name in PARAM_NAMES:
        pair = bounds[name]
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError(f"fit bounds {name} must be a pair")
        low = _finite_number(pair[0], f"fit bounds {name} lower")
        high = _finite_number(pair[1], f"fit bounds {name} upper")
        if high <= low:
            raise ValueError(f"fit bounds {name} must be increasing")
        value = _finite_number(guess[name], f"initial guess {name}")
        if not low <= value <= high:
            raise ValueError(f"initial guess {name} must be inside bounds")

    proposed = config.get("proposed_decision_metadata", {})
    if "proposed_not_owner_approved" not in proposed.get("approval_status", "") or "not_go_no_go" not in proposed.get("approval_status", ""):
        raise ValueError("decision metadata must remain proposed, unapproved, and not go/no-go")
    ratio_rule = proposed.get("symmetric_half_time_ratio", {})
    recovery_rule = proposed.get("both_arms_day14_synthesis_recovery", {})
    if ratio_rule.get("operator") != "<" or recovery_rule.get("operator") != ">=":
        raise ValueError("proposed threshold operators must be < and >=")
    _finite_number(ratio_rule.get("threshold"), "proposed ratio threshold", positive=True)
    _finite_number(recovery_rule.get("threshold"), "proposed recovery threshold", positive=True)
    if proposed.get("formal_equivalence") is not False:
        raise ValueError("formal equivalence must remain false")


def _stream_rng(seed: int, stream: int, system_index: int, replicate_index: int | None = None):
    hierarchy = [int(seed), int(stream), int(system_index)]
    if replicate_index is not None:
        hierarchy.append(int(replicate_index))
    return np.random.default_rng(np.random.SeedSequence(hierarchy))


def _lognormal_effects(rng, specification: dict) -> dict:
    return {name: float(np.exp(rng.normal(0.0, sd))) for name, sd in sorted(specification.items())}


def _scenario_ground_truths(design: dict, scenario: dict) -> dict:
    truths = copy.deepcopy(design["synthetic_ground_truths"])
    ratio = float(scenario["half_time_ratio"])
    truths[ARM_NAMES[1]]["k_c"] = truths[ARM_NAMES[0]]["k_c"] / ratio
    return truths


def generate_paired_experiment(design: dict, scenario: dict, noise: dict, seed: int) -> dict:
    """Generate one paired system/replicate record with common random numbers.

    ``design`` contains the single ``system``, its zero-based ``system_index``,
    zero-based ``replicate``, timepoints, generic ground truths, and system kinds.
    The returned arm data can be passed directly to the existing ``fit_washout``.
    """
    system_index = _positive_int(design.get("system_index"), "system_index", allow_zero=True)
    replicate = _positive_int(design.get("replicate"), "replicate", allow_zero=True)
    seed = _positive_int(seed, "seed", allow_zero=True)
    times = np.asarray(design["timepoints_days"], dtype=float)
    truths = _scenario_ground_truths(design, scenario)
    system_effects = _lognormal_effects(
        _stream_rng(seed, STREAM_SYSTEM, system_index), noise["system_log_sd"]
    )
    pair_effects = _lognormal_effects(
        _stream_rng(seed, STREAM_PAIR, system_index, replicate), noise["pair_log_sd"]
    )
    shared_rng = _stream_rng(seed, STREAM_SHARED_NOISE, system_index, replicate)
    shared = {key: shared_rng.normal(size=times.shape) for key in ("total", "old_fraction", "compound", "cell_count")}
    rho = float(noise["pair_correlation"])
    arms = {}
    for arm in ARM_NAMES:
        arm_rng = _stream_rng(seed, STREAM_ARM_NOISE[arm], system_index, replicate)
        independent = {key: arm_rng.normal(size=times.shape) for key in shared}
        truth = dict(truths[arm])
        for name in set(system_effects) | set(pair_effects):
            truth[name] *= system_effects.get(name, 1.0) * pair_effects.get(name, 1.0)
        sim = simulate_washout(times, **truth, hill=1.0)
        noise_z = {
            key: math.sqrt(rho) * shared[key] + math.sqrt(1.0 - rho) * independent[key]
            for key in shared
        }
        cell_count = np.clip(1.0 + float(noise["cell_count_sd"]) * noise_z["cell_count"], 0.01, None)
        total = np.clip(sim["total"] + float(noise["total_sd"]) * noise_z["total"], 0.0, None) / cell_count
        old_fraction = np.clip(sim["old_fraction"] + float(noise["old_fraction_sd"]) * noise_z["old_fraction"], 0.0, 1.0)
        compound = np.clip(sim["compound"] + float(noise["compound_sd"]) * noise_z["compound"], 0.0, None)
        arms[arm] = {
            "data": {
                "time": times.copy(), "total": total, "old_fraction": old_fraction,
                "compound": compound, "cell_count": cell_count,
            },
            "noise": {
                "shared_total": shared["total"].copy(),
                "independent_total": independent["total"].copy(),
            },
            "true_parameters": truth,
            "true_metrics": {
                "compound_half_time_days": compound_half_time(truth),
                "synthesis_recovery_day_14": synthesis_recovery(truth, 14.0),
            },
            "effects": {"system": dict(system_effects), "pair": dict(pair_effects)},
        }
    return {
        "design": design.get("name", "unspecified"),
        "scenario": scenario["name"],
        "scenario_half_time_ratio": float(scenario["half_time_ratio"]),
        "system": design["system"], "system_index": system_index,
        "system_kind": design["system_kinds"][design["system"]],
        "replicate": replicate, "effects": {"system": system_effects, "pair": pair_effects},
        "arms": arms,
    }


def subset_paired_experiment(paired_data: dict, design: dict) -> dict:
    """Select a nested time grid without regenerating any paired observation."""
    subset = copy.deepcopy(paired_data)
    full_times = np.asarray(paired_data["arms"][ARM_NAMES[0]]["data"]["time"], dtype=float)
    indices = []
    for time in design["timepoints_days"]:
        matches = np.flatnonzero(full_times == float(time))
        if len(matches) != 1:
            raise ValueError(f"timepoint {time} is not uniquely nested in the full design")
        indices.append(int(matches[0]))
    index = np.asarray(indices, dtype=int)
    subset["design"] = design.get("name", "unspecified")
    subset["source_design"] = paired_data.get("design", "unspecified")
    subset["observation_indices"] = indices
    for arm in ARM_NAMES:
        for key, values in paired_data["arms"][arm]["data"].items():
            subset["arms"][arm]["data"][key] = np.asarray(values)[index].copy()
        for key, values in paired_data["arms"][arm].get("noise", {}).items():
            subset["arms"][arm]["noise"][key] = np.asarray(values)[index].copy()
    return subset


def compound_half_time(params: dict) -> float:
    """Return ln(2)/k_c in days; zero clearance has infinite half-time."""
    k_c = _finite_number(params.get("k_c"), "k_c")
    if k_c < 0:
        raise ValueError("k_c must be nonnegative")
    return math.log(2.0) / k_c if k_c > 0 else float("inf")


def synthesis_recovery(params: dict, day: float) -> float:
    """Return free-compound-driven synthesis relative to its compound-free baseline."""
    day = _finite_number(day, "day", minimum=0.0)
    c0 = _finite_number(params.get("c0"), "c0", minimum=0.0)
    k_c = _finite_number(params.get("k_c"), "k_c", minimum=0.0)
    ic50 = _finite_number(params.get("ic50"), "ic50", positive=True)
    compound = c0 * math.exp(-k_c * day)
    return 1.0 / (1.0 + compound / ic50)


def symmetric_half_time_ratio(params_a: dict, params_b: dict) -> float:
    """Return max(ht_A,ht_B)/min(ht_A,ht_B), including explicit zero boundaries."""
    a = compound_half_time(params_a)
    b = compound_half_time(params_b)
    if math.isinf(a) and math.isinf(b):
        return float("nan")
    return max(a, b) / min(a, b)


def _linearized_ci(value: float, gradient: np.ndarray, covariance) -> tuple:
    try:
        cov = np.asarray(covariance, dtype=float)
        if cov.shape != (len(PARAM_NAMES), len(PARAM_NAMES)) or not np.all(np.isfinite(cov)):
            return None, None, "not_evaluable"
        variance = float(gradient @ cov @ gradient)
        if not math.isfinite(variance) or variance < -1e-12:
            return None, None, "not_evaluable"
        standard_error = math.sqrt(max(0.0, variance))
        return value - Z_95 * standard_error, value + Z_95 * standard_error, "evaluable_linearized"
    except (TypeError, ValueError, FloatingPointError):
        return None, None, "not_evaluable"


def _derived_metric_output(name: str, params: dict, covariance, cov_success: bool) -> dict:
    if name == "compound_half_time_days":
        value = compound_half_time(params)
        k_c = params["k_c"]
        gradient = np.zeros(len(PARAM_NAMES))
        if k_c > 0:
            gradient[PARAM_NAMES.index("k_c")] = -math.log(2.0) / k_c**2
    elif name == "synthesis_recovery_day_14":
        value = synthesis_recovery(params, 14.0)
        c0, k_c, ic50 = params["c0"], params["k_c"], params["ic50"]
        compound = c0 * math.exp(-k_c * 14.0)
        q = compound / ic50
        denominator = (1.0 + q) ** 2
        gradient = np.zeros(len(PARAM_NAMES))
        gradient[PARAM_NAMES.index("c0")] = -math.exp(-k_c * 14.0) / (ic50 * denominator)
        gradient[PARAM_NAMES.index("k_c")] = 14.0 * compound / (ic50 * denominator)
        gradient[PARAM_NAMES.index("ic50")] = compound / (ic50**2 * denominator)
    else:
        raise ValueError(f"unknown derived metric {name}")
    status = "evaluable" if math.isfinite(value) else "not_evaluable_nonfinite"
    lower = upper = None
    ci_status = "not_evaluable"
    if cov_success and status == "evaluable":
        lower, upper, ci_status = _linearized_ci(value, gradient, covariance)
    return {
        "value": value, "status": status, "ci95_lower": lower,
        "ci95_upper": upper, "ci_status": ci_status,
    }


def _decision_from_arms(arms: dict, proposed: dict) -> dict:
    ratio_rule = proposed["symmetric_half_time_ratio"]
    recovery_rule = proposed["both_arms_day14_synthesis_recovery"]
    base = {
        "approval_status": proposed["approval_status"],
        "ratio_threshold": ratio_rule["threshold"],
        "recovery_threshold": recovery_rule["threshold"],
        "formal_equivalence": False,
    }
    try:
        if any(arms[arm]["status"] != "evaluable" for arm in ARM_NAMES):
            raise ValueError("one or both arms not evaluable")
        half_times = [arms[arm]["derived_metrics"]["compound_half_time_days"]["value"] for arm in ARM_NAMES]
        recoveries = [arms[arm]["derived_metrics"]["synthesis_recovery_day_14"]["value"] for arm in ARM_NAMES]
        values = half_times + recoveries
        if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in values):
            raise ValueError("nonfinite derived decision value")
        ratio = max(half_times) / min(half_times)
        if not math.isfinite(ratio):
            raise ValueError("nonfinite half-time ratio")
        ratio_met = ratio < ratio_rule["threshold"]
        recovery_met = all(value >= recovery_rule["threshold"] for value in recoveries)
        return {
            **base, "status": "evaluable", "symmetric_half_time_ratio": ratio,
            "half_time_ratio_below_proposed_threshold": bool(ratio_met),
            "both_arms_day14_recovery_at_least_proposed_threshold": bool(recovery_met),
            "both_proposed_conditions_met": bool(ratio_met and recovery_met),
        }
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        return {**base, "status": "not_evaluable", "reason": str(error)}


def fit_paired_experiment(paired_data: dict, design: dict, config: dict) -> dict:
    """Fit arms separately with the unchanged legacy fitter; never impute failures."""
    flags = copy.deepcopy(design["readout_flags"])
    fitted = {key: copy.deepcopy(value) for key, value in paired_data.items() if key != "arms"}
    fitted["arms"] = {}
    for arm in ARM_NAMES:
        source = paired_data["arms"][arm]
        result_record = {
            "status": "not_evaluable", "covariance_status": "not_evaluable",
            "readout_flags": copy.deepcopy(flags), "parameters": None,
            "true_parameters": copy.deepcopy(source["true_parameters"]),
            "true_metrics": copy.deepcopy(source["true_metrics"]),
            "effects": copy.deepcopy(source["effects"]),
        }
        try:
            result = fit_washout(
                source["data"], flags,
                initial_guess=copy.deepcopy(config["initial_guess"]),
                bounds=copy.deepcopy(config["fit_bounds"]),
                weights=copy.deepcopy(config["fit_weights"]),
            )
            result_record["fit_summary"] = copy.deepcopy(result["fit_summary"])
            result_record["identifiability_notes"] = list(result.get("identifiability_notes", []))
            params = result.get("params", {})
            success = bool(result.get("fit_summary", {}).get("success"))
            if success and set(params) == set(PARAM_NAMES) and all(math.isfinite(params[name]) for name in PARAM_NAMES):
                result_record["status"] = "evaluable"
                result_record["parameters"] = {name: float(params[name]) for name in PARAM_NAMES}
                result_record["confidence_intervals"] = copy.deepcopy(result.get("confidence_intervals", {}))
                covariance = result.get("cov")
                cov_success = bool(result.get("cov_success")) and covariance is not None
                if cov_success:
                    result_record["covariance_status"] = "evaluable_linearized"
                result_record["derived_metrics"] = {
                    name: _derived_metric_output(name, params, covariance, cov_success)
                    for name in ("compound_half_time_days", "synthesis_recovery_day_14")
                }
                if not cov_success:
                    result_record["covariance_failure"] = result.get("confidence_intervals", {}).get(
                        "note", "Covariance unavailable or unreliable"
                    )
            else:
                result_record["failure"] = {"type": "fit_unsuccessful", "message": "Fit unsuccessful or nonfinite parameters"}
        except Exception as error:  # each failed arm remains an explicit missing estimate
            result_record["failure"] = {"type": type(error).__name__, "message": str(error)}
        fitted["arms"][arm] = result_record
    fitted["decision"] = _decision_from_arms(fitted["arms"], config["proposed_decision_metadata"])
    return fitted


def _descriptive_fraction(count: int, total: int, not_evaluable: int = 0) -> dict:
    """Return a descriptive matched-fit count/fraction, never a probability interval."""
    _positive_int(count, "count", allow_zero=True)
    _positive_int(total, "total", allow_zero=True)
    _positive_int(not_evaluable, "not_evaluable", allow_zero=True)
    if count > total:
        raise ValueError("count cannot exceed total")
    return {
        "count": count, "total": total, "not_evaluable": not_evaluable,
        "fraction": count / total if total else None,
        "status": "evaluable" if total else "not_evaluable_zero_denominator",
        "interpretation": "descriptive_matched_fit_fraction_not_an_independent_bernoulli_or_probability_estimate",
    }


def _numeric_summary(values: Iterable[float], missing: int = 0) -> dict:
    finite = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    nonfinite = sum(1 for value in values if value is not None and not math.isfinite(float(value)))
    result = {"n": len(finite), "missing": missing, "nonfinite": nonfinite}
    if not finite:
        result.update({key: None for key in ("mean", "sd", "median", "minimum", "maximum", "q05", "q95")})
        result["status"] = "not_evaluable_no_finite_values"
        return result
    array = np.asarray(finite, dtype=float)
    result.update({
        "mean": float(np.mean(array)), "sd": float(np.std(array, ddof=1)) if len(array) > 1 else None,
        "median": float(np.median(array)), "minimum": float(np.min(array)),
        "maximum": float(np.max(array)), "q05": float(np.quantile(array, 0.05)),
        "q95": float(np.quantile(array, 0.95)), "status": "evaluable",
    })
    return result


def _ci_diagnostic(rows: list) -> dict:
    intervals = [row for row in rows if row[0] is not None and row[1] is not None and math.isfinite(row[0]) and math.isfinite(row[1]) and math.isfinite(row[2])]
    widths = [upper - lower for lower, upper, _ in intervals]
    covered = sum(lower <= truth <= upper for lower, upper, truth in intervals)
    return {
        "n_records": len(rows), "n_intervals": len(intervals),
        "intervals_unavailable": len(rows) - len(intervals),
        "covered": covered, "coverage": _descriptive_fraction(covered, len(intervals)),
        "mean_width": float(np.mean(widths)) if widths else None,
        "median_width": float(np.median(widths)) if widths else None,
        "status": "evaluable" if intervals else "not_evaluable_no_finite_intervals",
    }


def summarize_paired_records(records: list, proposed_decision_metadata: dict | None = None) -> dict:
    """Summarize decision, recovery, failure, and linearized-CI diagnostics."""
    proposed = proposed_decision_metadata or DEFAULT_PROPOSED_DECISIONS
    n_pairs = len(records)
    decisions = [_decision_from_arms(record["arms"], proposed) for record in records]
    evaluable = [decision for decision in decisions if decision["status"] == "evaluable"]
    not_evaluable = n_pairs - len(evaluable)
    decision_summary = {}
    for key in (
        "half_time_ratio_below_proposed_threshold",
        "both_arms_day14_recovery_at_least_proposed_threshold",
        "both_proposed_conditions_met",
    ):
        decision_summary[key] = _descriptive_fraction(sum(bool(row[key]) for row in evaluable), len(evaluable), not_evaluable)

    fit_failures = {}
    covariance_failures = {}
    recovery = {}
    parameter_ci = {}
    derived_ci = {}
    for arm in ARM_NAMES:
        arm_records = [record["arms"][arm] for record in records]
        fit_bad = sum(row["status"] != "evaluable" for row in arm_records)
        fit_good = n_pairs - fit_bad
        cov_bad = sum(row["status"] == "evaluable" and row.get("covariance_status") != "evaluable_linearized" for row in arm_records)
        fit_failures[arm] = _descriptive_fraction(fit_bad, n_pairs)
        covariance_failures[arm] = _descriptive_fraction(cov_bad, fit_good, fit_bad)
        recovery_values = []
        missing = 0
        for row in arm_records:
            try:
                value = row["derived_metrics"]["synthesis_recovery_day_14"]["value"]
                if row["status"] != "evaluable":
                    raise KeyError
                recovery_values.append(value)
            except (KeyError, TypeError):
                missing += 1
        recovery[arm] = _numeric_summary(recovery_values, missing)
        parameter_ci[arm] = {}
        for name in PARAM_NAMES:
            rows = []
            for row in arm_records:
                if row["status"] != "evaluable":
                    continue
                ci = row.get("confidence_intervals", {})
                rows.append((ci.get(f"{name}_95_lower"), ci.get(f"{name}_95_upper"), row["true_parameters"][name]))
            parameter_ci[arm][name] = _ci_diagnostic(rows)
        derived_ci[arm] = {}
        for metric in ("compound_half_time_days", "synthesis_recovery_day_14"):
            rows = []
            for row in arm_records:
                if row["status"] != "evaluable":
                    continue
                values = row["derived_metrics"][metric]
                rows.append((values.get("ci95_lower"), values.get("ci95_upper"), row["true_metrics"][metric]))
            derived_ci[arm][metric] = _ci_diagnostic(rows)
    ratios = [row["symmetric_half_time_ratio"] for row in evaluable]
    return {
        "n_pairs": n_pairs,
        "n_pair_not_evaluable": not_evaluable,
        "proposed_decision_metadata": copy.deepcopy(proposed),
        "decision_counts": decision_summary,
        "summary_semantics": "descriptive_matched_fit_counts_and_fractions_within_one_scenario_design_only_no_record_level_inference_or_scenario_pooling",
        "day14_recovery": recovery,
        "symmetric_half_time_ratio": _numeric_summary(ratios, not_evaluable),
        "fit_failures": fit_failures,
        "covariance_failures": covariance_failures,
        "parameter_ci": parameter_ci,
        "derived_metric_ci": derived_ci,
        "ci_method": "legacy_Jacobian_linearized_parameter_and_delta_method_derived_intervals",
        "formal_equivalence": False,
    }


def compare_no_isotope(primary_records: list, control_records: list, proposed: dict) -> dict:
    """Compare one scenario/design's matched no-isotope fits without pooling scenarios."""
    if len(primary_records) != len(control_records):
        raise ValueError("primary and no-isotope control records must be matched one-to-one")
    identity_keys = ("scenario", "design", "system", "replicate")
    for primary_record, control_record in zip(primary_records, control_records):
        if any(primary_record.get(key) != control_record.get(key) for key in identity_keys):
            raise ValueError("primary and no-isotope control record identities differ")
        if primary_record.get("observation_indices") != control_record.get("observation_indices"):
            raise ValueError("primary and no-isotope control observation subsets differ")
    primary = summarize_paired_records(primary_records, proposed)
    control = summarize_paired_records(control_records, proposed)
    comparisons = {}
    for arm in ARM_NAMES:
        comparisons[arm] = {}
        for name in ("m_old0", "m_new0"):
            p = primary["parameter_ci"][arm][name]["median_width"]
            c = control["parameter_ci"][arm][name]["median_width"]
            comparisons[arm][name] = {
                "isotope_median_ci_width": p, "no_isotope_median_ci_width": c,
                "no_isotope_to_isotope_width_ratio": c / p if p is not None and c is not None and p > 0 else None,
                "status": "evaluable" if p is not None and c is not None and p > 0 else "not_evaluable_ci_unavailable",
            }
    return {
        "primary_summary": primary, "no_isotope_summary": control,
        "old_new_pool_ci_comparison": comparisons,
        "interpretation": "structural_identifiability_diagnostic_not_an_assay_LOD_measurement",
        "matching": "same_scenario_design_system_replicate_and_observations_no_scenario_pooling",
    }


def json_safe(value, path="results") -> tuple:
    """Convert NumPy/scalars and replace nonfinite floats with null plus statuses."""
    statuses = []
    def convert(item, location):
        if isinstance(item, np.generic):
            item = item.item()
        if isinstance(item, dict):
            return {str(key): convert(child, f"{location}.{key}") for key, child in item.items()}
        if isinstance(item, (list, tuple)):
            return [convert(child, f"{location}[{index}]") for index, child in enumerate(item)]
        if isinstance(item, float) and not math.isfinite(item):
            statuses.append({"path": location, "status": "null_because_not_evaluable_nonfinite"})
            return None
        return item
    return convert(value, path), statuses

"""Explore free/bound drug, membrane escape and pigment feedback as assumptions."""
import argparse
import csv
import hashlib
import itertools
import json
import math
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

# State: cytosolic free amount, melanosomal free amount, mobile-bound amount,
# persistent-bound amount, mobile pigment inventory, drug exited, drug entered.
FC, FL, BM, BP, M, EXIT, ENTER = range(7)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def save_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def parameters(config, **overrides):
    base = dict(capacity=100., kd=config["base_binding_Kd"], off_half=1., transport_half=1.,
                persistent=0., q=1., source_mode="suppression", pigment_dynamic=False, added_loss=False)
    base.update(overrides)
    base["ke"] = math.log(2)
    base["koff"] = math.log(2) / base["off_half"]
    base["kon"] = base["koff"] / base["kd"]
    base["conductance"] = math.log(2) * config["melanosome_volume"] / base["transport_half"]
    base["k0"] = math.log(2) / config["hypothetical_native_pigment_half_time"] if base["pigment_dynamic"] else 0.
    base["added"] = math.log(2) / config["hypothetical_added_loss_half_time"] if base["added_loss"] else 0.
    return base


def rhs(config, p, input_rate):
    def evaluate(time, y):
        cyt = y[FC] / config["cytosol_volume"]
        lum = y[FL] / config["melanosome_volume"]
        effect = lum / (1 + lum)
        source_factor = (1 - effect if p["source_mode"] == "suppression" else
                         1 + (config["activation_maximum_source_factor"] - 1) * effect)
        loss = p["k0"] + p["added"] * effect
        cm, cp = p["capacity"] * y[M], p["capacity"] * p["persistent"]
        jm = p["kon"] * lum * (cm - y[BM]) - p["koff"] * y[BM]
        jp = p["kon"] * lum * (cp - y[BP]) - p["koff"] * y[BP]
        transfer = p["conductance"] * (cyt - lum)
        carried = loss * y[BM]
        return [input_rate - p["ke"] * y[FC] - transfer,
                transfer - jm - jp + p["q"] * carried,
                jm - carried, jp,
                p["k0"] * (1 - p["persistent"]) * source_factor - loss * y[M],
                p["ke"] * y[FC] + (1 - p["q"]) * carried, input_rate]
    return evaluate


def solve(config, p, state, end, input_rate):
    events = []
    for threshold in config["effect_thresholds"]:
        target = threshold / (1 - threshold)
        def event(t, y, target=target):
            return y[FL] / config["melanosome_volume"] - target
        event.direction = -1
        event.terminal = False
        events.append(event)
    def jacobian(time, y):
        lum = y[FL] / config["melanosome_volume"]
        derivative_effect = 1 / (config["melanosome_volume"] * (1 + lum)**2)
        derivative_source = (-derivative_effect if p["source_mode"] == "suppression" else
                             (config["activation_maximum_source_factor"] - 1) * derivative_effect)
        loss = p["k0"] + p["added"] * lum / (1 + lum)
        derivative_loss = p["added"] * derivative_effect
        jm_l = p["kon"] * (p["capacity"] * y[M] - y[BM]) / config["melanosome_volume"]
        jp_l = p["kon"] * (p["capacity"] * p["persistent"] - y[BP]) / config["melanosome_volume"]
        j_bound = -p["kon"] * lum - p["koff"]
        jm_m = p["kon"] * lum * p["capacity"]
        tc = p["conductance"] / config["cytosol_volume"]
        tl = p["conductance"] / config["melanosome_volume"]
        jac = np.zeros((7, 7))
        jac[FC, FC], jac[FC, FL] = -p["ke"]-tc, tl
        jac[FL, FC], jac[FL, FL] = tc, -tl-jm_l-jp_l+p["q"]*derivative_loss*y[BM]
        jac[FL, BM], jac[FL, BP], jac[FL, M] = -j_bound+p["q"]*loss, -j_bound, -jm_m
        jac[BM, FL], jac[BM, BM], jac[BM, M] = jm_l-derivative_loss*y[BM], j_bound-loss, jm_m
        jac[BP, FL], jac[BP, BP] = jp_l, j_bound
        jac[M, FL] = p["k0"]*(1-p["persistent"])*derivative_source-derivative_loss*y[M]
        jac[M, M] = -loss
        jac[EXIT, FC], jac[EXIT, FL], jac[EXIT, BM] = p["ke"], (1-p["q"])*derivative_loss*y[BM], (1-p["q"])*loss
        return jac
    solution = solve_ivp(rhs(config, p, input_rate), (0, end), state, jac=jacobian,
                         dense_output=True, events=events, **config["solver"])
    if not solution.success:
        raise ValueError(solution.message)
    return solution


def diagnostics(config, p, solution):
    y = solution.y
    balance = y[FC] + y[FL] + y[BM] + y[BP] + y[EXIT] - y[ENTER]
    expected = balance[0]
    relative_error = float(np.max(np.abs(balance - expected)) / max(1., abs(expected), float(np.max(y[ENTER]))))
    mobile_excess = float(np.max(y[BM] - p["capacity"] * y[M]))
    persistent_excess = float(np.max(y[BP] - p["capacity"] * p["persistent"]))
    minimum = float(np.min(y))
    if relative_error > 1e-7 or max(mobile_excess, persistent_excess) > 1e-7 or minimum < -1e-7:
        raise ValueError("Numerical trajectory violates the declared inventory bounds.")
    return {"max_relative_drug_balance_residual": relative_error,
            "max_mobile_capacity_excess": max(0., mobile_excess),
            "max_persistent_capacity_excess": max(0., persistent_excess), "minimum_state": minimum}


def threshold_metrics(config, solution):
    result = {}
    for threshold, events in zip(config["effect_thresholds"], solution.t_events):
        ending = solution.y[FL, -1] / config["melanosome_volume"]
        target = threshold / (1 - threshold)
        # Last downward crossing in this finite simulation; not an infinite-horizon claim.
        crossing = None if ending > target else float(events[-1]) if len(events) else 0.
        result[f"last_downcross_effect_{threshold}"] = crossing
        result[f"effect_{threshold}_status"] = ("above_at_window_end" if crossing is None else
                                                "downcross_in_window" if len(events) else "already_below_at_withdrawal")
    return result


def sample_rows(config, p, solution, label, phase):
    times = np.unique(np.concatenate(([0.], np.geomspace(.001, solution.t[-1], 80))))
    states = solution.sol(times)
    rows = []
    for time, y in zip(times, states.T):
        lum = y[FL] / config["melanosome_volume"]
        effect = lum / (1 + lum)
        source = 1 - effect if p["source_mode"] == "suppression" else 1 + (config["activation_maximum_source_factor"] - 1) * effect
        rows.append({"case": label, "phase": phase, "time_from_phase_start": float(time),
                     "cytosolic_free_concentration": float(y[FC] / config["cytosol_volume"]),
                     "target_free_concentration": float(lum), "mobile_bound_amount": float(y[BM]),
                     "persistent_bound_amount": float(y[BP]), "total_drug_amount": float(sum(y[:4])),
                     "target_effect_fraction": float(effect), "synthesis_factor": float(source),
                     "pigment_inventory_fraction": float(p["persistent"] + y[M]),
                     "drug_exited": float(y[EXIT]), "drug_entered": float(y[ENTER])})
    return rows


def plot(config, fixed, histories, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "svg.hashsalt": "iris-exposure-hypothesis"})
    fig, axes = plt.subplots(2, 2, figsize=(11.4, 8.0), layout="constrained")
    times = np.linspace(0, 128, 700)
    colors = ["#4b5563", "#168083", "#c86928", "#7954a3"]
    selected = ["capacity0_transport1", "capacity100_off0.1_transport1", "capacity100_off1_transport1", "capacity100_off10_transport1"]
    for key, color in zip(selected, colors):
        p, sol = fixed[key]
        lum = sol.sol(times)[FL] / config["melanosome_volume"]
        label = "No binding" if p["capacity"] == 0 else f"Bound-drug dissociation half-time {p['off_half']:g}"
        axes[0, 0].plot(times, lum, color=color, label=label)
    axes[0, 0].set(title="Same starting free level; different stored inventories", ylabel="Target-accessible free drug (normalized)", yscale="log", ylim=(.03, 11))
    axes[0, 0].axhline(1/9, color="#888888", ls=":", lw=1)
    axes[0, 0].legend(fontsize=7.5)
    for h, color in zip([.1, 1., 10.], colors[:3]):
        key = f"capacity100_off1_transport{h:g}"
        lum = fixed[key][1].sol(times)[FL] / config["melanosome_volume"]
        axes[0, 1].plot(times, lum / (1 + lum), color=color, label=f"Membrane escape half-time {h:g}")
    axes[0, 1].set(title="Binding affinity does not set withdrawal time", ylabel="Hypothetical target effect", ylim=(0, 1))
    axes[0, 1].legend(fontsize=7.5)
    for key, color in zip(["suppress_added_none", "suppress_added_return", "suppress_added_coclear"], colors[:3]):
        p, pre, post = histories[key]
        y = post.sol(times)
        lum = y[FL] / config["melanosome_volume"]
        axes[1, 0].plot(times, 1/(1+lum), color=color, label={"suppress_added_none":"No binding", "suppress_added_return":"Lost pigment returns drug", "suppress_added_coclear":"Lost pigment co-clears drug"}[key])
    axes[1, 0].set(title="Same input and loss rule; bound-drug fate differs", ylabel="Synthesis / original source", ylim=(0, 1.05))
    axes[1, 0].legend(fontsize=7.5)
    pigment_times = np.linspace(0, config["withdrawal_horizon"], 900)
    for key, color in zip(["activate_none", "activate_return", "suppress_added_return", "suppress_added_persistent"], colors):
        p, pre, post = histories[key]
        axes[1, 1].plot(pigment_times, post.sol(pigment_times)[M] + p["persistent"], color=color,
                       label={"activate_none":"Activation, no binding", "activate_return":"Activation, with binding", "suppress_added_return":"Suppression + added loss", "suppress_added_persistent":"Same; 50% persistent"}[key])
    axes[1, 1].axhline(1, color="#888888", lw=1, ls=":")
    axes[1, 1].set(title="Pigment has a separate recovery clock", ylabel="Pigment / original inventory")
    axes[1, 1].legend(fontsize=7.5)
    for ax in axes.flat:
        ax.set_xlabel("Time after input stops (normalized units)")
        ax.grid(alpha=.17)
    fig.suptitle("Hypothetical exposure and pigment feedback\nAll parameters assumed; no drug doses, human times or eye colors assigned", fontsize=13)
    fig.savefig(out / "hypothetical_exposure.svg", metadata={"Date": None})
    fig.savefig(out.parent / "exposure-preview.png", dpi=150)
    plt.close(fig)


def run(config, out, make_plot):
    out.mkdir(parents=True, exist_ok=False)
    grid = [parameters(config, capacity=0., transport_half=h) for h in config["membrane_escape_half_time_grid"]]
    grid.extend(parameters(config, capacity=c, off_half=o, transport_half=t) for c, o, t in itertools.product(
        config["binding_capacity_grid"], config["dissociation_half_time_grid"], config["membrane_escape_half_time_grid"]))
    grid.extend(parameters(config, kd=k) for k in config["additional_Kd_grid"])
    fixed, fixed_rows, observations, numerical = {}, [], [], []
    initial_free = config["initial_equilibrated_free_concentration"]
    for p in grid:
        label = (f"capacity0_transport{p['transport_half']:g}" if p["capacity"] == 0 else
                 f"capacity{p['capacity']:g}_off{p['off_half']:g}_transport{p['transport_half']:g}" + (f"_kd{p['kd']:g}" if p["kd"] != config["base_binding_Kd"] else ""))
        state = [initial_free*config["cytosol_volume"], initial_free*config["melanosome_volume"],
                 p["capacity"]*initial_free/(p["kd"]+initial_free), 0., 1., 0., 0.]
        sol = solve(config, p, state, config["withdrawal_horizon"], 0.)
        fixed[label] = p, sol
        numerical.append({"case": label, **diagnostics(config, p, sol)})
        fixed_rows.append({"case": label, "capacity": p["capacity"], "binding_kd": p["kd"],
                           "dissociation_half_time": p["off_half"], "membrane_escape_half_time": p["transport_half"],
                           "initial_total_drug_amount": sum(state[:4]), **threshold_metrics(config, sol)})
        if (p["capacity"] in {0., 100.} and p["kd"] == 1 and (p["transport_half"] == 1 or p["off_half"] == 1)):
            observations.extend(sample_rows(config, p, sol, label, "equilibrated_withdrawal"))
    specifications = [
        ("suppress_none", dict(capacity=0.)),
        ("suppress_return", dict(q=1.)),
        ("suppress_coclear", dict(q=0.)),
        ("suppress_added_none", dict(capacity=0., added_loss=True)),
        ("suppress_added_return", dict(q=1., added_loss=True)),
        ("suppress_added_coclear", dict(q=0., added_loss=True)),
        ("suppress_added_persistent", dict(q=1., added_loss=True, persistent=.5)),
        ("activate_none", dict(capacity=0., source_mode="activation")),
        ("activate_return", dict(q=1., source_mode="activation")),
    ]
    histories, history_rows = {}, []
    for label, overrides in specifications:
        p = parameters(config, pigment_dynamic=True, **overrides)
        state = [0., 0., 0., 0., 1-p["persistent"], 0., 0.]
        pre = solve(config, p, state, config["input_phase_duration"], p["ke"]*initial_free)
        post = solve(config, p, pre.y[:, -1], config["withdrawal_horizon"], 0.)
        histories[label] = p, pre, post
        numerical.extend({"case": label, "phase": phase, **diagnostics(config, p, sol)} for phase, sol in [("input", pre), ("withdrawal", post)])
        observations.extend(sample_rows(config, p, pre, label, "input"))
        observations.extend(sample_rows(config, p, post, label, "withdrawal"))
        peak_times = np.linspace(0, config["withdrawal_horizon"], 4097)
        sampled = post.sol(peak_times)
        pigment = sampled[M] + p["persistent"]
        effect = (sampled[FL] / config["melanosome_volume"]) / (1 + sampled[FL] / config["melanosome_volume"])
        history_rows.append({"case": label, "capacity": p["capacity"], "persistent_fraction": p["persistent"],
                             "drug_return_fraction_q": p["q"], "source_mode": p["source_mode"], "added_loss": p["added_loss"],
                             "target_free_at_withdrawal": float(post.y[FL, 0]/config["melanosome_volume"]),
                             "initial_pigment": float(post.y[M, 0]+p["persistent"]),
                             "pigment_at_end": float(post.y[M, -1]+p["persistent"]),
                             "sampled_max_pigment": float(np.max(pigment)),
                             "sampled_max_pigment_time_after_withdrawal": float(peak_times[np.argmax(pigment)]),
                             "sampled_min_pigment": float(np.min(pigment)),
                             "sampled_min_pigment_time_after_withdrawal": float(peak_times[np.argmin(pigment)]),
                             "sampled_max_effect": float(np.max(effect)),
                             "sampled_max_effect_time_after_withdrawal": float(peak_times[np.argmax(effect)]),
                             "total_input_amount": float(pre.y[ENTER, -1]), **threshold_metrics(config, post)})
    save_csv(out / "fixed_capacity_summary.csv", fixed_rows)
    save_csv(out / "matched_history_summary.csv", history_rows)
    save_csv(out / "selected_trajectories.csv", observations)
    save_json(out / "numerical_accounting.json", numerical)
    save_json(out / "summary.json", {"fixed_capacity_cases": len(fixed_rows), "matched_history_cases": len(history_rows),
              "hypothetical": True, "equilibrated_withdrawal_cases_have_equal_initial_free_not_equal_total_drug": True,
              "matched_history_cases_have_equal_input_history_not_equal_free_exposure": True,
              "fixed_capacity_parameters": grid,
              "history_parameters": {label: histories[label][0] for label, _ in specifications},
              "threshold_time_meaning": "Last downward crossing within the finite withdrawal window; null if above threshold at the window end. A zero with already_below_at_withdrawal status means no downcross occurred.",
              "threshold_effect_is_not_always_fractional_synthesis_change": {
                  "effect_0.1_suppression_source_factor": .9,
                  "effect_0.1_activation_source_factor": 1 + .1*(config["activation_maximum_source_factor"]-1)},
              "membrane_escape_half_time_definition": "Nominal unbound luminal half-time with the cytosolic concentration clamped at zero; not the observed whole-cell withdrawal half-time.",
              "maximum_relative_drug_balance_residual": max(n["max_relative_drug_balance_residual"] for n in numerical)})
    if make_plot:
        plot(config, fixed, histories, out)
    outputs = {p.name: {"bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(out.iterdir()) if p.is_file()}
    save_json(out / "receipt.json", {"script_sha256": digest(Path(__file__)), "assumptions": config,
              "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "outputs": outputs})
    print(json.dumps({"output": str(out), "fixed_cases": len(fixed_rows), "history_cases": len(history_rows),
                      "max_relative_balance_residual": max(n["max_relative_drug_balance_residual"] for n in numerical)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assumptions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    run(json.loads(args.assumptions.read_text(encoding="utf-8")), args.out, args.plot)

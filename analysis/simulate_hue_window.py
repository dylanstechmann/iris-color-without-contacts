"""Explore which CIELAB hue windows a toy scatter-plus-absorber iris model can reach."""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import platform
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def wavelengths(spec):
    return list(range(spec["start"], spec["stop"] + 1, spec["step"]))


def logistic(x):
    return 1 / (1 + math.exp(-x))


def backscatter(wl, fraction_at_550, exponent):
    return min(1.0, fraction_at_550 * (550 / wl) ** exponent)


def absorbance(wl, amount, pheo_share, eu_exponent, pheo_exponent):
    return amount * ((1 - pheo_share) * (550 / wl) ** eu_exponent
                     + pheo_share * (550 / wl) ** pheo_exponent)


def back_return(wl, mode):
    if mode["type"] == "constant":
        return mode["value"]
    if mode["type"] == "red_edge":
        return mode["floor"] + (mode["plateau"] - mode["floor"]) * logistic((wl - mode["edge_nm"]) / mode["width_nm"])
    raise ValueError("Unknown back-return type: " + str(mode["type"]))


def reflectance(wl, config, amount, pheo_share, eu_exponent, pheo_exponent, mode):
    scatter = backscatter(wl, config["stroma_backscatter"]["fraction_at_550nm"],
                          config["stroma_backscatter"]["wavelength_exponent"])
    a = absorbance(wl, amount, pheo_share, eu_exponent, pheo_exponent)
    phi = config["overlying_pigment_path_fraction"]
    return scatter * math.exp(-2 * phi * a) + (1 - scatter) * math.exp(-2 * a) * back_return(wl, mode)


def reference_reflectance(wl, ref):
    w = ref["width_nm"]
    span = ref["high"] - ref["low"]
    if ref["type"] == "long_pass":
        return ref["low"] + span * logistic((wl - ref["edge_nm"]) / w)
    if ref["type"] == "short_pass":
        return ref["low"] + span * (1 - logistic((wl - ref["edge_nm"]) / w))
    if ref["type"] == "bimodal":
        return ref["low"] + span * ((1 - logistic((wl - ref["blue_edge_nm"]) / w))
                                    + logistic((wl - ref["red_edge_nm"]) / w))
    raise ValueError("Unknown reference type: " + str(ref["type"]))


def read_table(path, expected_sha256):
    blob = path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != expected_sha256:
        raise ValueError("Table differs from its pinned CIE checksum: " + str(path))
    return {int(row[0]): [float(v) for v in row[1:]] for row in csv.reader(blob.decode("utf-8").splitlines())}


def load_colorimetry(config, wls):
    """Illuminant-weighted colour-matching functions at the model wavelengths, plus the perfect-reflector white."""
    spec = config["colorimetry"]
    cmf = read_table(ROOT / spec["observer_csv"], spec["observer_sha256"])
    illuminant = read_table(ROOT / spec["illuminant_csv"], spec["illuminant_sha256"])
    weights = [[illuminant[wl][0] * value for value in cmf[wl]] for wl in wls]
    return {"weights": weights, "white": [sum(w[i] for w in weights) for i in range(3)]}


def lab(spectrum, colorimetry):
    """CIE 1976 L*a*b*; hue angle does not change when a spectrum is uniformly dimmed."""
    xyz = [sum(r * w[i] for r, w in zip(spectrum, colorimetry["weights"])) / colorimetry["white"][i]
           for i in range(3)]
    f = [t ** (1 / 3) if t > (6 / 29) ** 3 else t / (3 * (6 / 29) ** 2) + 4 / 29 for t in xyz]
    a, b = 500 * (f[0] - f[1]), 200 * (f[1] - f[2])
    return {"L_star": 116 * f[1] - 16, "a_star": a, "b_star": b, "chroma": math.hypot(a, b),
            "hue_degrees": math.degrees(math.atan2(b, a)) % 360, "luminance": xyz[1]}


def angle_gap(a, b):
    return abs((a - b + 180) % 360 - 180)


def classify(coords, windows, halfwidth, chroma_fraction, luminance_fraction=0.0):
    hits = []
    for name, ref in windows.items():
        if angle_gap(coords["hue_degrees"], ref["hue_degrees"]) <= halfwidth \
                and coords["chroma"] >= chroma_fraction * ref["chroma"] \
                and coords["luminance"] >= luminance_fraction * ref["luminance"]:
            hits.append(name)
    return hits


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def run(config, out):
    out.mkdir(parents=True, exist_ok=False)
    wls = wavelengths(config["wavelengths_nm"])
    colorimetry = load_colorimetry(config, wls)
    halfwidth = config["hue_window_halfwidth_degrees"]
    thresholds = config["chroma_fraction_thresholds"]
    floor = config["luminance_fraction_minimum"]
    windows = {name: lab([reference_reflectance(wl, ref) for wl in wls], colorimetry)
               for name, ref in config["reference_stimuli"].items()}
    rows = []
    grid = itertools.product(config["back_return_modes"].items(), config["eumelanin_spectral_exponent"],
                             config["pheomelanin_spectral_exponent"],
                             config["pigment_absorbance_at_550nm"], config["pheomelanin_share_of_absorbance"])
    for (mode_name, mode), ne, np_, amount, q in grid:
        if amount == 0 and q != config["pheomelanin_share_of_absorbance"][0]:
            continue  # pheomelanin share is undefined without pigment
        spectrum = [reflectance(wl, config, amount, q, ne, np_, mode) for wl in wls]
        coords = lab(spectrum, colorimetry)
        row = {"back_return": mode_name, "eumelanin_exponent": ne, "pheomelanin_exponent": np_,
               "absorbance_550nm": amount, "pheomelanin_share": q,
               "reflectance_450nm": spectrum[wls.index(450)], "reflectance_550nm": spectrum[wls.index(550)],
               "reflectance_650nm": spectrum[wls.index(650)], **coords}
        for t in thresholds:
            row["windows_at_chroma_fraction_" + str(t)] = ";".join(classify(coords, windows, halfwidth, t, floor)) or "none"
        rows.append(row)
    with (out / "scenario_sweep.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {"activity": "Toy scatter-plus-absorber CIELAB hue-window exploration", "scenario_count": len(rows),
               "reference_windows": windows, "by_back_return": {}}
    for mode_name in config["back_return_modes"]:
        mode_rows = [r for r in rows if r["back_return"] == mode_name]
        entry = {"scenarios": len(mode_rows)}
        for name, ref in windows.items():
            near = [r for r in mode_rows if angle_gap(r["hue_degrees"], ref["hue_degrees"]) <= halfwidth]
            entry[name] = {"scenarios_in_hue_window": len(near),
                           "scenarios_in_hue_window_below_luminance_floor": sum(
                               r["luminance"] < floor * ref["luminance"] for r in near),
                           "best_chroma_fraction_of_reference": max((r["chroma"] / ref["chroma"] for r in near), default=0.0),
                           "best_luminance_fraction_of_reference": max((r["luminance"] / ref["luminance"] for r in near), default=0.0)}
            for t in thresholds:
                entry[name]["scenarios_classified_at_chroma_fraction_" + str(t)] = sum(
                    name in r["windows_at_chroma_fraction_" + str(t)].split(";") for r in mode_rows)
        summary["by_back_return"][mode_name] = entry
    summary["luminance_fraction_minimum"] = floor
    summary["interpretation"] = ("Consequences of the stated spectral shapes and thresholds only. No measured iris spectrum, "
                                 "pigment amount, viewing condition, drug effect or achievable eye color.")
    write_json(out / "summary.json", summary)

    lines = ["# Hypothetical hue-window exploration", "",
             "The iris spectra, thresholds and windows are assumptions; only the colorimetry tables are standard.", "",
             "Model: reflectance = B*exp(-2*phi*A) + (1-B)*exp(-2*A)*rho, where B is bounded Rayleigh-like",
             "stromal backscatter, A is the sum of eumelanin and pheomelanin absorbance (power laws), phi is the",
             "fraction of pigment lying above the scattering events, and rho is the return from behind the stroma.",
             "Colour is CIE 1976 L*a*b* from the CIE 1931 2 degree observer under illuminant D65, sampled every",
             f"{config['wavelengths_nm']['step']} nm from {config['wavelengths_nm']['start']} to {config['wavelengths_nm']['stop']} nm. "
             "Windows are hue-angle ranges centred on reference spectra: a short-pass, a long-pass and a",
             f"bimodal (blue plus red) reflector. A scenario is in a window when its hue is within {halfwidth} degrees of",
             "the reference's. It is classified when its chroma is also at least the stated fraction of the reference",
             f"chroma and its luminance Y is at least {floor} of the reference's.", "",
             "| Back return | Window | Scenarios in hue window | Of those, below luminance floor | Best chroma / reference | Best luminance / reference | Classified at chroma fraction "
             + " / ".join(str(t) for t in thresholds) + " |", "| --- | --- | ---: | ---: | ---: | ---: | --- |"]
    for mode_name, entry in summary["by_back_return"].items():
        for name in windows:
            e = entry[name]
            counts = " / ".join(str(e["scenarios_classified_at_chroma_fraction_" + str(t)]) for t in thresholds)
            lines.append(f"| {mode_name} | {name} | {e['scenarios_in_hue_window']} of {entry['scenarios']} | "
                         f"{e['scenarios_in_hue_window_below_luminance_floor']} | {e['best_chroma_fraction_of_reference']:.2f} | {e['best_luminance_fraction_of_reference']:.2f} | {counts} |")
    lines.extend(["", "| Reference | Hue angle | Chroma | L* | Luminance Y |", "| --- | ---: | ---: | ---: | ---: |"])
    for name, ref in windows.items():
        lines.append(f"| {name} | {ref['hue_degrees']:.1f} | {ref['chroma']:.1f} | {ref['L_star']:.1f} | {ref['luminance']:.3f} |")
    lines.extend(["", "Counts come from an unweighted grid; they are not probabilities and do not rank outcomes.",
                  "A scenario that lands in a window shows that the assumed spectra allow it, not that an iris can.",
                  f"The {len(config['back_return_modes']) - 1} translucent-return modes assume a reddish return behind a pigment-poor stroma at",
                  "different strengths, because the real strength is unknown. Such a state is the transparency route",
                  "discussed in the sidequest note and is not a function-preserving target.",
                  "Measured melanin spectra and a measured back return are the first changes that could move these results."])
    (out / "MODEL_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    files = {}
    for path in sorted(out.iterdir()):
        if path.is_file():
            blob = path.read_bytes()
            files[path.name] = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
    inputs = {}
    for key in ("observer_csv", "illuminant_csv"):
        blob = (ROOT / config["colorimetry"][key]).read_bytes()
        inputs[config["colorimetry"][key]] = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
    source = Path(__file__).resolve()
    write_json(out / "receipt.json", {
        "model_status": "hypothetical", "python": platform.python_version(),
        "assumptions": config, "script_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "inputs": inputs, "scenario_count": len(rows), "outputs": files,
    })
    print(json.dumps({"scenarios": len(rows), "output": str(out), "measured_iris_parameters": False}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assumptions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(json.loads(args.assumptions.read_text(encoding="utf-8")), args.out)

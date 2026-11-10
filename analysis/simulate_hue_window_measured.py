"""Explore which CIELAB hue windows a toy scatter-plus-absorber iris model can reach.

Measured-melanin variant: melanin spectral SHAPES are the measured Sarna & Swartz 1988
extinction coefficients (Waterloo NPSG / Oregon Medical Laser Center), linearly
interpolated and normalized to 1.0 at 550 nm, replacing the previously assumed power-law
wavelength exponents. The 550 nm absorbance magnitudes, stroma settings, path fraction,
back return, thresholds and windows remain assumptions. A measured pheomelanin visible
spectrum is no longer an outstanding input; a measured back return still is.
"""
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
RANGE_FIELDS = ("pheomelanin_share", "absorbance_550nm",
                "backscatter_550nm", "backscatter_exponent", "path_fraction")


def wavelengths(spec):
    return list(range(spec["start"], spec["stop"] + 1, spec["step"]))


def logistic(x):
    return 1 / (1 + math.exp(-x))


def backscatter(wl, fraction_at_550, exponent):
    return min(1.0, fraction_at_550 * (550 / wl) ** exponent)


def read_melanin_table(path, expected_sha256):
    """Read a two-column melanin CSV: wavelength_nm, extinction."""
    blob = path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != expected_sha256:
        raise ValueError("Melanin table differs from its pinned checksum: " + str(path))
    rows = list(csv.reader(blob.decode("utf-8").splitlines()))
    if rows and rows[0][0].lower() in ("wavelength_nm", "wavelength"):
        rows = rows[1:]
    return {int(row[0]): float(row[1]) for row in rows if len(row) >= 2}


def melanin_shape(path, sha256, wl_nm):
    """Return the normalized melanin extinction at wl_nm, linearly interpolated.
    Normalization is to the 550 nm value in the table."""
    table = read_melanin_table(path, sha256)
    val_550 = table.get(550)
    if val_550 is None:
        raise ValueError("Melanin table missing 550 nm value")
    wls = sorted(table.keys())
    extincts = [table[w] for w in wls]
    if wl_nm <= wls[0]:
        val = extincts[0]
    elif wl_nm >= wls[-1]:
        val = extincts[-1]
    else:
        for i in range(len(wls) - 1):
            if wls[i] <= wl_nm <= wls[i + 1]:
                t = (wl_nm - wls[i]) / (wls[i + 1] - wls[i])
                val = extincts[i] + t * (extincts[i + 1] - extincts[i])
                break
        else:
            val = extincts[-1]
    return val / val_550


def load_melanin_shapes(config, wls):
    """550-normalized measured melanin shapes at the model wavelengths."""
    spec = config["melanin_spectra"]
    return ({wl: melanin_shape(ROOT / spec["eumelanin_csv"], spec["eumelanin_sha256"], wl) for wl in wls},
            {wl: melanin_shape(ROOT / spec["pheomelanin_csv"], spec["pheomelanin_sha256"], wl) for wl in wls})


def absorbance(wl, amount, pheo_share, eu_shape, ph_shape):
    return amount * ((1 - pheo_share) * eu_shape[wl] + pheo_share * ph_shape[wl])


def back_return(wl, mode):
    if mode["type"] == "constant":
        return mode["value"]
    if mode["type"] == "red_edge":
        return mode["floor"] + (mode["plateau"] - mode["floor"]) * logistic((wl - mode["edge_nm"]) / mode["width_nm"])
    raise ValueError("Unknown back-return type: " + str(mode["type"]))


def return_strength(mode):
    return mode["value"] if mode["type"] == "constant" else mode["plateau"]


def reflectance(wl, stroma, path_fraction, amount, pheo_share, eu_shape, ph_shape, mode):
    """stroma is (backscatter fraction at 550 nm, wavelength exponent)."""
    scatter = backscatter(wl, *stroma)
    a = absorbance(wl, amount, pheo_share, eu_shape, ph_shape)
    return scatter * math.exp(-2 * path_fraction * a) + (1 - scatter) * math.exp(-2 * a) * back_return(wl, mode)


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


def envelope(subset, name, ref, halfwidth, thresholds):
    """Counts for one window, and the parameter ranges of the cases that reach it."""
    near = [r for r in subset if angle_gap(r["hue_degrees"], ref["hue_degrees"]) <= halfwidth]
    colorful = [r for r in near if r["chroma"] >= thresholds[0] * ref["chroma"]]
    out = {"scenarios": len(subset), "in_hue_window": len(near), "in_hue_window_with_chroma": len(colorful),
           "best_luminance_fraction_with_chroma": max((r["luminance"] / ref["luminance"] for r in colorful), default=0.0)}
    if colorful:
        top = max(colorful, key=lambda r: r["luminance"])
        out["brightest_case_with_chroma"] = {f: top[f] for f in RANGE_FIELDS + ("L_star", "chroma", "hue_degrees")}
    for t in thresholds:
        hit = [r for r in subset if name in r["windows_at_chroma_fraction_" + str(t)].split(";")]
        out["classified_at_chroma_fraction_" + str(t)] = {"count": len(hit)}
        if hit:
            out["classified_at_chroma_fraction_" + str(t)]["ranges"] = {
                f: [min(r[f] for r in hit), max(r[f] for r in hit)] for f in RANGE_FIELDS}
    return out


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def span(pair):
    return f"{pair[0]:g}–{pair[1]:g}" if pair[0] != pair[1] else f"{pair[0]:g}"


def run(config, out):
    out.mkdir(parents=True, exist_ok=False)
    wls = wavelengths(config["wavelengths_nm"])
    colorimetry = load_colorimetry(config, wls)
    eu_shape, ph_shape = load_melanin_shapes(config, wls)
    halfwidth = config["hue_window_halfwidth_degrees"]
    thresholds = config["chroma_fraction_thresholds"]
    floor = config["luminance_fraction_minimum"]
    modes = config["back_return_modes"]
    windows = {name: lab([reference_reflectance(wl, ref) for wl in wls], colorimetry)
               for name, ref in config["reference_stimuli"].items()}

    stromas = list(itertools.product(config["stroma_backscatter"]["fraction_at_550nm"],
                                     config["stroma_backscatter"]["wavelength_exponent"]))
    cal = config["calibration"]
    stroma_settings = []
    for stroma in stromas:
        free = lab([reflectance(wl, stroma, 0.5, 0, 0, eu_shape, ph_shape, modes[cal["back_return"]])
                    for wl in wls], colorimetry)
        stroma_settings.append({"backscatter_550nm": stroma[0], "backscatter_exponent": stroma[1],
                                "blue_calibrated": cal["window"] in classify(free, windows, halfwidth,
                                                                              cal["chroma_fraction"], floor),
                                "pigment_free": free})
    calibrated = {(s["backscatter_550nm"], s["backscatter_exponent"]): s["blue_calibrated"] for s in stroma_settings}

    rows = []
    first_phi = config["path_fraction"][0]
    first_share = config["pheomelanin_share_of_absorbance"][0]
    grid = itertools.product(stromas, config["path_fraction"],
                             modes.items(), config["pigment_absorbance_at_550nm"],
                             config["pheomelanin_share_of_absorbance"])
    for stroma, phi, (mode_name, mode), amount, q in grid:
        if amount == 0 and (q != first_share or phi != first_phi):
            continue  # without pigment these two inputs change nothing
        spectrum = [reflectance(wl, stroma, phi, amount, q, eu_shape, ph_shape, mode) for wl in wls]
        coords = lab(spectrum, colorimetry)
        row = {"back_return": mode_name, "return_strength": return_strength(mode),
               "backscatter_550nm": stroma[0], "backscatter_exponent": stroma[1],
               "stroma_blue_calibrated": calibrated[stroma], "path_fraction": phi,
               "absorbance_550nm": amount, "pheomelanin_share": q,
               **{k: round(v, 5) for k, v in coords.items()}}
        for t in thresholds:
            row["windows_at_chroma_fraction_" + str(t)] = ";".join(classify(coords, windows, halfwidth, t, floor)) or "none"
        rows.append(row)
    with (out / "scenario_sweep.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {"activity": "Toy scatter-plus-absorber CIELAB hue-window exploration with measured melanin spectra",
               "scenario_count": len(rows),
               "reference_windows": windows, "stroma_settings": stroma_settings, "by_back_return": {},
               "luminance_fraction_minimum": floor}
    for mode_name in modes:
        mode_rows = [r for r in rows if r["back_return"] == mode_name]
        summary["by_back_return"][mode_name] = {
            group: {name: envelope([r for r in mode_rows if r["stroma_blue_calibrated"] == flag],
                                   name, ref, halfwidth, thresholds) for name, ref in windows.items()}
            for group, flag in (("blue_calibrated_stroma", True), ("other_stroma", False))}

    translucent = [n for n, m in modes.items() if m["type"] == "red_edge"]
    anchor = config["measured_anchors"][0]
    reached = {}
    for name in ("purple", "orange"):
        per_stroma = {}
        for r in rows:
            if r["back_return"] in translucent and r["stroma_blue_calibrated"] \
                    and name in r["windows_at_chroma_fraction_" + str(thresholds[0])].split(";"):
                key = (r["backscatter_550nm"], r["backscatter_exponent"])
                per_stroma[key] = min(per_stroma.get(key, 1.0), r["return_strength"])
        values = sorted(per_stroma.values())
        entry = {"blue_calibrated_stroma_settings": sum(calibrated.values()), "settings_reaching_window": len(values)}
        if values:
            entry.update({"smallest_return_strength_range": [values[0], values[-1]],
                          "implied_one_way_red_transmission_range": [math.sqrt(values[0]), math.sqrt(values[-1])]})
        reached[name] = entry
    summary["return_strength_needed"] = {
        "windows": reached,
        "implied_transmission_rule": "return = T^2 for a perfect reflector behind a layer crossed twice, so T = sqrt(return)",
        "measured_anchor": anchor,
    }
    summary["interpretation"] = ("Consequences of the stated spectral shapes, thresholds and calibration only. No measured iris "
                                 "spectrum, pigment amount, viewing condition, drug effect or achievable eye color.")
    write_json(out / "summary.json", summary)

    n_cal = sum(calibrated.values())
    lines = ["# Hypothetical hue-window exploration with measured melanin spectra", "",
             "The iris spectra, thresholds and windows are assumptions; the colorimetry tables and the melanin",
             "spectral shapes are the only sourced inputs (see the assumptions file for provenance). The melanin",
             "shapes are the measured Sarna & Swartz 1988 extinction coefficients, linearly interpolated and",
             "normalized to 1.0 at 550 nm; the 550 nm absorbance magnitudes remain assumptions.", "",
             "Model: reflectance = B*exp(-2*phi*A) + (1-B)*exp(-2*A)*rho, where B is bounded stromal backscatter,",
             "A is the sum of eumelanin and pheomelanin absorbance (measured 550-normalized shapes), phi is the",
             "fraction of pigment above the scattering events, and rho is the return from behind the stroma.",
             "Colour is CIE 1976 L*a*b* for the CIE 1931 2 degree observer under illuminant D65, sampled every",
             f"{config['wavelengths_nm']['step']} nm from {config['wavelengths_nm']['start']} to {config['wavelengths_nm']['stop']} nm. "
             "Windows are hue-angle ranges centred on reference spectra: a short-pass, a long-pass and a",
             f"bimodal (blue plus red) reflector. A case is in a window when its hue is within {halfwidth} degrees of the reference's.",
             "It is classified when its chroma is also at least the stated fraction of the reference chroma and its",
             f"luminance Y is at least {floor} of the reference's.", "",
             "## Calibration: which stroma settings can represent a blue iris at all", "",
             f"A stroma setting is used for interpretation only if, with no pigment over a dark back, it falls in the {cal['window']} window",
             f"(chroma fraction {cal['chroma_fraction']}). {n_cal} of {len(stroma_settings)} settings pass.", "",
             "| Backscatter at 550 nm | Wavelength exponent | Pigment-free hue | Chroma | L* | Calibrated |",
             "| ---: | ---: | ---: | ---: | ---: | --- |"]
    for s in stroma_settings:
        f = s["pigment_free"]
        lines.append(f"| {s['backscatter_550nm']:g} | {s['backscatter_exponent']:g} | {f['hue_degrees']:.0f} | "
                     f"{f['chroma']:.1f} | {f['L_star']:.0f} | {'yes' if s['blue_calibrated'] else 'no'} |")
    t0 = str(thresholds[0])
    lines.extend(["", "## Reachability in blue-calibrated stromas", "",
                  "\"Hue\" counts cases inside the hue window, which includes near-black cases where hue means little.",
                  f"\"Hue + chroma\" also requires chroma of at least {t0} of the reference. \"Classified\" also requires the luminance",
                  "floor. Ranges describe the classified cases only.", "",
                  "| Back return | Window | Hue | Hue + chroma | Classified | Brightest hue + chroma case (Y / reference, L*) | Pheomelanin share | Absorbance at 550 nm |",
                  "| --- | --- | ---: | ---: | ---: | --- | --- | --- |"])
    for mode_name, groups in summary["by_back_return"].items():
        for name in ("orange", "purple"):
            e = groups["blue_calibrated_stroma"][name]
            c = e["classified_at_chroma_fraction_" + t0]
            r = c.get("ranges")
            top = e.get("brightest_case_with_chroma")
            lines.append(f"| {mode_name} | {name} | {e['in_hue_window']} of {e['scenarios']} | {e['in_hue_window_with_chroma']} | {c['count']} | "
                         + (f"{e['best_luminance_fraction_with_chroma']:.2f}, L* {top['L_star']:.0f}" if top else "–") + " | "
                         + (" | ".join(span(r[k]) for k in ("pheomelanin_share", "absorbance_550nm"))
                            if r else "– | –") + " |")
    other = {name: summary["by_back_return"]["dark_pigment_epithelium"]["other_stroma"][name]
             ["classified_at_chroma_fraction_" + t0]["count"] for name in ("orange", "purple")}
    lines.extend(["", f"Over the dark back, the {len(stroma_settings) - n_cal} stroma settings that do not read blue when pigment-free",
                  f"classify {other['orange']} orange and {other['purple']} purple cases. They are not used: a stroma that is already",
                  "whitish before any pigment is added cannot be taken as evidence for what a pigmented iris does.", "",
                  "## Return strength needed behind the stroma", ""])
    for name, entry in reached.items():
        if "smallest_return_strength_range" in entry:
            lo, hi = entry["smallest_return_strength_range"]
            tl, th = entry["implied_one_way_red_transmission_range"]
            lines.append(f"- **{name}:** reached in {entry['settings_reaching_window']} of {entry['blue_calibrated_stroma_settings']} "
                         f"calibrated stroma settings, at a smallest red return of {lo:g} to {hi:g} on the swept grid. A round trip "
                         f"behind a perfect reflector implies one-way red transmission of {tl:.2f} to {th:.2f}.")
        else:
            lines.append(f"- **{name}:** not reached in any calibrated stroma setting on the swept grid.")
    lines.extend(["", f"Measured anchor: {anchor['claim']} ({anchor['source']}; {anchor['method']}). It concerns a non-albino iris and a",
                  "different geometry from the model's, so it is an order-of-magnitude comparison, not a calibration.", "",
                  "## Reference spectra", "", "| Reference | Hue angle | Chroma | L* | Luminance Y |", "| --- | ---: | ---: | ---: | ---: |"])
    for name, ref in windows.items():
        lines.append(f"| {name} | {ref['hue_degrees']:.1f} | {ref['chroma']:.1f} | {ref['L_star']:.1f} | {ref['luminance']:.3f} |")
    lines.extend(["", "Counts come from an unweighted grid; they are not probabilities and do not rank outcomes.",
                  "A case that lands in a window shows that the assumed spectra allow it, not that an iris can.",
                  "The translucent-return modes describe a reddish return behind a pigment-poor stroma, the transparency",
                  "route discussed in the sidequest note, which is not a function-preserving target.",
                  "The melanin spectral shapes are measured (Sarna & Swartz 1988, normalized at 550 nm); the 550 nm",
                  "magnitudes, the stroma settings, the path fraction and the return edge remain assumptions.",
                  "A measured back return is the input most able to change these results."])
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
    ms = config["melanin_spectra"]
    for key in ("eumelanin_csv", "pheomelanin_csv"):
        blob = (ROOT / ms[key]).read_bytes()
        inputs[ms[key]] = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
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

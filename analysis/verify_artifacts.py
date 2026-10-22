"""Verify the selected computational artifact bytes; this is not scientific validation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def check():
    checked = 0
    for name, key in [
        ("feasibility-run-2026-10-17", "outputs"),
        ("exposure-run-2026-10-17", "outputs"),
        ("binding-benchmark-run-2026-10-17", "outputs"),
        ("ampyrone-data-run-2026-10-17", "outputs"),
        ("withdrawal-evidence-run-2026-10-17", "outputs"),
        ("recovery-identifiability-run-2026-10-17", "outputs"),
        ("kt939-comparison-run-2026-10-22", "outputs"),
        ("iris-atlas-run-2026-10-17", "outputs"),
        ("workbench-comparison-2026-10-17", "files"),
        ("target-snapshots-2026-10-17", None),
    ]:
        folder = ROOT / name
        receipt = json.loads((folder / "receipt.json").read_text(encoding="utf-8-sig"))
        entries = ((row["file"], row) for row in receipt) if key is None else receipt[key].items()
        for relative, spec in entries:
            path = (folder / relative).resolve()
            if not path.is_relative_to(folder.resolve()):
                raise ValueError("Unexpected path outside receipt folder.")
            if not path.is_file() or path.stat().st_size != spec["bytes"] or digest(path) != spec["sha256"]:
                raise ValueError("Artifact mismatch: " + str(path))
            checked += 1
    model = json.loads((ROOT / "feasibility-run-2026-10-17" / "receipt.json").read_text())
    atlas = json.loads((ROOT / "iris-atlas-run-2026-10-17" / "receipt.json").read_text())
    if digest(ROOT / "simulate_feasibility.py") != model["script_sha256"]:
        raise ValueError("Model source differs from run receipt.")
    if digest(ROOT / "check_iris_targets.py") != atlas["script_sha256"]:
        raise ValueError("Iris analysis source differs from run receipt.")
    exposure = json.loads((ROOT / "exposure-run-2026-10-17" / "receipt.json").read_text())
    if digest(ROOT / "simulate_exposure.py") != exposure["script_sha256"]:
        raise ValueError("Exposure source differs from run receipt.")
    if json.loads((ROOT / "exposure_assumptions.json").read_text()) != exposure["assumptions"]:
        raise ValueError("Exposure assumptions differ from run receipt.")
    binding = json.loads((ROOT / "binding-benchmark-run-2026-10-17" / "receipt.json").read_text())
    if digest(ROOT / "build_binding_benchmark.py") != binding["script_sha256"]:
        raise ValueError("Binding benchmark source differs from run receipt.")
    if digest(ROOT / "binding_benchmark_inputs.json") != binding["input_sha256"]:
        raise ValueError("Binding benchmark inputs differ from run receipt.")
    ampyrone = json.loads((ROOT / "ampyrone-data-run-2026-10-17" / "receipt.json").read_text())
    for script, expected_hash in ampyrone["analysis_scripts"].items():
        if digest(ROOT / script) != expected_hash:
            raise ValueError("Ampyrone analysis source differs from receipt: " + script)
    for folder, script, input_file, input_key in [
        ("withdrawal-evidence-run-2026-10-17", "extract_withdrawal_evidence.py", "withdrawal_clinical_inputs.json", "clinical_inputs_sha256"),
        ("recovery-identifiability-run-2026-10-17", "demonstrate_recovery_identifiability.py", "recovery_identifiability_assumptions.json", "assumptions_sha256"),
    ]:
        run_receipt = json.loads((ROOT / folder / "receipt.json").read_text())
        if digest(ROOT / script) != run_receipt["script_sha256"] or digest(ROOT / input_file) != run_receipt[input_key]:
            raise ValueError("Recovery/withdrawal source or input differs from receipt: " + script)
    comparison = json.loads((ROOT / "kt939-comparison-run-2026-10-22" / "receipt.json").read_text())
    if digest(ROOT / "compare_kt939_thiamidol.py") != comparison["script_sha256"]:
        raise ValueError("KT-939 comparison script differs from run receipt.")
    reference = ROOT / "binding-benchmark-run-2026-10-17/pubchem/thiamidol.pubchem.json"
    if digest(reference) != comparison["reference_sha256"]:
        raise ValueError("KT-939 comparison reference differs from run receipt.")
    prior_sources = json.loads((ROOT / "withdrawal-evidence-run-2026-10-17/sources.json").read_text())
    if comparison["source_xml_sha256"] != next(row["sha256"] for row in prior_sources if row["file"] == "kt939.xml"):
        raise ValueError("KT-939 XML source hash differs from qualified withdrawal snapshot.")
    for name, receipt_name, script in [
        ("tyr-assay-audit-final-2026-10-17", "receipt.json", "audit_tyr_assays.py"),
        ("tyr-assay-audit-final-2026-10-17", "qualification_receipt.json", "qualify_tyr_records.py"),
        ("ip3r2-data-run-2026-10-17", "receipt.json", "extract_ip3r2_data.py"),
    ]:
        folder = ROOT / name
        receipt = json.loads((folder / receipt_name).read_text(encoding="utf-8"))
        entries = receipt["files"]
        if isinstance(entries, list):
            entries = {row["path"]: row for row in entries}
        for relative, spec in entries.items():
            path = (folder / relative).resolve()
            if not path.is_relative_to(folder.resolve()):
                raise ValueError("Unexpected path outside receipt folder.")
            if not path.is_file() or path.stat().st_size != spec["bytes"] or digest(path) != spec["sha256"]:
                raise ValueError("Artifact mismatch: " + str(path))
            checked += 1
        if digest(ROOT / script) != receipt["source_script_sha256"]:
            raise ValueError("Source differs from run receipt: " + script)
    print(json.dumps({"selected_artifacts_verified": checked, "analysis_scripts_match_receipts": True,
                      "scientific_validity": "not established by file hashes"}))


if __name__ == "__main__":
    check()

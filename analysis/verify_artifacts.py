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
    print(json.dumps({"selected_artifacts_verified": checked, "analysis_scripts_match_receipts": True,
                      "scientific_validity": "not established by file hashes"}))


if __name__ == "__main__":
    check()

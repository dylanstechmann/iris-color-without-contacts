"""Resolve research comparators and compute descriptors through a running Regen Desk."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

COMPARATORS = [
    ("thiamidol", "Thiamidol", "human-TYR synthesis probe"),
    ("butylresorcinol", "4-butylresorcinol", "alternative synthesis probe"),
    ("kojic_acid", "kojic acid", "enzyme-specificity comparator"),
    ("metyrosine", "metyrosine", "catecholamine-versus-melanogenesis comparator"),
    ("beta_mangostin", "beta-mangostin", "melanophagy mechanism probe"),
    ("levobunolol", "levobunolol", "indirect signaling comparator"),
    ("latanoprost", "latanoprost", "opposite-direction pigmentation comparator"),
]


def request(base, route, data=None):
    body = None if data is None else json.dumps(data).encode()
    req = Request(base + route, data=body, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=45) as response:
        return response.read()


def json_request(base, route, data=None):
    return json.loads(request(base, route, data))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://127.0.0.1:8092")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.base not in {"http://127.0.0.1:8092", "http://localhost:8092"}:
        parser.error("Use the local Regen Desk on port 8092")
    args.out.mkdir(parents=True, exist_ok=False)
    state = json_request(args.base, "/api/state")
    title = "Iris pigment: reversible production and disposal"
    campaign = next((c for c in state.get("campaigns", []) if c["title"] == title and c["blueprint_id"] == "appearance"), None)
    if campaign is None:
        campaign = json_request(args.base, "/api/campaigns", {
            "blueprint_id": "appearance", "title": title,
            "target": "Human TYR; melanosomal OCA2; selective pigment disposal",
            "species": "Human target, with non-iris and animal evidence labeled separately",
            "tissue": "Adult anterior iris stromal melanocytes",
            "hypothesis": "Reversible synthesis suppression can lower pigment if net loss continues; adding selective disposal may change the equilibrium and timescale.",
            "endpoint": "Hypothetical pigment balance, molecule identities and calculated descriptors; no color or efficacy prediction.",
            "falsifier": "No useful net loss, inability to reach the target compartment, failure of mature-pigment processing, or failure to preserve/recover cell function.",
            "evidence_stage": "Computational hypothesis and public compound identity",
            "study_design": "Inspect biological targets, public compound structures and explicit synthesis/loss models; no administration or formulation.",
        })
    # Persist only this newly selected research context, not other Desk areas or notes.
    write_json(args.out / "campaign.json", campaign)
    jobs = []
    for identity, name, role in COMPARATORS:
        payload = {"kind": "compound", "blueprint_id": "appearance", "campaign_id": campaign["id"], "name": name}
        run = json_request(args.base, "/api/jobs", payload)
        jobs.append({"id": identity, "name": name, "role": role, "run_id": run["id"], "request": payload})
        write_json(args.out / "jobs.json", jobs)
    pending = {job["run_id"]: job for job in jobs}
    deadline = time.monotonic() + 360
    rows, statuses = [], []
    while pending and time.monotonic() < deadline:
        for run_id, job in list(pending.items()):
            run = json_request(args.base, "/api/run/" + run_id)
            if run["status"] in {"queued", "running"}:
                continue
            folder = args.out / job["id"]
            folder.mkdir()
            write_json(folder / "request.json", job["request"])
            result = run.get("result", {})
            write_json(folder / "result.json", result)
            status = {"id": job["id"], "name": job["name"], "role": job["role"],
                      "run_id": run_id, "status": run["status"], "error": run.get("error"),
                      "rdkit_version": result.get("rdkit_version"),
                      "identity_note": result.get("identity_note", "")}
            for filename in ("manifest.json", "pubchem-reference.json"):
                try:
                    blob = request(args.base, "/api/artifact/" + run_id + "/" + filename)
                    (folder / filename).write_bytes(blob)
                except Exception as exc:
                    status[filename + "_retrieval"] = type(exc).__name__
            molecules = result.get("molecules", [])
            status["structures_resolved"] = len(molecules)
            for molecule in molecules:
                rows.append({
                    "id": job["id"], "requested_name": job["name"], "role": job["role"],
                    "run_id": run_id, "cid": molecule.get("cid"), "resolved_label": molecule.get("label"),
                    "smiles": molecule.get("smiles"), "mw": molecule.get("mw"),
                    "calculated_logp": molecule.get("logp"), "tpsa": molecule.get("tpsa"),
                    "hbd": molecule.get("hbd"), "hba": molecule.get("hba"),
                    "rotatable": molecule.get("rotatable"), "unspecified_stereo": molecule.get("unspecified_stereo"),
                    "pains": ";".join(molecule.get("pains", [])), "structure_status": molecule.get("status"),
                    "identity_ambiguity": result.get("identity_note", ""), "source_url": molecule.get("url"),
                })
            statuses.append(status)
            write_json(args.out / "status.json", statuses)
            del pending[run_id]
            print(job["id"] + ": " + run["status"] + " / " + str(len(molecules)) + " structures", flush=True)
        if pending:
            time.sleep(1)
    if rows:
        with (args.out / "compounds.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    inputs = {}
    for path in sorted(args.out.rglob("*")):
        if path.is_file():
            blob = path.read_bytes()
            inputs[path.relative_to(args.out).as_posix()] = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
    write_json(args.out / "receipt.json", {
        "activity": "Regen Desk public compound resolution and RDKit descriptors",
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "completed": len(statuses), "pending_run_ids": sorted(pending),
        "files": inputs, "interpretation": "No ocular exposure, binding, efficacy, toxicity or clinical outcome prediction.",
    })
    if pending:
        raise SystemExit("Some jobs remain pending; their IDs were retained.")


if __name__ == "__main__":
    main()

"""Fetch the identified public iris matrix through Regen's provenance wrapper."""
import argparse
import json
import sys
from pathlib import Path
from urllib.request import Request

sys.path.insert(0, "/lab/workbench/tools")
import regen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    args = parser.parse_args()
    args.data.mkdir(parents=True, exist_ok=True)
    metadata = args.data / "cellxgene-collection.json"
    if not metadata.exists():
        url = "https://api.cellxgene.cziscience.com/curation/v1/collections/63d03351-06be-478e-a0db-f7a653b6b19b"
        metadata.write_text(json.dumps(regen.http_json(url), indent=2))
        regen.record("iris-atlas-metadata", {"url": url}, [metadata])
    collection = json.loads(metadata.read_text())
    dataset = next(d for d in collection["datasets"] if d["dataset_id"] == "9a281de7-cee5-4e80-8584-1929f46f152f")
    asset = next(a for a in dataset["assets"] if a["filetype"] == "H5AD")
    path = args.data / "human-iris.h5ad"
    if not path.exists():
        temporary = path.with_suffix(".h5ad.partial")
        with regen._http_with_retry(Request(asset["url"], headers={"User-Agent": regen.UA}), 120) as response:
            with temporary.open("xb") as output:
                total = 0
                while chunk := response.read(8 * 1024 * 1024):
                    total += len(chunk)
                    if total > asset["filesize"]:
                        raise ValueError("Download exceeds declared asset size.")
                    output.write(chunk)
        if temporary.stat().st_size != asset["filesize"]:
            raise ValueError("Download size differs from declared asset size.")
        temporary.replace(path)
        regen.record("iris-atlas-matrix", {"url": asset["url"], "dataset_id": dataset["dataset_id"]}, [path])
    if path.stat().st_size != asset["filesize"]:
        raise ValueError("Cached matrix differs in size.")
    import anndata
    adata = anndata.read_h5ad(path, backed="r")
    print(json.dumps({
        "path": str(path), "bytes": path.stat().st_size, "sha256": regen.sha256_file(path),
        "shape": adata.shape, "obs_columns": list(adata.obs.columns),
        "var_columns": list(adata.var.columns), "raw_shape": None if adata.raw is None else adata.raw.shape,
        "layers": list(adata.layers), "uns_keys": list(adata.uns),
        "selected_obs_counts": {c: {str(k): int(v) for k, v in adata.obs[c].value_counts(dropna=False).items()}
                                for c in ["author_cell_type", "cell_type", "donor_id", "sample_uuid"] if c in adata.obs},
        "var_preview": adata.var.head(2).astype(str).to_dict(),
    }, indent=2))
    adata.file.close()


if __name__ == "__main__":
    main()

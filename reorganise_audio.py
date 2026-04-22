"""
Reorganise wandb audio exports into the website's expected structure:
  static/audio/restructured/{dataset}/{sample_id}/{model}.wav

Dry and wet are always taken from the reference model for each dataset.
Samples are aligned across models by matching the dry audio SHA256.
"""

import json
import shutil
from pathlib import Path

DOWNLOADS = Path("/home/tancrede/Downloads")
STATIC = Path(__file__).parent / "static"

# Each dataset config:
#   folder_prefix : subfolder inside DOWNLOADS containing model sub-folders
#   models        : dict of {subfolder_name: output_filename} for predictions
#   reference     : which model subfolder to use for dry/wet
#   out_name      : output dataset name (used in paths and txt)
DATASETS = [
    {
        "folder_prefix": "pedalboard_sample",
        "models": {
            "oa_cnf":   "oa_cnf",
            "oa_ast":   "oa_ast",
            "oa_stito": "oa_stito",
            "ua_cnf":   "ua_cnf",
            "ua_ast":   "ua_ast",
            "ua_stito": "ua_stito",
        },
        "reference": "oa_cnf",
        "out_name": "pedalboard",
    },
    {
        "folder_prefix": "ddsp_full_chain_sample",
        "models": {"cnf": "cnf", "ast": "ast"},
        "reference": "cnf",
        "out_name": "ddsp_full",
    },
    {
        "folder_prefix": "ddsp_simple_chain_sample",
        "models": {"cnf": "cnf", "ast": "ast"},
        "reference": "cnf",
        "out_name": "ddsp_simple",
    },
    {
        "folder_prefix": "BandEQ3",
        "models": {"CNF": "cnf", "stito": "stito", "random": "random"},
        "reference": "CNF",
        "out_name": "vst_bandeq3",
    },
    {
        "folder_prefix": "MaGigaReverb",
        "models": {"CNF": "cnf", "stito": "stito", "random": "random"},
        "reference": "CNF",
        "out_name": "vst_reverb",
    },
    {
        "folder_prefix": "WSTD_FL3NGR",
        "models": {"cnf": "cnf", "stito": "stito", "Random": "random"},
        "reference": "cnf",
        "out_name": "vst_flanger",
    },
    {
        "folder_prefix": "ZamCompX2",
        "models": {"CNF": "cnf", "stito": "stito", "random": "random"},
        "reference": "CNF",
        "out_name": "vst_comp",
    },
    {
        "folder_prefix": "VST Chain",
        "models": {"CNF": "cnf", "stito": "stito", "random": "random"},
        "reference": "CNF",
        "out_name": "vst_chain",
    },
]


def load_table(base_dir):
    json_path = base_dir / "test" / "audio_effects.table.json"
    with open(json_path) as f:
        data = json.load(f)
    rows = []
    for row in data["data"]:
        rows.append({
            "dry_sha":   row[0]["sha256"],
            "dry_path":  base_dir / row[0]["path"],
            "wet_path":  base_dir / row[1]["path"],
            "pred_path": base_dir / row[2]["path"],
        })
    return rows


def process_dataset(cfg):
    prefix = DOWNLOADS / cfg["folder_prefix"]
    out_name = cfg["out_name"]
    out_base = STATIC / "audio" / "restructured" / out_name
    txt_out  = STATIC / "txt" / f"{out_name}.txt"

    ref_key = cfg["reference"]
    ref_rows = load_table(prefix / ref_key)
    sha_to_idx = {r["dry_sha"]: i for i, r in enumerate(ref_rows)}

    model_data = {}
    for model_key in cfg["models"]:
        rows = load_table(prefix / model_key)
        model_data[model_key] = {r["dry_sha"]: r for r in rows}

    common_shas = set(sha_to_idx.keys())
    for lookup in model_data.values():
        common_shas &= set(lookup.keys())

    sorted_shas = sorted(common_shas, key=lambda s: sha_to_idx[s])
    print(f"\n[{out_name}] {len(sorted_shas)} / {len(ref_rows)} samples aligned")

    out_base.mkdir(parents=True, exist_ok=True)
    sample_ids = []

    for i, sha in enumerate(sorted_shas):
        sample_id = f"sample_{i:03d}"
        sample_dir = out_base / sample_id
        sample_dir.mkdir(exist_ok=True)

        ref_row = model_data[ref_key][sha]
        shutil.copy(ref_row["dry_path"], sample_dir / "dry.wav")
        shutil.copy(ref_row["wet_path"], sample_dir / "wet.wav")

        for model_key, out_filename in cfg["models"].items():
            row = model_data[model_key][sha]
            shutil.copy(row["pred_path"], sample_dir / f"{out_filename}.wav")

        sample_ids.append(sample_id)
        print(f"  {sample_id} -> done")

    txt_out.parent.mkdir(parents=True, exist_ok=True)
    txt_out.write_text("\n".join(sample_ids) + "\n")
    print(f"Wrote {txt_out}")


for dataset_cfg in DATASETS:
    process_dataset(dataset_cfg)

print("\nAll done.")

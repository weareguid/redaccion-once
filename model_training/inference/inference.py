#!/usr/bin/env python
"""
Convert cleaned notes + metadata to Alpaca‑style JSONL for DeepSeek.

Usage:
    python tasks/05_prepare_alpaca.py \
        --cleaned-dir cleaned \
        --out data/deepseek_sft.jsonl
"""
import json, argparse
from pathlib import Path

def build_record(text: str, meta: dict):
    instr = meta.get("instruction") or "Rewrite the following note in the target editorial voice."
    inp   = text
    out   = meta.get("target") or ""      # If you have gold completions
    return {"instruction": instr, "input": inp, "output": out}

def main(cleaned_dir: Path, out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)
    meta_files = sorted(cleaned_dir.glob("*_metadata.json"))
    with out.open("w", encoding="utf-8") as fout:
        for mpath in meta_files:
            txt = mpath.with_suffix("").with_suffix(".txt").read_text(encoding="utf-8").strip()
            meta = json.loads(mpath.read_text(encoding="utf-8"))
            if not txt: continue
            fout.write(json.dumps(build_record(txt, meta), ensure_ascii=False) + "\n")
    print(f"✅  Saved Alpaca file → {out}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cleaned-dir", type=Path, default=Path("cleaned"))
    ap.add_argument("--out", type=Path, default=Path("model_training/data/deepseek_sft.jsonl"))
    args = ap.parse_args()
    main(args.cleaned_dir, args.out)

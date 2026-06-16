#!/usr/bin/env python3
"""Batch-generate figures for a note from a JSON spec.

Usage:
    python3 gen_figures_batch.py <spec.json>

spec.json format:
    {
      "out_dir": "/abs/path/to/figures",
      "figures": [
        {"file": "fig1_concept.png", "prompt": "..."},
        {"file": "fig2_pipeline.png", "prompt": "..."}
      ]
    }

Already-existing files are skipped, so the script is safe to re-run.
"""
import sys, json, os
from gen_figure import generate


def main(spec_path: str) -> None:
    with open(spec_path) as f:
        spec = json.load(f)
    out_dir = spec["out_dir"]
    os.makedirs(out_dir, exist_ok=True)
    ok, fail = 0, 0
    for fig in spec["figures"]:
        path = os.path.join(out_dir, fig["file"])
        if os.path.exists(path) and os.path.getsize(path) > 10_000:
            print(f"skip {fig['file']} (exists)")
            ok += 1
            continue
        if generate(path, fig["prompt"]):
            ok += 1
        else:
            fail += 1
    print(f"DONE  ok={ok} fail={fail}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 gen_figures_batch.py <spec.json>")
        sys.exit(1)
    main(sys.argv[1])

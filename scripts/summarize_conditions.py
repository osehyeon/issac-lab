"""Collect one JSON of results for several conditions: closed-loop outcomes, motion metrics, replay deviation.

usage: python summarize_conditions.py --ref RUN_DIR --cond name=RUN_DIR[:replay.npz] ... --out summary.json
The reference run holds the recorded responses (obs_ep*.npz) that replays are compared against.
"""

import argparse
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from motion_metrics import run_table  # noqa: E402
from replay_obs import load_reference  # noqa: E402

COLS = ["sparc", "ldlj", "jerk_rms", "atv", "cont", "jump_boundary", "jump_within", "track_rms", "duration_s"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--cond", nargs="+", required=True)
    ap.add_argument("--skip", type=int, default=30)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    _, _, ref = load_reference(a.ref)
    out = {"ref": os.path.basename(os.path.normpath(a.ref)), "conditions": {}}
    for spec in a.cond:
        name, rest = spec.split("=", 1)
        run_dir, _, replay = rest.partition(":")
        rows = run_table(run_dir, a.skip)
        summ = json.load(open(os.path.join(run_dir, "summary.json")))["episodes"]
        c = {"outcomes": [e["outcome"] for e in summ],
             "success_steps": [e["steps"] for e in summ if e["outcome"] == "success"],
             "metrics": {}}
        for sub in ("all", "success", "timeout"):
            g = [r for r in rows if sub == "all" or r["outcome"] == sub]
            c["metrics"][sub] = {k: [float(np.mean([r[k] for r in g])), float(np.std([r[k] for r in g], ddof=1)) if len(g) > 1 else 0.0, len(g)] for k in COLS} if g else {}
        ms = np.concatenate([np.load(f)["call_ms"] for f in sorted(glob.glob(os.path.join(run_dir, "ep*.npz")))])
        c["call_ms_median"] = float(np.median(ms))
        if replay:
            acts = np.load(replay)["actions"]
            d = acts - ref
            c["replay"] = {"n": int(len(acts)),
                           "mae_joint": np.abs(d).mean((0, 1)).tolist(),
                           "mae_step": np.abs(d[:, :, :5]).mean((0, 2)).tolist(),
                           "max_arm": float(np.abs(d[:, :, :5]).max()),
                           "gripper_bias": float(d[:, :, 5].mean()),
                           "ms_median": float(np.median(np.load(replay)["ms"]))}
        out["conditions"][name] = c
    json.dump(out, open(a.out, "w"), indent=1)
    for name, c in out["conditions"].items():
        m = c["metrics"]["all"]
        print(f"{name:10s} success {c['outcomes'].count('success')}/{len(c['outcomes'])}  atv {m['atv'][0]:.4f}  jump_b {m['jump_boundary'][0]:.4f}  jump_w {m['jump_within'][0]:.4f}  sparc {m['sparc'][0]:.2f}"
              + (f"  replay MAE {np.mean(c['replay']['mae_joint'][:5]):.3f}" if "replay" in c else ""))


if __name__ == "__main__":
    main()

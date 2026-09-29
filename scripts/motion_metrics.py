"""Motion-quality metrics for trajectories recorded by traj_logger.py.

usage: python motion_metrics.py RUN_DIR [RUN_DIR ...] [--skip 30] [--csv out.csv]

Measured motion (joint positions, 60 Hz):
  SPARC   spectral arc length of the arm joint-space speed (Balasubramanian et al. 2012/2015).
          Dimensionless, <= 0, closer to 0 is smoother. Primary metric: robust to noise and duration.
  LDLJ    log dimensionless jerk of the same speed profile (Balasubramanian et al. 2015), scale D^3/v_peak^2
          as in the authors' reference code (the printed D^5 is not dimensionless for a speed profile).
  jerk_rms  RMS of the 3rd finite difference of each joint, rad/s^3. Duration-sensitive (Hogan & Sternad 2009);
          compare only between conditions with similar episode lengths.
  acc_max  max |2nd finite difference| of joint position, rad/s^2.
Command signal (policy actions, one per step):
  atv     action total variation, mean |a_t+1 - a_t| per joint (FocalPolicy).
  cont    gSDE continuity cost, 100 * E[((a_t+1 - a_t) / range)^2] with the SO-101 joint range.
  jump_boundary / jump_within  mean |a_t+1 - a_t| at chunk boundaries vs inside chunks (inter-chunk discontinuity).
  cmd_acc_max  max |2nd difference| of the command (RTC's jerkiness proxy).
track_rms  RMS tracking error |pos - action| per joint (not a smoothness metric).
The gripper is excluded from the speed profile; per-joint columns keep it.
"""

import argparse
import glob
import json
import os

import numpy as np

JOINT_RANGE_DEG = {"shoulder_pan": 220, "shoulder_lift": 200, "elbow_flex": 190, "wrist_flex": 190, "wrist_roll": 320, "gripper": 110}
ARM = slice(0, 5)


def sparc(speed, fs, padlevel=4, fc=10.0, amp_th=0.05):
    nfft = int(2 ** (np.ceil(np.log2(len(speed))) + padlevel))
    f = np.arange(0, fs, fs / nfft)
    mf = np.abs(np.fft.fft(speed, nfft))
    mf = mf / mf.max()
    sel = f <= fc
    f, mf = f[sel], mf[sel]
    inx = np.nonzero(mf >= amp_th)[0]
    f, mf = f[inx[0]:inx[-1] + 1], mf[inx[0]:inx[-1] + 1]
    return -np.sum(np.sqrt((np.diff(f) / (f[-1] - f[0])) ** 2 + np.diff(mf) ** 2))


def ldlj(speed, fs):
    dt = 1.0 / fs
    d2 = np.diff(speed, 2) / dt**2
    dlj = -(len(speed) * dt) ** 3 / speed.max() ** 2 * np.sum(d2**2) * dt
    return -np.log(abs(dlj))


def episode_metrics(npz, skip, names):
    d = np.load(npz)
    dt = float(np.diff(d["t"][:2])[0])
    fs = 1.0 / dt
    pos, act, chunk_i = d["pos"][skip:], d["action"][skip:], d["in_chunk"][skip:]
    if len(pos) < 64:
        return None
    vel = np.gradient(pos, dt, axis=0)
    speed = np.linalg.norm(vel[:, ARM], axis=1)
    acc = np.diff(pos, 2, axis=0) / dt**2
    jerk = np.diff(pos, 3, axis=0) / dt**3
    da = np.diff(act, axis=0)
    rng = np.deg2rad([JOINT_RANGE_DEG[n] for n in names])
    boundary = chunk_i[1:] == 0
    m = {
        "steps": len(pos), "duration_s": len(pos) * dt,
        "sparc": sparc(speed, fs), "ldlj": ldlj(speed, fs),
        "speed_peak": speed.max(), "speed_mean": speed.mean(),
        "jump_boundary": np.abs(da[boundary]).mean() if boundary.any() else np.nan,
        "jump_within": np.abs(da[~boundary]).mean(),
    }
    per = {
        "jerk_rms": np.sqrt((jerk**2).mean(0)), "acc_max": np.abs(acc).max(0),
        "atv": np.abs(da).mean(0), "cont": 100 * ((da / rng) ** 2).mean(0),
        "cmd_acc_max": np.abs(np.diff(act, 2, axis=0)).max(0) / dt**2,
        "track_rms": np.sqrt(((pos - act) ** 2).mean(0)),
    }
    for k, v in per.items():
        m[k] = float(v[ARM].mean())
        for n, x in zip(names, v):
            m[f"{k}/{n}"] = float(x)
    return m


def run_table(run_dir, skip):
    summary = json.load(open(os.path.join(run_dir, "summary.json")))
    names = summary["meta"]["joint_names"]
    outcome = {e["episode"]: e["outcome"] for e in summary["episodes"]}
    rows = []
    for f in sorted(glob.glob(os.path.join(run_dir, "ep*.npz"))):
        ep = int(os.path.basename(f)[2:5])
        m = episode_metrics(f, skip, names)
        if m:
            rows.append({"run": os.path.basename(os.path.normpath(run_dir)), "episode": ep, "outcome": outcome.get(ep, "?"), **m})
    return rows


def fmt(vals):
    v = np.array(vals, dtype=float)
    v = v[~np.isnan(v)]
    return f"{v.mean():.3g} ± {v.std(ddof=1) if len(v) > 1 else 0:.2g}" if len(v) else "-"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--skip", type=int, default=30, help="steps dropped at episode start (reset transient)")
    ap.add_argument("--csv")
    args = ap.parse_args()
    rows = [r for run in args.runs for r in run_table(run, args.skip)]
    if args.csv:
        keys = list(rows[0])
        with open(args.csv, "w") as f:
            f.write(",".join(keys) + "\n")
            for r in rows:
                f.write(",".join(str(r[k]) for k in keys) + "\n")
    cols = ["sparc", "ldlj", "jerk_rms", "acc_max", "atv", "cont", "jump_boundary", "jump_within", "cmd_acc_max", "track_rms", "duration_s"]
    groups = {}
    for r in rows:
        groups.setdefault((r["run"], "all"), []).append(r)
        groups.setdefault((r["run"], r["outcome"]), []).append(r)
    print("| run | subset | n | " + " | ".join(cols) + " |")
    print("|---|---|---|" + "---|" * len(cols))
    for (run, sub), g in groups.items():
        print(f"| {run} | {sub} | {len(g)} | " + " | ".join(fmt([r[c] for r in g]) for c in cols) + " |")
    print("\nper-joint (all episodes, arm mean shown above):")
    names = [k.split("/")[1] for k in rows[0] if k.startswith("jerk_rms/")]
    for metric in ("jerk_rms", "atv", "track_rms", "acc_max"):
        for run in dict.fromkeys(r["run"] for r in rows):
            g = [r for r in rows if r["run"] == run]
            print(f"  {metric:10s} {run}: " + ", ".join(f"{n} {np.mean([r[f'{metric}/{n}'] for r in g]):.3g}" for n in names))


if __name__ == "__main__":
    main()

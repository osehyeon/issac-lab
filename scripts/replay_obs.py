"""Matched-observation replay against a GR00T policy server.

usage (Isaac-GR00T venv, needs the gr00t package):
    python replay_obs.py RUN_DIR --out replay_fp.npz [--host localhost --port 5555]
    python replay_obs.py RUN_DIR --compare replay_a.npz replay_b.npz

Replay sends every saved request in RUN_DIR/obs_ep*.npz (written by traj_logger.py with TRAJ_OBS_EVERY)
to the server and stores the returned chunks. --compare reports action deviation between two replays
(or between a replay and the responses recorded in RUN_DIR when only one file is given):
MAE per joint, MAE per horizon step, signed gripper bias, cosine similarity, max deviation.
Units are the server's (LeRobot degrees / gripper percent), before leisaac conversion.
"""

import argparse
import glob
import os

import numpy as np

JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]


def iter_requests(run_dir):
    """Yield (ep, call, request, recorded_chunk) one file at a time to keep memory low."""
    for f in sorted(glob.glob(os.path.join(run_dir, "obs_ep*.npz"))):
        d = np.load(f)
        ep = int(os.path.basename(f)[6:9])
        task = str(d["task"])
        front, wrist = d["video.front"], d["video.wrist"]
        arm, grip = d["state.single_arm"], d["state.gripper"]
        ra, rg = d["resp/action.single_arm"], d["resp/action.gripper"]
        for i in range(len(d["call"])):
            req = {"video.front": front[i][None], "video.wrist": wrist[i][None],
                   "state.single_arm": arm[i][None], "state.gripper": grip[i][None],
                   "annotation.human.task_description": [task]}
            yield ep, int(d["call"][i]), req, np.concatenate([ra[i], rg[i]], axis=1)


def load_reference(run_dir):
    eps, calls, ref = [], [], []
    for ep, call, _, r in iter_requests(run_dir):
        eps.append(ep); calls.append(call); ref.append(r)
    return np.array(eps), np.array(calls), np.array(ref)


def replay(run_dir, host, port):
    from gr00t.eval.robot import RobotInferenceClient
    import time

    client = RobotInferenceClient(host=host, port=port)
    out, ms, ref, eps, calls = [], [], [], [], []
    for n, (ep, call, req, r) in enumerate(iter_requests(run_dir)):
        t = time.perf_counter()
        a = client.get_action(req)
        ms.append((time.perf_counter() - t) * 1000)
        out.append(np.concatenate([a["action.single_arm"], a["action.gripper"]], axis=1))
        ref.append(r); eps.append(ep); calls.append(call)
        if n % 100 == 0:
            print(f"  {n}", flush=True)
    return np.array(out), np.array(ms), np.array(ref), np.array(eps), np.array(calls)


def compare(a, b, label):
    d = b - a
    mae_j = np.abs(d).mean((0, 1))
    mae_h = np.abs(d[:, :, :5]).mean((0, 2))
    flat_a, flat_b = a[:, :, :5].reshape(len(a), -1), b[:, :, :5].reshape(len(b), -1)
    cos = np.sum(flat_a * flat_b, 1) / (np.linalg.norm(flat_a, axis=1) * np.linalg.norm(flat_b, axis=1) + 1e-9)
    print(f"\n{label}: {len(a)} chunks")
    print("  MAE per joint: " + ", ".join(f"{j} {m:.3f}" for j, m in zip(JOINTS, mae_j)))
    print("  arm MAE per horizon step: " + " ".join(f"{m:.3f}" for m in mae_h))
    print(f"  gripper bias (signed mean): {d[:, :, 5].mean():+.3f}, arm max |dev| {np.abs(d[:, :, :5]).max():.3f}")
    print(f"  arm cosine: median {np.median(cos):.5f}, min {cos.min():.5f}; identical chunks: {np.mean(np.all(d == 0, (1, 2))):.1%}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=5555)
    ap.add_argument("--out")
    ap.add_argument("--compare", nargs="+")
    args = ap.parse_args()
    if args.out:
        acts, ms, ref, eps, calls = replay(args.run_dir, args.host, args.port)
        np.savez_compressed(args.out, actions=acts, ms=ms, ep=eps, call=calls)
        print(f"{len(acts)} requests replayed; saved {args.out}; latency median {np.median(ms):.1f} ms")
        compare(ref, acts, f"recorded closed-loop responses vs {os.path.basename(args.out)}")
    if args.compare:
        files = [np.load(f)["actions"] for f in args.compare]
        if len(files) == 1:
            _, _, ref = load_reference(args.run_dir)
            compare(ref, files[0], f"recorded vs {args.compare[0]}")
        else:
            compare(files[0], files[1], f"{args.compare[0]} vs {args.compare[1]}")


if __name__ == "__main__":
    main()

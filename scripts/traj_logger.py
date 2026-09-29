"""Record joint trajectories while running leisaac's policy_inference.py.

usage: python traj_logger.py policy_inference.py <policy_inference args>
Writes one npz per episode to $TRAJ_OUT (default ./traj) plus summary.json.
Per env step: sim time, commanded action, and the joint state right before it is applied.
Per policy call: latency and the full action chunk. With TRAJ_OBS_EVERY=k, every k-th request payload
(images, state) and the server response are saved to obs_ep###.npz for matched-observation replay.
"""

import atexit
import builtins
import json
import os
import sys
import time

import numpy as np

OUT = os.environ.get("TRAJ_OUT", os.path.join(os.getcwd(), "traj"))
OBS_EVERY = int(os.environ.get("TRAJ_OBS_EVERY", "0"))  # save every k-th policy request/response; 0 = off
os.makedirs(OUT, exist_ok=True)

st = {"ep": 1, "call": 0, "in_chunk": 0, "t0": time.time(), "steps": [], "calls": [], "eps": [], "meta": None, "obs": []}
_orig_import = builtins.__import__
_patched = set()


def _np(x):
    x = getattr(x, "torch", x)
    return x[0].detach().cpu().numpy().astype(np.float32)


def _flush(outcome):
    ep = st["ep"]
    steps = st["steps"]
    if steps:
        arr = {k: np.array([s[k] for s in steps]) for k in steps[0]}
        arr["chunks"] = np.array([c["chunk"] for c in st["calls"]], dtype=np.float32)
        arr["call_ms"] = np.array([c["ms"] for c in st["calls"]], dtype=np.float32)
        arr["call_step"] = np.array([c["step"] for c in st["calls"]], dtype=np.int32)
        np.savez_compressed(os.path.join(OUT, f"ep{ep:03d}.npz"), **arr)
    _flush_obs(ep)
    st["eps"].append({"episode": ep, "outcome": outcome, "steps": len(steps), "calls": len(st["calls"]),
                      "wall_s": round(time.time() - st["t0"], 1)})
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump({"meta": st["meta"], "episodes": st["eps"]}, f, indent=1)
    print(f"[TRAJ] ep {ep} {outcome}: {len(steps)} steps, {len(st['calls'])} calls -> {OUT}", flush=True)
    st.update(ep=ep + 1, call=0, in_chunk=0, t0=time.time(), steps=[], calls=[])


def _patch_policy(mod):
    for name in ("Gr00tServicePolicyClient", "Gr00t16ServicePolicyClient", "LeRobotServicePolicyClient", "RandomPolicy"):
        cls = getattr(mod, name, None)
        if cls is None:
            continue
        get = cls.get_action

        def _get(self, obs, _get=get):
            st["call"] += 1
            t = time.perf_counter()
            a = _get(self, obs)
            st["in_chunk"] = 0
            st["calls"].append({"ms": (time.perf_counter() - t) * 1000, "step": len(st["steps"]),
                                "chunk": a[:, 0, :].cpu().numpy()})
            return a

        cls.get_action = _get

    if OBS_EVERY and hasattr(mod, "ZMQServicePolicy"):
        zcls = mod.ZMQServicePolicy
        call = zcls.call_endpoint

        def _call(self, endpoint, data=None, requires_input=True, _call=call):
            out = _call(self, endpoint, data, requires_input)
            if endpoint == "get_action" and st["call"] % OBS_EVERY == 0:
                st["obs"].append({"call": st["call"], "step": len(st["steps"]), "req": data, "resp": out})
            return out

        zcls.call_endpoint = _call


def _flush_obs(ep):
    if not st["obs"]:
        return
    keys = [k for k in st["obs"][0]["req"] if not k.startswith("annotation")]
    arr = {k: np.stack([o["req"][k][0] for o in st["obs"]]) for k in keys}
    arr.update({f"resp/{k}": np.stack([o["resp"][k] for o in st["obs"]]) for k in st["obs"][0]["resp"]})
    arr["call"] = np.array([o["call"] for o in st["obs"]])
    arr["step"] = np.array([o["step"] for o in st["obs"]])
    arr["task"] = np.array(st["obs"][0]["req"]["annotation.human.task_description"][0])
    np.savez_compressed(os.path.join(OUT, f"obs_ep{ep:03d}.npz"), **arr)
    st["obs"] = []


def _patch_env(mod):
    cls = mod.ManagerBasedRLEnv
    step = cls.step

    def _step(self, action):
        robot = self.scene["robot"]
        if st["meta"] is None:
            st["meta"] = {"step_dt": float(self.step_dt), "physics_dt": float(self.physics_dt),
                          "joint_names": list(robot.joint_names), "argv": sys.argv[1:]}
        # state is read before the step: a terminating step resets the env before returning
        d = robot.data
        st["steps"].append({
            "t": float(self.episode_length_buf[0].item()) * self.step_dt,
            "call": st["call"], "in_chunk": st["in_chunk"],
            "action": _np(action),
            "target": _np(d.joint_pos_target),
            "pos": _np(d.joint_pos),
            "vel": _np(d.joint_vel),
            "acc": _np(d.joint_acc),
            "torque": _np(d.applied_torque),
        })
        st["in_chunk"] += 1
        out = step(self, action)
        _, _, term, tout, _ = out
        if bool(term[0]):
            _flush("success")
        elif bool(tout[0]):
            _flush("timeout")
        return out

    cls.step = _step


def _import(name, *a, **k):
    m = _orig_import(name, *a, **k)
    pm = sys.modules.get("leisaac.policy.service_policy_clients")
    if "policy" not in _patched and pm is not None and hasattr(pm, "RandomPolicy"):
        _patched.add("policy")
        _patch_policy(pm)
    em = sys.modules.get("isaaclab.envs.manager_based_rl_env")
    if "env" not in _patched and em is not None and hasattr(em, "ManagerBasedRLEnv"):
        _patched.add("env")
        _patch_env(em)
    return m


builtins.__import__ = _import
atexit.register(lambda: st["steps"] and _flush("aborted"))
sys.argv = sys.argv[1:]
import runpy

runpy.run_path(sys.argv[0], run_name="__main__")

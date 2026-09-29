"""Build the GR00T TensorRT engines with the Python API (replaces deployment_scripts/build_engine.sh,
which needs the system trtexec binary).

usage (Isaac-GR00T venv, from the Isaac-GR00T dir):
    python build_trt_engines.py --onnx gr00t_onnx --out gr00t_engine --vit fp8 --llm nvfp4 --dit fp8 --views 2
Same shape profiles and flags as build_engine.sh: strongly typed networks, MIN/OPT/MAX sequence
lengths 80/568/600 for two camera views (80/296/300 for one), batch 1..MAX_BATCH (nvfp4 LLM: batch 1).
"""

import argparse
import os
import time

import tensorrt as trt

LOG = trt.Logger(trt.Logger.WARNING)


def build(onnx_path, engine_path, profiles):
    """profiles: {input_name: (min_shape, opt_shape, max_shape)}"""
    if os.path.exists(engine_path):
        print(f"skip {engine_path} (exists)")
        return
    builder = trt.Builder(LOG)
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.STRONGLY_TYPED))
    parser = trt.OnnxParser(network, LOG)
    with open(onnx_path, "rb") as f:
        if not parser.parse(f.read(), path=onnx_path):
            for i in range(parser.num_errors):
                print(parser.get_error(i))
            raise RuntimeError(f"failed to parse {onnx_path}")
    config = builder.create_builder_config()
    profile = builder.create_optimization_profile()
    for name, (mn, op, mx) in profiles.items():
        profile.set_shape(name, mn, op, mx)
    config.add_optimization_profile(profile)
    t = time.time()
    plan = builder.build_serialized_network(network, config)
    if plan is None:
        raise RuntimeError(f"build failed for {onnx_path}")
    with open(engine_path, "wb") as f:
        f.write(plan)
    print(f"built {engine_path} in {time.time() - t:.0f} s ({os.path.getsize(engine_path) / 1e6:.0f} MB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--onnx", default="gr00t_onnx")
    ap.add_argument("--out", default="gr00t_engine")
    ap.add_argument("--vit", default="fp8")
    ap.add_argument("--llm", default="nvfp4")
    ap.add_argument("--dit", default="fp8")
    ap.add_argument("--views", type=int, default=2)
    ap.add_argument("--max-batch", type=int, default=8)
    ap.add_argument("--only", nargs="*", help="subset: vlln dit state action_enc action_dec vit llm")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    mn, op, mx = (80, 568, 600) if a.views == 2 else (80, 296, 300)
    B = a.max_batch
    llm_b = 1 if a.llm.startswith("nvfp4") else B
    vb = max(B, a.views)  # the ViT batch is the number of camera views
    ah, eg = os.path.join(a.onnx, "action_head"), os.path.join(a.onnx, "eagle2")
    jobs = {
        "vlln": (f"{ah}/vlln_vl_self_attention.onnx", f"{a.out}/vlln_vl_self_attention.engine",
                 {"backbone_features": ((1, mn, 2048), (1, op, 2048), (B, mx, 2048))}),
        "dit": (f"{ah}/DiT_{a.dit}.onnx", f"{a.out}/DiT_{a.dit}.engine",
                {"sa_embs": ((1, 49, 1536), (1, 49, 1536), (B, 49, 1536)),
                 "vl_embs": ((1, mn, 2048), (1, op, 2048), (B, mx, 2048)),
                 "timesteps_tensor": ((1,), (1,), (B,))}),
        "state": (f"{ah}/state_encoder.onnx", f"{a.out}/state_encoder.engine",
                  {"state": ((1, 1, 64), (1, 1, 64), (B, 1, 64)), "embodiment_id": ((1,), (1,), (B,))}),
        "action_enc": (f"{ah}/action_encoder.onnx", f"{a.out}/action_encoder.engine",
                       {"actions": ((1, 16, 32), (1, 16, 32), (B, 16, 32)), "timesteps_tensor": ((1,), (1,), (B,)),
                        "embodiment_id": ((1,), (1,), (B,))}),
        "action_dec": (f"{ah}/action_decoder.onnx", f"{a.out}/action_decoder.engine",
                       {"model_output": ((1, 49, 1024), (1, 49, 1024), (B, 49, 1024)), "embodiment_id": ((1,), (1,), (B,))}),
        "vit": (f"{eg}/vit_{a.vit}.onnx", f"{a.out}/vit_{a.vit}.engine",
                {"pixel_values": ((1, 3, 224, 224), (a.views, 3, 224, 224), (vb, 3, 224, 224)),
                 "position_ids": ((1, 256), (a.views, 256), (vb, 256))}),
        "llm": (f"{eg}/llm_{a.llm}.onnx", f"{a.out}/llm_{a.llm}.engine",
                {"inputs_embeds": ((1, mn, 2048), (1, op, 2048), (llm_b, mx, 2048)),
                 "attention_mask": ((1, mn), (1, op), (llm_b, mx))}),
    }
    for name, (onnx_path, engine_path, profiles) in jobs.items():
        if a.only and name not in a.only:
            continue
        print(f"--- {name}: {onnx_path}")
        build(onnx_path, engine_path, profiles)


if __name__ == "__main__":
    main()

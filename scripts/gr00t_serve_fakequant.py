"""Serve GR00T with ModelOpt fake quantization applied inside PyTorch (no ONNX, no TensorRT).

usage (Isaac-GR00T venv, from the Isaac-GR00T dir):
    QUANT_CFG=INT8_DEFAULT_CFG QUANT_SCOPE=dit CALIB_DATASET=<lerobot dir> python gr00t_serve_fakequant.py --server ...
QUANT_CFG    any mtq.*_CFG name: INT8_DEFAULT_CFG, INT8_SMOOTHQUANT_CFG, INT4_AWQ_CFG, W4A8_AWQ_BETA_CFG,
             NVFP4_DEFAULT_CFG, FP8_DEFAULT_CFG, ...  (empty = no quantization, bf16 reference)
QUANT_SCOPE  dit | vlsa | dit+vlsa   (only nn.Linear layers quantize; the encoders/decoder use bmm parameters)
CALIB_N      calibration samples taken evenly from the dataset (default 16); each runs the full policy,
             so the DiT is calibrated over its 4 denoising steps
The flow-matching noise seed is fixed per call like gr00t_serve_seeded.py.
"""

import os
import runpy
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr00t_pyav_loader

from gr00t.model import policy as P

SEED = int(os.environ.get("GR00T_NOISE_SEED", "0"))
CFG = os.environ.get("QUANT_CFG", "")
SCOPE = os.environ.get("QUANT_SCOPE", "dit")
CALIB_N = int(os.environ.get("CALIB_N", "16"))
DATASET = os.environ.get("CALIB_DATASET", os.path.expanduser("~/gr00t-server/datasets/leisaac-pick-orange"))

_orig_get = P.Gr00tPolicy._get_action_from_normalized_input
_orig_init = P.Gr00tPolicy.__init__


def _seeded(self, normalized_input):
    torch.manual_seed(SEED)
    return _orig_get(self, normalized_input)


def _quantize(policy):
    import modelopt.torch.quantization as mtq
    from gr00t.data.dataset import LeRobotSingleDataset

    gr00t_pyav_loader.install()
    ds = LeRobotSingleDataset(dataset_path=DATASET, modality_configs=policy.modality_config,
                              embodiment_tag=policy.embodiment_tag, video_backend="decord", transforms=None)
    idx = [int(i) for i in torch.linspace(0, len(ds) - 1, CALIB_N)]
    samples = [ds[i] for i in idx]
    cfg = getattr(mtq, CFG)
    targets = {"dit": policy.model.action_head.model, "vlsa": policy.model.action_head.vl_self_attention}
    for name in SCOPE.split("+"):
        mod = targets[name]

        def calibrate(_m):
            for s in samples:
                policy.get_action(s)

        mtq.quantize(mod, cfg, forward_loop=calibrate)
        n = sum(1 for _ in mod.modules() if _.__class__.__name__ == "TensorQuantizer")
        print(f"[fakequant] {name}: {CFG} applied, {n} quantizers, calibrated on {CALIB_N} samples", flush=True)


def _init(self, *a, **k):
    _orig_init(self, *a, **k)
    if CFG:
        _quantize(self)
    else:
        print("[fakequant] QUANT_CFG empty: bf16 reference", flush=True)


P.Gr00tPolicy._get_action_from_normalized_input = _seeded
P.Gr00tPolicy.__init__ = _init
print(f"[seeded] noise seed {SEED}; fake quant cfg={CFG or 'none'} scope={SCOPE}", flush=True)
sys.argv = [os.path.join(os.getcwd(), "scripts", "inference_service.py")] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")

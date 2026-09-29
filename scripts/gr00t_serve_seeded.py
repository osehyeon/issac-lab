"""Run Isaac-GR00T's inference_service.py with a fixed flow-matching noise seed.

usage (from the Isaac-GR00T checkout, in its venv):
    GR00T_NOISE_SEED=0 python gr00t_serve_seeded.py --server --model-path ... [inference_service args]
Every get_action call reseeds torch before sampling the initial noise, so the same observation
always yields the same action chunk. Weights and the service are unchanged.
"""

import os
import runpy
import sys

import torch

from gr00t.model import policy as P

SEED = int(os.environ.get("GR00T_NOISE_SEED", "0"))
_orig = P.Gr00tPolicy._get_action_from_normalized_input


def _seeded(self, normalized_input):
    torch.manual_seed(SEED)
    return _orig(self, normalized_input)


P.Gr00tPolicy._get_action_from_normalized_input = _seeded
print(f"[seeded] flow-matching noise seed fixed to {SEED} on every call", flush=True)
sys.argv = [os.path.join(os.getcwd(), "scripts", "inference_service.py")] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")

"""Run Isaac-GR00T's deployment_scripts/export_onnx.py with PyAV video decoding.

usage (Isaac-GR00T venv, from the Isaac-GR00T dir):
    python gr00t_export_pyav.py --model-path ... --dataset-path ... [export_onnx args]
The LeIsaac datasets are AV1; this machine's decord/torchcodec/OpenCV cannot decode AV1 but PyAV
(libdav1d) can. The loader used by LeRobotSingleDataset is replaced; export_onnx.py itself is unchanged
(pass --video-backend decord or leave the default, the value is ignored).
"""

import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr00t_pyav_loader

gr00t_pyav_loader.install()
sys.argv = [os.path.join(os.getcwd(), "deployment_scripts", "export_onnx.py")] + sys.argv[1:]
sys.path.insert(0, os.getcwd())
runpy.run_path(sys.argv[0], run_name="__main__")

"""Figure: FP vs TensorRT fp16 vs FP8/NVFP4 on the same 30 placements. Reads summary.json from summarize_conditions.py."""

import json
import sys

sys.path.insert(0, "/Users/osehn/.claude/skills/paper-figures/scripts")
from figlib import *  # noqa

S = json.load(open(sys.argv[1]))
C = S["conditions"]
ORDER = [("fp", "bf16"), ("trt_fp16", "fp16 engine"), ("trt_quant", "FP8/FP4 engine"), ("fq_nvfp4", "W4A4 DiT")]
HI = "fq_nvfp4"
W = 520
o = [svg_open(W, 268), ARROW]

# (a) paired outcomes, one cell per episode
ya = 14
o.append(tx(2, ya + 8, "(a)"))
x0, cw = 110, 12
for i, (k, name) in enumerate(ORDER):
    y = ya + i * 16
    o.append(tx(x0 - 6, y + 9, name, "end"))
    outs = C[k]["outcomes"]
    for j, r in enumerate(outs):
        o.append(rc(x0 + j * cw, y, cw - 1.5, 11, fill=(ACC if k == HI else FILL) if r == "success" else "#fff"))
    o.append(tx(x0 + len(outs) * cw + 6, y + 9, f"{outs.count('success')} / {len(outs)}"))
o.append(tx(x0, ya + 4 * 16 + 8, "episode 1"))
o.append(tx(x0 + 30 * cw - 1.5, ya + 4 * 16 + 8, "30", "end"))
o.append(tx(x0 + 30 * cw + 60, ya + 4 * 16 + 8, "filled = success"))

# (b) replay deviation per horizon step, fp16 vs quant
yb = 116
o.append(tx(2, yb + 8, "(b)"))
bx, bw, bh = 110, 6, 46
top = max(max(C[k]["replay"]["mae_step"]) for k, _ in ORDER[1:])
for i, (k, name) in enumerate(ORDER[1:]):
    steps = C[k]["replay"]["mae_step"]
    for j, v in enumerate(steps):
        h = v / top * bh
        xx = bx + j * (bw * 3 + 3) + i * bw
        o.append(rc(xx, yb + bh - h, bw - 0.8, h, fill=ACC if k == HI else (BAND if k == "trt_quant" else FILL)))
o.append(ln(bx - 2, yb + bh, bx + 16 * (bw * 3 + 3), yb + bh, W1))
o.append(tx(bx, yb + bh + 10, "chunk step 1"))
o.append(tx(bx + 16 * (bw * 3 + 3) - 3, yb + bh + 10, "16", "end"))
o.append(tx(bx - 6, yb + 4, f"{top:.2f}°", "end"))
o.append(tx(bx - 6, yb + bh + 3, "0", "end"))
lx = bx + 16 * (bw * 3 + 3) + 14
o.append(tx(lx, yb + 2, "vs bf16"))
SHORT = {"trt_fp16": "fp16", "trt_quant": "FP8/FP4", "fq_nvfp4": "W4A4"}
for i, (k, name) in enumerate(ORDER[1:]):
    r = C[k]["replay"]; name = SHORT[k]
    o.append(rc(lx, yb + 9 + i * 12, 8, 8, fill=ACC if k == HI else (BAND if k == "trt_quant" else FILL)))
    o.append(tx(lx + 12, yb + 16 + i * 12, f"{name}  {sum(r['mae_step'])/16:.2f}°"))

# (c) closed-loop command metrics, success episodes, bars proportional
yc = 196
o.append(tx(2, yc + 8, "(c)"))
metrics = [("jump_boundary", "jump at chunk boundary"), ("jump_within", "jump within chunk"), ("atv", "mean |Δa| per step")]
mx = 110
top = max(C[k]["metrics"]["success"][m][0] for k, _ in ORDER for m, _ in metrics)
for mi, (m, label) in enumerate(metrics):
    xx = mx + mi * 140
    for i, (k, name) in enumerate(ORDER):
        v, sd, n = C[k]["metrics"]["success"][m]
        w = v / top * 90
        y = yc + i * 12
        o.append(rc(xx, y, w, 9, fill=ACC if k == HI else FILL))
        o.append(tx(xx + w + 3, y + 8, f"{v:.4f}"))
    o.append(tx(xx, yc + 4 * 12 + 8, label))
for i, (k, name) in enumerate(ORDER):
    o.append(tx(mx - 6, yc + 8 + i * 12, name, "end"))
o.append(tx(mx - 6, yc + 4 * 12 + 8, "rad, success episodes", "end"))
o.append("</svg>")
svg = "".join(o).replace(f"max-width:{W}px", "max-width:1040px")
open(sys.argv[2], "w").write(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>GR00T Quantization Motion</title>
<style>body{{margin:0;background:#fff;color:#000;font-family:Arial,Helvetica,sans-serif;padding:24px 16px}}main{{max-width:1040px;margin:0 auto}}svg{{display:block;width:100%;height:auto}}p{{font-size:14px;margin:12px 0 0}}</style></head>
<body><main>{svg}<p>(a) same 30 placements and noise seed. (b) open-loop replay. (c) closed-loop command smoothness.</p></main></body></html>''')

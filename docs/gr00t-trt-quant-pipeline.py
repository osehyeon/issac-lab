import sys

sys.path.insert(0, "/Users/osehn/.claude/skills/paper-figures/scripts")
from figlib import *  # noqa

W = 520
o = [svg_open(W, 222), ARROW]
U = 3.2  # px per bit


def bits(x, y, n, fill=FILL, h=10, cell=True, kept=None):
    """a tensor value drawn as its bits: length proportional to bit width; kept < n leaves the rounded-away bits empty"""
    out = [rc(x, y, n * U, h, fill=fill)]
    if kept is not None and kept < n:
        out.append(rc(x + kept * U, y, (n - kept) * U, h, fill="#fff"))
    if cell:
        for k in range(1, n):
            out.append(ln(x + k * U, y, x + k * U, y + h, 0.3, "#fff" if fill == ACC else "#999"))
    return "".join(out), x + n * U


def scale_box(x, y):
    return rc(x, y, 6, 10, fill="#fff") + tx(x + 3, y + 8, "s", "middle")


# ---------------------------------------------------------------- (a) build: what happens to one weight
ya = 16
o.append(tx(2, ya + 8, "(a)"))
stages = []
x = 24
# PyTorch: 16-bit weight
s, e = bits(x, ya, 16); o.append(s); o.append(tx(x, ya + 24, "PyTorch")); o.append(tx(x, ya + 34, "bf16")); stages.append((x, e))
o.append(ln(e + 2, ya + 5, e + 24, ya + 5, W1, end=AR)); o.append(tx((e + 13), ya - 3, "calibrate", "middle"))
x = e + 28
# ModelOpt: 16 bits + scale, rounding marked
s, e = bits(x, ya, 16, kept=8); o.append(s); o.append(scale_box(e + 2, ya)); o.append(tx(x, ya + 24, "ModelOpt")); o.append(tx(x, ya + 34, "10 samples"))
e2 = e + 8
o.append(ln(e2 + 2, ya + 5, e2 + 24, ya + 5, W1, end=AR)); o.append(tx(e2 + 13, ya - 3, "export", "middle"))
x = e2 + 28
# ONNX: same 16 bits + scale + Q DQ nodes
s, e = bits(x, ya, 16, kept=8); o.append(s); o.append(scale_box(e + 2, ya)); o.append(tx(x, ya + 24, "ONNX")); o.append(tx(x, ya + 34, "fp16 + Q/DQ"))
e2 = e + 8
o.append(ln(e2 + 2, ya + 5, e2 + 24, ya + 5, W1, end=AR)); o.append(tx(e2 + 13, ya - 3, "build", "middle"))
x = e2 + 28
# engine: 8-bit weight + scale ; 4-bit + scale per 16
s, e = bits(x, ya, 8, fill=ACC); o.append(s); o.append(scale_box(e + 2, ya)); o.append(tx(e + 12, ya + 8, "FP8"))
s, e4 = bits(x, ya + 14, 4, fill=ACC); o.append(s); o.append(scale_box(e4 + 2, ya + 14)); o.append(tx(e4 + 12, ya + 22, "FP4, s per 16"))
o.append(tx(x, ya + 38, "TensorRT engine"))
o.append(tx(x, ya + 48, "1212 → 635 MB"))

# ---------------------------------------------------------------- (b) run: one Linear layer on the Tensor Core
yb = 102
o.append(tx(2, yb + 8, "(b)"))
x = 24
s, e = bits(x, yb, 16); o.append(s); o.append(tx(x, yb + 22, "x  fp16"))
o.append(ln(e + 2, yb + 5, e + 20, yb + 5, W1, end=AR)); o.append(tx(e + 11, yb - 3, "÷ s", "middle"))
x = e + 24
s, e = bits(x, yb, 8, fill=ACC); o.append(s); o.append(tx(x, yb + 22, "FP8"))
# tensor core box
tcx = e + 16
o.append(rc(tcx, yb - 26, 92, 60, fill="none", stroke=INK, sw=W1)); o.append(tx(tcx + 46, yb - 16, "Tensor Core", "middle"))
o.append(ln(e + 2, yb + 5, tcx, yb + 5, W1, end=AR))
# weight from below
s, ew = bits(tcx + 30, yb + 44, 8, fill=ACC); o.append(s); o.append(tx(ew + 4, yb + 52, "W  FP8, stored"))
o.append(ln(tcx + 30 + 4 * U, yb + 44, tcx + 30 + 4 * U, yb + 34, W1, end=AR))
# accumulator 32 bits inside
s, ea = bits(tcx + 8, yb + 12, 24, fill="#fff", h=8); o.append(s); o.append(tx(tcx + 8, yb + 8, "× and Σ in FP32"))
# out
o.append(ln(tcx + 92, yb + 5, tcx + 122, yb + 5, W1, end=AR)); o.append(tx(tcx + 110, yb - 3, "× s·s", "middle"))
x = tcx + 126
s, e = bits(x, yb, 16); o.append(s); o.append(tx(x, yb + 22, "y  fp16"))
# latency bars to the right, proportional
lx = e + 36
o.append(tx(lx, yb - 16, "ms per call"))
for k, (name, v) in enumerate((("bf16 PyTorch", 43), ("fp16 engine", 22), ("FP8/FP4 engine", 21))):
    yy = yb - 8 + k * 14
    o.append(rc(lx, yy, v * 1.6, 9, fill=ACC if k == 2 else FILL))
    o.append(tx(lx + v * 1.6 + 3, yy + 8, f"{v}  {name}"))

# ---------------------------------------------------------------- (c) parameters by precision, width proportional
yc = 172
o.append(tx(2, yc + 8, "(c)"))
parts = [("ViT", 412, ACC, "8 bit"), ("LLM", 403, ACC, "4 bit"), ("o, down", 201, FILL, ""), ("embed", 311, FILL, ""),
         ("DiT", 550, ACC, "8 bit"), ("VL attn", 201, FILL, ""), ("enc, dec", 316, FILL, "")]
total = sum(p[1] for p in parts)
x0, wtot = 24, W - 30
x = x0
for name, m, fill, tag in parts:
    w = m / total * wtot
    o.append(rc(x, yc, w, 14, fill=fill))
    if name:
        o.append(tx(x + w / 2, yc + 24, name, "middle"))
    if tag:
        o.append(tx(x + w / 2, yc + 10, tag, "middle", "#fff"))
    x += w
o.append(tx(x0, yc + 36, "parameters, 2.4 B"))
o.append(tx(x0 + wtot, yc + 36, "gray: fp16", "end"))
o.append("</svg>")
svg = "".join(o)
html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Quantized GR00T Path</title>
<style>body{{margin:0;background:#fff;color:#000;font-family:Arial,Helvetica,sans-serif;padding:24px 16px}}main{{max-width:1040px;margin:0 auto}}svg{{display:block;width:100%;height:auto}}p{{font-size:14px;margin:12px 0 0;color:#000}}</style></head>
<body><main>{svg.replace(f"max-width:{W}px", "max-width:1040px")}
<p>(a) one weight, PyTorch to engine. (b) one Linear layer at run time. (c) parameters by precision.</p>
</main></body></html>'''
open(sys.argv[1], "w").write(html)

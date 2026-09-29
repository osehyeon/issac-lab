"""shoulder_lift command trace, bf16 vs W4A4 DiT, same placement (episode 3), 2 s window: what the eye cannot see in the stream."""

import sys

import numpy as np

sys.path.insert(0, "/Users/osehn/.claude/skills/paper-figures/scripts")
from figlib import *  # noqa

d = sys.argv[1]
fp = np.load(f"{d}/fp_ep003.npz"); q = np.load(f"{d}/w4a4_ep003.npz")
J = 1                                   # shoulder_lift
T0, N = 60, 120                         # steps 60..180 = 1.0 s .. 3.0 s
W, H = 520, 250
o = [svg_open(W, H), ARROW]
x0, xw = 60, 440
px = xw / N


def trace(y_top, h, a, ic, label, acc):
    seg = a[T0:T0 + N, J]
    lo, hi = seg.min(), seg.max(); span = max(hi - lo, 1e-6)
    pts = " ".join(f"{x0 + i * px:.1f},{y_top + h - (v - lo) / span * h:.1f}" for i, v in enumerate(seg))
    o.append(f'<polyline points="{pts}" style="fill:none;stroke:{ACC if acc else INK};stroke-width:{W2}"/>')
    for i in range(N):                  # chunk boundaries as faint ticks
        if ic[T0 + i] == 0:
            o.append(ln(x0 + i * px, y_top + h + 2, x0 + i * px, y_top + h + 6, W1, LIGHT))
    o.append(tx(x0 - 6, y_top + h / 2 + 3, label, "end", ACC if acc else INK))
    o.append(tx(x0 + xw + 4, y_top + 3, f"{np.degrees(hi):.0f}°")); o.append(tx(x0 + xw + 4, y_top + h - 2, f"{np.degrees(lo):.0f}°"))


def steps(y_mid, a, acc):
    da = np.degrees(np.diff(a[T0 - 1:T0 + N, J]))
    s = 14 / max(np.abs(da).max(), 1e-6)
    for i, v in enumerate(da):
        x = x0 + i * px
        o.append(rc(x, y_mid - max(v, 0) * s, max(px - 0.6, 0.8), abs(v) * s, fill=ACC if acc else FILL, stroke="none"))
    o.append(ln(x0, y_mid, x0 + xw, y_mid, W1))


o.append(tx(2, 12, "(a)"))
trace(18, 48, fp["action"], fp["in_chunk"], "bf16", False)
trace(84, 48, q["action"], q["in_chunk"], "W4A4", True)
o.append(tx(x0, 150, "1 s")); o.append(tx(x0 + xw, 150, "3 s", "end")); o.append(tx(x0 + xw / 2, 150, "shoulder_lift command, ticks = new chunk", "middle"))

o.append(tx(2, 176, "(b)"))
steps(190, fp["action"], False); o.append(tx(x0 - 6, 193, "bf16", "end"))
steps(228, q["action"], True); o.append(tx(x0 - 6, 231, "W4A4", "end", ACC))
o.append(tx(x0 + xw / 2, 248, "step-to-step change of the command, up = opening, down = closing", "middle"))
o.append("</svg>")
svg = "".join(o).replace(f"max-width:{W}px", "max-width:1040px")
open(sys.argv[2], "w").write(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Command Jitter Trace</title>
<style>body{{margin:0;background:#fff;color:#000;font-family:Arial,Helvetica,sans-serif;padding:24px 16px}}main{{max-width:1040px;margin:0 auto}}svg{{display:block;width:100%;height:auto}}p{{font-size:14px;margin:12px 0 0}}</style></head>
<body><main>{svg}<p>Episode 3, same placement and noise seed. (a) commanded shoulder_lift angle, (b) its change per 16.7 ms step; sign flips per step: bf16 40 %, W4A4 53 %.</p></main></body></html>''')

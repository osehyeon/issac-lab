"""Closed loop as it runs here: Isaac Sim -> observation -> leisaac client -> GR00T server -> 16-step chunk -> PD actuators."""

import sys

sys.path.insert(0, "/Users/osehn/.claude/skills/paper-figures/scripts")
from figlib import *  # noqa

W, H = 520, 236
o = [svg_open(W, H), ARROW]
VIEW = "#f1dcd6"


def img(x, y, w=32, label=""):
    h = w * 3 / 4
    out = [rc(x, y, w, h, fill=VIEW)]
    if label:
        out.append(tx(x + w / 2, y + h + 9, label, "middle"))
    return "".join(out), y + h


# ---- simulator (left)
sx, sy, sw, sh = 14, 22, 132, 118
o.append(rc(sx, sy, sw, sh, fill="none", sw=W1))
o.append(tx(sx + 4, sy - 4, "Isaac Sim, 60 Hz"))
# counter, robot, oranges, plate, cameras
o.append(rc(sx + 10, sy + 86, 112, 6, fill=BAND, stroke="none"))
o.append(f'<polygon points="{sx + 83},{sy + 39} {sx + 60},{sy + 86} {sx + 96},{sy + 86}" style="fill:{VIEW};stroke:none"/>')
o.append(rc(sx + 16, sy + 70, 16, 16, fill=FILL))
o.append(ln(sx + 24, sy + 70, sx + 34, sy + 40, 2.2)); o.append(ln(sx + 34, sy + 40, sx + 58, sy + 56, 2.2))
o.append(rc(sx + 56, sy + 54, 4, 4, fill=ACC, stroke=ACC))
for k in range(3):
    o.append(f'<circle cx="{sx + 66 + k * 9}" cy="{sy + 82}" r="4" style="fill:{FILL};stroke:{INK};stroke-width:{W1}"/>')
o.append(rc(sx + 92, sy + 84, 22, 2, fill="#fff"))
o.append(rc(sx + 80, sy + 34, 6, 5, fill=ACC, stroke=ACC))
o.append(tx(sx + 10, sy + 106, "PD joints, k 17.8, d 0.6"))

# ---- observation leaving the sim
ox = sx + sw + 10
s1, yb = img(ox, 30, 32, "front"); o.append(s1)
s2, yb = img(ox + 38, 30, 32, "wrist"); o.append(s2)
for k in range(6):
    o.append(rc(ox + k * 11, 74, 9, 9, fill=FILL))
o.append(tx(ox, 94, "joint pos ×6, rad"))
o.append(ln(sx + sw, 52, ox - 2, 52, W1, end=AR))
o.append(tx(ox + 84, 44, "every 16 steps"))

# ---- client and transport
cx0 = ox + 84
o.append(ln(ox + 74, 78, cx0 + 24, 78, W1, end=AR))
o.append(tx(cx0 + 28, 74, "rad → deg,"))
o.append(tx(cx0 + 28, 85, "ZMQ, msgpack"))

# ---- server (right)
gx, gy, gw, gh = 388, 22, 118, 118
o.append(rc(gx, gy, gw, gh, fill="none", sw=W1))
o.append(tx(gx + 4, gy - 4, "GR00T N1.5 server"))
for i, (name, ms) in enumerate((("bf16 PyTorch", 43), ("fp16 engine", 22), ("FP8/FP4 engine", 21))):
    yy = gy + 14 + i * 22
    o.append(rc(gx + 8, yy, ms * 1.6, 9, fill=ACC if i == 2 else FILL))
    o.append(tx(gx + 8, yy + 19, f"{name}  {ms} ms"))
o.append(tx(gx + 8, gy + 96, "noise seed fixed"))
o.append(tx(gx + 8, gy + 108, "4 Euler steps"))
o.append(ln(cx0 + 100, 78, gx - 2, 78, W1, end=AR))

# ---- chunk returning along the bottom
cy = 168
o.append(ln(gx + gw / 2, gy + gh, gx + gw / 2, cy + 5, W1))
o.append(ln(gx + gw / 2, cy + 5, ox + 16 * 11 + 8, cy + 5, W1, end=AR))
for k in range(16):
    fill = ACC if k == 0 else FILL
    o.append(rc(ox + k * 11, cy, 9, 10, fill=fill))
o.append(tx(ox, cy - 6, "16 actions × 6 joints, deg → rad"))
o.append(tx(ox, cy + 22, "step 1"))
o.append(tx(ox + 16 * 11 - 2, cy + 22, "16, then ask again", "end"))
o.append(ln(ox - 2, cy + 5, sx + 40, cy + 5, W1)); o.append(ln(sx + 40, cy + 5, sx + 40, sy + sh + 2, W1, end=AR))
o.append(tx(sx + 44, cy - 6, "1 action per 16.7 ms"))

# ---- timeline of one cycle
ty = 224
o.append(tx(sx, ty - 6, "one cycle, sim time"))
tx0 = sx + 96
o.append(rc(tx0, ty - 12, 0, 8, fill="none", stroke="none"))
o.append(rc(tx0, ty - 12, 46 * 0.9, 8, fill=ACC, stroke=ACC)); o.append(tx(tx0 + 46 * 0.9 / 2, ty + 4, "infer", "middle"))
for k in range(16):
    o.append(rc(tx0 + 46 * 0.9 + 4 + k * 9, ty - 12, 8, 8, fill=FILL))
o.append(tx(tx0 + 46 * 0.9 + 4 + 16 * 9 + 4, ty - 5, "16 × 16.7 ms = 0.27 s"))

o.append("</svg>")
svg = "".join(o).replace(f"max-width:{W}px", "max-width:1040px")
open(sys.argv[1], "w").write(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>GR00T Control Loop</title>
<style>body{{margin:0;background:#fff;color:#000;font-family:Arial,Helvetica,sans-serif;padding:24px 16px}}main{{max-width:1040px;margin:0 auto}}svg{{display:block;width:100%;height:auto}}p{{font-size:14px;margin:12px 0 0}}</style></head>
<body><main>{svg}<p>Synchronous loop: the simulator waits for the server, executes the 16 returned actions one per step, then sends a new observation.</p></main></body></html>''')

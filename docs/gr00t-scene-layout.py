"""PickOrange scene to scale, side view over top view sharing the forward axis. Values from the scene USD and leisaac configs."""

import math
import sys

sys.path.insert(0, "/Users/osehn/.claude/skills/paper-figures/scripts")
from figlib import *  # noqa

ROBOT_Y, TABLE_Z = -0.61, 0.92
CAM = (-0.11, 1.49)                       # (y, z): 0.50 m ahead of the base, 0.57 m above the counter
ORANGES = [(2.126, -0.304), (2.249, -0.332), (2.154, -0.405)]   # (x, y)
PLATE = (2.415, -0.338)
TILT, VFOV, HFOV = 19.0, 30.5, 40.0       # optical axis 19° from vertical towards the robot
VIEW = "#f1dcd6"                          # light tint of the accent: what a camera sees
S = 450
Y0, Y1 = -0.70, 0.02
W = int((Y1 - Y0) * S) + 100
o = [svg_open(W, 0), ARROW]


def side(y, z):
    return 24 + (y - Y0) * S, 14 + (1.56 - z) * S


def top(y, x):
    return 24 + (y - Y0) * S, 340 + (x - 1.93) * S


def poly(pts, fill, stroke="none", sw=W1, dash=""):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{p}" style="fill:{fill};stroke:{stroke};stroke-width:{sw}{";stroke-dasharray:" + dash if dash else ""}"/>'


def circ(cx, cy, r, fill=FILL):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" style="fill:{fill};stroke:{INK};stroke-width:{W1}"/>'


# ---------------------------------------------------------------- side view
h = CAM[1] - TABLE_Z
y_near = CAM[0] - h * math.tan(math.radians(TILT - VFOV / 2))
y_far = CAM[0] - h * math.tan(math.radians(TILT + VFOV / 2))
o.append(poly([side(*CAM), side(y_near, TABLE_Z), side(y_far, TABLE_Z)], VIEW))              # front camera view
# arm: base, shoulder, upper arm, forearm, wrist, gripper; wrist camera looks down-forward at the oranges
bx, bz = ROBOT_Y, TABLE_Z
sh = (bx + 0.01, bz + 0.09)
el = (bx + 0.03, bz + 0.24)
wr = (bx + 0.17, bz + 0.17)
gr = (bx + 0.22, bz + 0.10)
wc = (wr[0] + 0.02, wr[1] - 0.03)
wv = [side(*wc), side(wc[0] + 0.02, TABLE_Z), side(wc[0] + 0.22, TABLE_Z)]
x0, _ = side(Y0 + 0.02, TABLE_Z); x1, y1 = side(Y1 - 0.02, TABLE_Z)
o.append(rc(x0, y1, x1 - x0, 0.04 * S, fill=BAND, stroke="none"))                            # counter
for x, y in ORANGES:
    o.append(circ(*side(y, TABLE_Z + 0.027), 0.027 * S))
px, py = side(PLATE[1] - 0.10, TABLE_Z)
o.append(rc(px, py - 0.012 * S, 0.20 * S, 0.012 * S, fill="#fff"))
bxp, bzp = side(bx - 0.045, bz + 0.07)
o.append(rc(bxp, bzp, 0.09 * S, 0.07 * S, fill=FILL))
o.append(circ(*side(*sh), 0.02 * S))
for a, b in ((sh, el), (el, wr)):
    o.append(ln(*side(*a), *side(*b), 3.2))
o.append(ln(*side(*wr), *side(*gr), 2.0))
o.append(ln(*side(gr[0] - 0.01, gr[1] - 0.01), *side(gr[0] + 0.02, gr[1] - 0.06), 1.2))
o.append(ln(*side(gr[0] + 0.01, gr[1] + 0.01), *side(gr[0] + 0.04, gr[1] - 0.04), 1.2))
cx, cy = side(*wc); o.append(rc(cx - 3.5, cy - 3.5, 7, 7, fill=ACC, stroke=ACC))
cx, cy = side(*CAM); o.append(rc(cx - 6, cy - 5, 12, 10, fill=ACC, stroke=ACC))
o.append(tx(cx - 10, cy + 3, "front camera", "end", ACC))
wx, wy = side(*wr); o.append(tx(wx + 10, wy - 8, "wrist camera", color=ACC))
# dimensions: height of the camera over the counter, distance ahead of the base
dx = x1 + 18
o.append(ln(dx, cy, dx, y1, W1)); o.append(ln(dx - 3, cy, dx + 3, cy, W1)); o.append(ln(dx - 3, y1, dx + 3, y1, W1))
o.append(tx(dx + 5, (cy + y1) / 2 + 3, "0.57 m"))

# ---------------------------------------------------------------- top view, same horizontal axis
d_near = h / math.cos(math.radians(TILT - VFOV / 2)); d_far = h / math.cos(math.radians(TILT + VFOV / 2))
hw_n, hw_f = d_near * math.tan(math.radians(HFOV / 2)), d_far * math.tan(math.radians(HFOV / 2))
x0, y0 = top(Y0 + 0.02, 1.95); x1, y1 = top(Y1 - 0.02, 2.55)
o.append(rc(x0, y0, x1 - x0, y1 - y0, fill=BAND, stroke="none"))                             # counter
o.append(poly([top(y_near, 2.2 - hw_n), top(y_near, 2.2 + hw_n), top(y_far, 2.2 + hw_f), top(y_far, 2.2 - hw_f)], VIEW))
rx, ry = top(bx - 0.045, 2.2 - 0.045)
o.append(rc(rx, ry, 0.09 * S, 0.09 * S, fill=FILL))
o.append(ln(*top(sh[0], 2.2), *top(gr[0], 2.2), 3.2))                                        # arm seen from above
for x, y in ORANGES:
    o.append(circ(*top(y, x), 0.027 * S))
cx, cy = top(PLATE[1], PLATE[0]); o.append(circ(cx, cy, 0.10 * S, "#fff"))
cx, cy = top(CAM[0], 2.2); o.append(rc(cx - 6, cy - 5, 12, 10, fill=ACC, stroke=ACC))
bxp, byp = top(bx, 2.2 + 0.045)
o.append(ln(bxp, y1 + 14, cx, y1 + 14, W1)); o.append(ln(bxp, y1 + 11, bxp, y1 + 17, W1)); o.append(ln(cx, y1 + 11, cx, y1 + 17, W1))
o.append(tx((bxp + cx) / 2, y1 + 27, "0.50 m", "middle"))
o.append(tx(rx + 0.045 * S, ry + 0.09 * S + 12, "SO-101", "middle"))
o.append(tx(*[v + d for v, d in zip(top(ORANGES[1][1], ORANGES[1][0]), (0, 0.027 * S + 10))], "orange", "middle"))
o.append(tx(*top(PLATE[1], PLATE[0] + 0.10 + 0.03), "plate", "middle"))
H = int(y1 + 32)
o.append("</svg>")
svg = "".join(o).replace('viewBox="0 0 %d 0"' % W, 'viewBox="0 0 %d %d"' % (W, H)).replace(f"max-width:{W}px", "max-width:760px")
open(sys.argv[1], "w").write(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>PickOrange Scene Layout</title>
<style>body{{margin:0;background:#fff;color:#000;font-family:Arial,Helvetica,sans-serif;padding:24px 16px}}main{{max-width:760px;margin:0 auto}}svg{{display:block;width:100%;height:auto}}p{{font-size:14px;margin:12px 0 0}}</style></head>
<body><main>{svg}<p>Side view above, top view below, same scale; tinted area = what the front camera sees.</p></main></body></html>''')

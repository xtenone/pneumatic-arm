"""Small wall (docs/small-wall.md): the light arm, a stack of wooden blocks and the place for
the row, as at the start of stage 1.

    python full-arm/small_wall.py           # out/small_wall_start_<camera>.png
    python full-arm/small_wall.py --check   # joint angles for every pick and place

Light version: shoulder 2 × Ø32 × 200 on a 100 mm lever, elbow 2 × Ø25 × 80 on a 50 mm
lever, wrist pitch keeps the gripper pointing down, gripper yaw turns the block 90° from
the stack to the wall. Simple shapes, drawing code shared with cocktail.py.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cocktail as C  # noqa: E402

K = C.K
box, rod = C.box, C.rod
OUT = C.OUT

BLOCK = (0.136, 0.068, 0.068)                 # length, width, height (m)
GAP = 0.004                                   # joint between blocks in the row
TABLE_TOP = C.TABLE_TOP
C.TABLE = dict(x=(0.15, 1.0), y=(-0.85, 0.6))
STACK = C.polar(0.70, -70)                    # centre of the stack; blocks along x (turned 90° to the wall)
STACK_N = 4
WALL_X = 0.65                                 # row along y, starting against a strip at the -y end
WALL_Y = [-1.5 * (BLOCK[0] + GAP) + i * (BLOCK[0] + GAP) for i in range(4)]
GRIP_DEPTH = 0.020                            # grasp centre below the block's top (jaws on the top 40 mm)
OPEN, CLOSED = 0.095, 0.068
START = np.array([0.55, -0.30, TABLE_TOP + 0.28])

C.S[:] = [0.0, 0.0, TABLE_TOP + 0.66]          # shoulder 0.66 m above the table: elbow ≥ 12 cm above it
# light shoulder: 2 × Ø32 × 200 on a 100 mm hub (body about Ø40 over the profile)
C.SH_HUB, C.SH_LOW, C.SH_CYL = 0.10, (-0.22, -0.20), (0.020, 0.20, 0.006)
C.GRIP = 0.14                                 # wrist → grasp centre with the block gripper

LIGHT_WOOD, DARKER_WOOD, TAPE = (0.86, 0.72, 0.50, 1), (0.78, 0.62, 0.40, 1), (0.12, 0.12, 0.14, 1)


def tool(q, psi):
    """Gripper pointing straight down; psi turns it about the vertical."""
    yaw, p1, p2 = q
    Ru, Rf, Rw, E, W = K.chain([yaw, p1, 0.0, p2, 0.0, -p1 - p2])
    off = K.Rz(yaw) @ np.array([C.SH_OFF, 0.0, 0.0])
    E, W = E + off, W + off
    Rt = Rw @ K.Rz(psi)
    return Ru, Rf, Rw, Rt, E, W, W - C.GRIP * Rt[:, 2]


C.tool = tool


def pose(G, along, q0):
    """Joint angles for grasp centre G with the jaws across a block whose long axis has angle `along`."""
    q, err = C.solve(G, 0.0, q0)
    return q, along - q[0], err


def draw_gripper(palm, Rt, jaw):
    """Parallel gripper: MGN12 rail across the jaws, two carriages, rack-and-pinion, Ø16 cylinder."""
    xt, yt, zt = Rt[:, 0], Rt[:, 1], Rt[:, 2]
    base = palm - 0.010 * zt
    box(base, (0.022, 0.075, 0.006), C.ALU, Rt)                               # plate under the yaw motor
    box(base - 0.012 * zt, (0.006, 0.075, 0.005), C.STEEL, Rt)               # rail
    rod(base + 0.025 * xt - 0.060 * yt, base + 0.025 * xt + 0.010 * yt, 0.010, C.ALU)   # Ø16 cylinder
    rod(base + 0.025 * xt + 0.010 * yt, base + 0.025 * xt + 0.035 * yt, 0.003, C.STEEL)
    rod(base - 0.012 * zt - 0.012 * xt, base - 0.012 * zt + 0.012 * xt, 0.012, C.RED)    # pinion (drawn as a disc)
    for s in (1, -1):
        car = base - 0.022 * zt + s * (jaw / 2 + 0.008) * yt
        box(car, (0.014, 0.012, 0.005), C.STEEL, Rt)                          # carriage
        finger = car + s * 0.002 * yt - 0.048 * zt
        box(finger, (0.018, 0.005, 0.045), C.BLUE, Rt)
        box(finger - s * 0.006 * yt - 0.018 * zt, (0.016, 0.001, 0.022), C.DARK, Rt)   # rubber pad


C.draw_gripper = draw_gripper


def block(centre, along, rgba=LIGHT_WOOD):
    box(centre, (BLOCK[0] / 2, BLOCK[1] / 2, BLOCK[2] / 2), rgba, K.Rz(along))


def draw_scene():
    x0, x1 = C.TABLE["x"]
    y0, y1 = C.TABLE["y"]
    box(((x0 + x1) / 2, (y0 + y1) / 2, TABLE_TOP - 0.015), ((x1 - x0) / 2, (y1 - y0) / 2, 0.015), C.WOOD)
    for x in (x0 + 0.03, x1 - 0.03):
        for y in (y0 + 0.03, y1 - 0.03):
            box((x, y, (TABLE_TOP - 0.03) / 2), (0.02, 0.02, (TABLE_TOP - 0.03) / 2), C.WOOD)
    # stack in a corner jig (strips on the -y side and the +x side)
    for i in range(STACK_N):
        block(STACK + [0, 0, TABLE_TOP + (i + 0.5) * BLOCK[2]], 0.0, LIGHT_WOOD if i % 2 else DARKER_WOOD)
    sx, sy = STACK[0], STACK[1]
    box((sx, sy - BLOCK[1] / 2 - 0.01, TABLE_TOP + 0.02), (BLOCK[0] / 2 + 0.03, 0.01, 0.02), C.COLUMN)
    box((sx + BLOCK[0] / 2 + 0.01, sy, TABLE_TOP + 0.02), (0.01, BLOCK[1] / 2 + 0.02, 0.02), C.COLUMN)
    # row: stop strip at the -y end, tape marks for the four places
    y_start = WALL_Y[0] - BLOCK[0] / 2
    box((WALL_X, y_start - 0.01, TABLE_TOP + 0.015), (0.06, 0.01, 0.015), C.COLUMN)
    for y in WALL_Y:
        for s in (1, -1):
            box((WALL_X + s * (BLOCK[1] / 2 + 0.006), y, TABLE_TOP + 0.0005), (0.004, BLOCK[0] / 2 - 0.004, 0.0005), TAPE)
            box((WALL_X, y + s * (BLOCK[0] / 2 - 0.002), TABLE_TOP + 0.0005), (BLOCK[1] / 2 + 0.010, 0.002, 0.0005), TAPE)


def targets():
    """(name, grasp centre, block long-axis angle) for every pick and place of stage 1."""
    out = []
    for i in range(STACK_N):
        top = TABLE_TOP + (STACK_N - i) * BLOCK[2]
        out.append((f"pick {i + 1}", STACK + [0, 0, top - GRIP_DEPTH], 0.0))
        out.append((f"place {i + 1}", np.array([WALL_X, WALL_Y[i], TABLE_TOP + BLOCK[2] - GRIP_DEPTH]), math.pi / 2))
    return out


def shoulder_cylinder(q):
    """Pin-to-pin length and lever (m) of the shoulder cylinders in the arm plane."""
    h = C.SH_HUB * (K.Ry(q[1]) @ np.array([1.0, 0.0, 0.0]))
    h = np.array([h[0], h[2]])
    d = h - np.array(C.SH_LOW)
    u = d / np.linalg.norm(d)
    return np.linalg.norm(d), abs(h[0] * u[1] - h[1] * u[0])


def check():
    q = np.array([-0.5, -0.9, 1.3])
    print("| Move | Base yaw | Shoulder | Elbow bend | Gripper yaw | Shoulder cylinder pin-pin / lever | Error |")
    for name, G, along in [("start", START, math.pi / 2)] + targets():
        q, psi, err = pose(G, along, q)
        L, lev = shoulder_cylinder(q)
        print(f"| {name} | {math.degrees(q[0]):.0f}° | {math.degrees(q[1]):.0f}° | {math.degrees(q[2]):.0f}° | "
              f"{math.degrees(psi):.0f}° | {L * 1000:.0f} / {lev * 1000:.0f} mm | {err * 1000:.1f} mm |")


CAMS = {"main": ((1.05, -1.75, 1.55), (0.35, -0.2, 0.9)), "top": ((-0.25, -0.15, 2.5), (0.55, -0.15, 0.72)),
        "close": ((0.95, -0.80, 1.12), (0.52, -0.32, 0.95))}


def main():
    if "--check" in sys.argv:
        return check()
    C.CAMS = CAMS
    q, psi, err = pose(START, math.pi / 2, np.array([-0.5, -0.9, 1.3]))
    C.GEOMS.clear()
    C.draw_arm(q, psi, OPEN)
    draw_scene()
    os.makedirs(OUT, exist_ok=True)
    for cam in CAMS:
        path = os.path.join(OUT, f"small_wall_start_{cam}.png")
        Image.fromarray(C.render_frame(None, cam)).save(path)
        print(path)


if __name__ == "__main__":
    main()

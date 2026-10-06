"""Concept render of the full arm: placing a 15 kg block on a wall.

    python full-arm/concept.py      # out/render_concept_<camera>.png

Simple shapes only (MuJoCo primitives), to show the layout and proportions; dimensions
follow docs/full-arm-sizing.md. Not a worked-out design.

Layout:
- base yaw: slewing ring on a base plate, electric (no gravity torque about a vertical axis)
- shoulder: the test 2 joint at about 1.7× scale (pitch + roll), 2 × Ø63 × 300, lever 150 mm
- elbow: the same joint, 2 × Ø50 cylinders lying along the upper arm (like a biceps)
- wrist pitch: one small cylinder along the forearm
- gripper: two jaws closed by a pneumatic cylinder
"""
import math
import os
import sys

os.environ.setdefault("MUJOCO_GL", "egl")
import mujoco  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# --- dimensions (m) ---------------------------------------------------------------------
SHOULDER = np.array([0.0, 0.0, 1.0])
L_UPPER, L_FORE = 0.5, 0.5
BLOCK = np.array([0.15, 0.30, 0.15])           # x (wall thickness), y (along the wall), z; ≈ 15 kg concrete
WALL_X = 0.85
SHOULDER_HUB, SHOULDER_BAR = 0.15, 0.12        # hub along the upper arm, cross blocks beside it
SHOULDER_LOW = np.array([0.06, 0.0, 0.38])     # lower pivots (y = ±SHOULDER_BAR)
ELBOW_HUB, ELBOW_BAR, ELBOW_LOW = 0.10, 0.09, 0.22
GRIP_H = 0.12                                   # wrist → top of the block

ALU = (0.78, 0.80, 0.83, 1)
STEEL = (0.45, 0.46, 0.50, 1)
DARK = (0.22, 0.23, 0.26, 1)
RED = (0.75, 0.25, 0.20, 1)
BLUE = (0.20, 0.40, 0.75, 1)
CONCRETE = (0.66, 0.65, 0.61, 1)
WOOD = (0.72, 0.56, 0.36, 1)


def ik(target):
    """Shoulder and forearm pitch (elbow up) for a wrist point in the x-z plane."""
    d = target - SHOULDER
    dist = math.hypot(d[0], d[2])
    c = (dist ** 2 - L_UPPER ** 2 - L_FORE ** 2) / (2 * L_UPPER * L_FORE)
    bend = math.acos(max(-1.0, min(1.0, c)))
    p1 = math.atan2(d[2], d[0]) + math.atan2(L_FORE * math.sin(bend), L_UPPER + L_FORE * math.cos(bend))
    return p1, p1 - bend


def unit(p):
    return np.array([math.cos(p), 0.0, math.sin(p)])


# --- geometry helpers -------------------------------------------------------------------
G = []


def fmt(v):
    return " ".join(f"{x:.4f}" for x in v)


def rod(a, b, r, rgba, kind="capsule"):
    G.append(f'<geom type="{kind}" fromto="{fmt(a)} {fmt(b)}" size="{r}" rgba="{fmt(rgba)}"/>')


def box(c, half, rgba, x=(1, 0, 0), y=(0, 1, 0)):
    G.append(f'<geom type="box" pos="{fmt(c)}" size="{fmt(half)}" xyaxes="{fmt(x)} {fmt(y)}" rgba="{fmt(rgba)}"/>')


def cylinder(low, high, r_body, body_len, r_rod, rgba=ALU):
    """Cylinder from its rear pivot to its rod end: body, rod and the two eyes."""
    d = (high - low) / np.linalg.norm(high - low)
    end = low + d * body_len
    rod(low - d * 0.02, end, r_body, rgba, "cylinder")
    rod(end, high, r_rod, STEEL, "cylinder")
    rod(end - d * 0.01, end + d * 0.015, r_body * 0.75, DARK, "cylinder")     # front cover


# --- scene ------------------------------------------------------------------------------
def build():
    block_c = np.array([WALL_X, 0.0, 3 * BLOCK[2] + BLOCK[2] / 2 + 0.012])   # hovering above course 3
    wrist = block_c + np.array([0, 0, BLOCK[2] / 2 + GRIP_H])
    p1, p2 = ik(wrist)
    u, f = unit(p1), unit(p2)
    elbow = SHOULDER + L_UPPER * u
    nu = np.array([-u[2], 0, u[0]])                                      # normal to the upper arm (up)
    nf = np.array([-f[2], 0, f[0]])

    # base: plate, slewing ring, yaw motor with belt, column
    box((0, 0, 0.02), (0.35, 0.35, 0.02), DARK)
    rod((0, 0, 0.04), (0, 0, 0.09), 0.20, STEEL, "cylinder")
    box((-0.25, 0.0, 0.12), (0.045, 0.045, 0.06), (0.1, 0.1, 0.1, 1))
    rod((-0.25, 0, 0.18), (-0.25, 0, 0.19), 0.03, STEEL, "cylinder")
    rod((0, 0, 0.09), (0, 0, 0.93), 0.08, (0.35, 0.37, 0.40, 1), "cylinder")
    for s in (1, -1):                                                    # shoulder cheeks
        box((0, s * 0.075, 0.985), (0.07, 0.012, 0.075), (0.35, 0.37, 0.40, 1))
        low = SHOULDER_LOW + np.array([0, s * SHOULDER_BAR, 0])
        box(low - np.array([0.0, 0, 0.0]), (0.03, 0.025, 0.03), BLUE)      # lower U-joint
        rod(low, np.array([0.0, s * 0.07, low[2]]), 0.018, (0.35, 0.37, 0.40, 1), "cylinder")

    # shoulder joint, upper arm, hub, cylinders
    box(SHOULDER, (0.045, 0.06, 0.045), RED, x=u, y=(0, 1, 0))
    rod(SHOULDER + 0.04 * u, elbow - 0.04 * u, 0.025, ALU)
    hub = SHOULDER + SHOULDER_HUB * u
    rod(hub - 0.025 * u, hub + 0.025 * u, 0.042, ALU, "cylinder")
    rod(hub + np.array([0, -SHOULDER_BAR - 0.03, 0]), hub + np.array([0, SHOULDER_BAR + 0.03, 0]), 0.012, STEEL, "cylinder")
    for s in (1, -1):
        h = hub + np.array([0, s * SHOULDER_BAR, 0])
        box(h, (0.022, 0.022, 0.022), BLUE, x=u, y=(0, 1, 0))
        cylinder(SHOULDER_LOW + np.array([0, s * SHOULDER_BAR, 0]), h - np.array([0, 0, 0.03]), 0.037, 0.40, 0.011)

    # elbow joint, forearm, hub, cylinders along the upper arm
    box(elbow, (0.035, 0.05, 0.035), RED, x=u, y=(0, 1, 0))
    wrist_j = elbow + L_FORE * f
    rod(elbow + 0.03 * f, wrist_j - 0.03 * f, 0.02, ALU)
    ehub = elbow + ELBOW_HUB * f
    rod(ehub - 0.02 * f, ehub + 0.02 * f, 0.034, ALU, "cylinder")
    rod(ehub + np.array([0, -ELBOW_BAR - 0.025, 0]), ehub + np.array([0, ELBOW_BAR + 0.025, 0]), 0.01, STEEL, "cylinder")
    pivot = SHOULDER + ELBOW_LOW * u
    rod(pivot + np.array([0, -ELBOW_BAR - 0.02, 0]), pivot + np.array([0, ELBOW_BAR + 0.02, 0]), 0.01, STEEL, "cylinder")
    box(pivot, (0.025, 0.03, 0.03), ALU, x=u, y=(0, 1, 0))
    for s in (1, -1):
        h = ehub + np.array([0, s * ELBOW_BAR, 0])
        box(h, (0.018, 0.018, 0.018), BLUE, x=f, y=(0, 1, 0))
        lo = pivot + np.array([0, s * ELBOW_BAR, 0])
        box(lo, (0.018, 0.018, 0.018), BLUE, x=u, y=(0, 1, 0))
        cylinder(lo, h - 0.022 * (h - lo) / np.linalg.norm(h - lo), 0.03, 0.22, 0.009)

    # wrist: joint, small cylinder along the forearm, gripper hanging down
    box(wrist_j, (0.028, 0.04, 0.028), RED, x=f, y=(0, 1, 0))
    q = elbow + 0.18 * f + 0.045 * nf
    k = wrist_j + np.array([-0.05, 0, 0.05])
    box(q, (0.015, 0.02, 0.015), BLUE, x=f, y=(0, 1, 0))
    cylinder(q, k, 0.016, 0.16, 0.006)
    rod(wrist_j, k, 0.01, ALU, "capsule")                                  # wrist lever
    top = wrist_j - np.array([0, 0, 0.06])
    rod(wrist_j, top, 0.022, ALU, "cylinder")
    bar_c = top - np.array([0, 0, 0.012])
    box(bar_c, (0.035, BLOCK[1] / 2 + 0.03, 0.012), ALU)
    rod(bar_c + np.array([0, -0.13, 0.03]), bar_c + np.array([0, 0.13, 0.03]), 0.018, ALU, "cylinder")   # jaw cylinder
    for s in (1, -1):
        jaw_c = np.array([block_c[0], s * (BLOCK[1] / 2 + 0.008), (bar_c[2] + block_c[2]) / 2])
        box(jaw_c, (0.03, 0.008, (bar_c[2] - block_c[2]) / 2 + 0.01), BLUE)

    # the block being placed, the wall, a pallet with blocks
    box(block_c, BLOCK / 2, CONCRETE)
    pitch = BLOCK[1] + 0.01
    for course in range(4):
        z = course * BLOCK[2] + BLOCK[2] / 2
        ys = [(-1.5 + i) * pitch for i in range(4)] if course % 2 == 0 else [(-2 + i) * pitch for i in range(5)]
        if course == 3:
            ys = ys[:2]
        for y in ys:
            box((WALL_X, y, z), BLOCK / 2 - 0.002, CONCRETE)
    box((-0.1, 0.85, 0.06), (0.3, 0.2, 0.06), WOOD)
    for layer in range(2):
        for i in range(4):
            box((-0.1 + (i % 2 - 0.5) * 0.31, 0.85 + (i // 2 - 0.5) * 0.16, 0.12 + 0.075 + layer * 0.152),
                (BLOCK[1] / 2 - 0.002, BLOCK[0] / 2 - 0.002, BLOCK[2] / 2 - 0.002), CONCRETE)
    return math.degrees(p1), math.degrees(p2)


def camera(name, pos, target):
    pos, target = np.array(pos, float), np.array(target, float)
    fwd = (target - pos) / np.linalg.norm(target - pos)
    x = np.cross(fwd, [0, 0, 1])
    x /= np.linalg.norm(x)
    y = np.cross(x, fwd)
    return f'<camera name="{name}" pos="{fmt(pos)}" xyaxes="{fmt(x)} {fmt(y)}"/>'


CAMERAS = {
    "oblique": camera("oblique", (2.0, -2.1, 1.65), (0.4, 0.0, 0.55)),
    "side": camera("side", (0.45, -2.9, 0.75), (0.45, 0.0, 0.6)),
    "shoulder": camera("shoulder", (0.75, -0.95, 1.35), (0.2, 0.0, 0.85)),
}


def main():
    p1, p2 = build()
    xml = f"""<mujoco><visual><global offwidth="1280" offheight="960"/><quality shadowsize="8192"/>
<headlight ambient="0.35 0.35 0.35"/></visual>
<asset><texture type="skybox" builtin="gradient" rgb1="0.97 0.97 1" rgb2="0.72 0.76 0.84" width="512" height="512"/>
<texture name="grid" type="2d" builtin="checker" rgb1="0.90 0.90 0.90" rgb2="0.82 0.82 0.82" width="512" height="512"/>
<material name="floor" texture="grid" texrepeat="10 10"/></asset>
<worldbody><light pos="1.5 -1.5 3" dir="-0.4 0.4 -1" diffuse="0.75 0.75 0.75" castshadow="true"/>
<light pos="-1 1 2.5" dir="0.3 -0.3 -1" diffuse="0.3 0.3 0.3" castshadow="false"/>
<geom type="plane" size="4 4 0.01" material="floor"/>
{''.join(CAMERAS.values())}{''.join(G)}</worldbody></mujoco>"""
    mdl = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(mdl)
    mujoco.mj_forward(mdl, d)
    os.makedirs(OUT, exist_ok=True)
    r = mujoco.Renderer(mdl, 960, 1280)
    for cam in CAMERAS:
        r.update_scene(d, camera=cam)
        path = os.path.join(OUT, f"render_concept_{cam}.png")
        Image.fromarray(r.render()).save(path)
        print(path)
    r.close()
    print(f"shoulder pitch {p1:.1f}°, forearm pitch {p2:.1f}°")


if __name__ == "__main__":
    main()

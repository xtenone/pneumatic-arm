"""Concept render of the full arm: placing a 15 kg block on a low wall.

    python full-arm/concept.py            # out/render_concept_<camera>.png (biceps elbow, low wall)
    python full-arm/concept.py triceps    # out/render_triceps_<camera>.png
    python full-arm/concept.py glass      # out/render_glass_<camera>.png (holding a glass over a table)
    python full-arm/concept.py glass triceps_down   # the same with the upper arm hanging down

Simple shapes only (MuJoCo primitives), to show the layout and proportions; dimensions
follow docs/full-arm-sizing.md and the pose comes from full-arm/elbow.py (6 DOF). Not a
worked-out design.

Layout:
- base yaw: slewing ring on a base plate, electric (no gravity torque about a vertical axis)
- shoulder: the test 2 joint at about 1.7× scale (pitch + roll), 2 × Ø63 × 300, lever 150 mm
- elbow: the same joint (pitch + forearm roll); the forearm roll turns the gripper, like a
  human forearm. Two cylinders lie on top of the upper arm, like a biceps
- wrist pitch: one small cylinder along the forearm
- gripper: two jaws closed by a pneumatic cylinder, turned about the vertical by a small
  motor; the rolls stay at 0 here (they are for dexterity, not for lining up blocks)
"""
import math
import os
import sys

os.environ.setdefault("MUJOCO_GL", "egl")
import mujoco  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import elbow as K  # noqa: E402
from scipy.optimize import least_squares  # noqa: E402

OUT = os.path.join(HERE, "out")
BLOCK = np.array([0.15, 0.30, 0.15])           # x (wall thickness), y (along the wall), z; ≈ 15 kg concrete
SHOULDER_HUB, SHOULDER_BAR = 0.15, 0.12        # hub along the upper arm, cross blocks beside it
SHOULDER_LOW_Z, SHOULDER_LOW_X = 0.12, 0.06    # lower pivots on the turntable side of the column
GRIP_H = K.TOOL - BLOCK[2] / 2                  # wrist → top of the block
POSE_BLOCK = (0.3, 2)                           # the block being placed: y on the wall, course
ELBOW_CYL_D = 0.060                              # elbow cylinders, outside diameter (≈ a Ø50 bore ISO cylinder)
GRIP_BAR = 0.10                                 # wrist → gripper bar (yaw motor and post in between)
GLASS = dict(r=0.036, h=0.12, at=np.array([0.66, 0.10, 0.85]))   # held glass: radius, height, centre
TABLE = dict(x=0.66, y=0.05, top=0.72, half=(0.28, 0.45))
GLASS_C = (0.85, 0.92, 1.0, 0.28)
WATER = (0.35, 0.6, 0.95, 0.5)

ALU = (0.78, 0.80, 0.83, 1)
STEEL = (0.45, 0.46, 0.50, 1)
DARK = (0.22, 0.23, 0.26, 1)
COLUMN = (0.35, 0.37, 0.40, 1)
RED = (0.75, 0.25, 0.20, 1)
BLUE = (0.20, 0.40, 0.75, 1)
CONCRETE = (0.66, 0.65, 0.61, 1)
WOOD = (0.72, 0.56, 0.36, 1)

G = []


def fmt(v):
    return " ".join(f"{x:.4f}" for x in v)


def rod(a, b, r, rgba, kind="capsule"):
    G.append(f'<geom type="{kind}" fromto="{fmt(a)} {fmt(b)}" size="{r}" rgba="{fmt(rgba)}"/>')


def box(c, half, rgba, R=np.eye(3)):
    G.append(f'<geom type="box" pos="{fmt(c)}" size="{fmt(half)}" xyaxes="{fmt(R[:, 0])} {fmt(R[:, 1])}" rgba="{fmt(rgba)}"/>')


def cylinder(low, high, r_body, body_len, r_rod, rgba=ALU):
    """Cylinder from its rear pivot to its rod end: body, front cover and rod."""
    d = (high - low) / np.linalg.norm(high - low)
    end = low + d * body_len
    rod(low - d * 0.02, end, r_body, rgba, "cylinder")
    rod(end, high, r_rod, STEEL, "cylinder")
    rod(end - d * 0.01, end + d * 0.015, r_body * 0.75, DARK, "cylinder")


def solve_flat(centre, tool, align_wall):
    """Pose with both rolls at 0: base yaw, shoulder pitch, elbow pitch, wrist pitch keep the
    held object at `centre`, level; the gripper's own yaw motor lines it up with the wall
    (align_wall) or leaves the jaws square to the arm."""
    def pose(x):
        yaw, p1, p2, p3, psi = x
        q = [yaw, p1, 0.0, p2, 0.0, p3]
        Ru, Rf, Rw, E, W = K.chain(q)
        return q, Ru, Rf, Rw, Rw @ K.Rz(psi), E, W

    def res(x):
        _, _, _, _, Rt, _, W = pose(x)
        c = W - tool * Rt[:, 2]
        return np.concatenate([c - centre, Rt[:2, 2], [Rt[0, 1] if align_wall else x[4]]])
    yaw = math.atan2(centre[1], centre[0])
    if K.DOWN:                                 # elbow below the shoulder
        starts, lo, hi = [(-1.0, p2) for p2 in (1.4, 1.0, 1.8)], [-3, -1.7, 0, -2.6, -3.2], [3, 1.31, 2.6, 2.6, 3.2]
    else:
        starts, lo, hi = [(0.3, p2) for p2 in (-1.2, -0.8, -1.6)], [-3, -1.05, -2.6, -2.6, -3.2], [3, 1.31, 0, 2.6, 3.2]
    for p1, p2 in starts:
        sol = least_squares(res, [yaw, p1, p2, -(p1 + p2), -yaw], bounds=(lo, hi))
        if sol.cost < 1e-10:
            return pose(sol.x)
    raise ValueError("no pose")


def build(scene="wall"):
    if scene == "wall":
        y, course = POSE_BLOCK
        held_c = np.array([K.WALL_X, y, course * BLOCK[2] + BLOCK[2] / 2 + 0.012])
        tool = GRIP_BAR + 0.012 + BLOCK[2] / 2 + 0.01
    else:
        held_c = GLASS["at"]
        tool = GRIP_BAR + 0.012 + 0.008 + GLASS["h"] / 2
    q, Ru, Rf, Rw, Rt, E, W = solve_flat(held_c, tool, scene == "wall")
    S = K.S
    Rb = K.Rz(q[0])
    xu, yu, zu = Ru[:, 0], Ru[:, 1], Ru[:, 2]
    xf, yf = Rf[:, 0], Rf[:, 1]

    # base: plate, slewing ring, yaw motor, column, shoulder cheeks (turn with the base yaw)
    box((0, 0, 0.02), (0.3, 0.3, 0.02), DARK)
    rod((0, 0, 0.04), (0, 0, 0.09), 0.2, STEEL, "cylinder")
    box((-0.25, 0.0, 0.12), (0.045, 0.045, 0.06), (0.1, 0.1, 0.1, 1))
    rod((0, 0, 0.09), S - np.array([0, 0, 0.07]), 0.07, COLUMN, "cylinder")
    for s in (1, -1):
        box(S + Rb @ np.array([0, s * 0.075, -0.015]), (0.07, 0.012, 0.075), COLUMN, Rb)
        low = Rb @ np.array([SHOULDER_LOW_X, s * SHOULDER_BAR, SHOULDER_LOW_Z])
        box(low, (0.03, 0.025, 0.03), BLUE, Rb)
        rod(low, Rb @ np.array([0, s * 0.06, SHOULDER_LOW_Z]), 0.018, COLUMN, "cylinder")

    # shoulder joint, upper arm, hub with cross blocks, cylinders
    box(S, (0.045, 0.06, 0.045), RED, Ru)
    rod(S + 0.04 * xu, E - 0.04 * xu, 0.025, ALU)
    hub = S + SHOULDER_HUB * xu
    rod(hub - 0.025 * xu, hub + 0.025 * xu, 0.042, ALU, "cylinder")
    rod(hub - (SHOULDER_BAR + 0.03) * yu, hub + (SHOULDER_BAR + 0.03) * yu, 0.012, STEEL, "cylinder")
    for s in (1, -1):
        h = hub + s * SHOULDER_BAR * yu
        box(h, (0.022, 0.022, 0.022), BLUE, Ru)
        low = Rb @ np.array([SHOULDER_LOW_X, s * SHOULDER_BAR, SHOULDER_LOW_Z])
        cylinder(low, h - 0.03 * (h - low) / np.linalg.norm(h - low), 0.037, 0.40, 0.011)

    # elbow joint, forearm, hub, cylinders on top of the upper arm
    box(E, (0.035, 0.05, 0.035), RED, Rf)
    rod(E + 0.03 * xf, W - 0.03 * xf, 0.02, ALU)
    ehub = E + K.HUB_ALONG * xf
    if K.HUB_ALONG < 0:                                                        # triceps: lever behind the elbow
        rod(E, ehub, 0.015, ALU, "cylinder")
    rod(ehub - 0.02 * xf, ehub + 0.02 * xf, 0.034 if K.HUB_ALONG > 0 else 0.02, ALU, "cylinder")
    rod(ehub - (K.HUB_SIDE + 0.025) * yf, ehub + (K.HUB_SIDE + 0.025) * yf, 0.01, STEEL, "cylinder")
    pivot = S + K.LOW_ALONG * xu + K.LOW_UP * zu
    rod(S + max(K.LOW_ALONG, 0.06) * xu + 0.02 * zu, pivot, 0.012, ALU, "cylinder")   # post (leans back for the triceps)
    rod(pivot - (K.LOW_SIDE + 0.02) * yu, pivot + (K.LOW_SIDE + 0.02) * yu, 0.01, STEEL, "cylinder")
    for s in (1, -1):
        h = ehub + s * K.HUB_SIDE * yf
        lo = pivot + s * K.LOW_SIDE * yu
        box(h, (0.018, 0.018, 0.018), BLUE, Rf)
        box(lo, (0.018, 0.018, 0.018), BLUE, Ru)
        cylinder(lo, h - 0.022 * (h - lo) / np.linalg.norm(h - lo), ELBOW_CYL_D / 2, 0.30 if K.HUB_ALONG > 0 else 0.26, 0.01)

    # wrist: joint, small cylinder along the forearm, yaw motor, gripper
    box(W, (0.028, 0.04, 0.028), RED, Rw)
    zt, yt = Rt[:, 2], Rt[:, 1]
    k = W + 0.06 * Rw[:, 2] - 0.04 * Rw[:, 0]
    qp = E + 0.18 * xf + 0.045 * Rf[:, 2]
    box(qp, (0.015, 0.02, 0.015), BLUE, Rf)
    cylinder(qp, k, 0.016, 0.16, 0.006)
    rod(W, k, 0.01, ALU, "capsule")
    box(W - 0.045 * zt + 0.03 * Rw[:, 0], (0.021, 0.021, 0.021), (0.1, 0.1, 0.1, 1), Rw)      # yaw motor (NEMA17)
    rod(W - 0.03 * zt, W - 0.06 * zt, 0.032, (0.15, 0.15, 0.17, 1), "cylinder")                # yaw bearing
    rod(W - 0.06 * zt, W - (GRIP_BAR - 0.012) * zt, 0.018, ALU, "cylinder")
    bar_c = W - GRIP_BAR * zt
    box(bar_c, (0.03, BLOCK[1] / 2 + 0.03, 0.012), ALU, Rt)
    rod(bar_c + 0.028 * zt - 0.13 * yt, bar_c + 0.028 * zt + 0.13 * yt, 0.016, ALU, "cylinder")   # jaw cylinder
    held = W - tool * zt
    half_w = BLOCK[1] / 2 if scene == "wall" else GLASS["r"]
    depth = (bar_c - held) @ zt
    for s in (1, -1):
        jaw = held + s * (half_w + 0.008) * yt + depth / 2 * zt
        box(jaw, (0.025, 0.008, depth / 2 + 0.012), BLUE, Rt)
    if scene == "wall":
        box(held, BLOCK / 2, CONCRETE, Rt)
    else:
        glass(held)

    if scene == "glass":
        table()
        return np.degrees([q[0], q[1], q[2], q[3], q[4], q[5]])

    # low wall (courses below the one being placed, and the start of that course), pallet
    pitch = BLOCK[1] + 0.01
    for c in range(course + 1):
        z = c * BLOCK[2] + BLOCK[2] / 2
        ys = [(-1.5 + i) * pitch for i in range(4)] if c % 2 == 0 else [(-1 + i) * pitch for i in range(3)]
        if c == course:
            ys = [v for v in ys if v < y - 0.2]
        for v in ys:
            box((K.WALL_X, v, z), BLOCK / 2 - 0.002, CONCRETE)
    box((-0.15, 0.75, 0.06), (0.3, 0.2, 0.06), WOOD)
    for layer in range(2):
        for i in range(4):
            box((-0.15 + (i % 2 - 0.5) * 0.31, 0.75 + (i // 2 - 0.5) * 0.16, 0.12 + 0.075 + layer * 0.152),
                (BLOCK[1] / 2 - 0.002, BLOCK[0] / 2 - 0.002, BLOCK[2] / 2 - 0.002), CONCRETE)
    return np.degrees(q)


def glass(c, fill=0.6):
    """Drinking glass standing upright with its centre at c: wall, bottom, water."""
    h, r = GLASS["h"], GLASS["r"]
    base = np.asarray(c) - np.array([0, 0, h / 2])
    rod(base, base + np.array([0, 0, 0.008]), r, GLASS_C, "cylinder")
    rod(base + np.array([0, 0, 0.008]), base + np.array([0, 0, h]), r, GLASS_C, "cylinder")
    rod(base + np.array([0, 0, 0.009]), base + np.array([0, 0, 0.008 + fill * h]), r - 0.003, WATER, "cylinder")


def table():
    t = TABLE
    hx, hy = t["half"]
    box((t["x"], t["y"], t["top"] - 0.015), (hx, hy, 0.015), WOOD)
    for sx in (1, -1):
        for sy in (1, -1):
            box((t["x"] + sx * (hx - 0.03), t["y"] + sy * (hy - 0.03), (t["top"] - 0.03) / 2), (0.02, 0.02, (t["top"] - 0.03) / 2), WOOD)
    top = t["top"]
    g = GLASS["at"]
    glass((t["x"] + 0.12, t["y"] + 0.28, top + GLASS["h"] / 2))                           # a second glass
    bottle = (t["x"] + 0.2, t["y"] + 0.12)
    rod((*bottle, top), (*bottle, top + 0.22), 0.04, (0.2, 0.45, 0.3, 0.55), "cylinder")
    rod((*bottle, top + 0.22), (*bottle, top + 0.3), 0.014, (0.2, 0.45, 0.3, 0.55), "cylinder")
    rod((g[0], g[1], top), (g[0], g[1], top + 0.004), 0.05, (0.75, 0.3, 0.25, 1), "cylinder")   # coaster under the held glass


def camera(name, pos, target):
    pos, target = np.array(pos, float), np.array(target, float)
    fwd = (target - pos) / np.linalg.norm(target - pos)
    x = np.cross(fwd, [0, 0, 1])
    x /= np.linalg.norm(x)
    y = np.cross(x, fwd)
    return f'<camera name="{name}" pos="{fmt(pos)}" xyaxes="{fmt(x)} {fmt(y)}"/>'


SCENE_CAMERAS = {
    "wall": {
        "oblique": camera("oblique", (1.75, -1.75, 1.35), (0.3, 0.05, 0.45)),
        "front": camera("front", (2.2, 0.35, 0.85), (0.3, 0.05, 0.45)),
        "elbow": camera("elbow", (0.85, -0.75, 1.15), (0.3, 0.1, 0.65)),
    },
    "glass": {
        "oblique": camera("oblique", (1.65, -1.55, 1.45), (0.35, 0.05, 0.8)),
        "close": camera("close", (0.95, -0.6, 1.12), (0.5, 0.1, 0.92)),
        "side": camera("side", (0.55, -1.75, 1.05), (0.45, 0.05, 0.82)),
    },
}


def main():
    args = sys.argv[1:]
    scene = "glass" if "glass" in args else "wall"
    layout = next((a for a in args if a in K.LAYOUTS), "biceps")
    K.set_layout(layout)
    if K.DOWN:
        K.S = np.array([0.0, 0.0, 1.15])         # upper arm hanging: shoulder higher, like a person at a table
    prefix = ("concept" if layout == "biceps" else layout) if scene == "wall" else (scene if layout == "biceps" else f"{scene}_{layout}")
    CAMERAS = SCENE_CAMERAS[scene]
    q = build(scene)
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
        path = os.path.join(OUT, f"render_{prefix}_{cam}.png")
        Image.fromarray(r.render()).save(path)
        print(path)
    r.close()
    print("pose (base yaw, shoulder pitch, shoulder roll, elbow pitch, forearm roll, wrist pitch):",
          " ".join(f"{a:.0f}°" for a in q))


if __name__ == "__main__":
    main()

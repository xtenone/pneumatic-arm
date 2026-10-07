"""Impression video: the light arm (upper arm hanging) makes a cocktail.

    python full-arm/cocktail.py            # out/video_cocktail.mp4 (not kept in git)
    python full-arm/cocktail.py --stills   # a few frames as PNG, to check the poses

Kinematic only (no physics, no liquid). The gripper follows key poses; every frame the arm
solves base yaw, shoulder pitch and elbow pitch (rolls at 0, elbow 10–120°); the wrist
motor keeps the tool horizontal and the gripper's own motor turns the bottle to pour.

Light variant: elbow cylinders Ø25 × 80 on a 5 cm lever behind the elbow, rear pivots
beside the upper arm 23 cm from the shoulder (nearly in at 10°, fully out at 120°);
wrist pitch and gripper rotation by small motors; jaws by a small cylinder.
"""
import math
import os
import sys

os.environ.setdefault("MUJOCO_GL", "egl")
import mujoco  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from scipy.optimize import least_squares  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import elbow as K  # noqa: E402

OUT = os.path.join(HERE, "out")
FPS = 30
S = np.array([0.12, 0.0, 1.28])               # shoulder joint, on the base yaw axis; high enough to keep the forearm above the table
K.S = S
TABLE_TOP, TABLE = 0.72, dict(x=(0.32, 1.16), y=(-0.7, 0.7))
GRIP = 0.11                                   # wrist → grasp centre
ELBOW_LEVER, ELBOW_SIDE, ELBOW_REAR = 0.05, 0.06, 0.229
SH_HUB, SH_SIDE = 0.15, 0.10
SH_LOW = (-0.30, -0.36)                       # shoulder cylinders' lower pivots, from the shoulder joint (on the column)
SH_CYL = (0.024, 0.26, 0.008)                 # body radius, body length, rod radius

ALU, STEEL, DARK = (0.80, 0.82, 0.85, 1), (0.45, 0.46, 0.50, 1), (0.15, 0.15, 0.17, 1)
RED, BLUE, WOOD, COLUMN = (0.75, 0.25, 0.2, 1), (0.2, 0.4, 0.75, 1), (0.55, 0.38, 0.22, 1), (0.35, 0.37, 0.40, 1)
GLASS_C = (0.85, 0.92, 1.0, 0.28)


def polar(r, deg, z=0.0):
    a = math.radians(deg)
    return np.array([r * math.cos(a), r * math.sin(a), z])


# --- objects on the table -----------------------------------------------------------
BOTTLES = [  # position, colour, liquid colour
    (polar(0.80, -30), (0.55, 0.32, 0.10, 0.6), (0.85, 0.55, 0.15, 0.7)),
    (polar(0.80, -55), (0.15, 0.40, 0.20, 0.6), (0.55, 0.75, 0.25, 0.7)),
    (polar(0.80, 36), (0.75, 0.80, 0.90, 0.45), (0.95, 0.35, 0.35, 0.7)),
]
BOTTLE = dict(r=0.038, h=0.22, neck_r=0.012, neck_h=0.08, grasp=0.15)
GLASS0 = polar(0.80, 2)
GLASS_END = polar(1.03, 2)
GLASS = dict(r=0.036, h=0.11, grasp=0.075)
JAR = polar(0.79, 18)
SPOON = dict(len=0.27, grasp=0.15)            # grasp height above the jar bottom


class World:
    """Object poses (position, tool-frame attachment) and the glass content."""

    def __init__(self):
        self.objs = {f"bottle_{i}": dict(pos=p + [0, 0, TABLE_TOP], R=np.eye(3)) for i, (p, _, _) in enumerate(BOTTLES)}
        self.objs["glass"] = dict(pos=GLASS0 + [0, 0, TABLE_TOP], R=np.eye(3))
        self.objs["spoon"] = dict(pos=JAR + [0, 0, TABLE_TOP + 0.01], R=np.eye(3))
        self.held = None                          # (name, R_rel, p_rel)
        self.fill = []                            # liquid layers in the glass: (height, colour)

    def grab(self, name, Rt, G):
        o = self.objs[name]
        self.held = (name, Rt.T @ o["R"], Rt.T @ (o["pos"] - G))

    def release(self):
        self.held = None

    def follow(self, Rt, G):
        if self.held:
            name, Rr, pr = self.held
            self.objs[name]["R"] = Rt @ Rr
            self.objs[name]["pos"] = G + Rt @ pr


# --- kinematics ---------------------------------------------------------------------
def tool(q, psi):
    yaw, p1, p2 = q
    p3 = math.pi / 2 - p1 - p2                    # tool horizontal, pointing outwards
    Ru, Rf, Rw, E, W = K.chain([yaw, p1, 0.0, p2, 0.0, p3])
    Rt = Rw @ K.Rz(psi)
    return Ru, Rf, Rw, Rt, E, W, W - GRIP * Rt[:, 2]


def solve(G, psi, q0):
    def res(x):
        return tool(x, psi)[6] - G
    s = least_squares(res, q0, bounds=([-3.2, -1.6, math.radians(10)], [3.2, 0.9, math.radians(120)]))
    return s.x, np.linalg.norm(res(s.x))


# --- drawing ------------------------------------------------------------------------
GEOMS = []


def fmt(v):
    return " ".join(f"{x:.4f}" for x in v)


def rod(a, b, r, rgba, kind="cylinder"):
    GEOMS.append(f'<geom type="{kind}" fromto="{fmt(a)} {fmt(b)}" size="{r}" rgba="{fmt(rgba)}"/>')


def box(c, half, rgba, R=np.eye(3)):
    GEOMS.append(f'<geom type="box" pos="{fmt(c)}" size="{fmt(half)}" xyaxes="{fmt(R[:, 0])} {fmt(R[:, 1])}" rgba="{fmt(rgba)}"/>')


def cyl(low, high, r_body, body_len, r_rod):
    d = (high - low) / np.linalg.norm(high - low)
    end = low + d * body_len
    rod(low - 0.012 * d, end, r_body, ALU)
    rod(end - 0.005 * d, end + 0.008 * d, r_body * 0.8, DARK)
    rod(end, high, r_rod, STEEL)


def draw_arm(q, psi, jaw):
    Ru, Rf, Rw, Rt, E, W, G = tool(q, psi)
    xu, yu, zu = Ru[:, 0], Ru[:, 1], Ru[:, 2]
    xf, yf = Rf[:, 0], Rf[:, 1]
    Rb = K.Rz(q[0])
    # base: yaw bearing under the shoulder joint; turntable with the column behind the shoulder,
    # an arm over the top to the shoulder joint, the shoulder cylinders' pivots on the column
    foot = np.array([S[0], S[1], 0.0])
    xc = SH_LOW[0]                                                     # column axis, from the shoulder
    box(foot + [0, 0, 0.02], (0.28, 0.28, 0.02), DARK)
    rod(foot + [0, 0, 0.04], foot + [0, 0, 0.09], 0.18, STEEL)
    box(foot + Rb @ np.array([xc / 2, 0.0, 0.10]), (-xc / 2 + 0.08, 0.10, 0.012), COLUMN, Rb)   # turntable
    col = foot + Rb @ np.array([xc, 0.0, 0.0])
    box(col + [0, 0, (S[2] + 0.187) / 2], (0.04, 0.04, (S[2] - 0.037) / 2), COLUMN, Rb)   # column, 80 × 80 tube
    box(S + Rb @ np.array([(xc + 0.01) / 2, 0.0, 0.06]), ((0.09 - xc) / 2, 0.075, 0.015), COLUMN, Rb)   # arm to the shoulder
    Sp = S                                                             # shoulder joint
    for s in (1, -1):
        box(Sp + Rb @ np.array([0, s * 0.065, 0.0]), (0.05, 0.01, 0.065), COLUMN, Rb)
    box(Sp, (0.04, 0.05, 0.04), RED, Ru)
    rod(Sp + 0.035 * xu, E - 0.035 * xu, 0.02, ALU, "capsule")
    # shoulder cylinders: pushing the hub from the column behind the shoulder (deltoid)
    hub = Sp + SH_HUB * xu
    rod(hub - 0.02 * xu, hub + 0.02 * xu, 0.032, ALU)
    rod(hub - (SH_SIDE + 0.025) * yu, hub + (SH_SIDE + 0.025) * yu, 0.009, STEEL)
    for s in (1, -1):
        low = Sp + Rb @ np.array([SH_LOW[0], s * SH_SIDE, SH_LOW[1]])
        rod(low, low - s * (SH_SIDE - 0.03) * Rb[:, 1], 0.012, STEEL)                     # pin through the column
        box(low, (0.018, 0.018, 0.018), BLUE, Rb)
        h = hub + s * SH_SIDE * yu
        box(h, (0.017, 0.017, 0.017), BLUE, Ru)
        cyl(low, h - 0.02 * (h - low) / np.linalg.norm(h - low), *SH_CYL)
    # elbow: yoke, forearm, lever behind the elbow, Ø25 cylinders beside the upper arm
    box(E, (0.03, 0.04, 0.03), RED, Rf)
    rod(E + 0.03 * xf, W - 0.03 * xf, 0.016, ALU, "capsule")
    lever = E - ELBOW_LEVER * xf
    rod(E, lever, 0.012, ALU)
    rod(lever - (ELBOW_SIDE + 0.02) * yf, lever + (ELBOW_SIDE + 0.02) * yf, 0.007, STEEL)
    rear = Sp + ELBOW_REAR * xu
    rod(rear - (ELBOW_SIDE + 0.02) * yu, rear + (ELBOW_SIDE + 0.02) * yu, 0.007, STEEL)
    for s in (1, -1):
        h, lo = lever + s * ELBOW_SIDE * yf, rear + s * ELBOW_SIDE * yu
        box(h, (0.012, 0.012, 0.012), BLUE, Rf)
        box(lo, (0.012, 0.012, 0.012), BLUE, Ru)
        cyl(lo, h - 0.015 * (h - lo) / np.linalg.norm(h - lo), 0.016, 0.17, 0.005)
    # wrist pitch motor, gripper rotation motor, gripper
    zt = Rt[:, 2]
    box(W, (0.028, 0.035, 0.028), DARK, Rw)
    rod(W - 0.025 * zt, W - 0.06 * zt, 0.024, DARK)
    draw_gripper(W - 0.07 * zt, Rt, jaw)
    return Rt, G


def draw_gripper(palm, Rt, jaw):
    zt, yt = Rt[:, 2], Rt[:, 1]
    box(palm, (0.02, 0.07, 0.012), ALU, Rt)
    for s in (1, -1):
        f = palm + s * (jaw / 2 + 0.006) * yt - 0.035 * zt
        box(f, (0.015, 0.006, 0.04), BLUE, Rt)


def draw_world(w):
    x0, x1 = TABLE["x"]
    y0, y1 = TABLE["y"]
    box(((x0 + x1) / 2, (y0 + y1) / 2, TABLE_TOP - 0.015), ((x1 - x0) / 2, (y1 - y0) / 2, 0.015), WOOD)
    for x in (x0 + 0.03, x1 - 0.03):
        for y in (y0 + 0.03, y1 - 0.03):
            box((x, y, (TABLE_TOP - 0.03) / 2), (0.02, 0.02, (TABLE_TOP - 0.03) / 2), WOOD)
    jar = JAR + [0, 0, TABLE_TOP]
    rod(jar, jar + [0, 0, 0.12], 0.035, (0.9, 0.9, 0.95, 0.3))
    for i, (_, colour, liquid) in enumerate(BOTTLES):
        o = w.objs[f"bottle_{i}"]
        ax = o["R"][:, 2]
        b = o["pos"]
        rod(b, b + BOTTLE["h"] * ax, BOTTLE["r"], colour)
        rod(b + 0.005 * ax, b + 0.15 * ax, BOTTLE["r"] - 0.003, liquid)
        rod(b + BOTTLE["h"] * ax, b + (BOTTLE["h"] + BOTTLE["neck_h"]) * ax, BOTTLE["neck_r"], colour)
    g = w.objs["glass"]
    b, ax = g["pos"], g["R"][:, 2]
    rod(b, b + 0.006 * ax, GLASS["r"], GLASS_C)
    rod(b + 0.006 * ax, b + GLASS["h"] * ax, GLASS["r"], GLASS_C)
    z = 0.007
    for hgt, colour in w.fill:
        rod(b + z * ax, b + (z + hgt) * ax, GLASS["r"] - 0.003, colour)
        z += hgt
    sp = w.objs["spoon"]
    b, ax = sp["pos"], sp["R"][:, 2]
    rod(b + 0.01 * ax, b + SPOON["len"] * ax, 0.003, STEEL)
    rod(b, b + 0.012 * ax, 0.009, STEEL)


# --- motion script ------------------------------------------------------------------
def smooth(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def radial(p):
    """Unit vector from the base towards p, horizontal."""
    v = np.array([p[0] - S[0], p[1] - S[1], 0.0])
    return v / np.linalg.norm(v)


def script(w):
    """Key poses: (duration s, grasp centre, gripper turn rad, jaw opening m, event)."""
    keys = []
    rest = np.array([0.78, 0.0, TABLE_TOP + 0.24])
    keys.append((1.0, rest, 0.0, 0.10, None))
    glass_c = GLASS0 + [0, 0, TABLE_TOP]
    for i, (pos, _, liquid) in enumerate(BOTTLES):
        base = pos + [0, 0, TABLE_TOP]
        grasp = base + [0, 0, BOTTLE["grasp"]]
        out = radial(base)
        pre = grasp - 0.08 * out
        lift = grasp + [0, 0, 0.09]
        back = lift - 0.06 * out
        # pour: bottle tilted sideways about the approach axis; mouth 4 cm above the glass centre
        side = 1 if base[1] < glass_c[1] else -1
        tilt = side * math.radians(118)
        mouth = (BOTTLE["h"] + BOTTLE["neck_h"]) - BOTTLE["grasp"]
        target_mouth = glass_c + [0, 0, GLASS["h"] + 0.045]
        G = target_mouth.copy()
        for _ in range(6):                        # the approach direction depends on where G is
            yaw = math.atan2(G[1] - S[1], G[0] - S[0])
            Rt = K.Rz(yaw) @ K.Ry(math.pi / 2) @ K.Rz(tilt)
            G = target_mouth - mouth * Rt[:, 0]
        pour_up = G + [0, 0, 0.05]
        sp = 0.85 if i else 1.0
        keys += [(1.4 * sp, pre, 0.0, 0.10, None), (0.7 * sp, grasp, 0.0, 0.10, None),
                 (0.3, grasp, 0.0, 2 * BOTTLE["r"], ("grab", f"bottle_{i}")),
                 (0.6 * sp, lift, 0.0, 2 * BOTTLE["r"], None), (0.7 * sp, back, 0.0, 2 * BOTTLE["r"], None),
                 (1.0 * sp, pour_up, 0.0, 2 * BOTTLE["r"], None), (0.9 * sp, G, tilt, 2 * BOTTLE["r"], None),
                 (1.0, G, tilt, 2 * BOTTLE["r"], ("pour", liquid)),
                 (0.7 * sp, pour_up, 0.0, 2 * BOTTLE["r"], None), (1.0 * sp, back, 0.0, 2 * BOTTLE["r"], None),
                 (0.7 * sp, lift, 0.0, 2 * BOTTLE["r"], None), (0.5 * sp, grasp, 0.0, 2 * BOTTLE["r"], None),
                 (0.3, grasp, 0.0, 0.10, ("release",)), (0.6 * sp, pre, 0.0, 0.10, None)]
    # stir with the bar spoon
    jar = JAR + [0, 0, TABLE_TOP + 0.01]
    s_grasp = jar + [0, 0, SPOON["grasp"]]
    out = radial(jar)
    s_pre, s_lift = s_grasp - 0.08 * out, s_grasp + [0, 0, 0.13]
    s_over = glass_c + [0, 0, SPOON["grasp"] + 0.13]
    s_in = glass_c + [0, 0, SPOON["grasp"] + 0.03]
    keys += [(1.2, s_pre, 0.0, 0.05, None), (0.6, s_grasp, 0.0, 0.05, None), (0.3, s_grasp, 0.0, 0.008, ("grab", "spoon")),
             (0.8, s_lift, 0.0, 0.008, None), (1.0, s_over, 0.0, 0.008, None), (0.8, s_in, 0.0, 0.008, None)]
    for k in range(1, 25):                        # three rounds
        a = 2 * math.pi * k / 8
        keys.append((0.1, s_in + 0.016 * np.array([math.cos(a) - 1, math.sin(a), 0]), 0.0, 0.008, None))
    keys += [(0.8, s_over, 0.0, 0.008, None), (1.0, s_lift, 0.0, 0.008, None), (0.8, s_grasp, 0.0, 0.008, None),
             (0.3, s_grasp, 0.0, 0.05, ("release",)), (0.6, s_pre, 0.0, 0.05, None)]
    # slide the glass forward
    g_grasp = glass_c + [0, 0, GLASS["grasp"]]
    out = radial(glass_c)
    g_pre = g_grasp - 0.06 * out
    g_end = GLASS_END + [0, 0, TABLE_TOP + GLASS["grasp"]]
    keys += [(1.0, g_pre, 0.0, 0.10, None), (0.6, g_grasp, 0.0, 0.10, None),
             (0.3, g_grasp, 0.0, 2 * GLASS["r"], ("grab", "glass")),
             (0.4, g_grasp + [0, 0, 0.01], 0.0, 2 * GLASS["r"], None),
             (2.2, g_end + [0, 0, 0.01], 0.0, 2 * GLASS["r"], None), (0.4, g_end, 0.0, 2 * GLASS["r"], None),
             (0.3, g_end, 0.0, 0.10, ("release",)), (0.8, g_end - 0.10 * out + [0, 0, 0.05], 0.0, 0.10, None),
             (1.5, rest, 0.0, 0.10, None), (1.0, rest, 0.0, 0.10, None)]
    return keys


def frames(w):
    keys = script(w)
    G, psi, jaw = keys[0][1], keys[0][2], keys[0][3]
    for dur, G1, psi1, jaw1, event in keys:
        n = max(1, int(round(dur * FPS)))
        d0, d1 = G[:2] - S[:2], G1[:2] - S[:2]
        r0, r1 = math.hypot(*d0), math.hypot(*d1)
        a0, a1 = math.atan2(d0[1], d0[0]), math.atan2(d1[1], d1[0])
        for k in range(1, n + 1):
            s = smooth(k / n)
            r, a = r0 + s * (r1 - r0), a0 + s * (a1 - a0)        # around the base, not straight past it
            P = np.array([S[0] + r * math.cos(a), S[1] + r * math.sin(a), G[2] + s * (G1[2] - G[2])])
            yield P, psi + s * (psi1 - psi), jaw + s * (jaw1 - jaw), (event if k == 1 else None), s
        G, psi, jaw = G1, psi1, jaw1


CAMS = {"main": ((1.75, -0.35, 1.45), (0.4, -0.05, 0.85)), "side": ((0.55, -1.9, 1.3), (0.45, 0.0, 0.9))}


def camera_xml():
    out = []
    for name, (pos, target) in CAMS.items():
        pos, target = np.array(pos), np.array(target)
        f = (target - pos) / np.linalg.norm(target - pos)
        x = np.cross(f, [0, 0, 1])
        x /= np.linalg.norm(x)
        y = np.cross(x, f)
        out.append(f'<camera name="{name}" pos="{fmt(pos)}" xyaxes="{fmt(x)} {fmt(y)}"/>')
    return "".join(out)


def render_frame(renderer_cache, cam="main"):
    xml = f"""<mujoco><visual><global offwidth="1280" offheight="720"/><quality shadowsize="4096"/>
<headlight ambient="0.35 0.35 0.35"/></visual>
<asset><texture type="skybox" builtin="gradient" rgb1="0.97 0.97 1" rgb2="0.72 0.76 0.84" width="256" height="256"/>
<texture name="grid" type="2d" builtin="checker" rgb1="0.90 0.90 0.90" rgb2="0.82 0.82 0.82" width="256" height="256"/>
<material name="floor" texture="grid" texrepeat="10 10"/></asset>
<worldbody><light pos="1.2 -1.2 2.6" dir="-0.4 0.4 -1" diffuse="0.75 0.75 0.75"/>
<geom type="plane" size="4 4 0.01" material="floor"/>{camera_xml()}{''.join(GEOMS)}</worldbody></mujoco>"""
    mdl = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(mdl)
    mujoco.mj_forward(mdl, d)
    r = mujoco.Renderer(mdl, 720, 1280)
    r.update_scene(d, camera=cam)
    img = r.render()
    r.close()
    return img


def check():
    """Reachability of every key pose (elbow 10–120°)."""
    w = World()
    q = np.array([0.0, -0.9, 1.3])
    for i, (dur, G, psi, jaw, event) in enumerate(script(w)):
        best = None
        for q0 in (q, np.array([math.atan2(G[1] - S[1], G[0] - S[0]), -0.9, 1.3]), np.array([math.atan2(G[1] - S[1], G[0] - S[0]), -0.4, 0.8])):
            x, err = solve(G, psi, q0)
            if best is None or err < best[1]:
                best = (x, err)
        q = best[0]
        if best[1] > 0.003:
            print(f"key {i}: G {np.round(G, 3)} unreachable by {best[1] * 1000:.0f} mm (dist from shoulder {np.linalg.norm(G - S):.2f} m)")
    print("check done")


def main():
    if "--check" in sys.argv:
        return check()
    stills = next((a for a in sys.argv if a.startswith("--stills")), None)
    at = [float(t) for t in stills.split("=")[1].split(",")] if stills and "=" in stills else None
    w = World()
    q = np.array([0.0, -0.9, 1.3])
    worst, writer, n = 0.0, None, 0
    if not stills:
        import imageio.v2 as imageio
        os.makedirs(OUT, exist_ok=True)
        writer = imageio.get_writer(os.path.join(OUT, "video_cocktail.mp4"), fps=FPS, codec="libx264", quality=8, macro_block_size=8)
    pour = None
    for G, psi, jaw, event, s in frames(w):
        q, err = solve(G, psi, q)
        worst = max(worst, err)
        GEOMS.clear()
        Rt, Gw = draw_arm(q, psi, jaw)
        if event and event[0] == "grab":
            w.grab(event[1], Rt, Gw)
        elif event and event[0] == "release":
            w.release()
        elif event and event[0] == "pour":
            w.fill.append([0.0, event[1]])
            pour = w.fill[-1]
        if pour is not None:
            pour[0] = min(0.026, pour[0] + 0.026 / FPS)
            if pour[0] >= 0.026:
                pour = None
        w.follow(Rt, Gw)
        draw_world(w)
        if stills:
            if (at is None and n % 90 == 0) or (at and any(abs(n / FPS - t) < 0.5 / FPS for t in at)):
                os.makedirs(OUT, exist_ok=True)
                Image.fromarray(render_frame(None, "main")).save(os.path.join(OUT, f"cocktail_{n / FPS:05.1f}s.png"))
        else:
            writer.append_data(render_frame(None, "main"))
        n += 1
    if writer:
        writer.close()
    print(f"{n} frames ({n / FPS:.1f} s); largest pose error {worst * 1000:.1f} mm")


if __name__ == "__main__":
    main()

"""Small wall (docs/small-wall.md): the light arm, a stack of wooden blocks and the place for
the row, as at the start of stage 1.

    python full-arm/small_wall.py           # out/small_wall_start_<camera>.png
    python full-arm/small_wall.py --check   # joint angles for every pick and place
    python full-arm/small_wall.py --video [--fast]   # stage 1a (controlled) or 1b (fast), MP4 not in git

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
STACK_N = 4
WALL_X = 0.65                                 # row along y (0.53 m in front of the yaw axis), starting against a strip at the -y end
WALL_Y = [-1.5 * (BLOCK[0] + GAP) + i * (BLOCK[0] + GAP) for i in range(4)]
GRIP_DEPTH = 0.020                            # grasp centre below the block's top (jaws on the top 40 mm)
OPEN, CLOSED = 0.095, 0.062               # jaw drawing: closed = pads touching the block
START = np.array([0.55, -0.30, TABLE_TOP + 0.28])

C.S[:] = [0.12, 0.0, TABLE_TOP + 0.66]         # shoulder 0.66 m above the table: elbow ≥ 12 cm above it
STACK = C.S * [1, 1, 0] + C.polar(0.58, -70)  # centre of the stack, from the yaw axis; blocks along x (turned 90° to the wall)
# light shoulder: 2 × Ø32 × 200 on a 100 mm hub (body about Ø40 over the profile)
C.SH_HUB, C.SH_LOW, C.SH_CYL = 0.10, (-0.22, -0.20), (0.020, 0.20, 0.006)
C.GRIP = 0.14                                 # wrist → grasp centre with the block gripper

LIGHT_WOOD, DARKER_WOOD, TAPE = (0.86, 0.72, 0.50, 1), (0.78, 0.62, 0.40, 1), (0.12, 0.12, 0.14, 1)


def tool(q, psi):
    """Gripper pointing straight down; psi turns it about the vertical."""
    yaw, p1, p2 = q
    Ru, Rf, Rw, E, W = K.chain([yaw, p1, 0.0, p2, 0.0, -p1 - p2])
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


def stack_blocks():
    """Start state: (centre, long-axis angle, colour) of every block, bottom of the stack first."""
    return [[STACK + [0, 0, TABLE_TOP + (i + 0.5) * BLOCK[2]], 0.0, LIGHT_WOOD if i % 2 else DARKER_WOOD]
            for i in range(STACK_N)]


def draw_scene(blocks=None):
    x0, x1 = C.TABLE["x"]
    y0, y1 = C.TABLE["y"]
    box(((x0 + x1) / 2, (y0 + y1) / 2, TABLE_TOP - 0.015), ((x1 - x0) / 2, (y1 - y0) / 2, 0.015), C.WOOD)
    for x in (x0 + 0.03, x1 - 0.03):
        for y in (y0 + 0.03, y1 - 0.03):
            box((x, y, (TABLE_TOP - 0.03) / 2), (0.02, 0.02, (TABLE_TOP - 0.03) / 2), C.WOOD)
    # stack in a corner jig (strips on the -y side and the +x side)
    for centre, along, colour in blocks or stack_blocks():
        block(centre, along, colour)
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


# --- stage 1 video -----------------------------------------------------------------
SPEEDS = {  # joint speed caps (°/s): base yaw, shoulder, elbow, gripper yaw; slowest move (s)
    "controlled": dict(caps=(30, 30, 50, 90), short=1.0, grip=0.6, settle=0.4),
    "fast": dict(caps=(90, 55, 115, 180), short=0.5, grip=0.3, settle=0.2),
}
UP = 0.08                                     # lift above the stack / the row


def keys():
    """(grasp centre, block angle, jaw, event, kind) for stage 1; kind = 'travel', 'short', 'grip' or 'wait'."""
    k = [(START, math.pi / 2, OPEN, None, "wait")]
    for i, (_, G_pick, a_pick) in enumerate(targets()[0::2]):
        G_place, a_place = targets()[2 * i + 1][1], targets()[2 * i + 1][2]
        k += [(G_pick + [0, 0, UP], a_pick, OPEN, None, "travel"),
              (G_pick, a_pick, OPEN, None, "short"),
              (G_pick, a_pick, CLOSED, ("grab", STACK_N - 1 - i), "grip"),
              (G_pick + [0, 0, UP], a_pick, CLOSED, None, "short"),
              (G_place + [0, 0, UP], a_place, CLOSED, None, "travel"),
              (G_place, a_place, CLOSED, None, "short"),
              (G_place, a_place, OPEN, ("release",), "grip"),
              (G_place + [0, 0, UP], a_place, OPEN, None, "short")]
    k.append((START, math.pi / 2, OPEN, None, "travel"))
    return k


def segments(mode):
    """The planned moves of stage 1: list of dicts with kind, event, duration, the joint
    angles per video frame (qs, first = start of the move), block angles a0/a1, jaw0/jaw1
    and the target grasp centre G."""
    sp = SPEEDS[mode]
    caps = np.radians(sp["caps"])
    k = keys()
    q = pose(k[0][0], k[0][1], np.array([-0.5, -1.2, 1.5]))[0]
    G, a, jaw = k[0][0], k[0][1], k[0][2]
    out = []
    for G1, a1, jaw1, event, kind in k[1:]:
        q1 = pose(G1, a1, q)[0]
        dq = np.abs(np.append(q1 - q, (a1 - q1[0]) - (a - q[0])))
        if kind == "grip":
            dur = sp["grip"]
        else:
            # cosine profile: peak speed = π/2 × mean speed
            dur = max(math.pi / 2 * float(np.max(dq / caps)), sp["short"] if kind == "short" else 0.6)
        n = max(1, int(round(dur * FPS)))
        d0, d1 = G[:2] - C.S[:2], G1[:2] - C.S[:2]     # around the yaw axis
        r0, r1 = math.hypot(*d0), math.hypot(*d1)
        b0, b1 = math.atan2(d0[1], d0[0]), math.atan2(d1[1], d1[0])
        qs = [q]
        for j in range(1, n + 1):
            u = C.smooth(j / n)
            r, b = r0 + u * (r1 - r0), b0 + u * (b1 - b0)
            P = np.array([C.S[0] + r * math.cos(b), C.S[1] + r * math.sin(b), G[2] + u * (G1[2] - G[2])])
            if kind == "travel":                  # lift first, lower last: arc over the table
                P[2] += 0.04 * math.sin(math.pi * u)
            q = pose(P, 0.0, q)[0]
            qs.append(q)
        out.append(dict(kind=kind, event=event, dur=n / FPS, qs=np.array(qs), a0=a, a1=a1,
                        jaw0=jaw, jaw1=jaw1, G=G1, settle=sp["settle"] if kind == "short" else 0.0))
        G, a, jaw = G1, a1, jaw1
    return out


def frames(mode):
    """Per frame: joints q, gripper yaw psi, jaw, event (at the end of a move)."""
    segs = segments(mode)
    q0, a = segs[0]["qs"][0], segs[0]["a0"]
    for _ in range(int(FPS * 0.8)):
        yield q0, a - q0[0], segs[0]["jaw0"], None
    for sg in segs:
        n = len(sg["qs"]) - 1
        for j in range(1, n + 1):
            u = C.smooth(j / n)
            q = sg["qs"][j]
            yield q, (sg["a0"] + u * (sg["a1"] - sg["a0"])) - q[0], sg["jaw0"] + u * (sg["jaw1"] - sg["jaw0"]), \
                (sg["event"] if j == n else None)
        for _ in range(int(round(sg["settle"] * FPS))):
            yield q, sg["a1"] - q[0], sg["jaw1"], None
    for _ in range(FPS):
        yield q, sg["a1"] - q[0], sg["jaw1"], None


def video(mode):
    import imageio.v2 as imageio
    from PIL import ImageDraw, ImageFont
    global FONT
    FONT = ImageFont.load_default(size=28)
    blocks = stack_blocks()
    held = None
    label = {"controlled": "Stage 1a: controlled (speeds of the heavy arm)", "fast": "Stage 1b: fast (light arm)"}[mode]
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"video_small_wall_{mode}.mp4")
    writer = imageio.get_writer(path, fps=FPS, codec="libx264", quality=8, macro_block_size=8)
    n, worst = 0, 0.0
    for q, psi, jaw, event in frames(mode):
        C.GEOMS.clear()
        Rt, G = C.draw_arm(q, psi, jaw)
        if held is not None:
            blocks[held][0] = G - (BLOCK[2] / 2 - GRIP_DEPTH) * Rt[:, 2]
            blocks[held][1] = math.atan2(Rt[1, 0], Rt[0, 0])
        if event and event[0] == "grab":
            held = event[1]
        elif event and event[0] == "release":
            held = None
        draw_scene(blocks)
        img = Image.fromarray(C.render_frame(None, "main"))
        d = ImageDraw.Draw(img)
        d.text((24, 20), f"{label}    t = {n / FPS:4.1f} s", fill=(30, 30, 30), font=FONT)
        writer.append_data(np.asarray(img))
        n += 1
    writer.close()
    print(f"{path}: {n} frames ({n / FPS:.1f} s)")


FPS = C.FPS
FONT = None
CAMS = {"main": ((1.05, -1.75, 1.55), (0.35, -0.2, 0.9)), "top": ((-0.25, -0.15, 2.5), (0.55, -0.15, 0.72)),
        "close": ((0.95, -0.80, 1.12), (0.52, -0.32, 0.95)),
        "side": ((-1.15, -1.95, 1.25), (0.15, -0.10, 0.80))}       # across the arm plane: column, arm, cylinders


def main():
    if "--check" in sys.argv:
        return check()
    C.CAMS = CAMS
    if "--video" in sys.argv:
        return video("fast" if "--fast" in sys.argv else "controlled")
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

"""Feasibility of the elbow as a 2-DOF joint (pitch + forearm roll), like the shoulder.

The forearm roll replaces a separate wrist rotation, as in a human forearm. The question:
with base yaw, shoulder pitch + roll, elbow pitch + roll and wrist pitch (6 DOF), can the
arm place a block level and lined up with the wall along the whole wall, and what do the
elbow cylinders then need (stroke, force)?

    python full-arm/elbow.py

Frames as in test 2: x forward, z up; joint rotation = Ry(pitch) · Rx(roll).
"""
import itertools
import math

import numpy as np
from scipy.optimize import least_squares

G = 9.81
S = np.array([0.0, 0.0, 0.8])                # shoulder
L1, L2 = 0.5, 0.5                            # upper arm, forearm
TOOL = 0.195                                 # wrist → block centre (gripper 0.12 + half block)
M_LOAD, M_FORE = 18.0, 1.5                   # block 15 kg + gripper 3 kg; forearm
WALL_X = 0.6                                 # low wall: 3 blocks wide, 3 courses
BLOCK_H = 0.15

# elbow cylinders (concept). Rear pivots on a post on top of the upper arm (clear of the
# shoulder hub and its cross blocks; for the triceps the post leans back over the shoulder
# yoke); the rod ends hold cross blocks on a hub on the forearm.
# biceps:  hub 12 cm in front of the elbow; the cylinders push to hold the load
# triceps: hub on a short lever 10 cm behind the elbow (the forearm shaft sticks out
#          through the elbow); the cylinders never cross the elbow
LAYOUTS = {
    "biceps": dict(low_along=0.06, low_side=0.06, low_up=0.12, hub_along=0.12, hub_side=0.09),
    "triceps": dict(low_along=0.02, low_side=0.08, low_up=0.13, hub_along=-0.10, hub_side=0.08),
    # arm turned over, like a human arm: upper arm hanging down, elbow below the shoulder,
    # cylinders behind the upper arm pushing the lever behind the elbow to lift
    # (compact Ø50 × 160 cylinders: rear pivots 15 cm from the shoulder, 6 cm behind the arm;
    #  elbow 60–110°, forearm roll ±15°)
    "triceps_down": dict(low_along=0.15, low_side=0.08, low_up=-0.06, hub_along=-0.12, hub_side=0.08, down=True,
                         body=0.20),
}
DOWN = False
LAYOUT = "biceps"
LOW_ALONG = LOW_SIDE = LOW_UP = HUB_ALONG = HUB_SIDE = 0.0


def set_layout(name, **override):
    """Select an elbow cylinder layout (module globals), optionally with changed values."""
    global LAYOUT, LOW_ALONG, LOW_SIDE, LOW_UP, HUB_ALONG, HUB_SIDE, DOWN
    v = dict(LAYOUTS[name], **override)
    LAYOUT = name
    DOWN = v.get("down", False)
    LOW_ALONG, LOW_SIDE, LOW_UP = v["low_along"], v["low_side"], v["low_up"]
    HUB_ALONG, HUB_SIDE = v["hub_along"], v["hub_side"]


set_layout("biceps")
WALL_Y = (-0.3, 0.0, 0.3)
COURSES = 3
BORE, ROD, P_BAR = 50.0, 20.0, 5.0
F_PUSH = P_BAR * 0.1 * math.pi * (BORE / 2) ** 2
F_PULL = P_BAR * 0.1 * math.pi * ((BORE / 2) ** 2 - (ROD / 2) ** 2)


def Rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])


def Ry(p):        # pitch up positive: x → (cos, 0, sin)
    c, s = math.cos(p), math.sin(p)
    return np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])


def Rx(r):
    c, s = math.cos(r), math.sin(r)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def chain(q):
    yaw, p1, r1, p2, r2, p3 = q
    Ru = Rz(yaw) @ Ry(p1) @ Rx(r1)
    Rf = Ru @ Ry(p2) @ Rx(r2)
    Rt = Rf @ Ry(p3)
    E = S + Ru @ np.array([L1, 0, 0])
    W = E + Rf @ np.array([L2, 0, 0])
    return Ru, Rf, Rt, E, W


def residual(q, block):
    _, _, Rt, _, W = chain(q)
    c = W + Rt @ np.array([0, 0, -TOOL])
    return np.concatenate([c - block, Rt[:2, 2], [Rt[0, 1]]])   # position, level, long side along the wall


def solve(block, roll_limit=1.6):
    """6-DOF pose for a block position, elbow above or below the shoulder (DOWN), smallest rolls."""
    yaw = math.atan2(block[1], block[0])
    best = None
    p1s, p2s, p2_lim = ((-0.8, -1.1, -1.4), (0.8, 1.3, 1.8), (0.0, 2.6)) if DOWN else ((0.3,), (-0.6, -1.0, -1.4), (-2.6, 0.0))
    for p1, p2, r1 in itertools.product(p1s, p2s, (-0.3, 0.0, 0.3)):
        q0 = [yaw, p1, r1, p2, 0.0, -(p1 + p2)]
        sol = least_squares(residual, q0, args=(block,), bounds=([-3, -1.7, -roll_limit, p2_lim[0], -roll_limit, -2.6],
                                                                [3, 1.4, roll_limit, p2_lim[1], roll_limit, 2.6]))
        if sol.cost < 1e-10:
            score = abs(sol.x[2]) + abs(sol.x[4])          # prefer small rolls
            if best is None or score < best[0]:
                best = (score, sol.x)
    return None if best is None else best[1]


def elbow_cylinders(q):
    """Pin-to-pin lengths and push forces (N, + = push) of the two elbow cylinders."""
    Ru, Rf, Rt, E, W = chain(q)
    xu, yu, zu = Ru[:, 0], Ru[:, 1], Ru[:, 2]
    xf, yf = Rf[:, 0], Rf[:, 1]
    lows = [S + LOW_ALONG * xu + s * LOW_SIDE * yu + LOW_UP * zu for s in (1, -1)]
    hinges = [E + HUB_ALONG * xf + s * HUB_SIDE * yf for s in (1, -1)]
    g = np.array([0, 0, -G])
    load = W + Rt @ np.array([0, 0, -TOOL])
    tau = np.cross(load - E, M_LOAD * g) + np.cross(E + 0.25 * xf - E, M_FORE * g)
    axes = [yu, xf]                                            # elbow pitch axis, forearm roll axis
    A = np.zeros((2, 2))
    lengths = []
    for k, (lo, h) in enumerate(zip(lows, hinges)):
        c = (h - lo) / np.linalg.norm(h - lo)
        lengths.append(float(np.linalg.norm(h - lo)))
        m = np.cross(h - E, c)
        A[:, k] = [m @ a for a in axes]
    forces = np.linalg.solve(A, [-(tau @ a) for a in axes])
    levers = [abs(A[0, k]) for k in range(2)]
    return lengths, forces, [tau @ a for a in axes], levers


def main():
    import sys
    if len(sys.argv) > 1:
        set_layout(sys.argv[1])
    print(f"layout: {LAYOUT}")
    rows, all_l = [], []
    print("block (y, course)  yaw   sh.pitch sh.roll  el.pitch el.roll  wr.pitch | cyl. length (mm)   force (N)     pitch/roll torque  lever")
    for course in range(COURSES):
        z = course * BLOCK_H + BLOCK_H / 2 + 0.012
        for y in WALL_Y:
            q = solve(np.array([WALL_X, y, z]))
            if q is None:
                print(f"y {y:+.1f} course {course}: no solution")
                continue
            L, F, tau, lev = elbow_cylinders(q)
            all_l += L
            rows.append((q, F))
            d = [math.degrees(a) for a in q]
            print(f"y {y:+.1f}, course {course}: {d[0]:5.0f} {d[1]:7.0f} {d[2]:7.0f} {d[3]:8.0f} {d[4]:7.0f} {d[5]:8.0f}  | "
                  f"{L[0] * 1000:4.0f} {L[1] * 1000:4.0f}   {F[0]:5.0f} {F[1]:5.0f}   {tau[0]:5.0f} {tau[1]:5.0f} Nm   {lev[0] * 1000:3.0f} {lev[1] * 1000:3.0f}")
    qs = np.array([r[0] for r in rows])
    fs = np.array([r[1] for r in rows])
    deg = np.degrees(qs)
    names = ["base yaw", "shoulder pitch", "shoulder roll", "elbow pitch", "forearm roll", "wrist pitch"]
    print()
    for i, n in enumerate(names):
        print(f"{n:15s} {deg[:, i].min():6.0f}° … {deg[:, i].max():5.0f}°")
    print(f"elbow cylinders: pin-to-pin {min(all_l) * 1000:.0f}–{max(all_l) * 1000:.0f} mm (stroke used {1000 * (max(all_l) - min(all_l)):.0f} mm)")
    pull = max(0.0, -fs.min())
    print(f"forces: push up to {max(0.0, fs.max()):.0f} N, pull up to {pull:.0f} N; Ø{BORE:.0f} at {P_BAR} bar: push {F_PUSH:.0f} N, pull {F_PULL:.0f} N "
          f"→ load {100 * max(max(0.0, fs.max()) / F_PUSH, pull / F_PULL):.0f}%")


if __name__ == "__main__":
    main()

"""Clash and stroke check of the elbow joint (biceps layout), CadQuery, in the upper-arm frame.

    python full-arm/elbow_cad.py              # table over elbow pitch × forearm roll
    python full-arm/elbow_cad.py --render     # also out/render_elbow_<pose>.png

Frame: origin at the shoulder, x along the upper arm, y to the side, z up (the shoulder
roll and pitch only move this frame as a whole). The elbow is at x = 500. The forearm
attitude is Ry(pitch) · Rx(roll), as in elbow.py. Lengths in mm.

Parts:
- upper arm tube Ø50 with the shoulder hub (bar and cross blocks of the shoulder cylinders)
- a post on top of the upper arm with a bar for the rear U-joints of the elbow cylinders
- elbow: fork on the upper arm, yoke turning on the pitch pin, forearm shaft through it (roll)
- forearm tube Ø40 with a hub: bar and cross blocks for the rod forks
- two cylinders (body, rod, rod fork)
"""
import math
import os
import sys

import cadquery as cq
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import elbow as K  # noqa: E402

L1 = K.L1 * 1000
ELBOW = np.array([L1, 0.0, 0.0])
LOW = np.array([K.LOW_ALONG * 1000, 0.0, K.LOW_UP * 1000])     # rear bar centre
LOW_SIDE, HUB_ALONG, HUB_SIDE = K.LOW_SIDE * 1000, K.HUB_ALONG * 1000, K.HUB_SIDE * 1000
SHOULDER_HUB, SHOULDER_BAR = 150.0, 120.0
BLOCK = 30.0                                  # cross blocks (elbow)
CYL = dict(bore=50, body_d=62.0, rod_d=20.0, stroke=200.0, dead=190.0)   # Ø50 ISO 15552 with clevises (estimate)
YOKE = dict(x=60.0, y=70.0, z=60.0)
FORK_GAP = YOKE["y"] + 2.0


def rot(pitch, roll):
    return K.Ry(math.radians(pitch)) @ K.Rx(math.radians(roll))


def cyl_between(a, b, r):
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    return cq.Workplane(cq.Plane(origin=tuple(a), xDir=_perp(d), normal=tuple(d))).circle(r).extrude(float(np.linalg.norm(d))).val()


def _perp(d):
    d = d / np.linalg.norm(d)
    t = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0, 0])
    p = np.cross(d, t)
    return tuple(p / np.linalg.norm(p))


def box(c, size, R=np.eye(3)):
    b = cq.Workplane("XY").box(*size).val()
    m = cq.Matrix([[R[0, 0], R[0, 1], R[0, 2], c[0]], [R[1, 0], R[1, 1], R[1, 2], c[1]], [R[2, 0], R[2, 1], R[2, 2], c[2]]])
    return b.transformGeometry(m)


def frame(x_dir, y_dir):
    x = x_dir / np.linalg.norm(x_dir)
    y = y_dir - (y_dir @ x) * x
    y /= np.linalg.norm(y)
    return np.column_stack([x, y, np.cross(x, y)])


# --- fixed to the upper arm ---------------------------------------------------------------
def upper_parts():
    p = {}
    p["upper_tube"] = cyl_between((40, 0, 0), (L1 - 60, 0, 0), 25)
    p["shoulder_hub"] = cyl_between((SHOULDER_HUB - 25, 0, 0), (SHOULDER_HUB + 25, 0, 0), 42).fuse(
        cyl_between((SHOULDER_HUB, -SHOULDER_BAR - 30, 0), (SHOULDER_HUB, SHOULDER_BAR + 30, 0), 12))
    for s in (1, -1):
        p[f"shoulder_block_{s}"] = box((SHOULDER_HUB, s * SHOULDER_BAR, 0), (44, 44, 44))
    p["post"] = cyl_between((LOW[0], 0, 0), LOW + np.array([0, 0, 12]), 14).fuse(
        cyl_between(LOW + np.array([0, -LOW_SIDE - 22, 0]), LOW + np.array([0, LOW_SIDE + 22, 0]), 10))
    t = 12.0
    for s in (1, -1):                         # elbow fork cheeks around the yoke
        y0 = s * (FORK_GAP / 2 + t / 2)
        cheek = box((L1 - 25, y0, 0), (50, t, 80)).fuse(cyl_between((L1, y0 - t / 2, 0), (L1, y0 + t / 2, 0), 40))
        p[f"fork_{s}"] = cheek
    return p


# --- moving with the forearm --------------------------------------------------------------
def forearm_parts(pitch, roll):
    R = rot(pitch, roll)
    Rp = rot(pitch, 0.0)
    p = {"yoke": box(ELBOW, (YOKE["x"], YOKE["y"], YOKE["z"]), Rp)}
    xf, yf = R[:, 0], R[:, 1]
    p["fore_tube"] = cyl_between(ELBOW + 30 * xf, ELBOW + 480 * xf, 20)
    hub = ELBOW + HUB_ALONG * xf
    p["fore_hub"] = cyl_between(hub - 20 * xf, hub + 20 * xf, 34).fuse(
        cyl_between(hub - (HUB_SIDE + BLOCK / 2 + 6) * yf, hub + (HUB_SIDE + BLOCK / 2 + 6) * yf, 10))
    for s in (1, -1):
        p[f"fore_block_{s}"] = box(hub + s * HUB_SIDE * yf, (BLOCK, BLOCK, BLOCK), frame(xf, yf))
    return p


def cylinders(pitch, roll):
    """Body, rod and rod fork of both cylinders; lengths."""
    R = rot(pitch, roll)
    xf, yf = R[:, 0], R[:, 1]
    hub = ELBOW + HUB_ALONG * xf
    p, lengths = {}, []
    for s in (1, -1):
        lo = LOW + np.array([0, s * LOW_SIDE, 0])
        h = hub + s * HUB_SIDE * yf
        c = (h - lo) / np.linalg.norm(h - lo)
        L = float(np.linalg.norm(h - lo))
        lengths.append(L)
        body_end = lo + (CYL["dead"] - 60 + CYL["stroke"] - 40) * c       # body stops short of the rod eye
        p[f"cyl_body_{s}"] = cyl_between(lo + 15 * c, body_end, CYL["body_d"] / 2)
        fork_base = h - (BLOCK / 2 + 14) * c
        p[f"cyl_rod_{s}"] = cyl_between(body_end, fork_base, CYL["rod_d"] / 2)
        j = np.cross(yf * s, c)
        j /= np.linalg.norm(j)
        Rc = frame(c, j)
        fork = box(fork_base + 3 * c, (6, BLOCK + 2 * 9, 22), Rc)
        for k in (1, -1):
            fork = fork.fuse(box(h + k * (BLOCK / 2 + 5) * j - 0 * c + 2 * c, (BLOCK + 22, 6, 22), Rc))
        p[f"cyl_fork_{s}"] = fork
        p[f"low_block_{s}"] = box(lo, (BLOCK, BLOCK, BLOCK), frame(c, np.array([0, 1.0, 0])))
    return p, lengths


PAIRS = [("cyl", "upper_tube"), ("cyl", "shoulder"), ("cyl", "fork"), ("cyl", "yoke"), ("cyl", "fore_tube"),
         ("cyl", "fore_hub"), ("cyl_body_1", "cyl_body_-1"), ("cyl_rod", "fore_block"), ("fore", "fork"),
         ("fore_block", "upper_tube"), ("fore_hub", "upper_tube"), ("fore_tube", "upper_tube"),
         ("low_block", "cyl_rod"), ("cyl_fork", "fore_tube")]


def check(pitch, roll, upper=None):
    upper = upper or upper_parts()
    parts = dict(upper)
    parts.update(forearm_parts(pitch, roll))
    cyl, lengths = cylinders(pitch, roll)
    parts.update(cyl)
    found = set()
    for a, b in PAIRS:
        for na, sa in parts.items():
            for nb, sb in parts.items():
                if na != nb and na.startswith(a) and nb.startswith(b):
                    key = tuple(sorted((na, nb)))
                    if key in found:
                        continue
                    if sa.intersect(sb).Volume() > 1.0:
                        found.add(key)
    return sorted(f"{a}/{b}" for a, b in found), lengths


def main():
    lo, hi = CYL["dead"] + CYL["stroke"], CYL["dead"] + 2 * CYL["stroke"]       # pin to pin, retracted / extended
    print(f"elbow cylinders Ø{CYL['bore']} × {CYL['stroke']:.0f}: pin-to-pin {lo:.0f}–{hi:.0f} mm (dead length estimated), "
          f"rear pivots {LOW[0]:.0f} mm along and {LOW[2]:.0f} mm above the upper arm")
    upper = upper_parts()
    pitches = [int(a) for a in sys.argv[1].split(",")] if len(sys.argv) > 1 and sys.argv[1][0] in "-0123456789" else (-120, -105, -90, -75, -60, -45, -30)
    for pitch in pitches:
        row = []
        for roll in (-65, -45, 0, 45, 65):
            clash, L = check(pitch, roll, upper)
            ok_len = all(lo + 2 <= x <= hi - 2 for x in L)
            tag = "ok" if not clash and ok_len else ("LEN " if not ok_len else "") + ",".join(c.replace("cyl_", "") for c in clash)
            row.append(f"{roll:+d}: {tag} [{min(L):.0f}-{max(L):.0f}]")
        print(f"pitch {pitch:4d}: " + " | ".join(row))


if __name__ == "__main__":
    main()

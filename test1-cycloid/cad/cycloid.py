"""Printed cycloidal drive (CadQuery). Axis = z, z = 0 on the rear face, output towards +z.

    python cad/cycloid.py            # sizes and a clash check over one input turn
    python cad/cycloid.py --stl      # STL of the printed parts in out/stl/

placements(phi) gives every part's position for input angle phi (radians), so renders and
videos move the parts without rebuilding them.
"""
import math
import os
import sys

import cadquery as cq
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import cyparams as P  # noqa: E402

Z = P.z_stack()
B = P.BEARINGS
OUT = os.path.join(os.path.dirname(HERE), "out")


# --- helpers --------------------------------------------------------------------------
def cyl(r, z0, z1, x=0.0, y=0.0):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(r).extrude(z1 - z0)


def ring(r_in, r_out, z0, z1):
    return cyl(r_out, z0, z1).cut(cyl(r_in, z0 - 1, z1 + 1))


def polar(n, r, a0=0.0):
    return [(r * math.cos(a0 + 2 * math.pi * i / n), r * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


def holes(shape, pts, d, z0, z1):
    for x, y in pts:
        shape = shape.cut(cyl(d / 2, z0, z1, x, y))
    return shape


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def place(shape, R, t):
    m = cq.Matrix([[R[0, 0], R[0, 1], R[0, 2], t[0]],
                   [R[1, 0], R[1, 1], R[1, 2], t[1]],
                   [R[2, 0], R[2, 1], R[2, 2], t[2]]])
    return shape.transformGeometry(m)


# --- cycloid profile ------------------------------------------------------------------
def profile(n=1200):
    """Disc outline around its own centre, for the disc whose centre sits at +E on x
    when the input angle is 0. The pin radius is enlarged by the print clearance."""
    R, rp, E, N = P.R_PINS, P.D_PIN / 2 + P.CLEARANCE, P.E, P.N_PINS
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    psi = np.arctan2(np.sin((1 - N) * t), R / (E * N) - np.cos((1 - N) * t))
    x = R * np.cos(t) - rp * np.cos(t + psi) - E * np.cos(N * t)
    y = -R * np.sin(t) + rp * np.sin(t + psi) + E * np.sin(N * t)
    return list(zip(x[::-1], y[::-1]))            # counter-clockwise


# --- printed parts (own frame, z as in the assembly) ----------------------------------
def disc(k):
    """Disc k (0 or 1). Disc 1 runs half a lobe behind disc 0, so its output holes are
    turned half a lobe forward relative to its profile; both are printed separately."""
    d = cq.Workplane("XY").polyline(profile()).close().extrude(P.DISC_T)
    d = d.cut(cyl(B["6804"][1] / 2 + 0.05, -1, P.DISC_T + 1))
    return holes(d, polar(P.N_OUT, P.R_OUT, k * math.pi / P.RATIO), P.OUT_HOLE, -1, P.DISC_T + 1)


def housing():
    """Rear plate and ring in one print (a cup); the pins lie against the ring bore."""
    z0, z1 = Z["rear_plate"][0], Z["cavity"][1]
    h = cyl(P.HOUSING_R, z0, z1).cut(cyl(P.RING_BORE_R, P.PLATE_T, z1 + 1))
    h = h.cut(cyl(B["6808"][1] / 2, -1, B["6808"][2]))                 # bearing seat from the rear
    h = h.cut(cyl(B["6808"][1] / 2 - 4, -1, P.PLATE_T + 1))            # shoulder
    h = holes(h, polar(P.N_PINS, P.R_PINS), P.D_PIN + 0.1, P.PLATE_T - P.PIN_HOLE_DEPTH, P.PLATE_T + 1)
    h = holes(h, polar(6, P.BOLT_R, math.pi / 6), 4.4, -1, z1 + 1)
    m = 47.14 / 2                                                       # NEMA23 bolt square
    return holes(h, [(m, m), (-m, m), (-m, -m), (m, -m)], 5.2, -1, P.PLATE_T + 1)


def cover():
    z0, z1 = Z["front_plate"]
    c = cyl(P.HOUSING_R, z0, z1)
    c = c.cut(cyl(B["6808"][1] / 2, z1 - B["6808"][2], z1 + 1))
    c = c.cut(cyl(B["6808"][1] / 2 - 4, z0 - 1, z1 + 1))
    c = holes(c, polar(P.N_PINS, P.R_PINS), P.D_PIN + 0.1, z0 - 1, z0 + P.PIN_HOLE_DEPTH)
    return holes(c, polar(6, P.BOLT_R, math.pi / 6), 4.4, z0 - 1, z1 + 1)


def carrier_rear():
    f0, f1 = Z["rear_flange"]
    c = cyl(P.FLANGE_R, f0, f1).union(cyl(P.JOURNAL_D / 2, 0.0, f0 + 0.1))
    c = c.cut(cyl(B["608"][1] / 2, -1, B["608"][2])).cut(cyl(P.SHAFT_D / 2 + 0.3, -1, f1 + 1))
    return holes(c, polar(P.N_OUT, P.R_OUT), P.D_OUT, f1 - P.OUT_HOLE_DEPTH, f1 + 1)


def carrier_front():
    f0, f1 = Z["front_flange"]
    top = Z["front_plate"][1] + P.OUTPUT_EXT
    c = cyl(P.FLANGE_R, f0, f1).union(cyl(P.JOURNAL_D / 2, f1 - 0.1, top))
    c = c.cut(cyl(B["608"][1] / 2, f0 - 1, f0 + B["608"][2]))
    c = holes(c, polar(P.N_OUT, P.R_OUT), P.D_OUT, f0 - 1, f0 + P.OUT_HOLE_DEPTH)
    return holes(c, polar(4, 14.0, math.pi / 4), 3.4, top - 10, top + 1)   # output: 4 × M4 (tap or insert)


def cam():
    """Double eccentric on the input shaft (+E for disc 0, −E for disc 1)."""
    z0, z_mid, z1 = Z["disc_0"][0], (Z["disc_0"][1] + Z["disc_1"][0]) / 2, Z["disc_1"][1]
    r = B["6804"][0] / 2
    c = cyl(r, z0, z_mid, P.E, 0).union(cyl(r, z_mid, z1, -P.E, 0))
    return c.cut(cyl(P.SHAFT_D / 2 + 0.1, z0 - 1, z1 + 1))


def standoff():
    return ring(2.6, 5.0, -P.MOTOR_GAP, 0.0)


# --- bought parts ---------------------------------------------------------------------
def bearing(name, z0):
    i, o, w = B[name]
    return ring(i / 2, o / 2, z0, z0 + w)


def pin(z0, length, d):
    return cyl(d / 2, z0, z0 + length)


def shaft():
    return cyl(P.SHAFT_D / 2, -P.COUPLING["length"] / 2 - 2, Z["front_flange"][0] + B["608"][2])


def coupling():
    return cyl(P.COUPLING["d"] / 2, -2 - P.COUPLING["length"], -2)


def motor():
    body = (cq.Workplane("XY").workplane(offset=-P.MOTOR_GAP - 96).rect(56.4, 56.4).extrude(96)
            .edges("|Z").fillet(4))
    boss = cyl(19.05, -P.MOTOR_GAP, -P.MOTOR_GAP + 1.6)
    return body.union(boss).union(cyl(4, -P.MOTOR_GAP, -P.MOTOR_GAP + 21))


# --- assembly -------------------------------------------------------------------------
PLA_A, PLA_B, PLA_C, PLA_D = (0.95, 0.55, 0.15, 1), (0.98, 0.80, 0.20, 1), (0.30, 0.55, 0.85, 1), (0.35, 0.72, 0.35, 1)
GREY, STEEL, DARK = (0.80, 0.80, 0.82, 1), (0.55, 0.56, 0.60, 1), (0.18, 0.18, 0.20, 1)


def shapes():
    s = {"disc_0": disc(0), "disc_1": disc(1), "housing": housing(), "cover": cover(),
         "carrier_rear": carrier_rear(), "carrier_front": carrier_front(), "cam": cam(),
         "standoff": standoff(), "shaft": shaft(), "coupling": coupling(), "motor": motor(),
         "bearing_6808_rear": bearing("6808", 0.0),
         "bearing_6808_front": bearing("6808", Z["front_plate"][1] - B["6808"][2]),
         "bearing_608_rear": bearing("608", 0.0),
         "bearing_608_front": bearing("608", Z["front_flange"][0]),
         "housing_pin": pin((Z["cavity"][0] + Z["cavity"][1] - P.PIN_LEN) / 2, P.PIN_LEN, P.D_PIN),
         "output_pin": pin((Z["rear_flange"][1] + Z["front_flange"][0] - P.OUT_PIN_LEN) / 2, P.OUT_PIN_LEN, P.D_OUT)}
    for k in (0, 1):
        z0 = Z[f"disc_{k}"][0] + (P.DISC_T - B["6804"][2]) / 2
        s[f"bearing_6804_{k}"] = bearing("6804", z0).translate((0, 0, 0))
    return {k: (v.val() if hasattr(v, "val") else v) for k, v in s.items()}


def placements(phi=0.0):
    """[(name, shape name, R, t, rgba)] for input angle phi (radians)."""
    I, O = np.eye(3), np.zeros(3)
    out_rot = rot_z(-phi / P.RATIO)
    out = [("housing", "housing", I, O, (0.85, 0.85, 0.87, 1)), ("cover", "cover", I, O, (0.85, 0.85, 0.87, 1)),
           ("motor", "motor", I, O, DARK), ("bearing_6808_rear", "bearing_6808_rear", I, O, STEEL),
           ("bearing_6808_front", "bearing_6808_front", I, O, STEEL)]
    m = 47.14 / 2
    for i, (x, y) in enumerate([(m, m), (-m, m), (-m, -m), (m, -m)]):
        out.append((f"standoff_{i}", "standoff", I, np.array([x, y, 0.0]), PLA_C))
    for i, (x, y) in enumerate(polar(P.N_PINS, P.R_PINS)):
        out.append((f"housing_pin_{i}", "housing_pin", I, np.array([x, y, 0.0]), STEEL))
    for name in ("shaft", "coupling", "cam"):
        out.append((name, name, rot_z(phi), O, STEEL if name != "cam" else PLA_D))
    for name in ("carrier_rear", "carrier_front", "bearing_608_rear", "bearing_608_front"):
        out.append((name, name, out_rot, O, PLA_C if name.startswith("carrier") else STEEL))
    for i, (x, y) in enumerate(polar(P.N_OUT, P.R_OUT)):
        out.append((f"output_pin_{i}", "output_pin", I, out_rot @ np.array([x, y, 0.0]), STEEL))
    for k, colour in ((0, PLA_A), (1, PLA_B)):
        a = phi + k * math.pi
        centre = np.array([P.E * math.cos(a), P.E * math.sin(a), 0.0])
        R = rot_z(-phi / P.RATIO - k * math.pi / P.RATIO)
        out.append((f"disc_{k}", f"disc_{k}", R, centre + np.array([0, 0, Z[f"disc_{k}"][0]]), colour))
        out.append((f"bearing_6804_{k}", f"bearing_6804_{k}", I, centre, STEEL))
    return out


_SHAPES = {}


def pose(phi=0.0):
    if not _SHAPES:
        _SHAPES.update(shapes())
    return [(n, place(_SHAPES[k], R, t), rgba) for n, k, R, t, rgba in placements(phi)]


def clashes(phi, min_volume=0.5):
    items = {n: s for n, s, _ in pose(phi)}
    pairs = [("disc", "housing_pin"), ("disc", "output_pin"), ("disc", "carrier"), ("disc", "housing"),
             ("carrier", "housing"), ("carrier", "cover"), ("cam", "carrier"), ("disc_0", "disc_1")]
    found = []
    for a, b in pairs:
        for na, sa in items.items():
            for nb, sb in items.items():
                if na.startswith(a) and nb.startswith(b) and na != nb:
                    v = sa.intersect(sb).Volume()
                    if v > min_volume:
                        found.append(f"{na}/{nb} {v:.1f}")
    return sorted(set(found))


if __name__ == "__main__":
    if "--stl" in sys.argv:
        os.makedirs(os.path.join(OUT, "stl"), exist_ok=True)
        s = shapes()
        for name in ("disc_0", "disc_1", "housing", "cover", "carrier_rear", "carrier_front", "cam", "standoff"):
            path = os.path.join(OUT, "stl", f"{name}.stl")
            cq.exporters.export(cq.Workplane().add(s[name]), path, tolerance=0.02, angularTolerance=0.05)
            print(path)
    else:
        for deg in (0, 45, 90, 135, 180):
            c = clashes(math.radians(deg))
            print(f"input {deg:3d}°: {', '.join(c) if c else 'no clash'}")

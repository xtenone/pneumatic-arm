"""CadQuery concept model of test 2 (concept B): universal joint, hub with two hinged
bars, vertical cylinders with sliding sleeves.

pose(pitch, roll) returns the parts placed for one arm attitude (degrees).
"""
import math
import os
import sys

import cadquery as cq
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "test1", "cad"))
import t2params as P  # noqa: E402
import parts as T1parts  # noqa: E402

T1 = P.T1


def rot_matrix(pitch, roll):
    """Arm attitude: roll about the arm's x axis, then pitch up about y."""
    p, r = math.radians(pitch), math.radians(roll)
    Ry = np.array([[math.cos(p), 0, -math.sin(p)], [0, 1, 0], [math.sin(p), 0, math.cos(p)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(r), -math.sin(r)], [0, math.sin(r), math.cos(r)]])
    return Ry @ Rx


def hinge_points(pitch, roll):
    """World positions of the two bar hinges on the hub (left, right)."""
    R = rot_matrix(pitch, roll)
    J = np.array(P.JOINT)
    return [J + R @ np.array([P.HUB_X, s * P.HUB_R, 0.0]) for s in (1, -1)]


def sleeve_points(pitch, roll):
    """Where each bar passes through its cylinder sleeve: same x and z as the hinge
    (the bar is horizontal, along y), at y = ±BAR_Y."""
    return [np.array([h[0], s * P.BAR_Y, h[2]]) for h, s in zip(hinge_points(pitch, roll), (1, -1))]


def lower_points():
    x, z = P.LOWER_PIVOT
    return [np.array([x, s * P.BAR_Y, z]) for s in (1, -1)]


def cylinder_lengths(pitch, roll):
    return [float(np.linalg.norm(a - b)) for a, b in zip(sleeve_points(pitch, roll), lower_points())]


def bar_reach_ok(pitch, roll):
    """The bar must still pass through the sleeve: |sleeve y − hinge y| ≤ bar length − margin."""
    return all(abs(s[1] - h[1]) <= P.BAR_LENGTH - P.SLEEVE["length"] / 2
               for s, h in zip(sleeve_points(pitch, roll), hinge_points(pitch, roll)))


def place(shape, R, t):
    m = cq.Matrix([[R[0, 0], R[0, 1], R[0, 2], t[0]],
                   [R[1, 0], R[1, 1], R[1, 2], t[1]],
                   [R[2, 0], R[2, 1], R[2, 2], t[2]]])
    return shape.val().transformGeometry(m) if hasattr(shape, "val") else shape.transformGeometry(m)


def align_x_to(u):
    """Rotation matrix mapping +x onto u, with local y kept along world y where possible."""
    x = u / np.linalg.norm(u)
    y0 = np.array([0.0, 1.0, 0.0])
    z = np.cross(x, y0)
    if np.linalg.norm(z) < 1e-6:
        z = np.array([0.0, 0.0, 1.0])
    z /= np.linalg.norm(z)
    y = np.cross(z, x)
    return np.column_stack([x, y, z])


# --- parts -----------------------------------------------------------------------
def yoke():
    w, h, d = P.YOKE["width"], P.YOKE["height"], P.YOKE["depth"]
    y = cq.Workplane("XY").box(d, w, h)
    y = y.cut(cq.Workplane("XZ").circle(4.25).extrude(w, both=True))
    y = y.cut(cq.Workplane("YZ").circle(P.ROLL_SHAFT_D / 2 + 0.5).extrude(d, both=True))
    return y


def arm():
    """Arm in its own frame: roll axis along +x through the joint centre (origin)."""
    L = P.ARM_LENGTH
    shaft = cq.Workplane("YZ").circle(P.ROLL_SHAFT_D / 2).extrude(P.YOKE["depth"] + 40).translate((-P.YOKE["depth"] / 2 - 8, 0, 0))
    tube = cq.Workplane("YZ").circle(12).circle(9).extrude(L - 40).translate((40, 0, 0))
    hub = cq.Workplane("YZ").circle(P.HUB_R + 8).extrude(16).translate((P.HUB_X - 8, 0, 0))
    lugs = None
    for s in (1, -1):
        lug = (cq.Workplane("XY").box(16, 14, 14).translate((P.HUB_X, s * P.HUB_R, 0))
               .union(cq.Workplane("YZ").circle(3).extrude(24).translate((P.HUB_X - 12, s * P.HUB_R, 0))))
        lugs = lug if lugs is None else lugs.union(lug)
    return shaft.union(tube).union(hub).union(lugs)


def bar(side):
    """Horizontal bar along ±y, hinge eye at the origin (on the hub hinge)."""
    eye = cq.Workplane("YZ").circle(7).circle(3.2).extrude(8, both=True)
    rod = cq.Workplane("XZ").circle(P.BAR_D / 2).extrude(-side * P.BAR_LENGTH)
    return eye.union(rod)


def sleeve():
    """Sleeve block on the cylinder rod end; the bar runs through along y."""
    s = cq.Workplane("XZ").circle(P.SLEEVE["outer"] / 2).circle(P.BAR_D / 2 + 0.3).extrude(P.SLEEVE["length"] / 2, both=True)
    neck = cq.Workplane("XY").circle(6).extrude(16).translate((0, 0, -P.SLEEVE["outer"] / 2 - 14))
    return s.union(neck)


def lower_bracket(side):
    """Clevis on the base plate: the cylinder tilts about y."""
    x, z = P.LOWER_PIVOT
    base = cq.Workplane("XY").box(50, 40, 6).translate((x, side * P.BAR_Y, 3))
    cheeks = None
    for k in (1, -1):
        c = cq.Workplane("XY").box(30, 5, z + 10).translate((x, side * P.BAR_Y + k * 14, (z + 10) / 2))
        cheeks = c if cheeks is None else cheeks.union(c)
    pin = cq.Workplane("XZ").circle(4).extrude(20, both=True).translate((x, side * P.BAR_Y, z))
    return base.union(cheeks).union(pin)


def pose(pitch=0.0, roll=0.0):
    """Assembly (list of (name, shape, rgba)) for one arm attitude, plus cylinder lengths."""
    wood = (0.82, 0.68, 0.47, 1)
    alu = (0.75, 0.77, 0.80, 1)
    steel = (0.45, 0.45, 0.48, 1)
    red = (0.75, 0.25, 0.2, 1)
    blue = (0.2, 0.4, 0.75, 1)
    items = [
        ("base_plate", T1parts.base_plate().val(), wood),
        ("cheek_left", T1parts.cheek().translate((0, T1.CHEEK_GAP / 2, 0)).val(), wood),
        ("cheek_right", T1parts.cheek().mirror("XZ").translate((0, -T1.CHEEK_GAP / 2, 0)).val(), wood),
        ("spacer_block", T1parts.spacer_block().val(), wood),
    ]
    J = np.array(P.JOINT)
    items.append(("yoke", place(yoke(), rot_matrix(pitch, 0.0), J), red))
    items.append(("arm", place(arm(), rot_matrix(pitch, roll), J), alu))
    lengths = []
    for i, (side, h, s, low) in enumerate(zip((1, -1), hinge_points(pitch, roll),
                                              sleeve_points(pitch, roll), lower_points())):
        # bar: horizontal along y through the hinge; it only tilts with the pitch about its own axis
        Rb = rot_matrix(pitch, 0.0)
        items.append((f"bar_{i}", place(bar(side), Rb, h), steel))
        items.append((f"lower_bracket_{i}", lower_bracket(side).val(), alu))
        u = s - low
        L = float(np.linalg.norm(u))
        lengths.append(L)
        ext = max(0.0, min(P.CYL["stroke"], L - P.PIN_TO_PIN_MIN))
        Rc = align_x_to(u)
        items.append((f"cylinder_{i}", place(T1parts.cylinder_body(), Rc, low), alu))
        rod = T1parts.rod_assembly().translate((ext, 0, 0))
        items.append((f"rod_{i}", place(rod, Rc, low), steel))
        # sleeve at the top, local z along the cylinder axis
        Rs = Rc @ np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])
        items.append((f"sleeve_{i}", place(sleeve(), Rs, s), blue))
    return items, lengths


if __name__ == "__main__":
    lo, hi = P.PIN_TO_PIN_MIN, P.PIN_TO_PIN_MAX
    print(f"cylinder pin-to-pin range {lo:.0f}–{hi:.0f} mm")
    for p in range(-40, 41, 10):
        rs = [r for r in range(0, 91, 5)
              if all(lo + 2 <= L <= hi - 2 for L in cylinder_lengths(p, r) + cylinder_lengths(p, -r))
              and bar_reach_ok(p, r) and bar_reach_ok(p, -r)]
        print(f"pitch {p:4d}°: roll ±{max(rs) if rs else '—'}°   L at roll 0: {[round(x) for x in cylinder_lengths(p, 0)]}")

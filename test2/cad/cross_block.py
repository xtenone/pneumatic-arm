"""Variant of concept B: the bar is fixed to the hub and a cross block turns on it at a
fixed spot; a pin square to the bar carries the fork on the cylinder rod. Together this is
a small universal joint whose centre lies on the bar axis, so the cylinder force passes
through it and the rod carries no bending. Nothing slides; the cylinders tilt a few
degrees sideways when rolling, so the bottom is a second small universal joint: the rear eye
sits on a pin along y in a fork, and that fork swings on a bolt along x below it.

pose(pitch, roll) returns the parts placed for one arm attitude (degrees), like model.pose.
"""
import math

import cadquery as cq
import numpy as np

import model as M
from model import P, T1

C = P.CROSS
R_HUB = C["hub_r"]
B = C["block"]
LOW_D = C["low_drop"]          # x bolt this far below the rear pin


def arm_axis(pitch):
    return M.rot_matrix(pitch, 0.0) @ np.array([1.0, 0.0, 0.0])


def hinge_points(pitch, roll):
    """Cross block centres (left, right)."""
    R = M.rot_matrix(pitch, roll)
    J = np.array(P.JOINT)
    return [J + R @ np.array([P.HUB_X, s * R_HUB, 0.0]) for s in (1, -1)]


def lower_points():
    """Rear pin centres with the bottom fork upright (left, right)."""
    x, z = C["lower_pivot"]
    return [np.array([x, s * R_HUB, z]) for s in (1, -1)]


def lower_bolts():
    """Centres of the x bolts the bottom forks swing on."""
    return [p - np.array([0.0, 0.0, LOW_D]) for p in lower_points()]


def fork_tilt(h, q):
    """Sideways swing of the bottom fork about its x bolt (radians, + towards +y): the fork
    lines up with the cylinder seen from the front, because the eye cannot turn about x."""
    return math.atan2(h[1] - q[1], h[2] - q[2])


def lower_pins(pitch, roll):
    """Rear pin centres for this pose (the fork has swung a little sideways)."""
    out = []
    for h, q in zip(hinge_points(pitch, roll), lower_bolts()):
        b = fork_tilt(h, q)
        out.append(q + LOW_D * np.array([0.0, math.sin(b), math.cos(b)]))
    return out


def cylinder_lengths(pitch, roll):
    return [float(np.linalg.norm(h - b)) for h, b in zip(hinge_points(pitch, roll), lower_pins(pitch, roll))]


def reachable(pitch, roll):
    lo, hi = P.PIN_TO_PIN_MIN, P.PIN_TO_PIN_MAX
    return all(lo + 2 <= L <= hi - 2 for L in cylinder_lengths(pitch, roll))


def bottom_angles(pitch, roll):
    """Angles at the bottom joint (degrees, both cylinders): (forward/back about the y pin,
    sideways about the x bolt), measured from upright."""
    out = []
    for h, q, p in zip(hinge_points(pitch, roll), lower_bolts(), lower_pins(pitch, roll)):
        u = h - p
        fwd = math.degrees(math.atan2(u[0], math.hypot(u[1], u[2])))
        out.append((fwd, math.degrees(fork_tilt(h, q))))
    return out


def side_tilt(pitch, roll):
    """Largest sideways tilt of a cylinder (degrees)."""
    return max(abs(s) for _, s in bottom_angles(pitch, roll))


# --- parts -----------------------------------------------------------------------
def arm():
    """Arm with a stub bar on each side of the hub; own frame, roll axis along +x."""
    L = P.ARM_LENGTH
    hx = P.HUB_X
    shaft = cq.Workplane("YZ").circle(P.ROLL_SHAFT_D / 2).extrude(P.YOKE["depth"] + 40).translate((-P.YOKE["depth"] / 2 - 8, 0, 0))
    tube = cq.Workplane("YZ").circle(12).circle(9).extrude(L - 40).translate((40, 0, 0))
    hub = cq.Workplane("YZ").circle(16).extrude(20).translate((hx - 10, 0, 0))
    stub_end = R_HUB + B / 2 + 3.0
    bar = cq.Workplane("XZ").circle(P.BAR_D / 2).extrude(stub_end, both=True).translate((hx, 0, 0))
    return shaft.union(tube).union(hub).union(bar)


def cross_block():
    """Block turning on the bar (local y) with the fork pin square to it (local x)."""
    b = cq.Workplane("XY").box(B, B, B)
    b = b.cut(cq.Workplane("XZ").circle(P.BAR_D / 2 + 0.2).extrude(B, both=True))
    b = b.cut(cq.Workplane("YZ").circle(C["pin_d"] / 2 + 0.2).extrude(B, both=True))
    return b


def rod_fork():
    """Rod + nuts + fork, cylinder frame (origin = lower pivot, x = axis), retracted.
    The fork pin (local y) sits at PIN_TO_PIN_MIN."""
    c = P.CYL
    x_front = -c["rear_pin_from_end"] + c["overall_retracted"]
    rod_len = 40.0 + c["stroke"]
    rod = cq.Workplane("YZ").circle(c["rod"] / 2).extrude(rod_len).translate((x_front - rod_len, 0, 0))
    nuts = cq.Workplane("YZ").polygon(6, 14.0).extrude(c["rod_stack"]).translate((x_front, 0, 0))
    pin_x = P.PIN_TO_PIN_MIN
    base_x0 = x_front + c["rod_stack"]
    base_x1 = base_x0 + 4.0
    base = cq.Workplane("XY").box(base_x1 - base_x0, 26, 13).translate(((base_x0 + base_x1) / 2, 0, 0))
    fork = rod.union(nuts).union(base)
    for k in (1, -1):
        prong = cq.Workplane("XY").box(pin_x + 8.0 - base_x0, 4, 13).translate(((pin_x + 8.0 + base_x0) / 2, k * (B / 2 + 3), 0))
        fork = fork.union(prong)
    for k in (1, -1):                     # two stub pins: the bar runs through the block centre
        pin = (cq.Workplane("XZ").circle(C["pin_d"] / 2).extrude(B / 2)
               .translate((pin_x, k * (P.BAR_D / 2 + 1.0) + (B / 2 if k > 0 else 0), 0)))
        fork = fork.union(pin)
    return fork


def cheek(side):
    """Cheek with a round top around the joint; in front of the joint it is cut back so the
    cross blocks and cylinders can pass."""
    t = T1.CHEEK["thickness"]
    jx, jz = P.JOINT[0], P.JOINT[2]
    x0, x_front, r_top = P.CHEEK_X[0], C["cheek_front"], C["cheek_top_r"]
    body = cq.Workplane("XZ").center((x0 + x_front) / 2, jz / 2).rect(x_front - x0, jz).extrude(-t)
    back_top = cq.Workplane("XZ").center((x0 + jx) / 2, jz + r_top / 2).rect(jx - x0, r_top).extrude(-t)
    top = cq.Workplane("XZ").center(jx, jz).circle(r_top).extrude(-t)
    c = body.union(back_top).union(top).translate((0, side * T1.CHEEK_GAP / 2 + (0 if side > 0 else -t), 0))
    return c.cut(cq.Workplane("XZ").center(jx, jz).circle(5.0).extrude(100, both=True))


def lower_stand(side):
    """Fixed part of the bottom joint: foot plate and two cheeks across x carrying the M8
    bolt along x."""
    x, y, zq = C["lower_pivot"][0], side * R_HUB, C["lower_pivot"][1] - LOW_D
    t, gap = 5.0, 16.0 + 1.0                      # cheek thickness, room for the fork tongue
    stand = cq.Workplane("XY").box(gap + 2 * t + 16, 36, 6).translate((x, y, 3))
    for k in (1, -1):
        stand = stand.union(cq.Workplane("XY").box(t, 30, zq + 11).translate((x + k * (gap + t) / 2, y, (zq + 11) / 2)))
    stand = stand.cut(cq.Workplane("YZ").circle(4.2).extrude(60, both=True).translate((x, y, zq)))
    bolt = cq.Workplane("YZ").circle(4.0).extrude((gap + 2 * t) / 2 + 6, both=True).translate((x, y, zq))
    head = cq.Workplane("YZ").polygon(6, 14.0).extrude(5.5).translate((x + (gap + 2 * t) / 2, y, zq))
    return stand.union(bolt).union(head)


def lower_fork():
    """Swinging part of the bottom joint, own frame: origin on the x bolt, z up to the rear
    pin (along y) at LOW_D. Two plates either side of the cylinder eye and a tongue below;
    the plates stop 9 mm above the pin, under the cylinder tube."""
    t, w_in = 5.0, 22.0 + 2.0                     # plate thickness, room for the Ø22 rear eye
    tongue = cq.Workplane("XY").box(16, w_in + 2 * t, 16)
    tongue = tongue.cut(cq.Workplane("YZ").circle(4.2).extrude(20, both=True))
    fork = tongue
    for k in (1, -1):
        h = LOW_D + 9 + 8
        fork = fork.union(cq.Workplane("XY").box(16, t, h).translate((0, k * (w_in + t) / 2, h / 2 - 8)))
    pin = cq.Workplane("XZ").circle(3.9).extrude(w_in / 2 + t + 4, both=True).translate((0, 0, LOW_D))
    return fork.union(pin)


def frame(x_dir, y_dir):
    x = x_dir / np.linalg.norm(x_dir)
    y = y_dir - np.dot(y_dir, x) * x
    y /= np.linalg.norm(y)
    return np.column_stack([x, y, np.cross(x, y)])


def pose(pitch=0.0, roll=0.0):
    wood = (0.82, 0.68, 0.47, 1)
    alu = (0.75, 0.77, 0.80, 1)
    steel = (0.45, 0.45, 0.48, 1)
    red = (0.75, 0.25, 0.2, 1)
    blue = (0.2, 0.4, 0.75, 1)
    items = [
        ("base_plate", M.base_plate().val(), wood),
        ("cheek_left", cheek(1).val(), wood),
        ("cheek_right", cheek(-1).val(), wood),
        ("spacer_block", M.spacer_block().val(), wood),
    ]
    J = np.array(P.JOINT)
    items.append(("yoke", M.place(M.yoke(), M.rot_matrix(pitch, 0.0), J), red))
    items.append(("arm", M.place(arm(), M.rot_matrix(pitch, roll), J), alu))
    lengths = []
    for i, (side, h, low, q) in enumerate(zip((1, -1), hinge_points(pitch, roll), lower_pins(pitch, roll), lower_bolts())):
        u = h - low
        L = float(np.linalg.norm(u))
        lengths.append(L)
        c = u / L
        bar_dir = M.rot_matrix(pitch, roll) @ np.array([0.0, side, 0.0])
        j = np.cross(bar_dir, c)              # fork pin: square to the bar and to the cylinder
        j /= np.linalg.norm(j)
        items.append((f"cross_block_{i}", M.place(cross_block(), frame(j, bar_dir), h), blue))
        b = fork_tilt(h, q)
        y_low = np.array([0.0, math.cos(b), -math.sin(b)])   # rear pin, swung with the fork
        Rc = frame(c, y_low)
        ext = max(0.0, min(P.CYL["stroke"], L - P.PIN_TO_PIN_MIN))
        items.append((f"cylinder_{i}", M.place(M.t2_cylinder(M.T1parts.cylinder_body), Rc, low), alu))
        # the rod turns freely in the barrel, so its fork follows the cross block
        items.append((f"rod_{i}", M.place(M.t2_cylinder(rod_fork).translate((ext, 0, 0)), frame(c, j), low), steel))
        items.append((f"lower_stand_{i}", lower_stand(side).val(), alu))
        items.append((f"lower_fork_{i}", M.place(lower_fork(), frame(np.array([1.0, 0.0, 0.0]), y_low), q), blue))
    return items, lengths


CLASH_PAIRS = [("arm", "cheek"), ("arm", "base"), ("arm", "cylinder"), ("arm", "rod"),
               ("yoke", "cheek"), ("cross_block", "cheek"), ("cross_block", "cylinder"),
               ("cylinder", "cheek"), ("cylinder", "base"), ("rod", "cheek"), ("rod", "arm"),
               ("lower_stand", "cheek"), ("lower_fork", "cheek"), ("lower_fork", "lower_stand"),
               ("lower_fork", "cylinder"), ("rod", "cross_block")]


def clashes(pitch, roll, min_volume=1.0):
    items, _ = pose(pitch, roll)
    found = []
    for pa, pb in CLASH_PAIRS:
        for na, sa, _ in items:
            for nb, sb, _ in items:
                if na.startswith(pa) and nb.startswith(pb) and na != nb:
                    if sa.intersect(sb).Volume() > min_volume:
                        found.append(f"{na}/{nb}")
    return found


if __name__ == "__main__":
    import sys
    force = 2 * T1.P_SUPPLY * 0.1 * T1.AREA_A
    print(f"cross block: hub r {R_HUB}, lower pivots {C['lower_pivot']}, cylinders {P.PIN_TO_PIN_MIN:.0f}–{P.PIN_TO_PIN_MAX:.0f} mm")
    for p in range(-60, 91, 15):
        rs = [r for r in range(0, 91, 5) if reachable(p, r) and reachable(p, -r)]
        rmax = max(rs) if rs else None
        tilt = side_tilt(p, rmax) if rmax is not None else float("nan")
        print(f"pitch {p:4d}°: roll ±{rmax if rmax is not None else '—'}°  sideways tilt {tilt:3.0f}°  "
              f"L {[round(x) for x in cylinder_lengths(p, 0)]}")
    fwd, side = [], []
    for p in range(-60, 76, 5):
        for r in range(-65, 66, 5):
            if reachable(p, r):
                for f, sd in bottom_angles(p, r):
                    fwd.append(f)
                    side.append(sd)
    print(f"bottom joint: forward/back {min(fwd):.1f}° … {max(fwd):.1f}°, "
          f"sideways {min(side):.1f}° … {max(side):.1f}° (+ = towards +y)")
    if "--clash" in sys.argv:
        for p in (-60, -45, -20, 0, 25, 50, 75):
            for r in (-65, 0, 65):
                if not (reachable(p, r)):
                    continue
                c = clashes(p, r)
                print(f"pitch {p:4d} roll {r:4d}: {', '.join(c) if c else 'no clash'}")

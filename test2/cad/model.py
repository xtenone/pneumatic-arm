"""CadQuery concept model of test 2: universal joint, arm with crossbar, two cylinders.

pose(pitch, roll) returns the parts placed for a given arm attitude (degrees).
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


def attach_points(pitch, roll):
    """World positions of the two crossbar ball joints (left, right)."""
    R = rot_matrix(pitch, roll)
    J = np.array(P.JOINT)
    out = []
    for s in (1, -1):
        local = np.array([P.LEVER_X, s * P.LEVER_HALF, -P.LEVER_DROP])
        out.append(J + R @ local)
    return out


def rear_points():
    return [np.array([P.REAR_PIVOTS_X, s * P.LEVER_HALF, P.REAR_PIVOTS_Z]) for s in (1, -1)]


def cylinder_lengths(pitch, roll):
    return [float(np.linalg.norm(a - b)) for a, b in zip(attach_points(pitch, roll), rear_points())]


def place(shape, R, t):
    """Apply rotation matrix R (3×3) and translation t to a CadQuery shape."""
    m = cq.Matrix([[R[0, 0], R[0, 1], R[0, 2], t[0]],
                   [R[1, 0], R[1, 1], R[1, 2], t[1]],
                   [R[2, 0], R[2, 1], R[2, 2], t[2]]])
    return shape.val().transformGeometry(m) if hasattr(shape, "val") else shape.transformGeometry(m)


def align_x_to(u):
    """Rotation matrix that maps +x onto unit vector u (keeps the local z roughly up)."""
    x = u / np.linalg.norm(u)
    z0 = np.array([0.0, 0.0, 1.0])
    y = np.cross(z0, x)
    if np.linalg.norm(y) < 1e-6:
        y = np.array([0.0, 1.0, 0.0])
    y /= np.linalg.norm(y)
    z = np.cross(x, y)
    return np.column_stack([x, y, z])


# --- parts -----------------------------------------------------------------------
def yoke():
    """Pitch yoke: turns about y between the cheeks, carries the roll shaft along x."""
    w, h, d = P.YOKE["width"], P.YOKE["height"], P.YOKE["depth"]
    y = cq.Workplane("XY").box(d, w, h)
    y = y.cut(cq.Workplane("XZ").circle(4.25).extrude(w, both=True))          # pitch bolt
    y = y.cut(cq.Workplane("YZ").circle(P.ROLL_SHAFT_D / 2 + 0.5).extrude(d, both=True))  # roll shaft
    return y


def arm():
    """Arm in its own frame: roll axis along +x through the origin (the joint centre)."""
    L = P.ARM_LENGTH
    hub = cq.Workplane("YZ").circle(14).extrude(70).translate((P.YOKE["depth"] / 2 + 2, 0, 0))
    shaft = cq.Workplane("YZ").circle(P.ROLL_SHAFT_D / 2).extrude(P.YOKE["depth"] + 80).translate((-P.YOKE["depth"] / 2 - 8, 0, 0))
    bar = cq.Workplane("XY").box(L - 60, 5, 40).translate((60 + (L - 60) / 2, 0, 0))
    cross = cq.Workplane("XY").box(20, 2 * P.LEVER_HALF + 30, 6).translate((P.LEVER_X, 0, -P.LEVER_DROP))
    web = cq.Workplane("XY").box(20, 5, P.LEVER_DROP).translate((P.LEVER_X, 0, -P.LEVER_DROP / 2))
    balls = None
    for s in (1, -1):
        b = cq.Workplane("XY").sphere(7).translate((P.LEVER_X, s * P.LEVER_HALF, -P.LEVER_DROP - 10))
        stud = cq.Workplane("XY").circle(4).extrude(10).translate((P.LEVER_X, s * P.LEVER_HALF, -P.LEVER_DROP - 10))
        balls = b.union(stud) if balls is None else balls.union(b).union(stud)
    return hub.union(shaft).union(bar).union(cross).union(web).union(balls)


def outrigger(side):
    """Bracket on the outside of a cheek carrying a lower cylinder ball joint."""
    t = P.OUTRIGGER["thickness"]
    y_cheek_out = T1.CHEEK_GAP / 2 + T1.CHEEK["thickness"]
    width = P.LEVER_HALF - y_cheek_out + 15
    plate = cq.Workplane("XY").box(P.OUTRIGGER["length"], width, t).translate(
        (P.REAR_PIVOTS_X, side * (y_cheek_out + width / 2), P.REAR_PIVOTS_Z - 20))
    ball = cq.Workplane("XY").sphere(7).translate((P.REAR_PIVOTS_X, side * P.LEVER_HALF, P.REAR_PIVOTS_Z))
    post = cq.Workplane("XY").circle(4).extrude(20).translate((P.REAR_PIVOTS_X, side * P.LEVER_HALF, P.REAR_PIVOTS_Z - 20))
    return plate.union(ball).union(post)


def cylinder_parts(rear, attach):
    """Cylinder body + rod (with ball-joint eye) placed between two points."""
    u = attach - rear
    L = float(np.linalg.norm(u))
    ext = max(0.0, min(P.CYL["stroke"], L - P.PIN_TO_PIN_MIN))
    R = align_x_to(u)
    body = place(T1parts.cylinder_body(), R, rear)
    rod = T1parts.rod_assembly().translate((ext, 0, 0))
    # ball-joint eye instead of the clevis: a ring at the pin
    eye = (cq.Workplane("XZ").circle(10).circle(7.5).extrude(5, both=True)
           .translate((P.PIN_TO_PIN_MIN + ext, 0, 0)))
    rod_world = place(rod, R, rear)
    eye_world = place(eye, R, rear)
    return body, rod_world, eye_world, L, ext


def pose(pitch=0.0, roll=0.0):
    """Assembly (list of (name, shape, rgba)) for one arm attitude."""
    wood = (0.82, 0.68, 0.47, 1)
    alu = (0.75, 0.77, 0.80, 1)
    steel = (0.45, 0.45, 0.48, 1)
    red = (0.75, 0.25, 0.2, 1)
    items = [
        ("base_plate", T1parts.base_plate().val(), wood),
        ("cheek_left", T1parts.cheek().translate((0, T1.CHEEK_GAP / 2, 0)).val(), wood),
        ("cheek_right", T1parts.cheek().mirror("XZ").translate((0, -T1.CHEEK_GAP / 2, 0)).val(), wood),
        ("spacer_block", T1parts.spacer_block().val(), wood),
        ("outrigger_left", outrigger(1).val(), alu),
        ("outrigger_right", outrigger(-1).val(), alu),
    ]
    J = np.array(P.JOINT)
    Rp = rot_matrix(pitch, 0.0)
    items.append(("yoke", place(yoke(), Rp, J), red))
    R = rot_matrix(pitch, roll)
    items.append(("arm", place(arm(), R, J), alu))
    lengths = []
    for i, (rear, att) in enumerate(zip(rear_points(), attach_points(pitch, roll))):
        body, rod, eye, L, ext = cylinder_parts(rear, att)
        lengths.append(L)
        items += [(f"cylinder_{i}", body, alu), (f"rod_{i}", rod, steel), (f"eye_{i}", eye, steel)]
    return items, lengths


if __name__ == "__main__":
    for pr in ((0, 0), (30, 0), (0, 20), (0, -20), (-15, 0), (45, 15)):
        print(pr, [round(x, 1) for x in cylinder_lengths(*pr)], "range", round(P.PIN_TO_PIN_MIN), "–", round(P.PIN_TO_PIN_MAX))

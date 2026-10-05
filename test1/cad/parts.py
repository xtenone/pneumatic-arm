"""CAD of test 1, generated with CadQuery from params.py.

Home-made parts (plywood, aluminium) are exact; bought parts (cylinder,
potentiometer, bearings, bolts) are simplified shapes for fit and visuals.
Each part has its own local frame; assemble() puts them in place.
"""
import math
import os
import sys

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import params as P  # noqa: E402

GAP = P.CHEEK_GAP
T = P.CHEEK["thickness"]


# --- Home-made ---------------------------------------------------------------
def base_plate():
    x0, x1 = P.BASE_X
    plate = (cq.Workplane("XY").box(x1 - x0, P.BASE["width"], P.BASE["thickness"])
             .translate(((x0 + x1) / 2, 0, -P.BASE["thickness"] / 2)))
    return plate


def cheek():
    """One cheek, flat in the x-z plane, thickness in y (0..T). Holes: 608 bearing + pivot."""
    x0, x1 = P.CHEEK_X
    h = P.CHEEK["height"]
    w = (cq.Workplane("XZ").rect(x1 - x0, h, centered=False).extrude(-T)
         .translate((x0, 0, 0)))
    hx, hz = P.HINGE
    rx, rz = P.REAR_PIVOT
    # 10 mm through hole + Ø22 × 7 mm bearing seat on the outside
    w = w.cut(cq.Workplane("XZ").center(hx, hz).circle(5.0).extrude(-T))
    w = w.cut(cq.Workplane("XZ").center(hx, hz).circle(11.0).extrude(-7.0).translate((0, T - 7.0, 0)))
    w = w.cut(cq.Workplane("XZ").center(rx, rz).circle(4.25).extrude(-T))
    # two screw holes for the spacer block
    for z in (20.0, 45.0):
        w = w.cut(cq.Workplane("XZ").center(P.CHEEK_X[0] + 30.0, z).circle(2.5).extrude(-T))
    return w


def spacer_block():
    L, H = P.SPACER_BLOCK["length"], P.SPACER_BLOCK["height"]
    return (cq.Workplane("XY").box(L, GAP, H)
            .translate((P.CHEEK_X[0] + L / 2, 0, H / 2)))


def arm():
    """Arm in its own frame: hinge hole at the origin, along +x, flat in x-z."""
    L, H, t = P.ARM["length"], P.ARM["height"], P.ARM["thickness"]
    a = (cq.Workplane("XZ").rect(L, H).extrude(t / 2, both=True)
         .translate((L / 2 - P.ARM_BEHIND, 0, 0)))
    for x in (0.0, P.ARM_ATTACH, P.ARM_TIP):
        a = a.cut(cq.Workplane("XZ").center(x, 0).circle(P.ARM_HOLE / 2).extrude(t, both=True))
    return a


def pot_bracket():
    """20×3 strip clamped on the cylinder rod; it carries the potentiometer rod."""
    off = P.POT["offset"]
    s = cq.Workplane("XY").box(3.0, 20.0, off + 15.0).translate((0, 0, -(off + 15.0) / 2 + 7.5))
    s = s.cut(cq.Workplane("YZ").circle(4.25).extrude(3.0, both=True))
    s = s.cut(cq.Workplane("YZ").center(0, -off).circle(2.75).extrude(3.0, both=True))
    return s


# --- Bought (simplified) -----------------------------------------------------
def cylinder_body():
    """Cylinder without rod. Origin = centre of the rear pin, axis along +x."""
    c = P.CYL
    stub_len = 21.0
    body_len = 70.0 + c["stroke"]
    x_rear_end = -c["rear_pin_from_end"]
    stub = (cq.Workplane("YZ").circle(11.0).extrude(stub_len).translate((x_rear_end, 0, 0))
            .cut(cq.Workplane("XZ").circle(4.0).extrude(15.0, both=True)))
    body = cq.Workplane("YZ").circle(c["body_d"] / 2).extrude(body_len).translate((x_rear_end + stub_len, 0, 0))
    front = (cq.Workplane("YZ").circle(11.0).extrude(15.5)
             .translate((x_rear_end + stub_len + body_len, 0, 0)))
    nut = (cq.Workplane("YZ").polygon(6, 32.0).extrude(6.0)
           .translate((x_rear_end + stub_len + body_len + 4.0, 0, 0)))
    return stub.union(body).union(front).union(nut)


def rod_assembly():
    """Rod + nuts + clevis. Origin = centre of the rear pin, cylinder retracted."""
    c = P.CYL
    x_front = -c["rear_pin_from_end"] + c["overall_retracted"]  # rod end, retracted
    rod_len = 40.0 + c["stroke"]
    rod = cq.Workplane("YZ").circle(c["rod"] / 2).extrude(rod_len).translate((x_front - rod_len, 0, 0))
    nuts = cq.Workplane("YZ").polygon(6, 14.0).extrude(c["rod_stack"]).translate((x_front, 0, 0))
    y_start = x_front + c["rod_stack"]
    pin_x = P.PIN_TO_PIN_MIN
    clevis = cq.Workplane("XY").box(pin_x - y_start + 9.0, 16.0, 16.0).translate(((y_start + pin_x + 9.0) / 2, 0, 0))
    clevis = clevis.cut(cq.Workplane("XY").box(20.0, 8.2, 20.0).translate((pin_x, 0, 0)))
    return rod.union(nuts).union(clevis)


def pot_body():
    """KTC-175, fixed to the cylinder (hose clamps). Origin = centre of the rear pin."""
    L, wy, hz = P.POT["body"]
    return cq.Workplane("XY").box(L, wy, hz).translate((40.0 + L / 2, 0, -P.POT["offset"]))


def pot_rod():
    """Potentiometer rod, moves with the cylinder rod."""
    x_front = -P.CYL["rear_pin_from_end"] + P.CYL["overall_retracted"]
    length = 40.0 + P.CYL["stroke"] + 25.0
    return (cq.Workplane("YZ").circle(3.0).extrude(length)
            .translate((x_front + 1.5 - length, 0, -P.POT["offset"])))


def bearing_608():
    return cq.Workplane("XZ").circle(11.0).circle(4.0).extrude(7.0)


def bolt(length, d=8.0):
    return cq.Workplane("XZ").circle(d / 2).extrude(length / 2, both=True)


def bottle():
    return cq.Workplane("XY").circle(45.0).extrude(250.0).translate((0, 0, -250.0))


# --- Assembly ---------------------------------------------------------------------
def pose(theta_deg):
    """Placement of the moving parts at arm angle theta."""
    hx, hz = P.HINGE
    rx, rz = P.REAR_PIVOT
    t = math.radians(theta_deg)
    ax, az = hx + P.ARM_ATTACH * math.cos(t), hz + P.ARM_ATTACH * math.sin(t)
    L = math.hypot(ax - rx, az - rz)
    phi = math.degrees(math.atan2(az - rz, ax - rx))
    return dict(theta=theta_deg, L=L, phi=phi, ext=L - P.PIN_TO_PIN_MIN)


def assemble(theta_deg=0.0):
    p = pose(theta_deg)
    hx, hz = P.HINGE
    rx, rz = P.REAR_PIVOT
    y_cheek = GAP / 2

    def at_hinge(shape):
        return shape.rotate((0, 0, 0), (0, -1, 0), p["theta"]).translate((hx, 0, hz))

    def at_cyl(shape, ext=0.0):
        return (shape.translate((ext, 0, 0)).rotate((0, 0, 0), (0, -1, 0), p["phi"])
                .translate((rx, 0, rz)))

    assy = cq.Assembly(name="test1")
    wood = cq.Color(0.82, 0.68, 0.47)
    alu = cq.Color(0.75, 0.77, 0.80)
    steel = cq.Color(0.45, 0.45, 0.48)
    blue = cq.Color(0.15, 0.35, 0.75)
    assy.add(base_plate(), name="base_plate", color=wood)
    assy.add(cheek().translate((0, y_cheek, 0)), name="cheek_left", color=wood)
    assy.add(cheek().mirror("XZ").translate((0, -y_cheek, 0)), name="cheek_right", color=wood)
    assy.add(spacer_block(), name="spacer_block", color=wood)
    assy.add(at_hinge(arm()), name="arm", color=alu)
    assy.add(at_cyl(cylinder_body()), name="cylinder", color=alu)
    assy.add(at_cyl(rod_assembly(), p["ext"]), name="rod_clevis", color=steel)
    assy.add(at_cyl(pot_body()), name="potentiometer", color=blue)
    assy.add(at_cyl(pot_rod(), p["ext"]), name="pot_rod", color=steel)
    assy.add(at_cyl(pot_bracket().translate((-P.CYL["rear_pin_from_end"] + P.CYL["overall_retracted"] + 1.5, 0, 0)),
                    p["ext"]), name="pot_bracket", color=alu)
    for side in (1, -1):
        assy.add(bearing_608().translate((hx, side * (y_cheek + T) - (7.0 if side > 0 else 0.0) * 0 + (0 if side > 0 else 7.0), hz)),
                 name=f"bearing_{'left' if side > 0 else 'right'}", color=steel)
    assy.add(bolt(GAP + 2 * T + 20).translate((hx, 0, hz)), name="bolt_hinge", color=steel)
    assy.add(bolt(GAP + 2 * T + 20).translate((rx, 0, rz)), name="bolt_cylinder", color=steel)
    tip = at_hinge(cq.Workplane("XY").box(1, 1, 1).translate((P.ARM_TIP, 0, 0)))
    tx, _, tz = tip.val().Center().toTuple()
    assy.add(bottle().translate((tx, 0, tz - 60.0)), name="load_bottle", color=cq.Color(0.6, 0.8, 0.95, 0.6))
    return assy


MADE_PARTS = {
    "base_plate": base_plate,
    "cheek": cheek,
    "spacer_block": spacer_block,
    "arm": arm,
    "pot_bracket": pot_bracket,
}

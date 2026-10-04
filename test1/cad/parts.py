"""CAD van test 1, gegenereerd met CadQuery uit params.py.

Zelfgemaakte onderdelen (multiplex, aluminium) zijn exact; gekochte onderdelen
(cilinder, potmeter, lagers, bouten) zijn vereenvoudigde vormen voor passing en beeld.
Elk onderdeel heeft een eigen lokaal assenstelsel; assemble() zet ze op hun plek.
"""
import math
import os
import sys

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import params as P  # noqa: E402

GAP = P.CHEEK_GAP
T = P.CHEEK["thickness"]


# --- Zelfgemaakt -------------------------------------------------------------
def base_plate():
    x0, x1 = P.BASE_X
    plate = (cq.Workplane("XY").box(x1 - x0, P.BASE["width"], P.BASE["thickness"])
             .translate(((x0 + x1) / 2, 0, -P.BASE["thickness"] / 2)))
    return plate


def cheek():
    """Eén wang, plat in het x-z-vlak, dikte in y (0..T). Gaten: lager 608 + draaipunt."""
    x0, x1 = P.CHEEK_X
    h = P.CHEEK["height"]
    w = (cq.Workplane("XZ").rect(x1 - x0, h, centered=False).extrude(-T)
         .translate((x0, 0, 0)))
    hx, hz = P.HINGE
    rx, rz = P.REAR_PIVOT
    # doorgaand gat 10 mm + lagerzitting Ø22 × 7 mm aan de buitenkant
    w = w.cut(cq.Workplane("XZ").center(hx, hz).circle(5.0).extrude(-T))
    w = w.cut(cq.Workplane("XZ").center(hx, hz).circle(11.0).extrude(-7.0).translate((0, T - 7.0, 0)))
    w = w.cut(cq.Workplane("XZ").center(rx, rz).circle(4.25).extrude(-T))
    # twee schroefgaten voor het afstandsblok
    for z in (20.0, 45.0):
        w = w.cut(cq.Workplane("XZ").center(P.CHEEK_X[0] + 30.0, z).circle(2.5).extrude(-T))
    return w


def spacer_block():
    L, H = P.SPACER_BLOCK["length"], P.SPACER_BLOCK["height"]
    return (cq.Workplane("XY").box(L, GAP, H)
            .translate((P.CHEEK_X[0] + L / 2, 0, H / 2)))


def arm():
    """Arm in eigen assenstelsel: scharniergat in de oorsprong, langs +x, plat in x-z."""
    L, H, t = P.ARM["length"], P.ARM["height"], P.ARM["thickness"]
    a = (cq.Workplane("XZ").rect(L, H).extrude(t / 2, both=True)
         .translate((L / 2 - P.ARM_BEHIND, 0, 0)))
    for x in (0.0, P.ARM_ATTACH, P.ARM_TIP):
        a = a.cut(cq.Workplane("XZ").center(x, 0).circle(P.ARM_HOLE / 2).extrude(t, both=True))
    return a


def pot_bracket():
    """Strip 20×3 die op de cilinderstang klemt en de potmeterstang meeneemt."""
    off = P.POT["offset"]
    s = cq.Workplane("XY").box(3.0, 20.0, off + 15.0).translate((0, 0, -(off + 15.0) / 2 + 7.5))
    s = s.cut(cq.Workplane("YZ").circle(4.25).extrude(3.0, both=True))
    s = s.cut(cq.Workplane("YZ").center(0, -off).circle(2.75).extrude(3.0, both=True))
    return s


# --- Gekocht (vereenvoudigd) ----------------------------------------------------
def cylinder_body():
    """Cilinder zonder stang. Oorsprong = hart achterste pen, as langs +x."""
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
    """Stang + moeren + vorkkop. Oorsprong = hart achterste pen bij ingeschoven cilinder."""
    c = P.CYL
    x_front = -c["rear_pin_from_end"] + c["overall_retracted"]  # stangeinde, ingeschoven
    rod_len = 40.0 + c["stroke"]
    rod = cq.Workplane("YZ").circle(c["rod"] / 2).extrude(rod_len).translate((x_front - rod_len, 0, 0))
    nuts = cq.Workplane("YZ").polygon(6, 14.0).extrude(c["rod_stack"]).translate((x_front, 0, 0))
    y_start = x_front + c["rod_stack"]
    pin_x = P.PIN_TO_PIN_MIN
    clevis = cq.Workplane("XY").box(pin_x - y_start + 9.0, 16.0, 16.0).translate(((y_start + pin_x + 9.0) / 2, 0, 0))
    clevis = clevis.cut(cq.Workplane("XY").box(20.0, 8.2, 20.0).translate((pin_x, 0, 0)))
    return rod.union(nuts).union(clevis)


def pot_body():
    """KTC-175, vast aan de cilinder (via slangklemmen). Oorsprong = hart achterste pen."""
    L, wy, hz = P.POT["body"]
    return cq.Workplane("XY").box(L, wy, hz).translate((40.0 + L / 2, 0, -P.POT["offset"]))


def pot_rod():
    """Stang van de potmeter, beweegt mee met de cilinderstang."""
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


# --- Samenstelling ---------------------------------------------------------------
def pose(theta_deg):
    """Plaatsing van de bewegende delen bij armhoek theta."""
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
    assy.add(base_plate(), name="grondplaat", color=wood)
    assy.add(cheek().translate((0, y_cheek, 0)), name="wang_links", color=wood)
    assy.add(cheek().mirror("XZ").translate((0, -y_cheek, 0)), name="wang_rechts", color=wood)
    assy.add(spacer_block(), name="afstandsblok", color=wood)
    assy.add(at_hinge(arm()), name="arm", color=alu)
    assy.add(at_cyl(cylinder_body()), name="cilinder", color=alu)
    assy.add(at_cyl(rod_assembly(), p["ext"]), name="stang_vorkkop", color=steel)
    assy.add(at_cyl(pot_body()), name="potmeter", color=blue)
    assy.add(at_cyl(pot_rod(), p["ext"]), name="potmeter_stang", color=steel)
    assy.add(at_cyl(pot_bracket().translate((-P.CYL["rear_pin_from_end"] + P.CYL["overall_retracted"] + 1.5, 0, 0)),
                    p["ext"]), name="beugel_potmeter", color=alu)
    for side in (1, -1):
        assy.add(bearing_608().translate((hx, side * (y_cheek + T) - (7.0 if side > 0 else 0.0) * 0 + (0 if side > 0 else 7.0), hz)),
                 name=f"lager_{'links' if side > 0 else 'rechts'}", color=steel)
    assy.add(bolt(GAP + 2 * T + 20).translate((hx, 0, hz)), name="bout_scharnier", color=steel)
    assy.add(bolt(GAP + 2 * T + 20).translate((rx, 0, rz)), name="bout_cilinder", color=steel)
    tip = at_hinge(cq.Workplane("XY").box(1, 1, 1).translate((P.ARM_TIP, 0, 0)))
    tx, _, tz = tip.val().Center().toTuple()
    assy.add(bottle().translate((tx, 0, tz - 60.0)), name="last_fles", color=cq.Color(0.6, 0.8, 0.95, 0.6))
    return assy


MADE_PARTS = {
    "grondplaat": base_plate,
    "wang": cheek,
    "afstandsblok": spacer_block,
    "arm": arm,
    "beugel_potmeter": pot_bracket,
}

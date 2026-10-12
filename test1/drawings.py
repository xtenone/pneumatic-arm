"""Drawings of test 1 (from params.py): dimension drawings, wiring and pneumatics.

Output in out/drawings/ as PNG and PDF.
"""
import math
import os

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

import params as P  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "drawings")


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def dim(ax, a, b, off, text, side=1, fs=8):
    """Dimension line from a to b, offset `off` mm (perpendicular)."""
    (x0, y0), (x1, y1) = a, b
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * off * side, dx / L * off * side
    ax.annotate("", (x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
                arrowprops=dict(arrowstyle="<->", lw=0.7, color="k", shrinkA=0, shrinkB=0))
    for (x, y) in (a, b):
        ax.plot([x, x + nx * 1.1], [y, y + ny * 1.1], lw=0.4, color="k")
    ax.text((x0 + x1) / 2 + nx * 1.35, (y0 + y1) / 2 + ny * 1.35, text, ha="center", va="center", fontsize=fs,
            bbox=dict(fc="white", ec="none", pad=0.5))


def cheek():
    x0, x1 = P.CHEEK_X
    h = P.CHEEK["height"]
    fig, ax = plt.subplots(figsize=(5.5, 9))
    ax.add_patch(Rectangle((x0, 0), x1 - x0, h, fc="#e8d3a8", ec="k"))
    holes = [(P.HINGE, 22.0, "Ø22 × 7 deep (608 bearing)\n+ Ø10 through"), (P.REAR_PIVOT, 8.5, "Ø8.5 through"),
             ((x0 + 30, 20.0), 5.0, "Ø5 (block screw)"), ((x0 + 30, 45.0), 5.0, "Ø5 (block screw)")]
    for (cx, cz), d, txt in holes:
        ax.add_patch(Circle((cx, cz), d / 2, fc="white", ec="k"))
        ax.text(cx + 14, cz + (6 if d > 6 else -10), txt, fontsize=7)
    dim(ax, (x0, h), (x1, h), 18, f"{x1 - x0:.0f}")
    dim(ax, (x0, 0), (x0, h), 30, f"{h:.0f}", side=1)
    dim(ax, (x1, 0), (x1, P.HINGE[1]), -25, f"{P.HINGE[1]:.0f}", side=1)
    dim(ax, (x1, 0), (x1, P.REAR_PIVOT[1]), -55, f"{P.REAR_PIVOT[1]:.0f}", side=1)
    dim(ax, (x0, P.HINGE[1] + 5), (P.HINGE[0], P.HINGE[1] + 5), 0, f"{P.HINGE[0] - x0:.0f}", fs=7)
    dim(ax, (x0, 32), (x0 + 30, 32), 0, "30", fs=7)
    ax.text(x0 + 32, 2, "holes at 20 and 45 high", fontsize=6.5)
    ax.text(x0 - 8, h / 2, "back", rotation=90, ha="right", va="center", fontsize=7, color="0.4")
    ax.text(x1 + 8, h / 2 - 60, "front\n(arm)", ha="left", va="center", fontsize=7, color="0.4")
    ax.text(0, -40, f"Cheek — 2 pieces, plywood {P.CHEEK['thickness']:.0f} mm\n"
            "Bearing seat on the OUTSIDE (mirror image for the second cheek)\ndimensions in mm", ha="center", fontsize=8)
    ax.set_aspect("equal")
    ax.set_xlim(x0 - 90, x1 + 120)
    ax.set_ylim(-70, h + 60)
    ax.axis("off")
    save(fig, "cheek")


def arm():
    L, H = P.ARM["length"], P.ARM["height"]
    x0 = -P.ARM_BEHIND
    fig, ax = plt.subplots(figsize=(11, 2.8))
    ax.add_patch(Rectangle((x0, -H / 2), L, H, fc="#d0d4da", ec="k"))
    for x, txt in ((0.0, "hinge"), (P.ARM_ATTACH, "clevis"), (P.ARM_TIP, "load")):
        ax.add_patch(Circle((x, 0), P.ARM_HOLE / 2, fc="white", ec="k"))
        ax.text(x, -H / 2 - 10, f"{txt}\nØ{P.ARM_HOLE}", ha="center", va="top", fontsize=7)
    dim(ax, (x0, H / 2), (x0 + L, H / 2), 22, f"{L:.0f}")
    dim(ax, (x0, H / 2), (0, H / 2), 10, f"{P.ARM_BEHIND:.0f}", fs=7)
    dim(ax, (0, H / 2), (P.ARM_ATTACH, H / 2), 10, f"{P.ARM_ATTACH:.0f}", fs=7)
    dim(ax, (0, H / 2), (P.ARM_TIP, H / 2), 36, f"{P.ARM_TIP:.0f}", fs=7)
    dim(ax, (x0 + L, -H / 2), (x0 + L, H / 2), -14, f"{H:.0f}", fs=7)
    ax.text(x0, -H / 2 - 40, f"Arm — aluminium flat bar {H:.0f}×{P.ARM['thickness']:.0f} mm, holes on the centre line; dimensions in mm",
            fontsize=8)
    ax.set_aspect("equal")
    ax.set_xlim(x0 - 20, x0 + L + 40)
    ax.set_ylim(-H / 2 - 55, H / 2 + 50)
    ax.axis("off")
    save(fig, "arm")


def side_view():
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cad"))
    from parts import pose
    fig, ax = plt.subplots(figsize=(10, 7.5))
    bx0, bx1 = P.BASE_X
    ax.add_patch(Rectangle((bx0, -P.BASE["thickness"]), bx1 - bx0, P.BASE["thickness"], fc="#e8d3a8", ec="k"))
    ax.add_patch(Rectangle((bx0 - 150, -P.BASE["thickness"] - 30), bx1 - bx0 + 160, 30, fc="#9c7b58", ec="k", alpha=0.5))
    ax.text(bx0 - 140, -P.BASE["thickness"] - 22, "table", fontsize=7)
    ax.add_patch(Rectangle((P.CHEEK_X[0], 0), P.CHEEK_X[1] - P.CHEEK_X[0], P.CHEEK["height"], fc="#e8d3a8", ec="k", alpha=0.6))
    hx, hz = P.HINGE
    rx, rz = P.REAR_PIVOT
    for th, ls, col, lab in ((P.THETA_MIN, ":", "0.5", f"lowest position {P.THETA_MIN:.0f}°"),
                             (0.0, "-", "k", "horizontal"),
                             (P.THETA_MAX, ":", "0.5", f"highest position {P.THETA_MAX:.0f}°")):
        t = math.radians(th)
        ex, ez = hx + (P.ARM["length"] - P.ARM_BEHIND) * math.cos(t), hz + (P.ARM["length"] - P.ARM_BEHIND) * math.sin(t)
        ax.plot([hx - P.ARM_BEHIND * math.cos(t), ex], [hz - P.ARM_BEHIND * math.sin(t), ez], ls, color=col, lw=4 if ls == "-" else 1.5)
        ax_, az_ = hx + P.ARM_ATTACH * math.cos(t), hz + P.ARM_ATTACH * math.sin(t)
        ax.plot([rx, ax_], [rz, az_], ls, color="C0" if ls == "-" else "0.6", lw=6 if ls == "-" else 1)
        if ls != "-":
            ax.text(ex + 8, ez, lab, fontsize=7, color="0.4", va="center")
    t0 = pose(0.0)
    for (x, z), name, dz in ((P.HINGE, "hinge", 28), (P.REAR_PIVOT, "cylinder pivot", 0)):
        ax.add_patch(Circle((x, z), 6, fc="white", ec="k", zorder=5))
        ax.text(x - 70, z + dz, name, ha="right", va="center", fontsize=8,
                bbox=dict(fc="white", ec="none", pad=0.5))
    tipx, tipz = hx + P.ARM_TIP, hz
    ax.add_patch(Circle((tipx, tipz), P.PLATE["d"] / 2, fc="0.25", ec="k", alpha=0.85, zorder=4))
    ax.add_patch(Circle((tipx, tipz), 4, fc="white", ec="k", zorder=6))
    ax.text(tipx, tipz - 14, f"{P.TIP_MASS:g} kg", ha="center", va="top", fontsize=8, color="white", zorder=7)
    dim(ax, (P.CHEEK_X[1], hz), (P.CHEEK_X[1], rz), -40, f"{hz - rz:.0f}")
    dim(ax, (hx, 0), (hx, hz), 150, f"{hz:.0f}")
    dim(ax, (hx, hz), (hx + P.ARM_ATTACH, hz), 25, f"{P.ARM_ATTACH:.0f}")
    dim(ax, (hx, hz), (hx + P.ARM_TIP, hz), 55, f"{P.ARM_TIP:.0f}")
    dim(ax, (bx0, -P.BASE["thickness"]), (bx1, -P.BASE["thickness"]), -60, f"{bx1 - bx0:.0f}")
    ax.text(rx + 175, rz + 40, f"cylinder MAL20×150\npin to pin {P.PIN_TO_PIN_MIN:.0f}–{P.PIN_TO_PIN_MAX:.0f} mm\n"
            f"at 0°: {t0['L']:.0f} mm", fontsize=8, color="C0")
    ax.set_aspect("equal")
    ax.set_xlim(bx0 - 160, hx + P.ARM["length"] + 120)
    ax.set_ylim(-140, hz + P.ARM["length"] * math.sin(math.radians(P.THETA_MAX)) + 40)
    ax.set_title("Test 1 — side view (dimensions in mm)", fontsize=10)
    ax.axis("off")
    save(fig, "side_view")


def pneumatics():
    fig, ax = plt.subplots(figsize=(11, 7))

    def box(x, y, w, h, text, fc="#f2f2f2"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05", fc=fc, ec="k"))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8)

    def line(pts, **kw):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=kw.get("color", "k"), lw=kw.get("lw", 1.4))

    box(0.0, 6.0, 1.6, 0.8, "compressor\n24 l, 8 bar", "#dfe8f5")
    box(2.1, 6.0, 1.6, 0.8, "filter +\nregulator\nAFR-2000", "#dfe8f5")
    box(4.2, 6.0, 1.6, 0.8, "shut-off slide\nHSV-08", "#dfe8f5")
    box(6.3, 6.0, 1.6, 0.8, "main valve\n3V210-08 (NC)\n24 V via e-stop", "#fde7c8")
    line([(1.6, 6.4), (2.1, 6.4)])
    line([(3.7, 6.4), (4.2, 6.4)])
    line([(5.8, 6.4), (6.3, 6.4)])
    line([(7.9, 6.4), (8.6, 6.4), (8.6, 5.3)])
    ax.text(8.7, 5.9, "4 mm", fontsize=7)
    line([(2.7, 5.3), (8.6, 5.3)])
    ax.plot([8.6], [5.3], "ko", ms=4)
    ax.text(8.65, 5.15, "tee", fontsize=7)
    # chambers
    for xc, k, fill, vent in ((2.7, "A", "V1", "V2"), (6.7, "B", "V3", "V4")):
        line([(xc, 5.3), (xc, 4.6)])
        ax.text(xc + 0.05, 5.0, "(flow restrictor,\nlater)", fontsize=6, color="0.4")
        box(xc - 0.6, 3.8, 1.2, 0.8, f"{fill}\nfill {k}\nVQ110U", "#fde7c8")
        line([(xc, 3.8), (xc, 3.0)])
        ax.plot([xc], [3.0], "ko", ms=4)
        sx = xc - 2.0 if k == "A" else xc + 0.8
        box(sx, 2.7, 1.2, 0.6, f"pressure sensor\np{k} (G1/4)", "#e3f2e1")
        line([(xc, 3.0), (sx + (1.2 if k == "A" else 0.0), 3.0)])
        line([(xc, 3.0), (xc, 2.2)])
        box(xc - 0.6, 1.4, 1.2, 0.8, f"{vent}\nvent {k}\nVQ110U", "#fde7c8")
        line([(xc, 1.4), (xc, 0.9)])
        ax.text(xc, 0.75, "M5 silencer", ha="center", fontsize=7)
    # cylinder
    ax.add_patch(Rectangle((3.6, 2.6), 2.6, 0.8, fc="#d0d4da", ec="k"))
    ax.plot([4.9, 4.9], [2.6, 3.4], "k", lw=3)
    ax.plot([4.9, 6.2], [2.95, 2.95], "k", lw=2)
    ax.text(4.25, 3.0, "chamber A", ha="center", va="center", fontsize=8)
    ax.text(5.55, 3.15, "chamber B", ha="center", va="center", fontsize=8)
    ax.text(4.9, 2.4, "cylinder MAL20×150", ha="center", fontsize=8)
    line([(2.7, 3.0), (3.0, 3.0), (3.0, 2.75), (3.6, 2.75)])
    line([(6.7, 3.0), (6.45, 3.0), (6.45, 3.25), (6.2, 3.25)])
    ax.text(0.0, 0.2, "All valves normally closed. Fill = P←supply, A→chamber, R plugged. "
            "Vent = P←chamber, A→silencer, R plugged.\nTubes between valves and cylinder < 30 cm. "
            "All 4 mm tube except the compressor hose.", fontsize=7.5)
    ax.set_xlim(-0.3, 10.2)
    ax.set_ylim(0, 7.1)
    ax.axis("off")
    ax.set_title("Pneumatic diagram test 1", fontsize=10)
    save(fig, "pneumatics")


def wiring():
    """Wiring diagram (schemdraw)."""
    import schemdraw
    import schemdraw.elements as elm
    schemdraw.use("matplotlib")
    with schemdraw.Drawing(show=False, fontsize=9) as d:
        d.config(unit=2.0)
        pico = elm.Ic(pins=[elm.IcPin(name="GP2", side="right", anchorname="gp2"),
                            elm.IcPin(name="GP3", side="right", anchorname="gp3"),
                            elm.IcPin(name="GP4", side="right", anchorname="gp4"),
                            elm.IcPin(name="GP5", side="right", anchorname="gp5"),
                            elm.IcPin(name="GP28 ADC2", side="left", anchorname="adc2"),
                            elm.IcPin(name="GP27 ADC1", side="left", anchorname="adc1"),
                            elm.IcPin(name="GP26 ADC0", side="left", anchorname="adc0"),
                            elm.IcPin(name="3V3", side="left", anchorname="v33"),
                            elm.IcPin(name="GND", side="bottom", anchorname="gnd")],
                      size=(5.5, 11), label="Pico 2\nUSB → PC")
        d += pico
        uln = (elm.Ic(pins=[elm.IcPin(name="IN1", pin="1", side="left", anchorname="in1"),
                            elm.IcPin(name="IN2", pin="2", side="left", anchorname="in2"),
                            elm.IcPin(name="IN3", pin="3", side="left", anchorname="in3"),
                            elm.IcPin(name="IN4", pin="4", side="left", anchorname="in4"),
                            elm.IcPin(name="OUT1", pin="18", side="right", anchorname="o1"),
                            elm.IcPin(name="OUT2", pin="17", side="right", anchorname="o2"),
                            elm.IcPin(name="OUT3", pin="16", side="right", anchorname="o3"),
                            elm.IcPin(name="OUT4", pin="15", side="right", anchorname="o4"),
                            elm.IcPin(name="COM", pin="10", side="top", anchorname="com"),
                            elm.IcPin(name="GND", pin="9", side="bottom", anchorname="gnd")],
                       size=(3, 11), label="ULN2803A")
               .anchor("in1").at((pico.gp2[0] + 4, pico.gp2[1])))
        d += uln
        for a, b in (("gp2", "in1"), ("gp3", "in2"), ("gp4", "in3"), ("gp5", "in4")):
            d += elm.Wire("-").at(getattr(pico, a)).to(getattr(uln, b))
        rail_y = uln.com[1] + 2.0
        names = ("V1 fill A", "V2 vent A", "V3 fill B", "V4 vent B")
        xs = []
        for i, o in enumerate(("o1", "o2", "o3", "o4")):
            pt = getattr(uln, o)
            x = uln.o1[0] + 1.5 + i * 2.4
            xs.append(x)
            d += elm.Wire("-").at(pt).to((x, pt[1]))
            d += elm.Line().at((x, pt[1])).to((x, rail_y - 2.2))
            d += elm.Inductor2(loops=3).at((x, rail_y - 2.2)).up().to((x, rail_y)).label(names[i], loc="bottom", ofst=0.2)
        x_hv = xs[-1] + 2.6
        d += elm.Line().at((uln.com[0], rail_y)).to((x_hv, rail_y))
        d += elm.Wire("-").at(uln.com).to((uln.com[0], rail_y))
        d += elm.Dot().at((uln.com[0], rail_y))
        d += elm.Inductor2(loops=3).at((x_hv, rail_y)).down().length(3).label("main valve\n3V210-08", loc="bottom")
        d += elm.Ground()
        d += elm.Label().at(((uln.com[0] + x_hv) / 2, rail_y + 0.5)).label("+24 V after e-stop (red wire of all coils)")
        d += elm.Ground().at(uln.gnd)
        d += elm.Ground().at(pico.gnd)
        # e-stop and supply
        x_in = pico.adc0[0] - 11
        d += elm.Switch(nc=True).at((uln.com[0], rail_y)).left().to((pico.gp2[0] - 1, rail_y)).label("e-stop (NC)")
        d += elm.Line().left().to((x_in, rail_y))
        d += elm.Dot(open=True).label("+24 V\nadapter", loc="left")
        # the 7805 is fed from the 24 V before the e-stop
        x_reg = x_in + 2.0
        d += elm.Dot().at((x_reg, rail_y))
        d += elm.Line().at((x_reg, rail_y)).down().length(1.0)
        n_in = d.here
        d += elm.Capacitor().at(n_in).down().length(1.6).label("1 µF", loc="bottom")
        d += elm.Ground()
        reg = (elm.Ic(pins=[elm.IcPin(name="IN", pin="1", side="left", anchorname="vin"),
                            elm.IcPin(name="OUT", pin="3", side="right", anchorname="vout"),
                            elm.IcPin(name="GND", pin="2", side="bottom", anchorname="g")],
                      size=(2.6, 1.6), label="LM7805C", lblofst=0.9).anchor("vin").at((n_in[0] + 1.0, n_in[1])))
        d += elm.Line().at(n_in).to(reg.vin)
        d += reg
        d += elm.Ground().at(reg.g)
        d += elm.Line().at(reg.vout).right().length(1.2)
        n5 = d.here
        d += elm.Capacitor().at(n5).down().length(1.6).label("100 nF", loc="bottom")
        d += elm.Ground()
        d += elm.Line().at(n5).right().length(0.8)
        d += elm.Dot(open=True).label("+5 V → red wire\npressure sensors", loc="right")
        # pressure sensors: signal → 10 kΩ → node → ADC; 15 kΩ node → GND
        for pin, name in (("adc1", "signal pressure sensor A"), ("adc2", "signal pressure sensor B")):
            pp = getattr(pico, pin)
            d += elm.Line().at(pp).left().length(1.2)
            node = d.here
            d += elm.Dot()
            d += elm.Resistor().left().length(2.2).label("10 kΩ", loc="top")
            d += elm.Dot(open=True).label(name, loc="left")
            d += elm.Resistor().at(node).down().length(1.4).label("15 kΩ", loc="bottom")
            d += elm.Ground()
        # potentiometer between 3V3 and GND (horizontal), wiper to ADC0
        pot = elm.Potentiometer().at(pico.v33).left().length(2.6).label("potentiometer KTC 5 kΩ", loc="top")
        d += pot
        d += elm.Ground().at(pot.end)
        d += elm.Wire("|-").at(pot.tap).to(pico.adc0)
        d.save(os.path.join(OUT, "wiring.svg"))
        d.save(os.path.join(OUT, "wiring.png"), dpi=150)


def wiring_list():
    """Connection list as a table figure (always readable, also when printed)."""
    rows = [
        ("Pico GP2", "ULN2803A IN1 (pin 1)", "V1 fill A"),
        ("Pico GP3", "ULN2803A IN2 (pin 2)", "V2 vent A"),
        ("Pico GP4", "ULN2803A IN3 (pin 3)", "V3 fill B"),
        ("Pico GP5", "ULN2803A IN4 (pin 4)", "V4 vent B"),
        ("ULN2803A OUT1–OUT4 (pin 18–15)", "black wire V1–V4", "red of V1–V4 → +24 V after e-stop"),
        ("ULN2803A COM (pin 10)", "+24 V after e-stop", "flyback diodes"),
        ("ULN2803A GND (pin 9)", "GND (adapter minus)", ""),
        ("+24 V adapter", "e-stop NC", "→ +24 V after e-stop"),
        ("+24 V after e-stop", "main valve 3V210-08", "other side of coil → GND"),
        ("+24 V adapter (before e-stop)", "LM7805C IN (pin 1)", "1 µF IN–GND"),
        ("LM7805C OUT (pin 3)", "red wire pressure sensors A and B", "100 nF OUT–GND"),
        ("pressure sensor A signal", "10 kΩ → GP27, 15 kΩ GP27→GND", "100 nF GP27→GND"),
        ("pressure sensor B signal", "10 kΩ → GP28, 15 kΩ GP28→GND", "100 nF GP28→GND"),
        ("potentiometer ends", "Pico 3V3 (pin 36) and GND", ""),
        ("potentiometer wiper", "Pico GP26/ADC0", "100 nF GP26→GND"),
        ("all GND", "Pico GND, ULN pin 9, 7805 pin 2, adapter minus, sensor black wires", "one common ground"),
    ]
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.axis("off")
    t = ax.table(cellText=rows, colLabels=("from", "to", "note"), loc="center", cellLoc="left",
                 colWidths=(0.3, 0.42, 0.28))
    t.auto_set_font_size(False)
    t.set_fontsize(8.5)
    t.scale(1, 1.45)
    ax.set_title("Wiring test 1 — connection list", fontsize=10)
    save(fig, "wiring_list")


# --- Breadboard layout -------------------------------------------------------------
# 830-point breadboard seen from above: columns 1–63, rows a–e and f–j, a rail pair on
# each side. Hole positions in units of 0.1" (2.54 mm).
BB_ROWS = dict(a=12, b=11, c=10, d=9, e=8, f=5, g=4, h=3, i=2, j=1,
               top_plus=15, top_gnd=14, bot_gnd=-1, bot_plus=-2)
# Pico 2 pin numbers (USB to the left, components up: pins 1–20 along row h from the
# left, pins 21–40 back along row c, so pin 40 is top left)
PICO_PIN = dict(GP0=1, GP1=2, GP2=4, GP3=5, GP4=6, GP5=7, GP26=31, GP27=32, GP28=34,
                AGND=33, V3V3=36, GND_TOP=38, GND_BOT=3)
ULN_COL = 37                 # column of ULN2803A pin 1 / 18 (notch to the left)
REG_COL = 57                 # LM7805C IN, GND, OUT in columns 57, 58, 59
DIV_COLS = ((23, 27), (30, 34))   # pressure sensor A, B: signal in, divider node


def pico_hole(name):
    n = PICO_PIN[name]
    return (n, "h") if n <= 20 else (41 - n, "c")


def bb_parts():
    """Everything on the breadboard: (kind, hole, hole or None, colour, label).
    kind: jumper, res, cap, wire (off-board wire up out of the drawing)."""
    gp = {k: f"GP{v}" for k, v in P.PINS.items()}
    top = lambda col, row: (col, row)  # noqa: E731
    parts = []
    # Pico ground to both GND rails
    c, _ = pico_hole("GND_TOP")
    parts.append(("jumper", (c, "a"), (c, "top_gnd"), "k", "Pico GND (pin 38) → GND rail"))
    c, _ = pico_hole("GND_BOT")
    parts.append(("jumper", (c, "i"), (c, "bot_gnd"), "k", "Pico GND (pin 3) → GND rail"))
    # valves: Pico → ULN2803A inputs, outputs → black coil wires
    for k, (key, valve) in enumerate((("fill_a", "V1 fill A"), ("vent_a", "V2 vent A"),
                                      ("fill_b", "V3 fill B"), ("vent_b", "V4 vent B"))):
        c, _ = pico_hole(gp[key])
        parts.append(("jumper", (c, "j"), (ULN_COL + k, "j"), "b", f"{gp[key]} → ULN IN{k + 1} (pin {k + 1})"))
        parts.append(("wire", (ULN_COL + k, "a"), None, "k", f"{valve} black"))
    com, hv = ULN_COL + 8, ULN_COL + 11
    parts.append(("jumper", (com, "j"), (com, "bot_gnd"), "k", "ULN GND (pin 9) → GND rail"))
    # +24 V after the e-stop: two joined columns, to COM and the red coil wires
    parts.append(("wire", (hv, "a"), None, "r", "+24 V after e-stop (red 0.5 mm²)"))
    parts.append(("jumper", (com, "a"), (hv, "b"), "r", "ULN COM (pin 10) → +24 V after e-stop"))
    parts.append(("jumper", (hv, "e"), (hv + 1, "e"), "r", "joins the two +24 V columns"))
    for row, valve in (((hv, "c"), "V1"), ((hv, "d"), "V2"), ((hv + 1, "a"), "V3"), ((hv + 1, "b"), "V4")):
        parts.append(("wire", row, None, "r", f"{valve} red"))
    # 5 V regulator, fed from the 24 V before the e-stop
    vin, g, vout = REG_COL, REG_COL + 1, REG_COL + 2
    parts.append(("wire", (vin, "a"), None, "r", "+24 V before e-stop (red 0.5 mm²)"))
    parts.append(("cap", (vin, "d"), (g, "d"), "c", "1 µF"))
    parts.append(("cap", (g, "e"), (vout, "e"), "c", "100 nF"))
    parts.append(("jumper", (g, "a"), (g, "top_gnd"), "k", "7805 GND → GND rail"))
    parts.append(("jumper", (vout, "a"), (vout, "top_plus"), "r", "7805 OUT → +5 V rail"))
    parts.append(("wire", (61, "top_gnd"), None, "k", "adapter minus (black 0.5 mm²)"))
    parts.append(("jumper", (62, "top_gnd"), (62, "bot_gnd"), "k", "joins both GND rails"))
    # pressure sensors: signal → 10 kΩ → node → Pico; 3× 47 kΩ (≈ 15 kΩ) node → GND
    top_k, bot_k = (v / 1000 for v in P.DIVIDER)
    for (cin, node), key, s in zip(DIV_COLS, ("adc_pa", "adc_pb"), "AB"):
        pc, _ = pico_hole(gp[key])
        parts.append(("wire", (cin - 1, "top_plus"), None, "r", f"sensor {s} red (+5 V)"))
        parts.append(("wire", (cin, "a"), None, "b", f"sensor {s} signal"))
        parts.append(("wire", (cin + 1, "top_gnd"), None, "k", f"sensor {s} black"))
        parts.append(("res", (cin, "c"), (node, "c"), "res", f"{top_k:g} kΩ"))
        parts.append(("res", (node, "a"), (node, "top_gnd"), "res", "3× 47 kΩ"))
        parts.append(("jumper", (pc, "b"), (node, "b"), "b", f"divider {s} → {gp[key]}"))
        parts.append(("cap", (pc, "a"), (pc + 0.4, "top_gnd"), "c", ""))
    # potentiometer: ends to 3V3 and AGND, wiper to the ADC with 100 nF
    c, _ = pico_hole(gp["adc_pos"])
    parts.append(("wire", (pico_hole("V3V3")[0], "a"), None, "r", "pot end (3V3)"))
    parts.append(("wire", (pico_hole("AGND")[0], "a"), None, "k", "pot end (AGND)"))
    parts.append(("wire", (c, "b"), None, "b", "pot wiper"))
    parts.append(("cap", (c, "a"), (c + 0.4, "top_gnd"), "c", ""))
    return parts


def breadboard():
    """Breadboard layout: top view with every part and wire on its hole."""
    from matplotlib.patches import Wedge
    colours = dict(r="#d62728", k="#222222", b="#1f5fbf", res="#c8a46e", c="#e8a33d")
    fig, ax = plt.subplots(figsize=(17, 8.5))
    Y = BB_ROWS

    def xy(h):
        return h[0], Y[h[1]]
    ax.add_patch(FancyBboxPatch((-0.2, -3.0), 64.4, 19.0, boxstyle="round,pad=0.2", fc="#f4f1ea", ec="#999"))
    ax.add_patch(Rectangle((-0.2, 6.0), 64.4, 1.0, fc="#e2ddd2", ec="none"))
    for row, y in Y.items():
        for col in range(1, 64):
            ax.add_patch(Rectangle((col - 0.18, y - 0.18), 0.36, 0.36, fc="#bbb", ec="none"))
    for y, colr, text in ((15.55, "r", "+5 V"), (13.45, "b", "GND"), (-0.45, "b", "GND"), (-2.55, "r", "not used")):
        ax.plot([0.3, 63.7], [y, y], color=colours["r"] if colr == "r" else colours["b"], lw=1)
        ax.text(64.6, y, text, va="center", fontsize=7.5)
    for col in (1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60):
        ax.text(col, 13.1, str(col), ha="center", va="center", fontsize=6, color="#666")
        ax.text(col, 0.0, str(col), ha="center", va="center", fontsize=6, color="#666")
    for row in "abcdefghij":
        ax.text(-0.9, Y[row], row, ha="center", va="center", fontsize=7, color="#666")
    # Pico (21 × 51 mm, pins in rows c and h)
    ax.add_patch(FancyBboxPatch((0.45, 2.35), 20.1, 8.3, boxstyle="round,pad=0.1", fc="#2e7d32", ec="k", alpha=0.85))
    ax.add_patch(Rectangle((-0.9, 5.5), 1.6, 2.0, fc="#aaa", ec="k"))
    ax.text(10.5, 6.5, "Raspberry Pi Pico 2 W\nUSB → PC (left), components up", ha="center", va="center",
            color="white", fontsize=9)
    names = {v: k.replace("V3V3", "3V3").replace("_TOP", "").replace("_BOT", "") for k, v in PICO_PIN.items()}
    for n in range(1, 41):
        col, row = (n, "h") if n <= 20 else (41 - n, "c")
        ax.add_patch(Rectangle((col - 0.22, Y[row] - 0.22), 0.44, 0.44, fc="gold", ec="k", lw=0.4))
        if n in names:
            ax.text(col, Y[row] + (-0.75 if row == "c" else 0.75), names[n], ha="center", va="center",
                    fontsize=5.5, color="white", rotation=90)
    # ULN2803A across the gap (pin 1 bottom left, notch left)
    ax.add_patch(Rectangle((ULN_COL - 0.5, 5.3), 8.9, 2.4, fc="#333", ec="k"))
    ax.add_patch(Wedge((ULN_COL - 0.5, 6.5), 0.45, -90, 90, fc="#f4f1ea"))
    ax.text(ULN_COL + 4, 6.5, "ULN2803A", ha="center", va="center", color="white", fontsize=8.5)
    for k in range(9):
        ax.text(ULN_COL + k, 4.35, str(k + 1), ha="center", fontsize=5.5, color="#333")
        ax.text(ULN_COL + k, 8.45, str(18 - k), ha="center", fontsize=5.5, color="#333")
    # LM7805C, legs IN–GND–OUT in row c, text facing the viewer (towards row e)
    ax.add_patch(Rectangle((REG_COL - 0.9, 10.25), 3.8, 1.1, fc="#333", ec="k"))
    ax.add_patch(Rectangle((REG_COL - 0.9, 11.35), 3.8, 0.35, fc="#bbb", ec="k"))
    for k, t in enumerate(("IN", "GND", "OUT")):
        ax.text(REG_COL + k, 10.75, t, ha="center", va="center", fontsize=5.5, color="white")
        ax.add_patch(Rectangle((REG_COL + k - 0.2, Y["c"] - 0.2), 0.4, 0.4, fc="#aaa", ec="k", lw=0.4))
    ax.text(REG_COL + 1, 9.5 - 2.8, "LM7805C\n(text side towards row e)", ha="center", va="top", fontsize=7)
    ax.text(11.0, 12.8, "← 3× 100 nF, ADC pins to GND", fontsize=6, va="center")
    ins = ", ".join(f"GP{P.PINS[k]} → pin {i + 1}" for i, k in enumerate(("fill_a", "vent_a", "fill_b", "vent_b")))
    ax.text(28.5, 2.0, f"valve wires: {ins}", fontsize=7, ha="center", va="center",
            bbox=dict(fc="#f4f1ea", ec="none", pad=0.5))
    # parts and wires
    parts = bb_parts()
    wires = sorted((p for p in parts if p[0] == "wire"), key=lambda p: (p[1][0], -Y[p[1][1]]))
    label_x, last = {}, -9.0
    for p in wires:
        last = max(p[1][0], last + 1.0)
        label_x[id(p)] = last
    bottom_arc = 0
    for p in parts:
        kind, a, b, col, label = p
        x0, y0 = xy(a)
        if kind == "jumper":
            x1, y1 = xy(b)
            if y0 == y1:                     # same row: arc, above the top half, below the bottom half
                if y0 < 6:
                    h = -(1.4 + 0.7 * bottom_arc)
                    bottom_arc += 1
                else:
                    h = 1.0 + 0.06 * abs(x1 - x0)
                t = np.linspace(0, 1, 40)
                bx = x0 + (x1 - x0) * t
                by = y0 + 2 * h * t * (1 - t)
                ax.plot(bx, by, color=colours[col], lw=2.2, solid_capstyle="round")
            else:
                ax.plot([x0, x1], [y0, y1], color=colours[col], lw=2.2, solid_capstyle="round")
            for x, y in ((x0, y0), (x1, y1)):
                ax.plot(x, y, "o", ms=3.5, color=colours[col])
        elif kind == "res":
            x1, y1 = xy(b)
            ax.plot([x0, x1], [y0, y1], color="#777", lw=1)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            w, h = (1.8, 0.5) if y0 == y1 else (0.5, 1.1)
            ax.add_patch(FancyBboxPatch((mx - w / 2, my - h / 2), w, h, boxstyle="round,pad=0.05",
                                        fc=colours["res"], ec="k", lw=0.5, zorder=3))
            if y0 == y1:
                ax.text(mx, my + 0.4, label, ha="center", va="bottom", fontsize=6.5, zorder=4)
            else:
                ax.text(mx + 0.45, my, label, ha="left", va="center", fontsize=6.5, zorder=4)
        elif kind == "cap":
            x1, y1 = xy(b)
            ax.plot([x0, x1], [y0, y1], color="#777", lw=1)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            ax.add_patch(Circle((mx, my), 0.3, fc=colours["c"], ec="k", lw=0.5, zorder=3))
            ax.text(mx + 0.38, my, label, fontsize=5.5, va="center", zorder=4)
        elif kind == "wire":
            lx = label_x[id(p)]
            ax.plot([x0, x0 + (lx - x0) * 0.15, lx, lx], [y0, y0 + 0.6, 17.0, 17.6], color=colours[col], lw=1.6)
            ax.plot(x0, y0, "o", ms=3.5, color=colours[col])
            ax.text(lx, 17.8, label, rotation=90, ha="center", va="bottom", fontsize=6.5)
    ax.set_xlim(-2.5, 67)
    ax.set_ylim(-4, 31)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Breadboard test 1 — top view. Jumpers: red = plus, black = ground, blue = signal. "
                 "Wires going up leave the board.\nThe Pico runs on USB: nothing on VSYS/VBUS. "
                 "The 3× 47 kΩ per sensor are soldered into one bundle (≈ 15.7 kΩ).", fontsize=9)
    save(fig, "breadboard")


def cut_plan():
    """Saw plan for the DIY store: all plywood parts from one 1220 × 610 sheet (through cuts only)."""
    W, H, k = 1220.0, 610.0, 4.0                     # sheet, saw kerf
    bl, bw = P.BASE["length"], P.BASE["width"]
    ch, cd = P.CHEEK["height"], P.CHEEK["depth"]
    sb = P.SPACER_BLOCK["length"]
    wood, rest = "#e8d3a8", "#f4f4f4"
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.add_patch(Rectangle((0, 0), W, H, fc=rest, ec="k", lw=1.2))
    # left: cheeks and block strip (cut 1 at x = 450)
    y = H
    parts = []
    for name in ("cheek 1", "cheek 2"):
        parts.append(((0, y - cd), ch, cd, f"{name}\n{ch:.0f} × {cd:.0f}"))
        y -= cd + k
    for i in range(2):
        parts.append(((i * (sb + k), y - sb), sb, sb, f"block\n{i + 1}"))
    strip_y = y - sb
    left_rest = strip_y - k
    # right: base plate (cut 5 at x = 450 + k + 400, cut 6 at y = 300)
    bx = ch + k
    parts.append(((bx, H - bw), bl, bw, f"base plate\n{bl:.0f} × {bw:.0f}"))
    for (x, yy), w, h, txt in parts:
        ax.add_patch(Rectangle((x, yy), w, h, fc=wood, ec="k"))
        ax.text(x + w / 2, yy + h / 2, txt, ha="center", va="center", fontsize=9 if w > 100 else 7)
    ax.add_patch(Rectangle((2 * (sb + k), strip_y), ch - 2 * (sb + k), sb, fc=rest, ec="k", ls=":"))
    ax.text(2 * (sb + k) + (ch - 2 * (sb + k)) / 2, strip_y + sb / 2, "rest of the block strip", ha="center",
            va="center", fontsize=7, color="0.4")
    ax.text(ch / 2, left_rest / 2, f"leftover {ch:.0f} × {left_rest:.0f}\n(2 discs Ø80 for the load, at home)",
            ha="center", va="center", fontsize=8, color="0.4")
    ax.text(bx + bl / 2, (H - bw - k) / 2, f"leftover {bl:.0f} × {H - bw - k:.0f}", ha="center", va="center",
            fontsize=8, color="0.4")
    rx = bx + bl + k
    ax.text(rx + (W - rx) / 2, H / 2, f"leftover\n{W - rx:.0f} × {H:.0f}", ha="center", va="center", fontsize=8,
            color="0.4")
    # cut lines with their order
    cuts = [((ch + k / 2, -15), (ch + k / 2, H + 15), "1"),
            ((-15, H - cd - k / 2), (ch + 15, H - cd - k / 2), "2"),
            ((-15, H - 2 * cd - 1.5 * k), (ch + 15, H - 2 * cd - 1.5 * k), "3"),
            ((-15, strip_y - k / 2), (ch + 15, strip_y - k / 2), "4"),
            ((sb + k / 2, strip_y - 10), (sb + k / 2, strip_y + sb + 10), "7"),
            ((2 * sb + 1.5 * k, strip_y - 10), (2 * sb + 1.5 * k, strip_y + sb + 10), "8"),
            ((rx - k / 2, -15), (rx - k / 2, H + 15), "5"),
            ((rx + 15, H - bw - k / 2), (bx - 15, H - bw - k / 2), "6")]
    for (x0, y0), (x1, y1), n in cuts:
        ax.plot([x0, x1], [y0, y1], color="red", lw=1.0, ls="--")
        ax.text(x0, y0, n, color="white", fontsize=8, ha="center", va="center", fontweight="bold",
                bbox=dict(boxstyle="circle,pad=0.25", fc="red", ec="none"))
    dim(ax, (0, H), (W, H), 45, f"{W:.0f}")
    dim(ax, (0, 0), (0, H), 55, f"{H:.0f}")
    dim(ax, (0, 0), (ch, 0), -45, f"{ch:.0f}")
    dim(ax, (bx, 0), (bx + bl, 0), -45, f"{bl:.0f}")
    dim(ax, (rx, H - bw), (rx, H), -35, f"{bw:.0f}", side=1)
    ax.text(0, -150,
            f"Plywood {P.BASE['thickness']:.0f} mm, one sheet 1220 × 610. Through cuts in the numbered order; "
            f"saw kerf ≈ {k:.0f} mm, already left between the parts.\n"
            f"Cut list: 1 base plate {bl:.0f} × {bw:.0f}, 2 cheeks {ch:.0f} × {cd:.0f}, "
            f"2 blocks {sb:.0f} × {sb:.0f}. Cut both cheeks at the same saw setting, so they are exactly alike.\n"
            f"If the saw will not take pieces as small as {sb:.0f} × {sb:.0f}: stop after cut 4 and saw the "
            "2 blocks from the strip at home (cuts 7 and 8). Keep all leftovers.\n"
            "Dimensions in mm.", fontsize=9, va="top")
    ax.set_aspect("equal")
    ax.set_xlim(-90, W + 80)
    ax.set_ylim(-260, H + 90)
    ax.axis("off")
    save(fig, "cut_plan")


def main():
    cut_plan()
    cheek()
    arm()
    side_view()
    pneumatics()
    wiring_list()
    breadboard()
    try:
        wiring()
    except Exception as e:  # noqa: BLE001
        print("wiring diagram (schemdraw) skipped:", e)
    print("drawings in", OUT)


if __name__ == "__main__":
    main()

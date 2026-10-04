"""Tekeningen van test 1 (uit params.py): maattekeningen, bedrading en pneumatiek.

Uitvoer in out/tekeningen/ als PNG en PDF.
"""
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

import params as P  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "tekeningen")


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), dpi=150, bbox_inches="tight")
    plt.close(fig)


def dim(ax, a, b, off, text, side=1, fs=8):
    """Maatlijn van a naar b, `off` mm verschoven (loodrecht)."""
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


def wang():
    x0, x1 = P.CHEEK_X
    h = P.CHEEK["height"]
    fig, ax = plt.subplots(figsize=(5.5, 9))
    ax.add_patch(Rectangle((x0, 0), x1 - x0, h, fc="#e8d3a8", ec="k"))
    holes = [(P.HINGE, 22.0, "Ø22 × 7 diep (lager 608)\n+ Ø10 door"), (P.REAR_PIVOT, 8.5, "Ø8,5 door"),
             ((x0 + 30, 20.0), 5.0, "Ø5 (schroef blok)"), ((x0 + 30, 45.0), 5.0, "Ø5 (schroef blok)")]
    for (cx, cz), d, txt in holes:
        ax.add_patch(Circle((cx, cz), d / 2, fc="white", ec="k"))
        ax.text(cx + 14, cz + (6 if d > 6 else -10), txt, fontsize=7)
    dim(ax, (x0, h), (x1, h), 18, f"{x1 - x0:.0f}")
    dim(ax, (x0, 0), (x0, h), 30, f"{h:.0f}", side=1)
    dim(ax, (x1, 0), (x1, P.HINGE[1]), -25, f"{P.HINGE[1]:.0f}", side=1)
    dim(ax, (x1, 0), (x1, P.REAR_PIVOT[1]), -55, f"{P.REAR_PIVOT[1]:.0f}", side=1)
    dim(ax, (x0, P.HINGE[1] + 5), (P.HINGE[0], P.HINGE[1] + 5), 0, f"{P.HINGE[0] - x0:.0f}", fs=7)
    dim(ax, (x0, 32), (x0 + 30, 32), 0, "30", fs=7)
    ax.text(x0 + 32, 2, "gaatjes op 20 en 45 hoog", fontsize=6.5)
    ax.text(x0 - 8, h / 2, "achterkant", rotation=90, ha="right", va="center", fontsize=7, color="0.4")
    ax.text(x1 + 8, h / 2 - 60, "voorkant\n(arm)", ha="left", va="center", fontsize=7, color="0.4")
    ax.text(0, -40, f"Wang — 2 stuks, multiplex {P.CHEEK['thickness']:.0f} mm\n"
            "Lagerzitting aan de BUITENkant (spiegelbeeld bij de tweede wang)\nmaten in mm", ha="center", fontsize=8)
    ax.set_aspect("equal")
    ax.set_xlim(x0 - 90, x1 + 120)
    ax.set_ylim(-70, h + 60)
    ax.axis("off")
    save(fig, "wang")


def arm():
    L, H = P.ARM["length"], P.ARM["height"]
    x0 = -P.ARM_BEHIND
    fig, ax = plt.subplots(figsize=(11, 2.8))
    ax.add_patch(Rectangle((x0, -H / 2), L, H, fc="#d0d4da", ec="k"))
    for x, txt in ((0.0, "scharnier"), (P.ARM_ATTACH, "vorkkop"), (P.ARM_TIP, "last")):
        ax.add_patch(Circle((x, 0), P.ARM_HOLE / 2, fc="white", ec="k"))
        ax.text(x, -H / 2 - 10, f"{txt}\nØ{P.ARM_HOLE}", ha="center", va="top", fontsize=7)
    dim(ax, (x0, H / 2), (x0 + L, H / 2), 22, f"{L:.0f}")
    dim(ax, (x0, H / 2), (0, H / 2), 10, f"{P.ARM_BEHIND:.0f}", fs=7)
    dim(ax, (0, H / 2), (P.ARM_ATTACH, H / 2), 10, f"{P.ARM_ATTACH:.0f}", fs=7)
    dim(ax, (0, H / 2), (P.ARM_TIP, H / 2), 36, f"{P.ARM_TIP:.0f}", fs=7)
    dim(ax, (x0 + L, -H / 2), (x0 + L, H / 2), -14, f"{H:.0f}", fs=7)
    ax.text(x0, -H / 2 - 40, f"Arm — aluminium platstrip {H:.0f}×{P.ARM['thickness']:.0f} mm, gaten midden op de hoogte; maten in mm",
            fontsize=8)
    ax.set_aspect("equal")
    ax.set_xlim(x0 - 20, x0 + L + 40)
    ax.set_ylim(-H / 2 - 55, H / 2 + 50)
    ax.axis("off")
    save(fig, "arm")


def zijaanzicht():
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cad"))
    from parts import pose
    fig, ax = plt.subplots(figsize=(10, 7.5))
    bx0, bx1 = P.BASE_X
    ax.add_patch(Rectangle((bx0, -P.BASE["thickness"]), bx1 - bx0, P.BASE["thickness"], fc="#e8d3a8", ec="k"))
    ax.add_patch(Rectangle((bx0 - 150, -P.BASE["thickness"] - 30), bx1 - bx0 + 160, 30, fc="#9c7b58", ec="k", alpha=0.5))
    ax.text(bx0 - 140, -P.BASE["thickness"] - 22, "tafel", fontsize=7)
    ax.add_patch(Rectangle((P.CHEEK_X[0], 0), P.CHEEK_X[1] - P.CHEEK_X[0], P.CHEEK["height"], fc="#e8d3a8", ec="k", alpha=0.6))
    hx, hz = P.HINGE
    rx, rz = P.REAR_PIVOT
    for th, ls, col, lab in ((P.THETA_MIN, ":", "0.5", f"laagste stand {P.THETA_MIN:.0f}°"),
                             (0.0, "-", "k", "horizontaal"),
                             (P.THETA_MAX, ":", "0.5", f"hoogste stand {P.THETA_MAX:.0f}°")):
        t = math.radians(th)
        ex, ez = hx + (P.ARM["length"] - P.ARM_BEHIND) * math.cos(t), hz + (P.ARM["length"] - P.ARM_BEHIND) * math.sin(t)
        ax.plot([hx - P.ARM_BEHIND * math.cos(t), ex], [hz - P.ARM_BEHIND * math.sin(t), ez], ls, color=col, lw=4 if ls == "-" else 1.5)
        ax_, az_ = hx + P.ARM_ATTACH * math.cos(t), hz + P.ARM_ATTACH * math.sin(t)
        ax.plot([rx, ax_], [rz, az_], ls, color="C0" if ls == "-" else "0.6", lw=6 if ls == "-" else 1)
        if ls != "-":
            ax.text(ex + 8, ez, lab, fontsize=7, color="0.4", va="center")
    t0 = pose(0.0)
    for (x, z), name, dz in ((P.HINGE, "scharnier", 28), (P.REAR_PIVOT, "draaipunt cilinder", 0)):
        ax.add_patch(Circle((x, z), 6, fc="white", ec="k", zorder=5))
        ax.text(x - 70, z + dz, name, ha="right", va="center", fontsize=8,
                bbox=dict(fc="white", ec="none", pad=0.5))
    tipx, tipz = hx + P.ARM_TIP, hz
    ax.plot([tipx, tipx], [tipz, tipz - 60], "k", lw=0.8)
    ax.add_patch(Rectangle((tipx - 45, tipz - 310), 90, 250, fc="#a9cbe8", ec="k", alpha=0.7))
    ax.text(tipx, tipz - 185, f"last\n{P.TIP_MASS} kg", ha="center", fontsize=8)
    dim(ax, (P.CHEEK_X[1], hz), (P.CHEEK_X[1], rz), -40, f"{hz - rz:.0f}")
    dim(ax, (hx, 0), (hx, hz), 150, f"{hz:.0f}")
    dim(ax, (hx, hz), (hx + P.ARM_ATTACH, hz), 25, f"{P.ARM_ATTACH:.0f}")
    dim(ax, (hx, hz), (hx + P.ARM_TIP, hz), 55, f"{P.ARM_TIP:.0f}")
    dim(ax, (bx0, -P.BASE["thickness"]), (bx1, -P.BASE["thickness"]), -60, f"{bx1 - bx0:.0f}")
    ax.text(rx + 175, rz + 40, f"cilinder MAL20×150\npen–pen {P.PIN_TO_PIN_MIN:.0f}–{P.PIN_TO_PIN_MAX:.0f} mm\n"
            f"bij 0°: {t0['L']:.0f} mm", fontsize=8, color="C0")
    ax.set_aspect("equal")
    ax.set_xlim(bx0 - 160, hx + P.ARM["length"] + 120)
    ax.set_ylim(-140, hz + P.ARM["length"] * math.sin(math.radians(P.THETA_MAX)) + 40)
    ax.set_title("Test 1 — zijaanzicht (maten in mm)", fontsize=10)
    ax.axis("off")
    save(fig, "zijaanzicht")


def pneumatiek():
    fig, ax = plt.subplots(figsize=(11, 7))

    def box(x, y, w, h, text, fc="#f2f2f2"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05", fc=fc, ec="k"))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8)

    def line(pts, **kw):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=kw.get("color", "k"), lw=kw.get("lw", 1.4))

    box(0.0, 6.0, 1.6, 0.8, "compressor\n24 l, 8 bar", "#dfe8f5")
    box(2.1, 6.0, 1.6, 0.8, "filter +\ndrukregelaar\nAFR-2000", "#dfe8f5")
    box(4.2, 6.0, 1.6, 0.8, "afsluitschuif\nHSV-08", "#dfe8f5")
    box(6.3, 6.0, 1.6, 0.8, "hoofdventiel\n3V210-08 (NC)\n24 V via noodstop", "#fde7c8")
    line([(1.6, 6.4), (2.1, 6.4)])
    line([(3.7, 6.4), (4.2, 6.4)])
    line([(5.8, 6.4), (6.3, 6.4)])
    line([(7.9, 6.4), (8.6, 6.4), (8.6, 5.3)])
    ax.text(8.7, 5.9, "4 mm", fontsize=7)
    line([(2.7, 5.3), (8.6, 5.3)])
    ax.plot([8.6], [5.3], "ko", ms=4)
    ax.text(8.65, 5.15, "T-stuk", fontsize=7)
    # kamers
    for xc, k, vul, leeg in ((2.7, "A", "V1", "V2"), (6.7, "B", "V3", "V4")):
        line([(xc, 5.3), (xc, 4.6)])
        ax.text(xc + 0.05, 5.0, "(smoorventiel,\nlater)", fontsize=6, color="0.4")
        box(xc - 0.6, 3.8, 1.2, 0.8, f"{vul}\nvul {k}\nVQ110U", "#fde7c8")
        line([(xc, 3.8), (xc, 3.0)])
        ax.plot([xc], [3.0], "ko", ms=4)
        sx = xc - 2.0 if k == "A" else xc + 0.8
        box(sx, 2.7, 1.2, 0.6, f"druksensor\np{k} (G1/4)", "#e3f2e1")
        line([(xc, 3.0), (sx + (1.2 if k == "A" else 0.0), 3.0)])
        line([(xc, 3.0), (xc, 2.2)])
        box(xc - 0.6, 1.4, 1.2, 0.8, f"{leeg}\nleeg {k}\nVQ110U", "#fde7c8")
        line([(xc, 1.4), (xc, 0.9)])
        ax.text(xc, 0.75, "M5-demper", ha="center", fontsize=7)
    # cilinder
    ax.add_patch(Rectangle((3.6, 2.6), 2.6, 0.8, fc="#d0d4da", ec="k"))
    ax.plot([4.9, 4.9], [2.6, 3.4], "k", lw=3)
    ax.plot([4.9, 6.2], [2.95, 2.95], "k", lw=2)
    ax.text(4.25, 3.0, "kamer A", ha="center", va="center", fontsize=8)
    ax.text(5.55, 3.15, "kamer B", ha="center", va="center", fontsize=8)
    ax.text(4.9, 2.4, "cilinder MAL20×150", ha="center", fontsize=8)
    line([(2.7, 3.0), (3.0, 3.0), (3.0, 2.75), (3.6, 2.75)])
    line([(6.7, 3.0), (6.45, 3.0), (6.45, 3.25), (6.2, 3.25)])
    ax.text(0.0, 0.2, "Alle ventielen normaal gesloten. Vul = P←voeding, A→kamer, R dicht. "
            "Leeg = P←kamer, A→demper, R dicht.\nSlangen tussen ventielen en cilinder < 30 cm. "
            "Alles 4 mm slang, behalve de compressorslang.", fontsize=7.5)
    ax.set_xlim(-0.3, 10.2)
    ax.set_ylim(0, 7.1)
    ax.axis("off")
    ax.set_title("Pneumatisch schema test 1", fontsize=10)
    save(fig, "pneumatiek")


def bedrading():
    """Elektrisch schema (schemdraw)."""
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
                      size=(5.5, 11), label="Pico 2\nUSB → pc")
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
        names = ("V1 vul A", "V2 leeg A", "V3 vul B", "V4 leeg B")
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
        d += elm.Inductor2(loops=3).at((x_hv, rail_y)).down().length(3).label("hoofdventiel\n3V210-08", loc="bottom")
        d += elm.Ground()
        d += elm.Label().at(((uln.com[0] + x_hv) / 2, rail_y + 0.5)).label("+24 V ná noodstop (rood van alle spoelen)")
        d += elm.Ground().at(uln.gnd)
        d += elm.Ground().at(pico.gnd)
        # noodstop en voeding
        x_in = pico.adc0[0] - 11
        d += elm.Switch(nc=True).at((uln.com[0], rail_y)).left().to((pico.gp2[0] - 1, rail_y)).label("noodstop (NC)")
        d += elm.Line().left().to((x_in, rail_y))
        d += elm.Dot(open=True).label("+24 V\nadapter", loc="left")
        # 7805 hangt vóór de noodstop aan de 24 V
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
        d += elm.Dot(open=True).label("+5 V → rood\ndruksensoren", loc="right")
        # druksensoren: signaal → 10 kΩ → knooppunt → ADC; 15 kΩ knooppunt → GND
        for pin, name in (("adc1", "signaal druksensor A"), ("adc2", "signaal druksensor B")):
            pp = getattr(pico, pin)
            d += elm.Line().at(pp).left().length(1.2)
            node = d.here
            d += elm.Dot()
            d += elm.Resistor().left().length(2.2).label("10 kΩ", loc="top")
            d += elm.Dot(open=True).label(name, loc="left")
            d += elm.Resistor().at(node).down().length(1.4).label("15 kΩ", loc="bottom")
            d += elm.Ground()
        # potmeter tussen 3V3 en GND (horizontaal), loper naar ADC0
        pot = elm.Potentiometer().at(pico.v33).left().length(2.6).label("potmeter KTC 5 kΩ", loc="top")
        d += pot
        d += elm.Ground().at(pot.end)
        d += elm.Wire("|-").at(pot.tap).to(pico.adc0)
        d.save(os.path.join(OUT, "bedrading.svg"))
        d.save(os.path.join(OUT, "bedrading.png"), dpi=150)


def bedrading_simple():
    """Overzichtelijk aansluitschema als tabel-figuur (altijd leesbaar, ook geprint)."""
    rows = [
        ("Pico GP2", "ULN2803A IN1 (pin 1)", "V1 vul A"),
        ("Pico GP3", "ULN2803A IN2 (pin 2)", "V2 leeg A"),
        ("Pico GP4", "ULN2803A IN3 (pin 3)", "V3 vul B"),
        ("Pico GP5", "ULN2803A IN4 (pin 4)", "V4 leeg B"),
        ("ULN2803A OUT1–OUT4 (pin 18–15)", "zwarte draad V1–V4", "rood van V1–V4 → +24 V na noodstop"),
        ("ULN2803A COM (pin 10)", "+24 V na noodstop", "vrijloopdiodes"),
        ("ULN2803A GND (pin 9)", "GND (min adapter)", ""),
        ("+24 V adapter", "noodstop NC", "→ +24 V na noodstop"),
        ("+24 V na noodstop", "hoofdventiel 3V210-08", "andere kant spoel → GND"),
        ("+24 V adapter (vóór noodstop)", "LM7805C IN (pin 1)", "1 µF IN–GND"),
        ("LM7805C OUT (pin 3)", "rood druksensor A en B", "100 nF OUT–GND"),
        ("druksensor A signaal", "10 kΩ → GP27, 15 kΩ GP27→GND", "100 nF GP27→GND"),
        ("druksensor B signaal", "10 kΩ → GP28, 15 kΩ GP28→GND", "100 nF GP28→GND"),
        ("potmeter uiteinden", "Pico 3V3 (pin 36) en GND", ""),
        ("potmeter loper", "Pico GP26/ADC0", "100 nF GP26→GND"),
        ("alle GND", "Pico GND, ULN pin 9, 7805 pin 2, adapter min, sensoren zwart", "één gemeenschappelijke massa"),
    ]
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.axis("off")
    t = ax.table(cellText=rows, colLabels=("van", "naar", "opmerking"), loc="center", cellLoc="left",
                 colWidths=(0.3, 0.42, 0.28))
    t.auto_set_font_size(False)
    t.set_fontsize(8.5)
    t.scale(1, 1.45)
    ax.set_title("Bedrading test 1 — aansluitlijst", fontsize=10)
    save(fig, "bedrading_lijst")


def main():
    wang()
    arm()
    zijaanzicht()
    pneumatiek()
    bedrading_simple()
    try:
        bedrading()
    except Exception as e:  # noqa: BLE001
        print("schema (schemdraw) overgeslagen:", e)
    print("tekeningen in", OUT)


if __name__ == "__main__":
    main()

"""Sizing of the full-size joint: 15 kg at 1 m, driven like test 2 (two cylinders standing
under a hub on the arm, pitch −60° … +75°). Prints the tables in docs/full-arm-sizing.md.

    python tools/full_arm_sizing.py

Flow model as in test 1 (ISO 6358, sonic conductance C and critical ratio b). Steady
speed with the arm horizontal: the fill valve feeds the piston side, the vent valve
empties the rod side; the rod-side pressure is chosen to give the highest speed.
"""
import math

G = 9.81
P_ATM = 1.013                       # bar absolute
P_SUPPLY = 5.0                      # bar gauge
LOAD, REACH = 15.0, 1.0             # kg, m
ARMS = {"arm 3 kg (one 1 m segment)": 3.0, "arm 30 kg (complete arm, from docs/2dof-joint.md)": 30.0}
MAX_RATIO = 0.40                    # static load / available torque (test 1 is designed at 30–39 %)
PEAK_RATIO = 0.70                   # same, for the rare peak: 15 kg at full reach, slow and briefly
WORK_REACH = 0.6                    # m: normal work, 15 kg held closer in
BORES = [(32, 12), (40, 16), (50, 20), (63, 20), (80, 25), (100, 25)]   # bore, rod (mm), ISO 15552
STROKES = [200, 250, 300, 320, 400, 500, 600, 700, 800]
SPAN = math.sin(math.radians(75)) + math.sin(math.radians(60))           # stroke / lever for −60 … +75°
VALVES = {"1 × VQ110U": 0.144, "4 × VQ110U": 0.576, "4V210 (5/2)": 2.8}  # C in dm³/(s·bar)


def gravity_torque(arm_mass):
    """Nm with the arm horizontal; the arm's centre of mass at half the reach."""
    return G * (LOAD * REACH + arm_mass * REACH / 2)


def work_torque(arm_mass):
    """Nm for normal work: 15 kg at WORK_REACH, arm bent so its centre of mass is at half that."""
    return G * (LOAD * WORK_REACH + arm_mass * WORK_REACH / 2)


def area(d):
    return math.pi * (d / 2) ** 2


def flow(p1, p2, C, b=0.3):
    """Nl/s through a valve, ISO 6358 (pressures absolute, bar)."""
    x = p2 / p1
    return C * p1 if x <= b else C * p1 * math.sqrt(max(0.0, 1 - ((x - b) / (1 - b)) ** 2))


def speed(bore, rod, lever_m, torque, C):
    """Highest steady cylinder speed (mm/s) lifting the arm at horizontal."""
    aa, ab = area(bore), area(bore) - area(rod)
    force = torque / (2 * lever_m)                  # N per cylinder
    ps = P_SUPPLY + P_ATM
    best = 0.0
    for i in range(1, 500):
        pb = P_ATM + 0.01 * i
        pa = (force + (pb - P_ATM) * 0.1 * ab) / (0.1 * aa) + P_ATM
        if pa >= ps:
            break
        va = flow(ps, pa, C) / pa * 1e6 / aa
        vb = flow(pb, P_ATM, C) / pb * 1e6 / ab
        best = max(best, min(va, vb))
    return best


def main():
    for name, arm_mass in ARMS.items():
        T = gravity_torque(arm_mass)
        print(f"\n## {name}: {T:.0f} Nm with the arm horizontal")
        print("| Lever | Cylinder | Stroke | Load | " + " | ".join(VALVES) + " |")
        for lever in (150, 250, 370):
            def ratio_of(b):
                return T / (2 * P_SUPPLY * 0.1 * area(b) * lever / 1000)
            bore, rod = next((b, r) for b, r in BORES if ratio_of(b) <= MAX_RATIO)
            ratio = ratio_of(bore)
            stroke = next(s for s in STROKES if s >= SPAN * lever * 0.98)
            v = [speed(bore, rod, lever / 1000, T, C) for C in VALVES.values()]
            cells = [f"{math.degrees(x / lever):.0f}°/s ({math.radians(math.degrees(x / lever)) * REACH:.2f} m/s)" for x in v]
            print(f"| {lever} mm | Ø{bore} | {stroke} mm | {ratio * 100:.0f}% | " + " | ".join(cells) + " |")
    print("\n## Load cases, lever 150 mm: smallest bore with work ≤ 40% and peak ≤ 70%")
    print("| Arm | Work (15 kg at 0.6 m) | Peak (15 kg at 1 m) | Cylinder | Work load | Peak load | Speed work / peak |")
    for name, arm_mass in ARMS.items():
        Tw, Tp = work_torque(arm_mass), gravity_torque(arm_mass)
        avail = {b: 2 * P_SUPPLY * 0.1 * area(b) * 0.150 for b, _ in BORES}
        bore, rod = next((b, r) for b, r in BORES if Tw / avail[b] <= MAX_RATIO and Tp / avail[b] <= PEAK_RATIO)
        v = [math.degrees(speed(bore, rod, 0.150, T, VALVES["1 × VQ110U"]) / 1000 / 0.150) for T in (Tw, Tp)]
        print(f"| {name} | {Tw:.0f} Nm | {Tp:.0f} Nm | Ø{bore} | {Tw / avail[bore] * 100:.0f}% | {Tp / avail[bore] * 100:.0f}% | {v[0]:.0f} / {v[1]:.0f}°/s |")
    print("\n## Speed with 1 × VQ110U per chamber, with and without the 15 kg")
    elbow_T = G * (LOAD * 0.5 + 1.5 * 0.25)       # 15 kg at 0.5 m, forearm 1.5 kg
    for name, bore, rod, lever, loaded, empty in (
            ("shoulder Ø50, lever 150", 50, 20, 0.150, gravity_torque(3.0), G * 3.0 * REACH / 2),
            ("shoulder Ø63, lever 150", 63, 20, 0.150, gravity_torque(3.0), G * 3.0 * REACH / 2),
            ("elbow Ø50, lever 100", 50, 20, 0.100, elbow_T, G * 1.5 * 0.25)):
        v = [math.degrees(speed(bore, rod, lever, T, VALVES["1 × VQ110U"]) / 1000 / lever) for T in (loaded, empty)]
        print(f"| {name} | {loaded:.0f} Nm | {v[0]:.0f}°/s | {v[1]:.0f}°/s |")
    print()
    for bore in (50, 63, 80):
        litres = 2 * area(bore) * SPAN * 150 / 1e6
        print(f"Ø{bore}, lever 150: {litres:.2f} l swept per full lift, ≈{litres * 3.5:.0f} Nl free air")

    light()


# Light version: 1.5 kg at 1 m (upper arm and forearm 0.5 m each)
LIGHT_MASSES = dict(tip=(1.5, 1.0, 0.5), wrist=(1.1, 0.95, 0.45), forearm=(0.5, 0.75, 0.25), upper=(1.2, 0.25, None))
# kg, distance from the shoulder and from the elbow with the arm stretched (m); wrist = wrist
# pitch motor + gripper rotation motor + gripper; upper arm includes the elbow cylinders
LIGHT_JOINTS = (("shoulder", 0, ((25, 10, 0.100), (32, 12, 0.100), (25, 10, 0.150))),
                ("elbow", 1, ((20, 8, 0.075), (25, 10, 0.050), (25, 10, 0.075))))


def light():
    print("\n## Light version: 1.5 kg at 1 m (work = 0.6 × peak)")
    print("| Joint | Peak / work torque | Cylinders | Lever | Peak load | Work load | Speed peak / empty, 1 × VQ110U |")
    for joint, k, options in LIGHT_JOINTS:
        Tp = G * sum(m * d[k] for m, *d in LIGHT_MASSES.values() if d[k] is not None)
        for bore, rod, lever in options:
            avail = 2 * P_SUPPLY * 0.1 * area(bore) * lever
            v = [math.degrees(speed(bore, rod, lever, T, VALVES["1 × VQ110U"]) / 1000 / lever) for T in (Tp, 0.01)]
            print(f"| {joint} | {Tp:.1f} / {0.6 * Tp:.1f} Nm | 2 × Ø{bore} | {lever * 1000:.0f} mm | {Tp / avail * 100:.0f}% | "
                  f"{0.6 * Tp / avail * 100:.0f}% | {v[0]:.0f} / {v[1]:.0f}°/s |")


if __name__ == "__main__":
    main()

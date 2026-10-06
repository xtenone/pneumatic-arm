"""Dimensions and sizing of the printed cycloidal drive for the test 1 arm.

Module name cyparams because test 1 already owns "params". Arm and load come from test 1,
the motor is the same NEMA23 closed-loop stepper as the harmonic drive reference
(../test1-harmonic-drive), so only the gearbox differs. Lengths in mm.

Layout (axis = z, z = 0 on the rear face, output towards +z):
rear plate | rear carrier flange | disc 1 | disc 2 | front carrier flange | front plate
The 25 housing pins and 6 output pins are steel dowel pins; discs, housing, carriers and
the cam are printed (PLA).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "test1-harmonic-drive"))
import hdparams as HD  # noqa: E402  (motor, arm and load case are shared)

T1 = HD.T1

# --- Cycloid --------------------------------------------------------------------------
N_PINS = 25                  # housing pins; the discs have N_PINS - 1 lobes
RATIO = N_PINS - 1           # 24:1, output turns opposite to the input
R_PINS = 45.0                # pin circle radius
D_PIN = 6.0                  # steel dowel pins Ø6
E = 1.2                      # eccentricity; E·N/R = 0.67 keeps the lobes round (min radius 3.4 mm)
CLEARANCE = 0.10             # profile offset for printing (backlash)

# --- Output pins (in the carriers, through holes in the discs) -----------------------
N_OUT = 6
R_OUT = 25.0
D_OUT = 6.0                  # steel dowel pins Ø6
OUT_HOLE = D_OUT + 2 * E + 0.4

# --- Stack along the axis -------------------------------------------------------------
PLATE_T = 10.0               # rear and front plate
FLANGE_T = 8.0               # carrier flange inside the housing
DISC_T = 10.0
GAP = 0.5                    # between flange, discs and plates
DISC_GAP = 1.0
FLANGE_R = 31.0
JOURNAL_D = 40.0             # carrier journal in the 6808 bearing
OUTPUT_EXT = 8.0             # front journal sticks out as the output face
HOUSING_R = 58.0             # outer radius (Ø116)
RING_BORE_R = R_PINS + D_PIN / 2   # pins lie against the ring bore
BOLT_R = 53.0                # 6 × M4 through the housing
PIN_HOLE_DEPTH = 4.0           # housing pin holes in both plates
OUT_HOLE_DEPTH = 7.0           # output pin holes in both carrier flanges (1 mm floor)
PIN_LEN = 45.0                 # standard dowel lengths that fit (checked in __main__)
OUT_PIN_LEN = 35.0

# --- Bought parts ---------------------------------------------------------------------
BEARINGS = {                 # name: (inner, outer, width)
    "6808": (40.0, 52.0, 7.0),   # carriers in the plates (2×)
    "6804": (20.0, 32.0, 7.0),   # discs on the cam (2×)
    "608": (8.0, 22.0, 7.0),     # input shaft in the carriers (2×)
}
SHAFT_D = 8.0                # input shaft, cut from 8 mm linear rod
COUPLING = dict(d=19.0, length=25.0)   # 8–8 mm flexible coupling
MOTOR_GAP = 38.0             # rear face → motor flange (printed standoffs)

# --- Material: PLA (printed, 100% infill or ≥ 6 perimeters for the discs) ------------
PLA = dict(E=3500.0, compressive=60.0, poisson=0.36)   # MPa; printed parts are weaker than the datasheet


def z_stack():
    """z ranges of the stacked parts."""
    z = {"rear_plate": (0.0, PLATE_T)}
    c0 = PLATE_T
    z["rear_flange"] = (c0 + GAP, c0 + GAP + FLANGE_T)
    z["disc_0"] = (z["rear_flange"][1] + GAP, z["rear_flange"][1] + GAP + DISC_T)
    z["disc_1"] = (z["disc_0"][1] + DISC_GAP, z["disc_0"][1] + DISC_GAP + DISC_T)
    z["front_flange"] = (z["disc_1"][1] + GAP, z["disc_1"][1] + GAP + FLANGE_T)
    z["cavity"] = (c0, z["front_flange"][1] + GAP)
    z["front_plate"] = (z["cavity"][1], z["cavity"][1] + PLATE_T)
    return z


def pin_force_max(torque_nm):
    """Largest single housing pin force (N) for a total output torque, two discs sharing
    it (approximation for cycloid drives: F ≈ 4·T / (K1·z·R) per disc)."""
    k1 = E * N_PINS / R_PINS
    t_disc = torque_nm * 1000 / 2
    return 4 * t_disc / (k1 * N_PINS * R_PINS)


def contact_stress(force_n, length=DISC_T, r_pin=D_PIN / 2, r_lobe=3.4):
    """Hertz line contact steel pin on PLA lobe (MPa); r_lobe is the smallest lobe radius."""
    e_star = PLA["E"] / (1 - PLA["poisson"] ** 2)
    r_star = 1 / (1 / r_pin + 1 / r_lobe)
    return math.sqrt(force_n / length * e_star / (2 * math.pi * r_star))


EFFICIENCY = 0.75            # estimate: printed discs, steel pins without rollers, greased


if __name__ == "__main__":
    z = z_stack()
    print(f"ratio {RATIO}:1, Ø{2 * HOUSING_R:.0f} × {z['front_plate'][1] + OUTPUT_EXT:.0f} mm, cavity {z['cavity'][1] - z['cavity'][0]:.1f} mm")
    for m in (T1.TIP_MASS, HD.TIP_MASS_MAX):
        g = HD.gravity_torque(m)
        j = HD.arm_inertia(m) + HD.MOTOR["rotor_inertia"] * RATIO ** 2
        need = g + j * HD.ACCEL
        f = pin_force_max(need)
        print(f"load {m} kg: {need:4.1f} Nm at the joint → {need / (RATIO * EFFICIENCY):.2f} Nm at the motor; "
              f"pin force ≤ {f:.0f} N, contact stress ≈ {contact_stress(f):.0f} MPa (PLA ≈ {PLA['compressive']:.0f})")
    print(f"output speed ≈ {HD.MOTOR['speed_rpm'] / RATIO * 6:.0f}°/s at {HD.MOTOR['speed_rpm']:.0f} rpm")
    cav = z["cavity"][1] - z["cavity"][0]
    span = z["front_flange"][0] - z["rear_flange"][1]
    assert cav < PIN_LEN <= cav + 2 * PIN_HOLE_DEPTH, "housing pins do not fit"
    assert span < OUT_PIN_LEN <= span + 2 * OUT_HOLE_DEPTH, "output pins do not fit"
    print(f"housing pins {N_PINS} × Ø{D_PIN:.0f} × {PIN_LEN:.0f} (room {cav:.0f}–{cav + 2 * PIN_HOLE_DEPTH:.0f}), "
          f"output pins {N_OUT} × Ø{D_OUT:.0f} × {OUT_PIN_LEN:.0f} (room {span:.0f}–{span + 2 * OUT_HOLE_DEPTH:.0f})")

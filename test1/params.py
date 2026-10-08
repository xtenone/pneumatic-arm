"""All dimensions and physical values of test 1 (arm with one degree of freedom).

This is the single source: CAD, simulation, firmware settings, bill of materials and
drawings are generated from it. Lengths in mm unless stated otherwise.

Coordinate frame (side view): x forward, z up, y = hinge axis (to the left).
The origin is on the top face of the base plate, directly below the hinge.
"""
import math

# --- Base plate and upright ---------------------------------------------------
BASE = dict(length=400.0, width=300.0, thickness=18.0)    # plywood, x × y
BASE_X = (-150.0, 250.0)     # x range; the arm reaches past the table edge (clamp with 2 F-clamps)
CHEEK = dict(height=450.0, depth=120.0, thickness=18.0)   # 2 cheeks, plywood
CHEEK_GAP = 36.0             # space between the cheeks = 2 layers of plywood (spacer block)
CHEEK_X = (-60.0, 60.0)      # x range of the cheeks (back, front)
SPACER_BLOCK = dict(length=60.0, height=60.0)  # wooden block between the cheeks, back bottom

# Pivots (in the x-z plane)
HINGE = (0.0, 420.0)         # arm hinge (2× 608 ball bearings in the cheeks)
REAR_PIVOT = (0.0, 100.0)    # rear pivot of the cylinder (M8 bolt)

# --- Arm ------------------------------------------------------------------------
ARM = dict(length=450.0, height=40.0, thickness=5.0)  # aluminium flat bar 40×5
ARM_BEHIND = 20.0            # arm extends 20 mm behind the hinge hole
ARM_ATTACH = 150.0           # hinge → clevis bolt
ARM_TIP = 400.0              # hinge → load bolt (dumbbell plates)
ARM_HOLE = 8.5               # holes in the arm (M8)
ARM_MASS = ARM["length"] * ARM["height"] * ARM["thickness"] * 2.7e-6       # kg, aluminium
ARM_MOMENT = ARM_MASS * (ARM["length"] / 2 - ARM_BEHIND)                   # kg·mm about the hinge
ARM_INERTIA = ARM_MASS * (ARM["length"] ** 2 / 12 + (ARM["length"] / 2 - ARM_BEHIND) ** 2)   # kg·mm²

# --- Cylinder MAL20×150 (seller's dimension drawing) ----------------------------
CYL = dict(
    bore=20.0, rod=8.0, stroke=150.0,
    body_d=26.0,             # tube outer diameter (B)
    overall_retracted=281.0, # rod end to rear end, retracted (131 + stroke)
    rear_pin_from_end=10.0,  # centre of rear pin hole to rear end (estimate, measure!)
    clevis_pin_from_rod_end=30.0,  # centre of clevis pin to rod end (estimate, measure!)
    rod_stack=10.0,          # nuts + potentiometer bracket between rod and clevis
    friction_coulomb=8.0,    # N, seals (estimate; measure in T3/T4)
    friction_viscous=40.0,   # N·s/m
)
PIN_TO_PIN_MIN = (CYL["overall_retracted"] - CYL["rear_pin_from_end"]
                  + CYL["clevis_pin_from_rod_end"] + CYL["rod_stack"])
PIN_TO_PIN_MAX = PIN_TO_PIN_MIN + CYL["stroke"]
AREA_A = math.pi * (CYL["bore"] / 2) ** 2                       # mm², piston side
AREA_B = AREA_A - math.pi * (CYL["rod"] / 2) ** 2                # mm², rod side

# --- Potentiometer KTC-175 -------------------------------------------------------
POT = dict(stroke=175.0, body=(275.0, 22.0, 19.0), offset=24.0,  # offset from the cylinder axis
           ohm=5000.0)

# --- Load -----------------------------------------------------------------------
PLATE = dict(mass=1.0, d=120.0, hole=25.0, thickness=13.0)   # 1 kg dumbbell plate (typical cast iron; measure yours)
TIP_MASS = 1.0               # kg of plates on the bolt at the arm end, alternately left and right
ALU_DENSITY = 2.7e-6         # kg/mm³

# --- Pneumatics -------------------------------------------------------------------
P_ATM = 1.013                # bar absolute
P_SUPPLY = 5.0               # bar gauge after the pressure regulator
VALVE = dict(
    sonic_conductance=0.144, # dm³/(s·bar), VQ110U (Cv 0.04 ≈ 0.7 mm²)
    critical_ratio=0.3,
    t_on=0.0035, t_off=0.002,  # s, SMC datasheet
)
DEAD_VOLUME = 2.5            # cm³ per chamber: 30 cm of 4×2.5 tube + tees + sensor
POLYTROPIC = 1.2
T_AIR = 293.0                # K

# --- Control (tuned in the simulation, sim/run.py; the tests refine them) --------
PWM_HZ = 50
LOOP_HZ = 500
P_SUM = 4.0                  # bar, sum of both chamber pressures (stiffness)
KP_FORCE = 12.0              # N per mm position error
KI_FORCE = 90.0              # N per mm·s (only close to the target or when the arm is stalled)
KD_FORCE = 0.6               # N per mm/s
KP_PRESSURE = 2.0            # duty per bar pressure error
P_DEADBAND = 0.1             # bar
SOFT_LIMIT = 5.0             # mm, stay away from both end stops
V_MAX = 250.0                # mm/s, maximum speed of the target (full stroke in ~0.6 s)
P_MAX = 6.0                  # bar; above this: vent and, if it persists, fault
# move (T8): smooth profile + feedforward. The fastest profile that meets the T8 criteria in
# the simulation is about 1.1× this one (190°/s, 1900°/s²); these limits keep 10% margin
# in time (speed × 1/1.1, acceleration × 1/1.1², jerk × 1/1.1³). See out/sim/results.md.
MOVE_W_MAX = 170.0           # degrees/s, peak speed of the arm in the profile
MOVE_ALPHA_MAX = 1550.0      # degrees/s², peak acceleration of the arm in the profile
MOVE_JERK_MAX = 24000.0      # degrees/s³: how fast the force may change (the valves need time to swap the pressures)
FF_FRICTION = CYL["friction_coulomb"]   # N, cylinder seal friction in the feedforward (measure in T3/T4)
FF_VISCOUS = 0.0             # N·s/m

# --- Electronics (Pico 2 pins) ------------------------------------------------------
PINS = dict(fill_a=2, vent_a=3, fill_b=4, vent_b=5,   # → ULN2803A IN1..IN4
            adc_pos=26, adc_pa=27, adc_pb=28)
DIVIDER = (10_000, 15_000)   # top, bottom: sensor output → ADC
ADC_VREF = 3.3


def cylinder_length(theta_deg):
    """Pin-to-pin length of the cylinder at arm angle theta (degrees, 0 = horizontal)."""
    a = HINGE[1] - REAR_PIVOT[1]
    b = ARM_ATTACH
    t = math.radians(theta_deg)
    return math.sqrt(a * a + b * b + 2 * a * b * math.sin(t))


def arm_angle(length):
    """Arm angle (degrees) for a cylinder pin-to-pin length."""
    a = HINGE[1] - REAR_PIVOT[1]
    b = ARM_ATTACH
    s = (length * length - a * a - b * b) / (2 * a * b)
    return math.degrees(math.asin(max(-1.0, min(1.0, s))))


def moment_arm(theta_deg):
    """Lever arm (mm) of the cylinder force about the hinge."""
    a = HINGE[1] - REAR_PIVOT[1]
    b = ARM_ATTACH
    return a * b * math.cos(math.radians(theta_deg)) / cylinder_length(theta_deg)


THETA_MIN = arm_angle(PIN_TO_PIN_MIN)
THETA_MAX = arm_angle(PIN_TO_PIN_MAX)

if __name__ == "__main__":
    print(f"pin-to-pin {PIN_TO_PIN_MIN:.0f}–{PIN_TO_PIN_MAX:.0f} mm, "
          f"arm {THETA_MIN:.1f}° … {THETA_MAX:.1f}°")
    arm_mass = ARM["length"] * ARM["height"] * ARM["thickness"] * ALU_DENSITY
    for th in (THETA_MIN, -10, 0, 20, 40, 60, THETA_MAX):
        r = moment_arm(th)
        f_push = P_SUPPLY * 0.1 * AREA_A          # N (bar·0.1 = N/mm²)
        grav = 9.81 * (arm_mass * ARM["length"] / 2 + TIP_MASS * ARM_TIP) / 1000 * math.cos(math.radians(th))
        print(f"θ={th:6.1f}°  L={cylinder_length(th):6.1f}  lever={r:5.1f} mm  "
              f"max torque={f_push * r / 1000:5.1f} Nm  gravity={grav:4.1f} Nm  "
              f"load={grav / (f_push * r / 1000) * 100:4.0f}%")

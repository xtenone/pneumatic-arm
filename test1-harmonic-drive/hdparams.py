"""Dimensions and sizing of the electric reference for test 1: the same arm and load on a
harmonic drive driven by a closed-loop stepper motor.

Module name hdparams because test 1 already owns "params". Arm, load and base come from
test 1, so both set-ups are tested under the same conditions. Lengths in mm.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test1"))
import params as T1  # noqa: E402  (arm, load and base are shared)

# --- Harmonic drive: size 17, cup type (CSF-17 pattern, clones widely available) ---
GEAR = dict(
    size=17,
    ratio=100,
    repeated_peak_torque=54.0,   # Nm, limit for repeated peak torque (CSF-17-100)
    efficiency=0.70,             # estimate at moderate load; lower when cold or lightly loaded
    backlash_arcmin=1.0,         # zero-backlash type; clones: measure
)

# --- Motor: NEMA23 closed-loop stepper (motor with encoder + driver, step/dir) ---------
MOTOR = dict(
    holding_torque=1.2,          # Nm (NEMA23, ~56 mm long); falls with speed
    rotor_inertia=2.8e-5,        # kg·m² (≈280 g·cm²); seen ×ratio² at the arm
    speed_rpm=600.0,             # usable speed with useful torque (estimate)
)

# --- Load case: the heaviest test of test 1 (T5) ----------------------------------------
TIP_MASS_MAX = 3.0               # kg at T1.ARM_TIP
ACCEL = math.radians(180.0)      # rad/s², arm acceleration used for sizing


def arm_mass():
    return T1.ARM["length"] * T1.ARM["height"] * T1.ARM["thickness"] * T1.ALU_DENSITY


def gravity_torque(tip_mass, theta_deg=0.0):
    """Nm at the joint, arm at angle theta (same formula as test 1)."""
    return (9.81 * (arm_mass() * T1.ARM["length"] / 2 + tip_mass * T1.ARM_TIP) / 1000
            * math.cos(math.radians(theta_deg)))


def arm_inertia(tip_mass):
    """kg·m² about the joint: point load at the tip plus the bar."""
    L, r = T1.ARM["length"] / 1000, T1.ARM_TIP / 1000
    return tip_mass * r ** 2 + arm_mass() * L ** 2 / 3


def reflected_rotor_inertia():
    return MOTOR["rotor_inertia"] * GEAR["ratio"] ** 2


def output_speed_deg_s():
    return MOTOR["speed_rpm"] / GEAR["ratio"] * 360.0 / 60.0


if __name__ == "__main__":
    n, eta = GEAR["ratio"], GEAR["efficiency"]
    for m in (T1.TIP_MASS, TIP_MASS_MAX):
        g = gravity_torque(m)
        j = arm_inertia(m) + reflected_rotor_inertia()
        need = g + j * ACCEL
        print(f"load {m} kg: gravity {g:4.1f} Nm, inertia arm {arm_inertia(m):.3f} + rotor "
              f"{reflected_rotor_inertia():.3f} kg·m², with {math.degrees(ACCEL):.0f}°/s² "
              f"{need:4.1f} Nm at the joint → {need / (n * eta):.2f} Nm at the motor "
              f"(gear limit {GEAR['repeated_peak_torque']} Nm, motor {MOTOR['holding_torque']} Nm)")
    print(f"output speed ≈ {output_speed_deg_s():.0f}°/s; "
          f"1 arcmin backlash = {T1.ARM_TIP * math.radians(GEAR['backlash_arcmin'] / 60):.2f} mm at the load")

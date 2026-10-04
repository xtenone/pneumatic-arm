"""Alle maten en natuurkundige waarden van test 1 (arm met één vrijheidsgraad).

Dit is de enige bron: CAD, simulatie, firmware-instellingen, stuklijst en tekeningen
worden hieruit gegenereerd. Lengtes in mm, tenzij anders vermeld.

Assenstelsel (zijaanzicht): x naar voren, z omhoog, y = scharnieras (naar links).
De oorsprong ligt op de bovenkant van de grondplaat, midden onder het scharnier.
"""
import math

# --- Grondplaat en staander --------------------------------------------------
BASE = dict(length=400.0, width=300.0, thickness=18.0)    # multiplex, x × y
BASE_X = (-150.0, 250.0)     # x-bereik; de arm steekt over de tafelrand (vastzetten met 2 lijmklemmen)
CHEEK = dict(height=450.0, depth=120.0, thickness=18.0)   # 2 wangen, multiplex
CHEEK_GAP = 36.0             # binnenruimte tussen de wangen = 2 lagen multiplex (afstandsblok)
CHEEK_X = (-60.0, 60.0)      # x-bereik van de wangen (achterkant, voorkant)
SPACER_BLOCK = dict(length=60.0, height=60.0)  # houten blok achter-onder tussen de wangen

# Draaipunten (in het x-z-vlak)
HINGE = (0.0, 420.0)         # scharnier van de arm (2× kogellager 608 in de wangen)
REAR_PIVOT = (0.0, 100.0)    # achterste draaipunt van de cilinder (M8-bout)

# --- Arm ----------------------------------------------------------------------
ARM = dict(length=450.0, height=40.0, thickness=5.0)  # aluminium strip 40×5
ARM_BEHIND = 20.0            # arm steekt 20 mm achter het scharniergat uit
ARM_ATTACH = 150.0           # afstand scharnier → bout van de vorkkop
ARM_TIP = 400.0              # afstand scharnier → ophangpunt last
ARM_HOLE = 8.5               # gaten in de arm (M8)

# --- Cilinder MAL20×150 (maattekening verkoper) --------------------------------
CYL = dict(
    bore=20.0, rod=8.0, stroke=150.0,
    body_d=26.0,             # buitenmaat buis (B)
    overall_retracted=281.0, # stangeinde tot achterkant, ingeschoven (131 + slag)
    rear_pin_from_end=10.0,  # hart pengat achter tot achterkant (schatting, meten!)
    clevis_pin_from_rod_end=30.0,  # hart pen vorkkop tot stangeinde (schatting, meten!)
    rod_stack=10.0,          # moeren + beugeltje potmeter tussen stang en vorkkop
    friction_coulomb=8.0,    # N, afdichtingen (schatting; T3/T4 meten)
    friction_viscous=40.0,   # N·s/m
)
PIN_TO_PIN_MIN = (CYL["overall_retracted"] - CYL["rear_pin_from_end"]
                  + CYL["clevis_pin_from_rod_end"] + CYL["rod_stack"])
PIN_TO_PIN_MAX = PIN_TO_PIN_MIN + CYL["stroke"]
AREA_A = math.pi * (CYL["bore"] / 2) ** 2                       # mm², zuigerzijde
AREA_B = AREA_A - math.pi * (CYL["rod"] / 2) ** 2                # mm², stangzijde

# --- Potmeter KTC-175 ----------------------------------------------------------
POT = dict(stroke=175.0, body=(275.0, 22.0, 19.0), offset=24.0,  # offset t.o.v. cilinderas
           ohm=5000.0)

# --- Last ---------------------------------------------------------------------
TIP_MASS = 1.5               # kg, fles water aan het einde van de arm (T5: tot ~3 kg)
ALU_DENSITY = 2.7e-6         # kg/mm³

# --- Pneumatiek ----------------------------------------------------------------
P_ATM = 1.013                # bar absoluut
P_SUPPLY = 5.0               # bar overdruk na de drukregelaar
VALVE = dict(
    sonic_conductance=0.144, # dm³/(s·bar), VQ110U (Cv 0,04 ≈ 0,7 mm²)
    critical_ratio=0.3,
    t_on=0.0035, t_off=0.002,  # s, SMC-opgave
)
DEAD_VOLUME = 2.5            # cm³ per kamer: 30 cm slang 4×2,5 + T-stukken + sensor
POLYTROPIC = 1.2
T_AIR = 293.0                # K

# --- Regeling (afgesteld in de simulatie, sim/run.py; de proeven stellen ze bij) ---
PWM_HZ = 50
LOOP_HZ = 500
P_SUM = 4.0                  # bar, som van beide kamerdrukken (stijfheid)
KP_FORCE = 12.0              # N per mm positiefout
KI_FORCE = 90.0              # N per mm·s (alleen dicht bij het doel of als de arm stilstaat)
KD_FORCE = 0.6               # N per mm/s
KP_PRESSURE = 2.0            # duty per bar drukfout
P_DEADBAND = 0.1             # bar
SOFT_LIMIT = 5.0             # mm van beide eindaanslagen wegblijven
V_MAX = 250.0                # mm/s, maximale snelheid van het doel (volle slag in ~0,6 s)
P_MAX = 6.0                  # bar, daarboven: leeglopen en fout

# --- Elektronica (pinnen Pico 2) -----------------------------------------------
PINS = dict(fill_a=2, vent_a=3, fill_b=4, vent_b=5,   # → ULN2803A IN1..IN4
            adc_pos=26, adc_pa=27, adc_pb=28)
DIVIDER = (10_000, 15_000)   # boven, onder: sensoruitgang → ADC
ADC_VREF = 3.3


def cylinder_length(theta_deg):
    """Pen-pen-lengte van de cilinder bij armhoek theta (graden, 0 = horizontaal)."""
    a = HINGE[1] - REAR_PIVOT[1]
    b = ARM_ATTACH
    t = math.radians(theta_deg)
    return math.sqrt(a * a + b * b + 2 * a * b * math.sin(t))


def arm_angle(length):
    """Armhoek (graden) bij een pen-pen-lengte van de cilinder."""
    a = HINGE[1] - REAR_PIVOT[1]
    b = ARM_ATTACH
    s = (length * length - a * a - b * b) / (2 * a * b)
    return math.degrees(math.asin(max(-1.0, min(1.0, s))))


def moment_arm(theta_deg):
    """Hefboom (mm) van de cilinderkracht om het scharnier."""
    a = HINGE[1] - REAR_PIVOT[1]
    b = ARM_ATTACH
    return a * b * math.cos(math.radians(theta_deg)) / cylinder_length(theta_deg)


THETA_MIN = arm_angle(PIN_TO_PIN_MIN)
THETA_MAX = arm_angle(PIN_TO_PIN_MAX)

if __name__ == "__main__":
    print(f"pen-pen {PIN_TO_PIN_MIN:.0f}–{PIN_TO_PIN_MAX:.0f} mm, "
          f"arm {THETA_MIN:.1f}° … {THETA_MAX:.1f}°")
    arm_mass = ARM["length"] * ARM["height"] * ARM["thickness"] * ALU_DENSITY
    for th in (THETA_MIN, -10, 0, 20, 40, 60, THETA_MAX):
        r = moment_arm(th)
        f_push = P_SUPPLY * 0.1 * AREA_A          # N (bar·0,1 = N/mm²)
        grav = 9.81 * (arm_mass * ARM["length"] / 2 + TIP_MASS * ARM_TIP) / 1000 * math.cos(math.radians(th))
        print(f"θ={th:6.1f}°  L={cylinder_length(th):6.1f}  hefboom={r:5.1f} mm  "
              f"koppel max={f_push * r / 1000:5.1f} Nm  zwaartekracht={grav:4.1f} Nm  "
              f"belasting={grav / (f_push * r / 1000) * 100:4.0f}%")

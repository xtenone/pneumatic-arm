"""Dimensions of test 2: 2-DOF joint (pitch + roll) with two cylinders.

Module name t2params because test 1 already owns "params".

Concept B (from the customer's sketch): a hub on the arm axis carries two hinges
(axis parallel to the arm, ±90°). From each hinge a horizontal bar runs outward through
a sleeve on top of a cylinder. The sleeve lets the bar turn about its own axis and slide
sideways. The cylinders (stroke 200) stand on low brackets far below the joint; the
stand is 100 mm taller than in test 1 to make room for them and for the arm pointing
down. Lengths in mm; frame as in
test 1 (x forward, z up, y left, origin on the base plate below the joint).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test1"))
import params as T1  # noqa: E402  (cylinder, base and cheek dimensions are shared)

JOINT = (0.0, 0.0, 520.0)        # centre of the universal joint (pitch and roll axes cross here)
HUB_X = 90.0                     # joint → hub along the arm axis (pitch lever)
HUB_R = 40.0                     # hub axis → bar hinge (roll lever); hinges clear the cheeks
BAR_Y = 90.0                     # sideways position of the cylinders (and sleeves)
BAR_D = 10.0                     # bar diameter
BAR_LENGTH = 110.0               # hinge → bar end (must reach past the sleeve at all rolls)
SLEEVE = dict(length=30.0, outer=22.0)
LOWER_PIVOT = (40.0, 60.0)       # x, z of the lower cylinder pivots (axis along y), 460 mm below the joint
PITCH_RANGE = (-45.0, 75.0)      # design range with roll ±65° (down to -60° without roll); end stop at about 80°
ROLL_RANGE = 65.0                # ± roll that must be reachable over the whole pitch range

BASE_X = T1.BASE_X
CHEEK_X = (T1.CHEEK_X[0], 25.0)   # cut back at the front so the hub clears them with the arm down
CHEEK_HEIGHT = JOINT[2] + 30.0   # test 1: 450
ARM_LENGTH = 450.0

YOKE = dict(width=T1.CHEEK_GAP - 2.0, height=50.0, depth=60.0)   # pitch yoke between the cheeks
ROLL_SHAFT_D = 16.0

CYL = dict(T1.CYL, stroke=200.0, overall_retracted=131.0 + 200.0)   # MAL20×200
PIN_TO_PIN_MIN = T1.PIN_TO_PIN_MIN + CYL["overall_retracted"] - T1.CYL["overall_retracted"]
PIN_TO_PIN_MAX = PIN_TO_PIN_MIN + CYL["stroke"]

# Variant "cross block": the cylinder rod ends in a fork on a cross block in the hub hinge
# (a small universal joint), so the cylinder force passes through the hinge. No bars or
# sleeves. The cylinders tilt a few degrees sideways when rolling: rod end bearing below.
CROSS = dict(
    hub_r=45.0,                  # hub axis → cross block centre
    lower_pivot=(40.0, 60.0),    # x, z of the cylinder rear pins (at y = ±hub_r)
    low_drop=26.0,               # bottom joint: the x bolt sits this far below the rear pin
    block=16.0,                  # cross block, cube
    pin_d=6.0,
    cheek_front=0.0,             # cheek front edge below the joint (x)
    cheek_top_r=30.0,            # round top of the cheek around the joint
)

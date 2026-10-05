"""Dimensions of test 2: 2-DOF joint (pitch + roll) with two cylinders.

Module name t2params because test 1 already owns "params".

Concept B (from the customer's sketch): a hub on the arm axis carries two hinges
(axis parallel to the arm, ±90°). From each hinge a horizontal bar runs outward through
a sleeve on top of a vertical cylinder. The sleeve lets the bar turn about its own axis
and slide sideways, so the cylinders only push straight up. Lengths in mm; frame as in
test 1 (x forward, z up, y left, origin on the base plate below the joint).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test1"))
import params as T1  # noqa: E402  (cylinder, base and cheek dimensions are shared)

JOINT = (0.0, 0.0, 420.0)        # centre of the universal joint (pitch and roll axes cross here)
HUB_X = 150.0                    # joint → hub along the arm axis
HUB_R = 30.0                     # hub axis → bar hinge (roll lever)
BAR_Y = 90.0                     # sideways position of the cylinders (and sleeves)
BAR_D = 10.0                     # bar diameter
BAR_LENGTH = 110.0               # hinge → bar end (must reach past the sleeve at all rolls)
SLEEVE = dict(length=30.0, outer=22.0)
LOWER_PIVOT = (150.0, 34.0)      # x, z of the lower cylinder pivots (axis along y), on the base plate
ARM_LENGTH = 450.0

YOKE = dict(width=T1.CHEEK_GAP - 2.0, height=50.0, depth=60.0)   # pitch yoke between the cheeks
ROLL_SHAFT_D = 16.0

CYL = T1.CYL
PIN_TO_PIN_MIN = T1.PIN_TO_PIN_MIN
PIN_TO_PIN_MAX = T1.PIN_TO_PIN_MAX

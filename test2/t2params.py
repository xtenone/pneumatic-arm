"""Dimensions of test 2: 2-DOF joint (pitch + roll) with two cylinders.

Module name t2params because test 1 already owns "params".

First concept, built on test 1: the hinge becomes a universal joint and a second
cylinder is added next to the first. Lengths in mm. Frame as in test 1: x forward,
z up, y to the left; origin on the base plate below the joint.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test1"))
import params as T1  # noqa: E402  (cylinder, base and cheek dimensions are shared)

JOINT = (0.0, 0.0, 420.0)        # centre of the universal joint (pitch and roll axes cross here)
LEVER_X = 150.0                  # joint → crossbar along the arm
LEVER_HALF = 70.0                # half width of the crossbar (roll lever, "b")
LEVER_DROP = 30.0                # crossbar sits this far below the arm axis
REAR_PIVOTS_Z = 60.0             # height of the lower cylinder pivots
REAR_PIVOTS_X = 0.0
ARM_LENGTH = 450.0
ARM_BEHIND = 40.0

YOKE = dict(width=T1.CHEEK_GAP - 2.0, height=50.0, depth=60.0)   # pitch yoke between the cheeks
ROLL_SHAFT_D = 16.0
OUTRIGGER = dict(length=60.0, height=60.0, thickness=10.0)        # brackets for the lower pivots

CYL = T1.CYL
PIN_TO_PIN_MIN = T1.PIN_TO_PIN_MIN
PIN_TO_PIN_MAX = T1.PIN_TO_PIN_MAX

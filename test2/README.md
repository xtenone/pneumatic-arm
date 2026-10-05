# Test 2 — 2-DOF joint (concept)

Concept of the joint from [docs/2dof-joint.md](../docs/2dof-joint.md), built on test 1:
the hinge becomes a universal joint (pitch + roll) and a second cylinder is added. Same
Ø20 × 150 cylinders, same upright.

![Concept](out/render_neutral_close.png)

**Mechanism (concept B, from the customer's sketch):**
- A hub on the arm axis, 150 mm from the joint, carries two hinges (axis parallel to the
  arm, ±90°), 30 mm left and right of the axis.
- From each hinge a horizontal bar (Ø10) runs outward through a sleeve on top of a
  cylinder. The sleeve lets the bar turn about its own axis and slide sideways, so the
  bars stay horizontal and the cylinders only push straight up.
- The cylinders stand upright under the bars, 90 mm to the sides, on clevis brackets on
  the base plate that let them tilt forward and back as the arm pitches.
- Both cylinders out: pitch up. One out, one in: roll about the arm's own axis.

**Range (cylinder stroke and bar length only):** pitch about ±28°; roll ±90° within
±10° of horizontal, ±45–50° at ±20° pitch. The roll torque scales with cos(roll): it
drops to zero at ±90°, so about ±60–70° is the useful roll range.

![Roll 60°](out/render_roll_front.png)

Files: `t2params.py` (dimensions), `cad/model.py` (CadQuery), `render.py` (renders and
`out/test2_concept.step`).

Status: concept for discussion, not yet worked out or simulated.

# Full-size joint: 15 kg at 1 m

First sizing of the real arm joint, scaled up from the [test 2](../test2/README.md)
design: two cylinders standing under a hub on the arm, both out = pitch up, one out and
one in = roll. Range as test 2: pitch −60° … +75°.

The numbers come from `python tools/full_arm_sizing.py`. They are an estimate: the
outcome of test T7 (how much of the available force the control can use) sets the
final cylinder size.

## Requirement

| Case | Torque with the arm horizontal |
|---|---|
| 15 kg at 1 m, arm 3 kg (one 1 m segment) | **162 Nm** |
| 15 kg at 1 m, arm 30 kg (complete arm, estimate from [2dof-joint.md](2dof-joint.md)) | 294 Nm |

For comparison: test 1 delivers at most 21 Nm, test 2 (2 × Ø20 on a 90 mm lever) 28 Nm.

## Cylinders

Rule: the static load may use at most about 40% of the available torque (test 1 is
designed at 30–39%), at 5 bar, two cylinders pushing together.

The lever (hub distance from the joint) trades cylinder diameter against stroke: the
stroke for −60° … +75° is about 1.83 × the lever. The air used per movement is the same
for every choice; it follows from torque × angle.

**Arm 3 kg (162 Nm):**

| Lever | Cylinder | Stroke | Load |
|---|---|---|---|
| **150 mm** | **Ø63** | **300 mm** | **35%** |
| 250 mm | Ø50 | 500 mm | 33% |
| 370 mm | Ø40 | 700 mm | 35% |

**Arm 30 kg (294 Nm):**

| Lever | Cylinder | Stroke | Load |
|---|---|---|---|
| 150 mm | Ø80 | 300 mm | 39% |
| 250 mm | Ø63 | 500 mm | 38% |
| 370 mm | Ø63 | 700 mm | 26% |

Choice for now: **lever 150 mm with Ø63 × 300** (Ø80 for the heavy arm). This keeps the
joint compact, is the test 2 layout at about 1.7× scale, and avoids long slender
cylinders that buckle sooner. The joint then sits about 90 cm above its base.

Roll is not limiting: at this size more than 200 Nm is available about the arm axis,
while a block hanging 10 cm beside the axis needs about 15 Nm.

## Speed

Steady speed lifting with the arm horizontal, flow model as in test 1 (ISO 6358). Filling
the piston side and venting the rod side both count; venting is often the limit.

| Valves per chamber | Arm 3 kg, Ø63 | Arm 30 kg, Ø80 | Valve effective area |
|---|---|---|---|
| 1 × VQ110U (test 1 valve) | 20°/s, 0.34 m/s at the tip | 12°/s, 0.21 m/s | 0.7 mm² |
| 4 × VQ110U in parallel | 78°/s, 1.4 m/s | 48°/s, 0.84 m/s | 2.9 mm² |
| 1 × 4V210-type 5/2 valve | not the limit (hoses, regulator, compressor are) | idem | ~14 mm² |

The speed hardly depends on the lever: a longer lever moves a thinner cylinder further.

- The test 1 valves give a slow but usable speed for placing blocks.
- Faster needs more flow. The large 5/2 valves are cheap but switch in 15–30 ms instead
  of 2–4 ms, so the control has to be adapted (for example coarse + fine valves).

## Air use

One full lift (−60° → +75°) with two cylinders Ø63 × 275 mm sweeps 1.7 l, about
**6 l of free air** at a chamber pressure of 3.5 bar absolute (Ø80: about 10 l). One full
lift every 5 s is about 70 l/min; to be checked against the compressor's delivery.

## Arm and joint

- **Arm:** aluminium tube Ø50 × 3 (6060). Bending stress below 70 MPa including 2× for
  acceleration; tip deflection with 15 kg about 6 mm.
- **Joint:** scales with the forces: shafts about Ø20 and proper bearings instead of bolts
  as pivots, bar and cross blocks at the hub about Ø20 / 30 mm.

## Open

- T7 result: maximum load ratio → final cylinder diameter.
- Valve choice for the large cylinders: number of VQ110U in parallel, or coarse + fine.
- Compressor delivery versus the air use above.
- Mass of the complete arm (elbow, forearm, gripper) → 3 kg or 30 kg case or in between.

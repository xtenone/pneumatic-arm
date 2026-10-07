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

15 kg with the arm stretched is the limit, not the normal work: it happens rarely, briefly
and slowly. Normal work holds the 15 kg closer in, at about 0.6 m.

| Load case | Arm 3 kg | Arm 30 kg | Allowed share of the available torque |
|---|---|---|---|
| Work: 15 kg at 0.6 m | 97 Nm | 177 Nm | 40% |
| Peak: 15 kg at 1 m | 162 Nm | 294 Nm | 70% |

The peak may use more of the force because it is held still or moved slowly: the margin
for accelerating and for the control is small there. How long it lasts does not matter to
a cylinder: holding a force costs no air and nothing heats up (unlike a motor).

## Cylinders

Rule (first sizing, before the load cases above): the static load may use at most about 40% of the available torque (test 1 is
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

Lever 150 mm keeps the joint compact, is the test 2 layout at about 1.7× scale, and
avoids long slender cylinders that buckle sooner. The joint then sits about 90 cm above
its base.

**With the load cases** (work ≤ 40%, peak ≤ 70%, lever 150 mm):

| Arm | Cylinder | Work load | Peak load | Speed work / peak (1 × VQ110U) |
|---|---|---|---|---|
| 3 kg | **Ø50 × 300** | 33% | 55% | 33 / 30°/s |
| 30 kg | Ø63 × 300 | 38% | 63% | 19 / 17°/s |

Choice for now: **lever 150 mm with Ø50 × 300** (Ø63 for the heavy arm), one size smaller
than with the 40% rule for the peak: about 1.5× faster and 37% less air per lift. If T7
shows that less than about 70% is usable at slow speed, the shoulder goes back to Ø63
(Ø80).

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

### Speed per joint with the test 1 valve

With 1 × VQ110U per chamber the speed is set by the valve flow and the size of the
cylinder (bore × lever), and hardly by the load:

| Joint | Torque with 15 kg | With 15 kg | Without load |
|---|---|---|---|
| Shoulder, Ø50, lever 150 mm | 162 Nm | 30°/s | 33°/s |
| Shoulder, Ø63, lever 150 mm (40% rule for the peak) | 162 Nm | 20°/s | 20°/s |
| Elbow, Ø50, lever 100 mm (15 kg at 0.5 m) | 77 Nm | 49°/s | 50°/s |

**Decision:** the shoulder may be slow; it positions the arm. Fast movements (for other
work such as scrubbing) come from the elbow and the wrist, which have smaller cylinders
and are faster with the same valve. One VQ110U per chamber is therefore the starting
point. If the shoulder turns out to be too slow: 4 VQ110U in parallel or one larger,
cheaper valve per chamber.

## Air use

One full lift (−60° → +75°) with two cylinders Ø50 × 275 mm sweeps 1.1 l, about
**4 l of free air** at a chamber pressure of 3.5 bar absolute (Ø63: about 6 l, Ø80: about
10 l). One full lift every 5 s is about 45 l/min; to be checked against the compressor's
delivery.

## Light version: 1.5 kg at 1 m

A second version for most small tasks (glass, sponge, tools): 1.5 kg at the hand, upper
arm and forearm 0.5 m each, same joints. Here the arm's own mass weighs as much as the
load. Estimated masses: wrist pitch motor + gripper rotation motor + gripper 1.1 kg,
forearm 0.5 kg, upper arm 1.2 kg including the elbow cylinders.

| Joint | Peak (stretched) | Work (0.6 × peak) |
|---|---|---|
| Shoulder | 31.6 Nm | 19.0 Nm |
| Elbow | 13.4 Nm | 8.1 Nm |

Options (two cylinders per joint, 5 bar, same rules: work ≤ 40%, peak ≤ 70%):

| Joint | Cylinders | Lever | Peak load | Work load | Speed with the load / empty, 1 × VQ110U |
|---|---|---|---|---|---|
| Shoulder | 2 × Ø25 | 100 mm | 64% | 39% | 164 / 200°/s |
| Shoulder | **2 × Ø32 × 200** | **100 mm** | **39%** | **24%** | **118 / 119°/s** |
| Shoulder | 2 × Ø25 × 300 | 150 mm | 43% | 26% | 130 / 133°/s |
| Elbow | 2 × Ø20 | 75 mm | 57% | 34% | 374 / 417°/s |
| Elbow | **2 × Ø25 × 80** | **50 mm** | **55%** | **33%** | **366 / 400°/s** |
| Elbow | 2 × Ø25 × 125 | 75 mm | 37% | 22% | 265 / 267°/s |

Choice:

- **Shoulder 2 × Ø32 × 200 on a 100 mm lever:** the test 2 joint (2 × Ø20, 90 mm) with
  one size larger cylinders. Ø25 would just do, but leaves no room for errors in the mass
  estimate.
- **Elbow 2 × Ø25 × 80 on a 50 mm lever** (as in the cocktail impression, elbow 10–120°).
  The hand may become about 0.75 kg heavier before the peak reaches 70%.

Speed is no longer limited by the valve: the test 1 valve already gives more than 100°/s.
The limit becomes the control and safety. A cap of about 1 m/s at the hand means about
55°/s at the shoulder and 115°/s at the elbow. One VQ110U per chamber is plenty.

## Arm and joint

- **Arm:** aluminium tube Ø50 × 3 (6060). Bending stress below 70 MPa including 2× for
  acceleration; tip deflection with 15 kg about 6 mm.
- **Joint:** scales with the forces: shafts about Ø20 and proper bearings instead of bolts
  as pivots, bar and cross blocks at the hub about Ø20 / 30 mm.

## Open

- T7 result: usable load ratio at slow speed (≥ 70% → Ø50, otherwise Ø63) → final cylinder diameter.
- Valve choice for the large cylinders: 1 × VQ110U per chamber unless the shoulder proves too slow.
- Compressor delivery versus the air use above.
- Mass of the complete arm (elbow, forearm, gripper) → 3 kg or 30 kg case or in between.
- Light version: weigh the wrist motors and gripper → check the elbow margin.
- If much more force is needed: hydraulics with the same joint layout, see
  [hydraulics.md](hydraulics.md).

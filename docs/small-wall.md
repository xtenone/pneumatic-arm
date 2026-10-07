# Intermediate goal: a small wall of wooden blocks

The light arm (1.5 kg at 1 m, see [full-arm-sizing.md](full-arm-sizing.md#light-version-15-kg-at-1-m))
takes blocks from a stack and lays them in a row, and then in a small wall of two
courses. It is the wall task of the [goal](../goal.md) at small scale: the same steps
(pick, turn, place, line up) with light, safe blocks.

## Blocks

| | |
|---|---|
| Material | Planed pine beam, nominal 70 × 70 mm (actual ≈ 68 × 68) |
| Full block | 68 × 68 × 136 mm (length = 2 × width), ≈ 0.3 kg |
| Half block | 68 × 68 × 68 mm (cube), ≈ 0.15 kg |
| Finish | All edges chamfered 2 mm, so a block slides into place instead of catching |

- **Why wood:** easy to saw to size with a mitre saw, cheap, square, and harmless when
  dropped. Length 2 × width allows a running bond, like bricks.
- **Why this size:** the gripper only needs one opening (68 mm across the block) for
  full and half blocks; at 0.3 kg the arm works at about a quarter of its load limit, so
  speed and accuracy can be tested without the load in the way.
- **Heavier later:** steel in a drilled hole brings a block to about 1 kg (stage 3).

## Layout on the table

```
          wall (start against a stop strip)
        ┌────┬────┬────┬────┐
        │    │    │    │    │          ← ≈ 0.53 m in front of the yaw axis
        └────┴────┴────┴────┘
                                    ┌──┐
              (arm base)            │  │ stack(s), ≈ 0.58 m from the yaw axis,
                 ●                  └──┘ about 70° to the side, turned 90°
                                         relative to the wall
```

- The base yaw axis runs through the shoulder joint; distances are measured from it.
- The shoulder is about 0.66 m above the table top, so the elbow stays at least 12 cm
  above the table.
- Stack: full blocks 4 high (0.27 m) in a corner jig, so their positions are known.
- Wall: 4 full blocks long (≈ 0.55 m), starting against a strip screwed to the table.
- Reach (2 × 0.5 m arm, `python full-arm/small_wall.py --check`): the elbow bends 85–89°
  at the wall and 83–101° at the stack, within its 10–120°. Further away the arm is more
  stretched and settles worse: in the simulation the stack at 0.67 m made the picks
  oscillate.
- No camera: the positions are fixed by the jig and the strip and known to the program.

## Joints used

| Joint | Drive | Task |
|---|---|---|
| Base yaw | Motor | Between the stack and the wall |
| Shoulder pitch | 2 × Ø32 | Reach and height |
| Elbow pitch | 2 × Ø25 | Reach and height |
| Wrist pitch | Motor | Keeps the gripper pointing straight down |
| Gripper yaw | Motor | Turns the block 90° from the stack to the wall |
| Gripper | Cylinder | Clamps the block across its 68 mm width |

The shoulder and forearm rolls are held at 0: both cylinders of a joint get the same
command.

## Gripper

Requirements:

- Two jaws gripping the 68 mm width from above, on the long faces of the block (these
  stay free in the wall), opening ≥ 95 mm (≥ 13 mm free on each side, more than the
  expected placement error).
- Self-centring: both jaws move together, so closing does not push the block sideways.
- Squeeze ≥ 40 N: friction 2 × 0.4 × 40 = 32 N (rubber on wood), about 3× the weight of
  a 1 kg block.
- About 0.3 kg, within the 1.1 kg budget for the wrist end.
- Detects a missed block.

Proposal: a parallel gripper built from ordinary parts.

| Part | |
|---|---|
| Guide | MGN12 rail, 150 mm, with two carriages, one per jaw |
| Synchronisation | Two printed racks on one printed pinion (module 1.5, 16 teeth, PETG): the jaws always move mirror-wise |
| Drive | One double-acting cylinder Ø16 × 25 with magnetic piston, on one jaw; pushing closes |
| Force | Ø16 at 5 bar pushes 100 N; through the pinion the squeeze is half: 50 N |
| Stroke | 20 mm per jaw: opening 95 mm, empty closed 55 mm |
| Missed block | Reed switch on the cylinder at the "closed empty" end |
| Jaws | Printed fingers with 2 mm rubber pads and a lead-in chamfer at the tips; they grip the upper 40 mm of the block, so they clear the course below |
| Valve | One plain 5/2 solenoid valve (4V110 type, 24 V): open/close only, no control valve |
| Cost | About €40 (rail €15, cylinder €10, valve €8, reed switch €3, fittings) |

The printed parts get fit allowances and a fit-test print first.

## Stages and success criteria

| Stage | Task | Success |
|---|---|---|
| 1a. Row, controlled | 4 full blocks from the stack in a row against the strip, at the speeds of the heavy version | 9 of 10 runs: every block within ±5 mm and ±3° of its place, joints ≤ 5 mm, nothing knocked over; ≤ 20 s per block |
| 1b. Row, fast | The same at the light arm's own speed | 9 of 10 runs, same tolerances; ≤ 10 s per block |
| 2. Small wall | 2 courses in running bond: 4 full blocks, then half + 3 full + half (2 stacks of full blocks, half blocks beside them) | 9 of 10 runs, same tolerances, the wall stays standing |
| 3. Heavier blocks | Stage 2 with blocks of about 1 kg | as stage 2 |

Speeds:

| | Base yaw | Shoulder | Elbow | Hand |
|---|---|---|---|---|
| Controlled (as the heavy version, see [plan.md](plan.md#first-complete-arm-the-light-version)) | 30°/s | 30°/s | 50°/s | ≈ 0.5 m/s |
| Fast (safety cap of the light arm) | 90°/s | 55°/s | 115°/s | 1 m/s |

- Rough time per block: controlled ≈ 13 s, fast ≈ 6 s (two moves between stack and wall,
  four short moves down and up, grip and release, settling). The limits in the table
  leave room for slower settling.
- In both runs the last few centimetres before placing may be slower; the tolerances are
  the same.
- Stage 1b is the test for compensating the swinging out (feedforward, trajectory
  shaping, braking early). Once it passes, the speed goes up further.
- Stages 2 and 3 run at the controlled speeds first.
- Every run is recorded (video + joint log), as for the other tests.

## Open

- Gripper: CAD of the proposal above, fit test, then build.
- Reach and layout check in simulation (positions of the stack and the wall).
- Simulation of stage 1 ([full-arm/README.md](../full-arm/README.md#dynamic-simulation-python-full-armarm_simpy)):
  up to 1.5 kg the fast run takes about 24 s with blocks within 3 mm; 3 kg needs the
  controlled speeds or feedforward compensation.
- Repeatability of the arm: tests T4 (test 1) and test 2 show whether ±5 mm is
  realistic at 0.65 m.

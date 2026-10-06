# Full arm — concept

A first picture of the complete arm, placing a 15 kg block on a low wall. Simple shapes
only, to show the layout and proportions; the sizes come from
[docs/full-arm-sizing.md](../docs/full-arm-sizing.md) and the pose from `elbow.py`. Not a
worked-out design.

![Concept](out/render_concept_oblique.png)

## Layout

| Joint | DOF | Drive | Why |
|---|---|---|---|
| Base yaw | 1 | Electric: stepper with belt on a slewing ring | A vertical axis carries no gravity torque, so a small motor is enough, and it can turn further than the ≈ 120° of a cylinder |
| Shoulder | 2 (pitch + roll) | 2 × Ø63 × 300, lever 150 mm; the [test 2](../test2/README.md) joint at ≈ 1.7× scale | 162 Nm with 15 kg at 1 m |
| Elbow | 2 (pitch + forearm roll) | 2 × Ø40–50 lying on top of the upper arm, like a biceps; the same joint as the shoulder | see below |
| Wrist | 1 (pitch) | 1 small cylinder along the forearm | keeps the block level |
| Gripper | — | two jaws closed by a pneumatic cylinder | clamps the block at its ends |

- Upper arm and forearm 0.5 m each, shoulder 0.8 m above the floor, wall 0.6 m in front of
  the base: a low wall of 3 courses, about 1 m wide.
- Cylinders for the heavy joints, a small motor where there is no gravity torque.

## Elbow: forearm roll instead of a wrist rotation (`python full-arm/elbow.py`)

The elbow uses the same 2-DOF joint as the shoulder. Its roll turns the forearm about its
own axis, as in a human forearm, so the gripper needs no separate rotation. With base
yaw, shoulder pitch + roll, elbow pitch + roll and wrist pitch the arm has 6 DOF: enough
to hold the block level and lined up with the wall.

Required for 9 block positions (3 along the wall, 3 courses), 15 kg block + 3 kg gripper:

| | Range |
|---|---|
| Base yaw | ±41° |
| Shoulder pitch / roll | −7° … +30° / ±20° |
| Elbow pitch | −101° … −64° (forearm steep) |
| Forearm roll | ±42° |
| Wrist pitch | 59° … 78° |
| Elbow cylinders, pin to pin | 454–582 mm (128 mm of stroke used) |
| Elbow cylinder force | ≤ 187 N push: 19% of Ø50, 30% of Ø40 at 5 bar |

- **Feasible.** Both rolls stay well within the ±65° of the cross block joint.
- The rolls grow with the base yaw: for a wall 1.2 m wide (base yaw ±42° at the ends of a
  wall 0.5 m away) the shoulder needs up to ±86° and the forearm ±69°, beyond the
  joint. For wider walls the base moves along the wall, or the gripper gets its own
  rotation about the vertical (a small motor; no gravity torque there).
- The cylinders lie on top of the upper arm (rear pivots 6 cm from the shoulder, 12 cm
  above the arm axis and 6 cm to the sides, clear of the shoulder hub and its cross
  blocks), on a forearm hub 12 cm from the elbow. A Ø50 × 200 (pin to pin ≈ 390–590 mm)
  covers the lengths.
- Ø40 is enough for the low wall (forearm steep). With the forearm horizontal the elbow
  needs up to ≈ 80 Nm, then Ø50.

![Elbow](out/render_concept_elbow.png)

![Front](out/render_concept_front.png)

### Clash check (`python full-arm/elbow_cad.py`)

CadQuery model of the elbow region in the upper-arm frame: upper arm with the shoulder hub
and its cross blocks, the post with the rear U-joints, the elbow fork and yoke, the forearm
hub with cross blocks, and the two cylinders with rod forks.

| Elbow pitch | Roll 0° | Roll ±42–45° | Roll ±65° |
|---|---|---|---|
| −110° | ok | rod fork touches the forearm hub | many clashes, too short |
| −100° | ok | ok at ±42°, rod fork touches the hub at ±45° | cylinder bodies on the upper arm and shoulder hub |
| −90° … −64° | ok | ok | cylinder bodies on the upper arm and shoulder hub |
| −50° | ok | stroke too short | stroke too short, clashes |

- **The low wall works:** its whole range (pitch −101° … −64°, roll ±42°) is clash-free and
  within the stroke.
- **But the margin is small.** The forearm roll of this layout ends at about ±45°, not the
  ±65° of the shoulder: when rolling, one cylinder dives onto the upper arm and the rod fork
  comes close to the forearm hub.
- Next to compare: the cylinders behind the elbow, pulling a short lever on the back of the
  forearm (like a triceps, or the stick cylinder of an excavator). They then never cross
  the elbow, which leaves more room for the roll.

## Open

- Reach: with 2 × 0.5 m the arm builds a low wall from one spot; more needs a longer arm
  or a base that moves.
- Gripper for blocks versus a tool mount for light tasks.
- Base: fixed, on a pallet with counterweight, or on wheels.

`python full-arm/concept.py` renders the views into `out/` (the first version is in
`out/archive/`).

# Plan

What is done and what is left. Updated: 2026-10-07.

Roles: **(B)** = build, buy, measure; **(D)** = design, software, documentation, review.

## Phase 0 — Goal ✅

- [x] Goal and requirements (15 kg per arm, build a wall, safe, ordinary parts) — [goal.md](../goal.md)
- [x] Actuation: cylinders, pneumatics as the first candidate
- [x] 2-DOF joint sketch and first analysis — [2dof-joint.md](2dof-joint.md)

## Phase 1 — Test rig design ✅

- [x] Principle: one cylinder, 4 fast 2/2 functions (fill/vent per chamber) with PWM — [test1/docs/design.md](../test1/docs/design.md)
- [x] Valves: SMC VQ110U (large flow), each on its own sub-plate (a manifold would connect the chambers)
- [x] Sensors: KTC linear potentiometer 175 mm, 2 pressure sensors G1/4
- [x] Electronics: Pico 2W, ULN2803A, LM7805C for the sensors, emergency stop that cuts the 24 V
- [x] Pneumatic connections, everything in 4 mm tube
- [x] Tests T0–T7 with measurable criteria
- [x] Cost per DOF — [cost-per-dof.md](cost-per-dof.md)

## Phase 2 — Purchasing (in progress)

- [x] AliExpress: valves, pneumatics, sensors, ULN2803A — ordered 2026-10-04 (B)
- [x] Electronics (Tinytronics): Pico 2W, LM7805C, capacitors, 10k + 47k resistors, breadboard, DC jack, USB cable, wire, jumper wires, headers — ordered 2026-10-05 (B)
- [ ] Check the 24 V adapter: DC (not AC), at least 0.5 A, plug size (5.5/2.1 or 5.5/2.5) (B)
- [x] Compressor Stanley DST 100/8/6 (6 l, 59 dB) — ordered 2026-10-05 (B)
- [ ] DIY store, after the compressor: plug nipple G1/4 matching its coupler, tube cutter, PTFE tape, plywood, aluminium, bearings, bolts, multimeter if needed (B)

Order list: [order-list.json](order-list.json); `tools/order_list.py` turns it into a
clickable page.

## Phase 3 — Test 1 as a complete package ✅

- [x] Test 1 = arm with one degree of freedom (a cylinder lifts an arm with a load) — [test1/](../test1/README.md)
- [x] One parameter file (`test1/params.py`) for CAD, simulation, firmware and drawings
- [x] CAD (CadQuery): STEP, STL, DXF, GLB
- [x] MuJoCo simulation with a pneumatics model; control tuned, T3 passes in simulation
- [x] Firmware (MicroPython, Pico 2) and PC tools (logger, tests T0–T7), tested with simulated hardware
- [x] Drawings: side view, cheek, arm, wiring diagram, connection list, pneumatic diagram
- [x] Manual (incl. incoming inspection), design, bill of materials; bundle `dist/test1-package.zip`

## Phase 4 — Build (B, reviewed by D)

- [ ] Upright, arm on bearings, cylinder pivoting between upright and arm, potentiometer on the cylinder (manual 3–6)
- [ ] Pneumatics according to the connection tables; tubes between valve and cylinder < 30 cm
- [ ] Electronics on the breadboard; test without air first (valves click, sensors read)
- [ ] Safety: emergency stop, shut-off slide, start at 2–3 bar

## Phase 5 — Tests and measurements

- [ ] T0 leak test
- [ ] T1 valve response, choose the PWM frequency
- [ ] T2 on/off control
- [ ] T3 PWM control (0° → 30° → −5°)
- [ ] T4 repeatability
- [ ] T5 holding with load
- [ ] T6 stiffness
- [ ] T7 load ratio (how much of the static force the control can use)
- [ ] Comparison with flow restrictors: smaller flow versus speed and precision

## Phase 6 — Decide

- [ ] Does pneumatic feedback control work well enough for the arm? Based on T3–T7.
- [ ] If so: size the shoulder and elbow cylinders with the outcome of T7 (first estimate: [full-arm-sizing.md](full-arm-sizing.md))
- [ ] Choose valves for the large cylinders (flow, possibly coarse + fine)

## First complete arm: the light version

The first complete arm is the light version for 1.5 kg at 1 m (shoulder 2 × Ø32 × 200,
elbow 2 × Ø25 × 80; see [full-arm-sizing.md](full-arm-sizing.md#light-version-15-kg-at-1-m)).
Its forces are close to tests 1 and 2, so their results carry over directly. The heavy
version (15 kg) follows when the light arm works.

The wall is practised with light blocks (≤ 1.5 kg including the gripper margin), with the
speeds capped in software to what the heavy version would reach with one VQ110U per
chamber:

| Joint | Cap | Heavy version |
|---|---|---|
| Shoulder | 30°/s | 2 × Ø50, lever 150 mm |
| Elbow | 50°/s | 2 × Ø50, lever 100 mm |

This shows the tasks, the reach and the pace of the heavy arm. It does not show its
dynamics: a heavier load sags more under a pressure change and takes longer to stop,
so control settings do not carry over one to one. The load share is similar (light
shoulder 24% / 39%, heavy 33% / 55% for work / peak), so the control works in the same range.

Intermediate goal for the light arm: [a small wall of wooden blocks](small-wall.md) (row from a
stack, then two courses).

## After that

- Work out the 2-DOF joint (universal joint, ball joints, pilot-operated check valves
  against sagging when a tube breaks), first in simulation, then build it
- Angle sensors on the joints (e.g. AS5600) instead of linear potentiometers

## First demo task: cleaning a toilet

Before the heavy work, the working arm practises on light tasks that show what it can do.
The first is cleaning a toilet. The first runs are a rehearsal: the toilet is cleaned
beforehand and the sponge is dry, so the arm, the control and the recording can be
practised without water or dirt.

What the task asks of the arm:
- [ ] Reach into the bowl and under the rim: a wrist with enough orientations (at least
  pitch and rotation) and a slim forearm
- [ ] Constant, gentle contact force while wiping: with cylinders the chamber pressure
  sets the force, so force control comes almost for free
- [ ] Tool mount for a sponge or brush on the wrist
- [ ] Remote control by a person (joystick or a small leader arm the large arm follows),
  with recording of the movements and camera images
- [ ] Camera on or near the arm
- [ ] Later, with water and cleaning agent: splash-proof joints, sensors and wiring

After that: learn the task from the recorded runs (imitation learning) so the arm does it
by itself. Other candidate tasks: laundry from the washing machine to the dryer.

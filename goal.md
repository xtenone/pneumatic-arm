# Goal

Steps 1–4 of the stepwise method this project follows: a goal in plain words, the
approach, a concrete target, and a one-sentence presentation that makes it testable.
Each step is the cheapest way to answer a question before taking the next, more
expensive one (text → drawing → simulation → physical test).

## 1. Goal

Build an accessible robot arm: made from commonly available parts, and controlled with
feedback by a program or AI. It does not need industrial speed or precision: half of
what a human arm can do is enough.

## 2. Approach

The joints are moved by cylinders or linear actuators, the way muscles move a human arm,
instead of by motors with gearboxes in the joint. Pneumatics is the first candidate:
compressed air gives way in a collision, and the force can be limited by the pressure.

A simple test rig proves first that a cylinder can be controlled with feedback. Joints
are then added step by step, starting with a two-degree-of-freedom (2-DOF) joint moved
by cylinders.

## 3. Target

An arm that picks up blocks and stacks them into a wall.

## 4. Presentation

A home-built, cylinder-driven arm picks up blocks of about 15 kg and builds a wall
with them.

## Requirements

- Payload: about 15 kg per arm.
- Safety: a fault must not cause a dangerous blow; force and speed must be limited.
- Parts can be bought normally (web shops, AliExpress): no special industrial motors or
  custom drives.

## Open questions

- Reach and accuracy of the arm: how far must it reach, and how precisely must a block be
  placed?
- Keep the cost of the test rigs as low as possible.

## Status (updated when it changes)

The full plan with what is done and what is left: [docs/plan.md](docs/plan.md).

- **Test 1 (arm with one degree of freedom: one cylinder, 4 fast valves with PWM)**:
  complete package in [test1/](test1/README.md) (CAD, simulation, firmware, manual, bill
  of materials); design in [test1/docs/design.md](test1/docs/design.md). AliExpress parts
  ordered on 2026-10-04, electronics on 2026-10-05; compressor and DIY-store parts still to buy. Order list:
  [docs/order-list.json](docs/order-list.json).
- **2-DOF joint**: sketch and first analysis in [docs/2dof-joint.md](docs/2dof-joint.md);
  not yet worked out.

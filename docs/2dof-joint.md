# 2-DOF joint with two cylinders

![Sketch](sketches/2dof-joint-customer-2026-10-04.jpg)

## The principle

A universal joint (cardan joint) in the middle carries the arm. On each side of the
middle there is a lever, and at the end of each lever a cylinder.

- **Both cylinders in the same direction:** the arm tilts up and down (pitch).
- **One cylinder out, the other in:** the arm rotates about the axis pointing away from
  the viewer in the bottom sketches (roll).

The same principle is used in the ankles and wrists of many humanoid robots: two linear
actuators side by side on a universal joint.

## Properties

- **For up and down the cylinders work together:** together they provide the torque
  against gravity, so the heavy axis gets the force of two cylinders.
- **Torque:** pitch = (F1 + F2) · r, roll = (F1 − F2) · b, where r is the distance from
  the pitch axis to the attachment points and b half the distance between the two
  attachment points.
- **Rotating under load:** the cylinders share the work. At maximum load for up and
  down, less is left for rotating.
- **Coupled, non-linear motion:** the software converts the desired angles into two
  cylinder lengths (inverse kinematics).

## What the design has to solve

1. **Centre joint:** a universal joint with intersecting axes. It carries all weight and
   all side loads of the arm, so it must be sturdy.
2. **Cylinder ends:** the attachment points move in three dimensions, so both ends of
   each cylinder need a ball joint or universal joint. Ordinary rod end bearings only
   allow about ±13–15° of misalignment. At larger angles they bind; then high-angle rod
   ends or small universal joints are needed.
3. **Leverage at the extremes:** torque is highest when cylinder and lever are at right
   angles and drops as they line up. The range of motion is chosen so they stay within
   about ±30–40° of perpendicular.
4. **No side loads on the rods:** the universal joint takes the side loads, not the
   cylinders.

## Holding position when a tube breaks

The cylinders must hold their position. Closed valves do that as long as the tubes stay
intact. If a tube between valve and cylinder breaks or comes loose, that chamber empties
and the arm sags with its load. The arm therefore gets pilot-operated check valves
directly on the cylinder ports. They only let air out of the chamber when pilot pressure
is applied; without it the air stays trapped in the cylinder. Not needed for the test rig.

## Holding position under a higher force (for later)

Closed valves hold the air, but air is springy. If an extra force pushes on the arm,
the air is compressed and the arm gives way, even if the valves stay perfectly closed. In
test 1 that is about 10° of deflection for 15 N extra on the load (simulation, 5 bar).
The pressure in the compressed chamber also rises, and the valves have to keep holding
it.

| Measure | What it does | Note |
|---|---|---|
| Higher chamber pressure (stiffness) | gives way less | limited by the weakest component (now 0.7 MPa) |
| Valves rated for higher pressure | stay closed during a pressure peak | fast direct-operated valves go up to about 8 bar, see below |
| Pilot-operated check valves on the cylinder ports | air cannot leave the cylinder, not even when a tube breaks | cheap; makes fine control harder |
| **Mechanical brake or rod lock** | the arm really stays put, independent of the air | e.g. a spring-applied disc brake on the joint, released by air: if air or power fails, it brakes |

Fast valves rated for higher pressure than the VQ110U:

| Valve | Max. pressure | Switching time | Note |
|---|---|---|---|
| SMC VQ110U (current) | 0.7 MPa | 3.5 / 2 ms | large flow (0.7 mm²) |
| SMC VQ110 high-pressure type | 0.8 MPa | ≤ 6.5 ms | smaller flow (0.3 mm²) |
| Festo MHE2 | 0.8 MPa | 1.7–2 ms, up to 330 Hz | more expensive; MHE3 has more flow |
| Ordinary 1 MPa solenoid valves (2V, 4V series) | 0.8–1.0 MPa | 20–50 ms | too slow for fine PWM; usable as a coarse valve |

Fast direct-operated valves above about 8 bar are rare. Really holding position under
overload is therefore more likely to come from a mechanical brake than from higher air
pressure.

## Shoulder force calculation (first rough estimate)

Assumptions: 15 kg at 1 m from the hinge, cylinders 50 cm long and attached at most
37 cm from the hinge, 5 bar, two cylinders pushing together with the full piston area.

| Case | Torque | Total force (lever 0.37 m) | Minimum Ø per cylinder |
|---|---|---|---|
| Weightless arm, 15 kg at 1 m | 147 Nm | 398 N | 2.3–2.4 cm |
| Plus a 30 kg arm with its centre of mass at 0.5 m | 294 Nm | 795 N | 3.2–3.4 cm |

This is the static lower bound: cylinder perpendicular to the lever, no acceleration,
no friction. A working control needs margin on top:

- **Lever at an angle:** the effective lever is 0.37 m · sin(angle between cylinder and
  lever). At 45° off the required force is 1.4× higher.
- **Control headroom:** to accelerate and brake, the static load may only use part of
  the available force. The back pressure in the other chamber and the pressure drop over
  the valves while moving also reduce the force. Test T7 measures how much margin is
  needed.
- **Rotating under load:** in roll one cylinder carries more than half.
- **Standard sizes:** Ø25, 32, 40, 50. With Ø40 the static load uses 63% of the
  available force (2× 628 N at 5 bar), with Ø50 40% (2× 982 N).

**Force versus range.** A long lever gives a lot of force but little angle per
centimetre of stroke. The angle is roughly stroke / lever (in radians): 20 cm of stroke
on a 37 cm lever gives about 30°. More angle needs a shorter lever and therefore a
thicker cylinder.

## Open questions

- Is "rotate" meant as rotation about the arm's own axis (like a wrist turning a key) or
  as swinging sideways (left–right)? The sketch shows the first. For swinging sideways
  the second axis of the universal joint has to be oriented differently.
- Desired range in degrees for up/down and for rotation. Together with the stroke this
  sets the lever length.
- Stroke of the 50 cm cylinders.
- Dimensions: lever lengths, and where the cylinders are attached at the bottom.

## Status

The joint is meant for both the shoulder and the elbow, with different cylinder sizes.
First force calculation for the shoulder above. Detailed design and simulation wait until
the test rig proves that pneumatics work.

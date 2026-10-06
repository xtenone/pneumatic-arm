# Cost per DOF

A DOF (degree of freedom) here is one cylinder with its valves, sensors and controller.
Shared parts (compressor, regulator, power supply) are not included.

## Test rig (October 2026)

| Part | Price |
|---|---|
| 4× SMC VQ110U | €104 |
| Cylinder MAL20 | €10 |
| Linear potentiometer KTC-175 | €16–28 |
| 2× pressure sensor (stainless, G1/4) | €25–32 |
| Fittings, tube, silencers | ~€10 |
| Raspberry Pi Pico 2 | €7 |
| **Total** | **approx. €175–190** |

The valves are about 58% of the cost. The test rig keeps all sensors and four valves,
because it has to show what the arm really needs.

## Possible savings for the arm

Each saving depends on a measurement in the test rig:

| Saving | From → to | Decided by |
|---|---|---|
| AS5600 angle sensor on the joint instead of a linear potentiometer | €16–28 → ~€3 | Accuracy of the AS5600 on the joint |
| Bare pressure sensor chips (e.g. XGZP6847A, 0–1000 kPa, 0.5–4.5 V) instead of stainless transducers | €25–32 → ~€6–10 | Whether pressure feedback is needed (T3/T6 with and without) |

With both savings: about €150 per DOF, plus the larger cylinders for shoulder and elbow.

Four valves per cylinder remain necessary: the cylinder has to be able to hold its
position for safety. Cheap "VQ110" listings at €7–13 are bait prices for a different
item, not a real alternative.

## Cost per DOF versus joint torque (estimate)

A rough estimate per drive type, per DOF, without shared parts (compressor, hydraulic power
unit, power supply). Prices are indicative (October 2026) and still to be checked when a
choice depends on them.

| Joint torque | Electric (gearbox + motor) | Pneumatic | Hydraulic |
|---|---|---|---|
| Small (wrist, ~20 Nm) | **cheapest**: stepper with planetary gearbox, €50–100 | €150–190 | €450–600 + power unit |
| Medium (elbow, ~80 Nm) | €300–600 | €170–220 (Ø50) | €450–600 |
| Large (shoulder, 160–300 Nm) | €600–1200+ (harmonic size 32, servo, brake) | €180–250 (Ø63–80), but slow | €450–600 |
| Very large (1000+ Nm) | thousands of euros | impractically large cylinders | €500–700 |

Why it scales this way:
- **Electric:** the torque goes through gears and bearings, which have to become heavier
  and more precise, so the price rises steeply with torque.
- **Hydraulic:** more force mainly means a slightly larger cylinder, which is cheap; the
  valves and sensors stay almost the same. The power unit (€400–800) is a fixed cost
  shared by all DOFs. See [hydraulics.md](hydraulics.md).
- **Pneumatic:** the low pressure makes the cylinders large. The cost per DOF stays
  reasonable, but speed drops and air use rises.

Consequences:
- The hydraulic figure is mostly the four proportional cartridges (≈ €100 each); it
  hardly changes with force.
- At 15 kg pneumatics is the cheapest per DOF for the heavy joints; hydraulics costs more
  per DOF plus the power unit, and only pays back at large forces.
- For heavier work hydraulics wins.
- A mix is logical: cylinders for the heavy joints (shoulder, elbow), a small electric
  motor for the light ones (wrist rotation, gripper).

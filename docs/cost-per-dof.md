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

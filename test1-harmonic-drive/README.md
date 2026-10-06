# Test 1 reference — the same arm on a harmonic drive

The electric counterpart of [test 1](../test1/README.md): the same arm, load and base,
but the joint is driven the way most robot arms are driven: a motor with a harmonic
drive (strain wave gear) in the joint. Cobots (Universal Robots, Franka, Kinova) use
this in every joint; industrial robots use it in the wrist.

It answers: **how does the pneumatic joint compare with the standard electric joint on
precision, speed, stiffness, behaviour when pushed, cost and weight?**

## Set-up

- **Gear:** harmonic drive size 17, ratio 100:1, cup type (CSF-17 pattern; clones are
  widely available). Zero backlash: 1 arcmin is 0.12 mm at the load.
- **Motor:** NEMA23 closed-loop stepper (motor with encoder and driver), step/dir from
  the Pico. The flange takes a servo motor of the same frame size later, for the full
  cobot set-up with torque control.
- **Arm, load, base:** as test 1 (flat bar 40×5, 450 mm, load hook at 400 mm, plywood
  cheeks).
- **Sensor:** an AS5600 magnetic angle sensor on the joint. Test 1 gets the same sensor,
  so both are measured the same way (test 1 itself measures the cylinder length).

## Sizing (`python hdparams.py`)

| | 1.5 kg | 3 kg (T5) |
|---|---|---|
| Gravity torque, arm horizontal | 6.4 Nm | 12.3 Nm |
| Arm inertia / motor rotor seen through the gear | 0.26 / 0.28 kg·m² | 0.50 / 0.28 kg·m² |
| Torque at 180°/s², arm horizontal | 8.1 Nm | 14.7 Nm |
| Torque at the motor (efficiency 70%) | 0.12 Nm | 0.21 Nm |

- The gear's limit for repeated peak torque is 54 Nm, also above the 21 Nm the cylinder
  of test 1 can deliver.
- The motor's rotor, multiplied by 100² through the gear, weighs as much as the arm with
  1.5 kg. This is typical for geared joints and one of the things the comparison shows.
- Output speed about 36°/s (motor at 600 rpm).

The [printed cycloidal drive](../test1-cycloid/README.md) (on hold) would use the same
motor, so only the gearbox would differ.

## Comparison

Both set-ups run the tests of the [test 1 manual](../test1/docs/manual.md) with the same
criteria:
- step response (T3): overshoot, settling time and error;
- load (T7): the largest load that still meets the criteria;
- stiffness (T6): deflection under a push;
- also speed, behaviour when the arm hits something, energy use, cost and weight.

## Status

Folder created; sizing done. Next: CAD with renders, simulation with the same tests,
bill of materials.

Open: ratio 100:1 or 50:1 (twice the speed and a quarter of the rotor inertia, at
lower peak torque).

# Simulation of test 1 — results

Load 1.5 kg, supply 5.0 bar, tuning from `params.py`. T3 criteria: overshoot < 5 mm, settled (within ±1 mm) within 1 s, error < 1 mm.

## T3 PWM control and T2 on/off control

| Step | Overshoot (mm) | Settling (s) | Error (mm) | Passed |
|---|---|---|---|---|
| PWM: 0° → 30° | 1.04 | 0.92 | 0.27 | yes |
| PWM: 30° → −5° | 1.17 | 0.508 | 0.11 | yes |
| on/off (3 bar): 0° → 30° | 15.09 | 1.998 | 21.6 | no |
| on/off (3 bar): 30° → −5° | 24.77 | 1.998 | 13.32 | no |

![PWM control](step.png)

![on/off control](onoff.png)

## T7 load ratio

| Load (kg) | Load (%) | Overshoot (mm) | Settling (s) | Error (mm) | Passed |
|---|---|---|---|---|---|
| 0.5 | 14 | 1.74 | 1.936 | 0.46 | no |
| 1.5 | 35 | 1.04 | 0.92 | 0.27 | yes |
| 2.5 | 57 | 3.04 | 1.982 | 0.45 | no |
| 3.5 | 78 | 2.24 | 1.998 | 1.2 | no |
| 4.5 | 100 | 0.0 | 1.998 | 53.69 | no |
| 5.5 | 122 | 0.0 | 1.998 | 105.49 | no |

## T6 stiffness (valves closed, 15 N extra on the load)

| Sum of chamber pressures (bar) | Deflection (degrees) |
|---|---|
| 2.0 | 14.13 |
| 5.0 | 10.44 |

## T8 knob and button: smooth profile with feedforward

Load 1.5 kg strapped under the arm end, 5.0 bar. Knob targets 30°, -5°, 50°, 10°, 40°, 20° (the last two 0.15 s apart: a new target during a move). Criteria per move: tracking error < 3 mm, overshoot < 2 mm, within ±1.5 mm at most 0.2 s after the profile ends, mean error at rest < 1 mm. Worst case of 3 runs with different sensor noise.

| Move | Profile (s) | Tracking (mm) | Overshoot (mm) | Settled after the profile (s) | Press → settled (s) | Passed |
|---|---|---|---|---|---|---|
| → 30° | 0.414 | 2.02 | 1.04 | 0.0 | 0.414 | yes |
| → -5° | 0.442 | 1.62 | 1.12 | 0.0 | 0.442 | yes |
| → 50° | 0.689 | 1.11 | 0.93 | 0.0 | 0.689 | yes |
| → 10° | 0.504 | 2.52 | 1.16 | 0.0 | 0.504 | yes |
| → 20° | 0.566 | 1.7 | 18.19 | 0.0 | 0.566 | yes |

(one run; the last row is the new target during a move: its overshoot is past the new, nearer target and does not count)

![T8](t8.png)

| Controller / setting | Tracking (mm) | Overshoot (mm) | Settled after the profile (s) | New target during a move: tracking (mm) | Passed |
|---|---|---|---|---|---|
| profile 150°/s, 1500°/s² (params.py) | 2.52 | 1.33 | 0.0 | 2.22 | yes |
| profile 100°/s, 1000°/s² | 1.34 | 1.32 | 0.0 | 1.1 | yes |
| profile 200°/s, 2000°/s² | 3.59 | 1.63 | 0.062 | 5.59 | no |
| profile 250°/s, 2500°/s² | 9.23 | 9.58 | 0.476 | 15.11 | no |
| load set to 1.2 kg (real 1.5 kg) | 3.5 | 1.97 | 0.0 | 2.8 | no |
| load set to 1.8 kg (real 1.5 kg) | 2.52 | 1.64 | 0.37 | 2.5 | no |
| T3 controller (ramp 250 mm/s, no feedforward) | 21.15 | 9.32 | 0.743 | 24.45 | no |

![T8 with the T3 controller](t8_t3_controller.png)

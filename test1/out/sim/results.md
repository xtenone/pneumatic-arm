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
| → 30° | 0.447 | 1.52 | 1.09 | 0.0 | 0.447 | yes |
| → -5° | 0.471 | 1.17 | 0.92 | 0.0 | 0.471 | yes |
| → 50° | 0.609 | 1.42 | 1.28 | 0.0 | 0.609 | yes |
| → 10° | 0.489 | 1.32 | 0.91 | 0.0 | 0.489 | yes |
| → 20° | 0.646 | 0.85 | 18.09 | 0.0 | 0.646 | yes |

(one run; the last row is the new target during a move: its overshoot is past the new, nearer target and does not count)

![T8](t8.png)

| Controller / setting | Tracking (mm) | Overshoot (mm) | Settled after the profile (s) | New target during a move: tracking (mm) | Passed |
|---|---|---|---|---|---|
| profile 170°/s, 1550°/s² (params.py) | 1.99 | 1.53 | 0.0 | 1.57 | yes |
| 1.1× as fast (187°/s, 1876°/s²) | 2.24 | 1.68 | 0.0 | 2.34 | yes |
| 1.15× as fast (195°/s, 2050°/s²) | 5.87 | 2.02 | 0.08 | 8.66 | no |
| 1.3× as fast (221°/s, 2620°/s²) | 7.95 | 6.61 | 0.453 | 14.96 | no |
| load set to 1.35 kg (real 1.5 kg) | 1.88 | 1.78 | 0.0 | 1.42 | yes |
| load set to 1.65 kg (real 1.5 kg) | 2.35 | 1.28 | 0.0 | 1.47 | yes |
| load set to 1.2 kg (real 1.5 kg) | 2.63 | 2.08 | 0.205 | 2.05 | no |
| load set to 1.8 kg (real 1.5 kg) | 2.15 | 1.46 | 0.0 | 1.37 | yes |
| T3 controller (ramp 250 mm/s, no feedforward) | 21.15 | 9.32 | 0.743 | 24.45 | no |

![T8 with the T3 controller](t8_t3_controller.png)

# Simulation of test 1 — results

Load 1.0 kg, supply 5.0 bar, tuning from `params.py`. T3 criteria: overshoot < 5 mm, settled (within ±1 mm) within 1 s, error < 1 mm.

## T3 PWM control and T2 on/off control

| Step | Overshoot (mm) | Settling (s) | Error (mm) | Passed |
|---|---|---|---|---|
| PWM: 0° → 30° | 1.74 | 0.54 | 0.07 | yes |
| PWM: 30° → −5° | 1.87 | 0.666 | 0.33 | yes |
| on/off (3 bar): 0° → 30° | 22.19 | 1.998 | 23.45 | no |
| on/off (3 bar): 30° → −5° | 28.92 | 1.998 | 13.8 | no |

![PWM control](step.png)

![on/off control](onoff.png)

## T7 load ratio

| Load (kg) | Load (%) | Overshoot (mm) | Settling (s) | Error (mm) | Passed |
|---|---|---|---|---|---|
| 1.0 | 24 | 1.74 | 0.54 | 0.07 | yes |
| 2.0 | 46 | 1.64 | 1.45 | 0.37 | no |
| 3.0 | 68 | 4.14 | 1.998 | 0.56 | no |
| 4.0 | 89 | 0.0 | 1.998 | 11.72 | no |
| 5.0 | 111 | 0.0 | 1.998 | 85.58 | no |

## T6 stiffness (valves closed, one 1 kg plate added)

| Sum of chamber pressures (bar) | Deflection (degrees) |
|---|---|
| 2.0 | 10.6 |
| 5.0 | 6.79 |

## T8 knob and button: smooth profile with feedforward

Load 1 kg (dumbbell plates bolted to the arm end), 5.0 bar. Knob targets 30°, -5°, 50°, 10°, 40°, 20° (the last two 0.15 s apart: a new target during a move). Criteria per move: tracking error < 3 mm, overshoot < 2 mm, within ±1.5 mm at most 0.2 s after the profile ends, mean error at rest < 1 mm. Worst case of 3 runs with different sensor noise.

| Move | Profile (s) | Tracking (mm) | Overshoot (mm) | Settled after the profile (s) | Press → settled (s) | Passed |
|---|---|---|---|---|---|---|
| → 30° | 0.447 | 1.26 | 1.09 | 0.0 | 0.447 | yes |
| → -5° | 0.471 | 1.52 | 1.02 | 0.0 | 0.471 | yes |
| → 50° | 0.609 | 1.39 | 1.33 | 0.0 | 0.609 | yes |
| → 10° | 0.489 | 2.05 | 1.26 | 0.0 | 0.489 | yes |
| → 20° | 0.646 | 1.16 | 18.74 | 0.0 | 0.646 | yes |

(one run; the last row is the new target during a move: its overshoot is past the new, nearer target and does not count)

![T8](t8.png)

| Controller / setting | Tracking (mm) | Overshoot (mm) | Settled after the profile (s) | New target during a move: tracking (mm) | Passed |
|---|---|---|---|---|---|
| profile 170°/s, 1550°/s² (params.py) | 2.05 | 1.48 | 0.0 | 1.82 | yes |
| 1.1× as fast (187°/s, 1876°/s²) | 3.15 | 1.81 | 0.037 | 1.37 | no |
| 1.15× as fast (195°/s, 2050°/s²) | 2.29 | 1.93 | 0.031 | 2.31 | yes |
| 1.3× as fast (221°/s, 2620°/s²) | 4.19 | 3.31 | 0.179 | 9.56 | no |
| 2 kg load, same profile | 2.68 | 1.93 | 0.891 | 2.83 | no |
| 2 kg load, 10% lower speed | 2.88 | 1.86 | 0.019 | 1.47 | yes |
| load set to 0.9 kg (real 1.0 kg) | 2.0 | 1.83 | 0.0 | 1.61 | yes |
| load set to 1.1 kg (real 1.0 kg) | 1.82 | 1.37 | 0.0 | 1.36 | yes |
| load set to 0.8 kg (real 1.0 kg) | 3.38 | 2.08 | 0.003 | 1.64 | no |
| load set to 1.2 kg (real 1.0 kg) | 1.44 | 1.46 | 0.0 | 1.33 | yes |
| T3 controller (ramp 250 mm/s, no feedforward) | 19.3 | 5.46 | 0.331 | 18.6 | no |

![T8 with the T3 controller](t8_t3_controller.png)

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

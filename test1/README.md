# Test 1 — pneumatic arm with one degree of freedom

![Test 1](out/sim/render_arm_horizontal_oblique.png)

## Project description

This is the first and smallest test of the [pneumatic-arm](../README.md) project: an
accessible robot arm that works with cylinders, like muscles, and is controlled with
feedback by a program or AI.

Test 1 answers one question: **can an ordinary pneumatic cylinder with cheap on/off
valves move an arm to a chosen angle and keep it there, fast and to the millimetre, also
with a load on it?**

**The set-up:**
- a 45 cm arm on a hinge, moved by one Ø20 × 150 mm cylinder;
- per cylinder chamber a fill valve and a vent valve (SMC VQ110U, 4 pieces), driven with
  PWM;
- a linear potentiometer for the position, a pressure sensor per chamber, and a
  Raspberry Pi Pico 2 that controls everything 500 times per second.

**What it delivers:**
- the answer whether pneumatics work for this arm;
- the number that sets how big the shoulder and elbow cylinders have to be (test T7);
- the control software that carries over to the real arm.

**Targets** (test T3): overshoot < 5 mm, settled within 1 s, error < 1 mm. The
simulation meets them with the current tuning; see the [results](out/sim/results.md).

## What is in this package

| Folder / file | Contents |
|---|---|
| [`docs/manual.md`](docs/manual.md) | **Start here.** Incoming inspection, building, wiring, software, calibration, tests T0–T7, troubleshooting |
| [`docs/design.md`](docs/design.md) | Why it is built this way: valves, pneumatics, electronics, mechanics, control, simulation |
| [`docs/bom.md`](docs/bom.md) | Bill of materials with items, variants, quantities and prices; also as CSV |
| `out/drawings/` | Side view, cheek and arm dimension drawings, wiring diagram, connection list, pneumatic diagram (PNG + PDF) |
| `out/cad/` | CAD: STEP per part and of the assembly, STL, DXF profiles, GLB (3D in a browser) |
| `out/sim/` | Simulation results, plots and renders |
| `params.py` | **All dimensions and settings.** Everything else is generated from it |
| `cad/` | CadQuery model (`parts.py`) and export (`export.py`) |
| `sim/` | MuJoCo model (`model.py`), pneumatics model (`pneumatics.py`), scenarios (`run.py`) |
| `firmware/` | MicroPython for the Pico 2: `main.py`, `control.py` (controller), `hw.py`, `config.py` (generated) |
| `host/` | PC tools: `logger.py` (manual control + recording), `tests_t0_t7.py` (tests T0–T7, automated), `analysis.py` |
| `tests/test_firmware.py` | Runs the firmware on a PC with simulated hardware |
| `build.py` | Regenerates everything and builds the bundle |

## Quick start

- **Build:** follow [the manual](docs/manual.md) from top to bottom.
- **Run the simulation:**
  ```
  pip install -r requirements.txt
  python sim/run.py --render
  ```
- **Change something** (a dimension, a gain): edit `params.py` and run
  `python build.py`. CAD, simulation, firmware settings, drawings and bill of materials
  are then in sync again.

## Status

| Part | Status |
|---|---|
| Design, CAD, drawings | done |
| Simulation and tuning | done; T3 passes in simulation |
| Firmware and PC tools | done, tested with simulated hardware; not yet on a real Pico |
| Parts | AliExpress ordered 2026-10-04; electronics, compressor and DIY-store parts still to buy |
| Build and tests T0–T7 | to do |

## Open and free to rebuild

Designed to be rebuilt with ordinary parts. All sources (CadQuery, MuJoCo, MicroPython,
Python) are plain text and open; no paid software is needed. See the
[licence](../LICENSE).

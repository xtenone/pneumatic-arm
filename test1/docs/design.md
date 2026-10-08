# Test 1 — design: arm with one degree of freedom, one cylinder, four fast valves

This document explains what was chosen and why. How to build and test it is in
[manual.md](manual.md); all dimensions are in `../params.py`.

## What this test has to prove

Can an ordinary pneumatic cylinder with cheap on/off valves and a microcontroller move
an arm to a chosen angle and keep it there, also with a load on it? And how precisely?
Each cylinder chamber gets its own pressure sensor. That lets the software control the
stiffness as well as the position: how hard the cylinder pushes back when you pull on it.

## The idea

A double-acting cylinder has two chambers, A (rod out) and B (rod in). Each chamber
gets two valves:

- a **fill valve**: when open, air flows into the chamber;
- a **vent valve**: when open, air flows out of the chamber.

When both valves of a chamber are closed, the air stays in. The valves open and close
tens of times per second (PWM). By keeping them open longer or shorter, the software
controls how fast a chamber fills or empties.

```
compressor ── filter + regulator ── shut-off slide ── main valve ──┐
                                                                   │
                                 ┌─────────────────────────────────┤
                                 │                                 │
                            [V1 fill A]                       [V3 fill B]
                                 │                                 │
      pressure sensor pA ── chamber A ═══ CYLINDER ═══ chamber B ── pressure sensor pB
                                 │                                 │
                            [V2 vent A]                       [V4 vent B]
                                 │                                 │
                              silencer                          silencer

             linear potentiometer along the rod ── position x
```

| V1 | V2 | Chamber A |
|----|----|-----------|
| off | off | holds pressure |
| on | off | fills |
| off | on | empties |
| on | on | **forbidden**: blows air straight through. The software blocks this. |

V3 and V4 work the same way for chamber B.

## The valves

**Choice: SMC VQ110U (large flow), 5 pieces: 4 plus 1 spare.**

- 3/2 valve, direct operated (poppet), normally closed
- Response time: on 3.5 ms, off 2 ms. Fast enough for PWM at 20–50 Hz.
- Maximum 0.7 MPa (7 bar), 24 V DC
- Small, and available on AliExpress
- Flow: Cv 0.02 (standard) or 0.04 (VQ110U, large flow)

| | Standard (VQ110) | Large flow (VQ110U) |
|---|---|---|
| Full stroke of the Ø20 cylinder, roughly | 0.5–1 s | 0.25–0.5 s |
| Smallest force step per pulse (approx. 4 ms) | 1–2 N | 3–4 N |

All four positions get a VQ110U. A cylinder is as fast as the slowest valve in the
loop: in every move one chamber fills while the other empties, so one standard valve in
that loop slows down the whole move. With four large valves the cylinder is fast in both
directions. The larger force steps (3–4 N) are expected to stay below the seal friction
(5–10 N), which limits the precision anyway.

To mimic a smaller valve, a flow restrictor can be put in series with each fill valve.
Turned in, the fill valve behaves like a smaller valve, continuously adjustable. This
measures which flow gives the best balance between speed and precision, and that
measurement drives the valve choice for the arm.

A 3/2 valve becomes a 2/2 valve by plugging one port with an M5 blanking plug:

- **Fill valve:** P ← supply, A → chamber, R plugged. Off = closed, on = filling.
- **Vent valve:** P ← chamber, A → silencer, R plugged. Off = P closed, on = venting.

The leak test (T0) checks that the closed position really stays closed.

**Order code** (from SMC's "How to order" chart):

- `U` = large flow type
- `5` = 24 V DC (`6` = 12 V DC; `1`–`4` are AC)
- `M` or `L` = plug connector *with* lead wire; `MO`/`LO` = without lead wire
- `-M5` = single valve on a sub-plate with M5 ports. Without `-M5` it is a valve for a
  manifold, and you need a base for it.

Order code used: **VQ110U-5M-M5** (5×).

The cheaper version without `-M5` (manifold valve) does not fit here. A manifold has a
common P port for all valves, while the vent valves need their own P, because that is
where the chamber is connected.

Two manifolds do not solve that either: a fill block of VQ110s with the common R plugged
and a vent block of VQ120s (normally open) with the common P plugged. With all valves
off, chambers A and B are both connected to that plugged common channel, and therefore
to each other. The pressures equalise and the cylinder sags. Every valve needs its own
plugged port, which only a sub-plate per valve gives.

**How a coil reaches 50 Hz.** The VQ110 is *direct operated*: the coil lifts a small,
light armature a few tenths of a millimetre, and that armature is the valve itself. Large
valves such as the 4V210 are *pilot operated*: the coil opens a small air passage and
that air moves a large spool, which takes 20–50 ms. At 50 Hz one period is 20 ms, and the
VQ110 needs about 5.5 ms to open and close again. That fits easily.

There are two kinds of PWM:

- **Slow (20–50 Hz), which this set-up uses.** The valve follows every pulse: fully
  open, fully closed. The cylinder and tubes act as a buffer and average the bursts, like
  a bucket filled with short splashes. The pulse width sets the average flow.
  - A pulse shorter than the opening time (approx. 3.5 ms) does not open the valve. At
    50 Hz roughly 20–85% duty is usable. The software compensates for this dead zone.
  - A lower frequency gives finer steps but more pressure ripple. T1 sets the frequency.
- **Fast (kHz) on the coil.** The valve does not follow this; the coil averages the
  current. It is used for "peak and hold": full current to open, less to hold open. Less
  heat, and the valve closes faster. It does **not** hold an on/off valve half open; only
  a proportional valve can do that, and it is built differently (spool against a spring).
  Not needed for now.

The `M`/`L` variants have a built-in LED and surge suppressor, so polarity matters: red
to +24 V, black to an output of the ULN2803A.

**Service life.** At 50 Hz a valve switches 180,000 times per hour, but only while the
arm moves; at rest the valves are closed. Not a concern for the test. For the arm, valve
life becomes a selection criterion.

**Why not a cheaper 2/2 valve?** Ordinary solenoid valves such as the 2V025 and the 2W
series (€5) respond in 20–50 ms. PWM above about 10 Hz is then impossible and the control
gets coarse. The small 10 mm "high-frequency" valves are cheap (€5–8) but rated for 30 Hz
with very little flow: usable for a first test, not for an arm joint.

**Why not the VT307?** Also SMC, direct operated, with much more flow and "universal
porting" (pressure allowed on any port, so the same valve works as normally closed,
normally open or diverter). But its response time is about 20 ms, more than five times
slower than the VQ110, which limits PWM to about 10 Hz: too coarse for this control. For
the arm it is a candidate as a *coarse* valve for fast moves next to a small fast valve
for fine control.

**Looking ahead:** the VQ110 is big enough for this Ø20 test cylinder, not for the
cylinders of the final arm. Those will be Ø40–63, because 15 kg at arm's length needs
hundreds to over a thousand newtons of cylinder force. They need larger fast valves, or
several valves in parallel. This test provides the control software and the measurements
to make that choice.

## Parts

The current list with items, variants, quantities and prices is in
[order-list.json](../../docs/order-list.json); `tools/order_list.py` turns it into a
clickable page, and `build.py` turns it into [bom.md](bom.md).

Summary:

- **Pneumatics (AliExpress):** 5× VQ110U-5M-M5, cylinder MAL20×150 (PT1/8 ports) with an
  M22×1.5 nut and an M8 rod clevis, AFR-2000 regulator with fibre filter, HSV-08 shut-off
  slide, 3V210-08 main valve (NC, 24 V DC), emergency stop in a box, 4 mm push-in
  fittings (M5, 1/8, 1/4), PCF4-02 for the pressure sensors, 4 mm tees, M5 blanking plugs,
  M5 silencers, 2 flow restrictors, 10 m of 4×2.5 mm PU tube.
- **Sensors (AliExpress):** KTC linear potentiometer 175 mm (5 kΩ, type B), 2 pressure
  sensors 0–100 psi G1/4 (output 0.5–4.5 V or 0–5 V; the 10k/15k divider is safe for both).
- **Electronics:** ULN2803A (AliExpress, 10 pieces); Pico 2, LM7805C, 1 µF and 100 nF
  capacitors, 10 kΩ and 15 kΩ resistors, breadboard, DC jack, USB cable and wire; a 24 V
  adapter.
- **DIY store:** plywood, aluminium flat bar and strip, 608 bearings, M8 bolts, tube for
  spacer sleeves, hose clamps, F-clamps, plug nipple to match the compressor, tube cutter,
  PTFE tape, and a multimeter if needed.
- **Compressor:** Stanley DST 100/8/6, 6 l, 8 bar, 59 dB (quiet enough for indoor testing).

EU import duty (since 1 July 2026): €3 + VAT per product category per consignment. Items
shipped by AliExpress itself are grouped into categories.

**Why not an optical distance sensor (VL6180X, VL53L series)?** It measures without
contact, which is attractive. But the VL6180X is rated up to 100 mm while the stroke is
150 mm, its noise is a few millimetres against a target of ±1 mm, and one measurement
takes about 10 ms: at 0.6 m/s the cylinder has moved 6 mm before the reading arrives. Too
slow for a fast control loop.

## Pneumatic connections

Each row is one connection; the quantities in the parts list follow from this.

**Supply**

| From | Fitting | Tube | To | Fitting |
|---|---|---|---|---|
| Compressor hose (Euro coupler) | – | – | regulator IN | plug nipple G1/4 + PTFE tape |
| Regulator OUT | – | – | shut-off slide IN | male thread of the slide straight into the regulator (otherwise PC4-02 + tube + PC4-02) |
| Shut-off slide OUT | PC4-02 | 4 mm | main valve P | PC4-02 |
| Main valve A | PC4-02 | 4 mm | 4 mm tee | – |
| Main valve R | leave open (only vents the supply line on an e-stop) | – | – | – |
| Tee branch 1 | – | 4 mm (later via a flow restrictor) | V1 P (fill A) | PC4-M5 |
| Tee branch 2 | – | 4 mm (later via a flow restrictor) | V3 P (fill B) | PC4-M5 |

**Per chamber (A with V1/V2, B with V3/V4)**

| From | Fitting | Tube | To | Fitting |
|---|---|---|---|---|
| Fill valve, port A | PC4-M5 | 4 mm | tee 1 | – |
| Tee 1 | – | 4 mm | vent valve, port P | PC4-M5 |
| Tee 1 | – | 4 mm | tee 2 | – |
| Tee 2 | – | 4 mm | cylinder port | PC4-01 |
| Tee 2 | – | 4 mm | pressure sensor | PCF4-02 |
| Vent valve, port A | M5 silencer | – | – | – |
| Port R of fill and vent valve | M5 blanking plug | – | – | – |

- **Short tubes:** keep every tube between valves and cylinder shorter than about
  30 cm, and put the pressure sensor close to the cylinder port.
- **Flow restrictors:** if the restrictor has an arrow (one-way type), point it towards
  the fill valve. Fully open, it does not restrict the flow.

**Threads**

- G1/8 and G1/4 are BSP threads (also sold as PT or BSPT on AliExpress). They fit each
  other; use PTFE tape on PT.
- **Do not buy NPT:** NPT has a different pitch (27 instead of 28 threads per inch) and
  jams or leaks in a G port. Watch out with pressure sensors in particular; they are often
  sold with 1/8 NPT.
- M5 is M5×0.8 everywhere.
- **Tube:** everything in 4 mm (4×2.5). During a move only one fill valve is open
  (approx. 40 Nl/min), and 4 mm tube is ample for that.
- **Import duty:** €3 + VAT per product category per consignment, so the design keeps
  the number of different parts low: no 6 mm tube and no Y-piece.

## Electrical

- **Pico 2 → ULN2803A:** 4 PWM pins, one per valve. The ULN2803A switches the low side
  of each coil. A VQ110 coil draws only about 40–60 mA, well within the chip's 500 mA
  per channel. The flyback diodes are inside the chip: pin 10 (COM) to +24 V.
  - A diode slows down the closing of the valve a little. If that shows up in T1, a
    Zener diode per coil will be added.
- **Coils:** red to +24 V, black to an output of the ULN2803A. Mind the polarity: the
  built-in LED and suppressor work in one direction only.
- **Emergency stop and main valve:** the +24 V from the adapter goes through the
  emergency stop first. After it come the main valve (directly, so it is on whenever the
  e-stop is released) and the plus of the four VQ110U coils. Pressed: everything drops
  out, even if the software hangs.
- **Potentiometer:** on the Pico's 3.3 V, wiper to ADC0 (GP26).
- **Pressure sensors:** on 5 V from an LM7805C fed from the 24 V, not on the USB 5 V.
  - The output of these sensors scales with their supply voltage. The USB voltage varies
    up to ±5%, which would directly give ±5% measurement error.
  - The two sensors draw about 20 mA together; the 7805 then dissipates
    (24 − 5) V × 0.02 A ≈ 0.4 W, fine without a heat sink. A linear regulator gives a
    quieter supply than a switching step-down, which is better for analogue readings.
  - Capacitors: 1 µF between IN and GND, 100 nF between OUT and GND, close to the pins.
  - The 7805 sits before the e-stop, so the sensors keep measuring when the e-stop is
    pressed.
  - Each sensor output goes through a 10 kΩ (top) / 15 kΩ (bottom) divider (or 3× 47 kΩ in
    parallel = 15.7 kΩ, ratio 0.61, 5 V → 3.05 V) to ADC1 (GP27)
    and ADC2 (GP28). That turns 5.0 V into 3.0 V, safe for the Pico whether the sensor
    gives 0.5–4.5 V or 0–5 V.
  - Which output type it is shows at the first reading: at 0 bar it gives about 0.5 V or
    about 0 V. The software calibrates at 0 bar and at a known pressure (the regulator's
    gauge).
- **Noise:** a 100 nF capacitor from each ADC input to GND.
- **Ground:** the adapter's minus, pin 9 (GND) of the ULN2803A and the Pico's GND
  connected together.
- **PC over USB:** powers the Pico and receives the data (position, two pressures,
  valve states), hundreds of times per second.
- **Supply:** a closed 24 V plug-in adapter (at least 0.5 A, 1–2 A preferred), no open
  mains supply with screw terminals, so there is no 230 V anywhere near the rig.
  Consumption: 4 valve coils at most ~250 mA, main valve ~125 mA, 7805 + sensors ~25 mA;
  about 400 mA in the worst case.

## Mechanical: the arm

The cylinder lifts an arm, as it will in the shoulder. This tests what happens in the
real arm: a force that changes with the angle, a load at the end, and the conversion from
cylinder length to angle. See `out/drawings/side_view.pdf`.

- **Upright:** two 18 mm plywood cheeks with a 36 mm spacer block between them (two
  layers of the same plywood), on a 40 × 30 cm base plate. The rig sits on the edge of a
  table, held by two F-clamps; the load hangs beside the table.
- **Hinge:** an M8 bolt through two 608 ball bearings (skateboard bearings) in the
  cheeks, 420 mm above the base plate. Cheap, available everywhere, and without play.
- **Arm:** aluminium flat bar 40×5 mm, 450 mm long. The cylinder's clevis attaches
  150 mm from the hinge, the load hangs at 400 mm.
- **Cylinder:** pivots at the rear on an M8 bolt, 320 mm straight below the hinge.
  Pin-to-pin 311–461 mm gives an arm angle of −17° to +66°.
- **Potentiometer:** fixed to the cylinder tube with hose clamps, its rod connected via a
  small bracket to the cylinder rod. It measures the cylinder length; the software
  converts that to the angle.

| Arm angle | Cylinder lever | Max. torque at 5 bar | Gravity (arm + 1.5 kg) | Load |
|---|---|---|---|---|
| −17° | 148 mm | 23.2 Nm | 6.1 Nm | 26% |
| 0° | 136 mm | 21.3 Nm | 6.4 Nm | 30% |
| 40° | 85 mm | 13.4 Nm | 4.9 Nm | 37% |
| 66° | 43 mm | 6.7 Nm | 2.6 Nm | 39% |

The higher the arm, the smaller the cylinder's lever: the same effect as in the 2-DOF
joint later (see `docs/2dof-joint.md` in the repository root).

## Control

The algorithm is in `firmware/control.py` and runs **unchanged** on the Pico and in the
simulation, so the tuning from the simulation is exactly what goes onto the Pico.

**Layers:**

- **Fast layer, on the Pico (500 times per second):** reads position and pressures and
  drives the valves.
  1. **Speed-limited target:** the target moves to the requested position at most
     250 mm/s. A full stroke takes about 0.6 s, without a step in the control error.
  2. **Position controller (PID) → desired force.**
     - The integral term only works close to the target (within 6 mm) or when the arm is
       stalled. That overcomes friction and load without overshoot.
  3. **Force → chamber pressures:** the desired force is split over chambers A and B, with
     the sum of both pressures as the **stiffness** (adjustable, default 4 bar).
  4. **Pressure loop per chamber → PWM duty:** fill, vent or hold. Filling and venting the
     same chamber at the same time is impossible. A minimum pulse length makes sure the
     valve really opens.
  5. **In position:** error < 0.3 mm, the arm is still and the pressures are at their
     targets. Then all valves close and the trapped air holds the arm. This saves air and
     valve wear; control resumes above 0.6 mm.
  6. **Relief:** if a chamber goes above 6 bar (e.g. air compressed when overshooting),
     that chamber's vent valve opens. If it lasts longer than 0.5 s, a fault follows: the
     regulator is set too high.
- **Slow layer, on the PC (program or AI):** sends the target angle and stiffness, and a
  `ping` every 0.2 s. If the Pico misses it for half a second, all valves close.

For holding and for the steps of T3 no feedforward is needed. The delays in the loop are
small: valve 2–3.5 ms, a pressure wave through 30 cm of tube about 1 ms, and filling a
chamber tens of ms.

**Fast and smooth (T8, mode `move`):** the speed-limited target of step 1 starts and stops
with a jolt, and the controller only pushes once an error has built up: on the moves of
T8 the arm lags up to 21 mm behind and overshoots up to 9 mm. Mode `move` replaces step 1
and adds to step 2:
- **Profile of the arm angle:** a quintic from the current state to the target, so
  position, speed and acceleration are continuous. Planned in degrees, not in cylinder
  length: near the top the cylinder's lever is small and the same acceleration in mm
  would need four times the force. Limits: speed 170°/s, acceleration 1550°/s², and a
  limit on the jerk, because the valves need time to swap the pressures. These keep 10%
  margin in time: about 1.1× as fast still passes in the simulation, 1.15× does not. A new target
  during a move starts a new profile from the current speed and acceleration.
- **Feedforward:** force = (gravity torque + inertia × planned angular acceleration) /
  lever, plus the seal friction in the direction of motion. The PID only corrects what is
  left; its D term works on the difference between planned and measured speed.
- The load must be known (weighed); the arm's own mass and inertia come from
  `params.py`.

## Simulation

`sim/run.py` simulates the arm in MuJoCo with a model of the pneumatics:
- valve flow according to ISO 6358
- valve opening and closing delays
- chamber pressures, seal friction
- sensor noise and ADC steps

Results with the current tuning (`out/sim/results.json`, plots in `out/sim/`):

| Test (simulation) | Result |
|---|---|
| T3 step 0° → 30° | overshoot 1.0 mm, settled in 0.9 s, error 0.3 mm — passed |
| T3 step 30° → −5° | overshoot 1.2 mm, settled in 0.5 s, error 0.1 mm — passed |
| T2 on/off control (3 bar) | stays 15–25 mm off target: PWM control is needed |
| T6 stiffness (15 N extra, valves closed) | 14° deflection at 2 bar chamber pressure, 10° at 5 bar |
| T7 load | target reached up to 3.5 kg (78% load), but within 1 s only around the tuning load (1.5 kg); not at 100% |
| T8 knob and button | 30° in 0.45 s, largest move (−5° → 50°) 0.61 s; follows the profile within 2 mm, overshoot ≤ 1.5 mm, at rest when the profile ends — passed. 1.15× as fast fails; so does the load set 20% too light, 10% off passes |

Exact numbers per run: [`../out/sim/results.md`](../out/sim/results.md).
T7 already shows that the tuning belongs to the load. The arm will probably need tuning
that scales with the load or the position.

The model is an estimate. Friction, dead volumes and the flow of these valves are measured
in T1–T4; after that the model is updated and the control re-tuned.

## Tests

Tests T0–T8, with criteria, are in [manual.md](manual.md), section 11.
`host/tests_t0_t7.py` runs them and assesses them with the same analysis as the
simulation (`host/analysis.py`).

## Safety

- **Pressure:** start at 2–3 bar and never go above 6 bar (the valves' limit is 7 bar).
- **Shut-off slide:** within reach. Closing it depressurises the supply line, but not
  the cylinder chambers: their air is trapped behind closed valves.
- **Emergency stop:** cuts the 24 V to all valves. All fill and vent valves close, so the
  cylinder keeps its air and does not sag. The main valve closes and vents the supply. If
  a fill valve sticks, no more air comes in.
- **At every start-up:** wear safety glasses, keep your hands away from the rod and the
  bracket, and secure the tubes. A tube that comes loose whips around.
- **Software:** closes all valves on a fault, at start-up and when USB contact is lost.
  With all valves closed the cylinder keeps its air.
- **Depressurising the cylinder:** first close the shut-off slide, then open vent valves
  V2 and V4, from the software or with the manual override button on the valve itself.
  Only then work on the rig.
- **Arm:** keep your hands out from between the arm and the upright. Clamp the base plate
  to the table edge with two F-clamps; the load hangs beside the table.
- **Relief:** above 6 bar the software opens that chamber's vent valve.
- **Pneumatics are not harmless:** Ø20 at 6 bar pushes almost 19 kg, and the arm's
  cylinders will be many times stronger. The arm's safety has to come from the design:
  limited pressure, limited speed and compliance. The medium alone does not make it safe.

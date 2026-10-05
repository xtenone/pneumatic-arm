# Manual for test 1 — arm with one degree of freedom

This manual takes you step by step through checking the parts, building, wiring,
installing the software, calibrating and running tests T0–T7.

At 📷 take a photo before you continue. It lets someone check your work before air or
power goes on; post it in an issue if you want feedback.

All dimensions come from `params.py` and are also in the drawings in `out/drawings/`.

---

## 0. Safety — read this first

- **Safety glasses on** as soon as there is compressed air on the rig. A tube that comes
  loose whips around and can hit your eye.
- **Start at 2–3 bar.** Only go to 5 bar after T0 to T2 went well. Never above 6 bar: the
  valves are rated for 7 bar, the pressure sensors for 6.9 bar.
- **Hands out from between the arm and the upright.** At 5 bar the cylinder pushes 157 N,
  which at the hinge is enough to crush fingers.
- **Emergency stop within reach.** Pressed: the 24 V drops out, all valves close and the
  main valve vents the supply line. The cylinder keeps its air; the arm stays where it is
  and does not fall.
- **Depressurise before working on the rig:**
  1. close the shut-off slide (supply depressurised);
  2. in the software `valve 0 1 0 1` (vent both chambers), or press the manual override
     button on vent valves V2 and V4;
  3. the regulator gauge and the pressure sensor readings must show 0 bar.
- **Clamp the rig down.** The arm reaches past the table edge. Clamp the base plate with
  two F-clamps, or the whole thing can tip over in a fast move.
- **No mains voltage on the rig.** Only the closed 24 V plug-in adapter.

---

## 1. Incoming inspection

Do this per parcel, **before** you confirm receipt on AliExpress. If something is wrong,
open a dispute with photos.

| Part | Check | Good if |
|---|---|---|
| 5× VQ110U-5M-M5 | label | says VQ110U-5M-M5, with sub-plate (white block with ports) |
| | coil resistance (multimeter Ω, red and black wire) | all five about equal: approx. 380–600 Ω (1–1.5 W at 24 V) |
| | 24 V on it briefly (red +, black −) | a clear click, the LED in the plug lights up |
| | blow into P (bicycle pump or mouth), coil off/on | off: closed, on: air comes out of A |
| Cylinder MAL20×150 | push the rod in and out by hand | moves evenly, without sticking |
| | ports | 1/8 thread; a PC4-01 screws in smoothly by hand for a few turns |
| | dimensions (measure!) | note the retracted pin-to-pin length — see step 5 |
| KTC-175 potentiometer | resistance between the pins | two pins give a fixed ~5 kΩ (the ends); the third is the wiper |
| | move the wiper | resistance wiper–end changes evenly with the rod |
| 2× pressure sensor | 5 V on it (red +, black −), measure the signal | 0 bar: approx. 0.5 V (or approx. 0 V for a 0–5 V type) |
| | thread | male G1/4 (fits the PCF4-02) |
| ULN2803A | — | tested in step 8 |
| Regulator, slide, main valve | thread sizes | G1/4 (the PC4-02 fittings fit) |
| Emergency stop | multimeter in beep mode, on the NC terminals | beeps when released, silent when pressed |

📷 Photo of all parts side by side, with the valve labels readable.

---

## 2. Tools

- jigsaw or hand saw (wood), hacksaw and file (aluminium)
- drill with wood bits 5 and 8.5 mm, metal bits 5.5 and 8.5 mm, 22 mm Forstner bit
- screwdrivers, spanners 8, 10, 13 mm, hex keys
- wire stripper, small screwdriver for screw terminals
- tape measure, try square, awl or centre punch
- multimeter
- safety glasses

---

## 3. Woodwork: base plate, cheeks and spacer block

Drawings: `out/drawings/cheek.pdf` and `out/drawings/side_view.pdf`.

1. **Saw** from 18 mm plywood. DIY stores often cut to size for free.
   - base plate 400 × 300 mm
   - 2 cheeks 450 × 120 mm
   - 2 blocks 60 × 60 mm (together the 36 mm spacer block)
2. **Mark the holes on both cheeks.** Put them exactly on top of each other and clamp
   them, so the holes line up perfectly in both cheeks.
   - hinge: middle of the width (60 mm), 420 mm from the bottom
   - cylinder pivot: middle (60 mm), 100 mm from the bottom
   - 2 screw holes for the block: 30 mm from the back, 20 and 45 mm high
3. **Drill** with the cheeks still clamped together:
   - Ø10 mm through, at the hinge
   - Ø8.5 mm through, at the cylinder pivot
   - Ø5 mm through, at the screw holes
4. **Bearing seats.** Separate the cheeks. On the **outside** of each cheek, at the
   hinge, drill a 22 mm hole **7 mm deep** with the Forstner bit. The two cheeks are
   mirror images.
   - Press a 608 bearing in. It should be a tight fit: tap it in with a block of wood.
   - If it is loose, fix it with a drop of two-component glue.
5. **Spacer block:** glue the two 60 × 60 blocks together (36 mm thick).
6. **Assembly:**
   - put the spacer block at the back bottom between the cheeks and screw it with
     4 screws 4×40 through the Ø5 holes;
   - fix the cheeks to the base plate with 4 angle brackets. The back of the cheeks is
     90 mm from the back edge of the base plate (the front is 190 mm from the front
     edge); the cheeks are centred across the width.
   - Check with the try square that the cheeks stand square.

📷 Photo of the upright on the base plate, from the side and from the front.

---

## 4. The arm

Drawing: `out/drawings/arm.pdf`.

1. Cut the 40×5 aluminium bar to **450 mm** and file the edges smooth.
2. **Mark the holes** on the centre line (20 mm from the edge):
   - hinge: 20 mm from one end
   - clevis: 150 mm from the hinge hole
   - load: 400 mm from the hinge hole
3. Centre-punch, drill Ø5 first, then **Ø8.5**, and deburr.
4. **Spacer sleeves:** cut four pieces of the 10×1 tube:
   - 2× **15.5 mm** for the arm in the hinge (36 − 5 = 31, split over 2 sides)
   - 2× **7 mm** for the cylinder's rear pivot (36 − 22 = 14, split)
5. **Assembly:** push an M8×80 bolt through the bearings and cheeks, with the sleeves and
   the arm in between: bearing — 15.5 sleeve — arm — 15.5 sleeve — bearing. Tighten the
   lock nut until there is no play but the arm still turns freely.

📷 Photo of the hinge from above. The arm must sit centred between the cheeks and swing
freely up and down.

---

## 5. The cylinder

1. **Measure the pin-to-pin length** with the rod fully retracted: from the centre of the
   rear hole to the centre of the clevis pin. Fit the clevis on the rod first, see step 2.
   - The calculation assumes **311 mm**.
   - If it differs by more than 5 mm, change `CYL` in `params.py` and run `build.py`:
     it changes the range of motion and the calibration.
2. **Clevis on the rod,** in this order: M8 nut — potentiometer bracket (8.5 hole) — M8
   nut — clevis. Screw the clevis about 12 mm onto the rod and lock it with the nuts.
3. **Rear pivot:** push the second M8×80 bolt through the cheek, a 7 mm sleeve, the hole
   at the back of the cylinder, another 7 mm sleeve and the other cheek. The air ports
   point to the **front** (away from the upright). Tighten the lock nut but let the
   cylinder pivot freely.
4. **To the arm:** fix the clevis with its pin in the hole at 150 mm. Fit the circlip or
   split pin.
5. Move the arm by hand all the way up and down. Nothing may touch.
   - Lowest position: about −17°, cylinder fully retracted.
   - Highest position: about +66°, cylinder fully extended.

📷 Photo from the side, with the arm horizontal.

---

## 6. The potentiometer

1. Bend a mounting strip from the 20×3 strip to fit the cylinder tube.
2. Fix the potentiometer to it with its own clips.
3. Clamp the mounting strip to the cylinder tube with two hose clamps, on the **underside**
   (away from the hinge). The potentiometer runs parallel to the cylinder.
4. Fix the ball joint of the potentiometer rod with an M5 bolt to the bracket on the
   cylinder rod.
5. Move the arm all the way up and down.
   - The potentiometer must never reach its own end stop: its stroke is 175 mm, the
     cylinder's 150 mm. Slide it so there is clearance at both ends.
   - Nothing may bind; the ball joint takes up small misalignment.

📷 Photo of the potentiometer on the cylinder, in the lowest and highest positions.

---

## 7. Pneumatics

Diagram: `out/drawings/pneumatics.pdf`. The connection tables are in
`docs/design.md` ("Pneumatic connections").

**Push-in fittings:**
- **Inserting a tube:** cut it square with the tube cutter and push it in firmly up to
  the stop (about 15 mm). Then give the tube a pull.
- **Removing a tube:** press the blue collar and pull.

**Threads:**
- G1/4 and 1/8: PTFE tape, 3–4 turns in the direction of the thread. Hand-tight, then a
  quarter turn with a spanner.
- M5 on the valves: not too tight, the sub-plate is plastic. The fitting's rubber ring
  seals.

**Assembly:**
1. **Prepare the valves** (see the table in the design document):
   - **fill valves V1, V3:** P = supply, A = to the chamber, **R = blanking plug**
   - **vent valves V2, V4:** P = from the chamber, A = silencer, **R = blanking plug**
   - Label each valve: V1 fill A, V2 vent A, V3 fill B, V4 vent B.
2. **Mount the valves close to the cylinder,** on the spacer block or a strip of wood.
   Keep every tube between valve and cylinder **shorter than 30 cm**.
3. **Chamber A** is the port at the back of the cylinder (piston side), **chamber B** the
   port at the front (rod side).
4. **Per chamber:** one tee to the fill valve, the vent valve and the cylinder port, and a
   second tee to the pressure sensor (screwed into a PCF4-02).
5. **Supply:** compressor — regulator — shut-off slide — main valve P → A — tee — to P of
   V1 and V3. The main valve's R port stays open: that is where the supply vents on an
   e-stop.
6. Do **not** fit the flow restrictors yet. They are for later (the comparison).

📷 Photo of the complete pneumatics, with the labels readable.

**First leak test with soapy water** (only after steps 8 and 9, when the e-stop works):
1. Regulator at 2 bar, shut-off slide open.
2. Main valve on: the e-stop is released and the 24 V is on.
3. Brush soapy water over every fitting. Bubbles = leak. Cut and re-insert the tube, or
   re-tape the thread.

---

## 8. Electronics

Diagram: `out/drawings/wiring.png`. Connection list: `out/drawings/wiring_list.png`.

**Work in this order and test after each step.** Only plug the 24 V adapter into the
mains when the steps say so.

1. **Pico and ULN2803A** on the breadboard. Put the ULN2803A across the middle gap with
   the notch to the left. Pin 1 is then bottom left (often marked with a dot); pins 1–9
   run along the bottom, pins 10–18 back along the top.
2. **Ground:** Pico GND, ULN2803A pin 9, LM7805C pin 2 and the adapter's minus together on
   the blue rail of the breadboard.
3. **Control wires:** GP2 → IN1 (pin 1), GP3 → IN2 (pin 2), GP4 → IN3 (pin 3),
   GP5 → IN4 (pin 4).
4. **24 V and emergency stop:**
   - Adapter plus via the DC jack to the **NC contact** of the e-stop.
   - The other side of the e-stop is "+24 V after e-stop". It goes to ULN2803A pin 10
     (COM) and to the red wire of all four VQ110 coils.
   - One side of the main valve also connects to "+24 V after e-stop". The other side of
     the main valve goes to GND.
5. **Coils:** black of V1 → OUT1 (pin 18), V2 → OUT2 (pin 17), V3 → OUT3 (pin 16),
   V4 → OUT4 (pin 15). **Mind the polarity:** the coil plugs contain an LED and a
   suppressor that work in one direction only.
6. **LM7805C:**
   - IN (pin 1) to the 24 V **before** the e-stop, with the 1 µF from IN to GND.
   - OUT (pin 3) becomes +5 V, with the 100 nF from OUT to GND.
   - Pin order, text facing you and legs down: IN – GND – OUT.
7. **Pressure sensors:**
   - red to +5 V, black to GND
   - signal via **10 kΩ** to GP27 (sensor A) and GP28 (sensor B)
   - from GP27 and GP28 each a **15 kΩ** to GND, and a **100 nF** to GND. No 15 kΩ? Use
     **3× 47 kΩ in parallel** (15.7 kΩ). Do not go above a ratio of 0.6 (bottom ÷
     (top + bottom)), or more than 3.3 V reaches the Pico pin at 5 V.
8. **Potentiometer:**
   - ends to **3V3** (Pico pin 36) and **GND**
   - wiper to **GP26**, with a 100 nF to GND

📷 Photo of the breadboard from above, sharp enough to follow the wires.

**First test, without compressed air** (shut-off slide closed):
1. **Measure 5 V:** adapter in, e-stop released. Measure OUT of the 7805: 4.9–5.1 V.
2. **Sensor voltage at the Pico pins:** measure GP27 and GP28 to GND. It must be below
   3.1 V, otherwise the divider is wrong. At 0 bar it is about 0.3 V.
3. **Make the valves click:** see step 9 (software), command `valve 1 0 0 0`. You hear V1
   click and see its LED. Test all four this way, then the e-stop: pressed = all quiet.

---

## 9. Software

### On the Pico (MicroPython)

1. **Install MicroPython:**
   - download MicroPython for your board from micropython.org (a `.uf2` file): the
     **Raspberry Pi Pico 2 W** build (`RPI_PICO2_W`) for the Wi-Fi version, or the
     **Pico 2** build (`RPI_PICO2`) without Wi-Fi. The wrong build does not start;
   - solder the header pins on first if your Pico came without them;
   - hold the BOOTSEL button and plug in the USB cable. The Pico shows up as a USB drive;
   - drag the `.uf2` file onto it. The Pico restarts by itself.
2. Install **Thonny** (thonny.org). Bottom right, choose "MicroPython (Raspberry Pi Pico)".
3. **Copy the firmware:** put the four files from `firmware/` on the Pico: `main.py`,
   `control.py`, `config.py` and `hw.py`. In Thonny: open the file, then "Save as…" →
   "Raspberry Pi Pico".
4. Press Stop/Restart in Thonny. At the bottom you see `OK,started`. Type `help` for the
   commands.

`config.py` is generated from `params.py` (`python gen_config.py`), so do not edit it by
hand.

### On the PC (Python 3.10 or newer)

```
cd test1/host
pip install -r requirements.txt
python logger.py              # finds the Pico itself; otherwise --port COM5 or /dev/ttyACM0
```

Close Thonny first: only one program at a time can talk to the Pico.

**Main commands** (also in `help`):

| Command | What |
|---|---|
| `off` | close all valves |
| `valve 1 0 0 0` | open V1 (manual, duty 0..1 per valve) |
| `pressure 2 2` | control both chambers to 2 bar |
| `angle 20` | arm to 20° |
| `bang 20` | on/off control to 20° (T2) |
| `stiffness 4` | sum of the chamber pressures |
| `zero`, `cal_pressure 3`, `cal_pos in`, `cal_pos out`, `save` | calibration (step 10) |

**Safety in the software:**
- If the PC sends nothing for half a second, all valves close. The logger and the test
  script therefore send `ping` every 0.2 s.
- The hardware watchdog starts at the first motion command. If the program hangs, the
  Pico resets itself, with all valves closed.

---

## 10. Calibration

Do this once, and again after moving the potentiometer or replacing a sensor.

1. **Pressure zero:** shut-off slide closed. Type `valve 0 1 0 1` (both vent valves open)
   and leave it like that up to and including step 3. Type **`zero`**.
2. **Potentiometer, bottom:** move the arm by hand all the way down (cylinder fully in).
   The arm moves freely because both chambers are open to the atmosphere. Type
   **`cal_pos in`**.
3. **Potentiometer, top:** move the arm by hand all the way up (cylinder fully out). Type
   **`cal_pos out`**, lower the arm gently and type `off`.
4. **Pressure gain:**
   - regulator at **3.0 bar**, shut-off slide open;
   - type **`valve 1 0 1 0`**: both chambers fill to 3 bar. With the load on, the arm
     stays down or moves a little; that is fine. Wait 3 seconds;
   - read the gauge and type **`cal_pressure 3.0`** (or whatever the gauge shows);
   - type `off`.
5. **`save`**: the calibration goes to `cal.json` on the Pico.
6. **Check:**
   - move the arm by hand to horizontal. The logger should show an angle of about 0°;
     check with a spirit level;
   - the gauge and the measured pressure must agree within 0.1 bar.

📷 Screenshot of the logger with the arm horizontal.

---

## 11. The tests

Start: `python tests_t0_t7.py T0` (and so on), or `python tests_t0_t7.py all`.
Each test stores its run, plot and outcome in `host/results/`.

| Test | Pressure | Load | What | Passed if |
|---|---|---|---|---|
| T0 leak test | 3 bar | 1.5 kg | arm to 20°, all valves closed, measure 60 s | pressure drop < 0.1 bar |
| T1 valves | 3 bar | – | open each valve for 10 ms, sample the pressure fast | response < 10 ms |
| T2 on/off | 3 bar | 1.5 kg | 0° → 30° → −5° with fully open/closed valves only | comes to rest within ±3 mm |
| T3 PWM control | 5 bar | 1.5 kg | 0° → 30° → −5° | overshoot < 5 mm, settled within 1 s, error < 1 mm |
| T4 repeatability | 5 bar | 1.5 kg | 10× to 20°, alternately from above and below | spread < ±1 mm |
| T5 holding | 5 bar | 1.5 kg | 60 s at 30° | deviation < 1 mm |
| T6 stiffness | 5 bar | 1.5 + 1 kg | at 20°, valves closed, add 1 kg; chamber pressure sum 2 and 5 bar | clearly less deflection at 5 bar |
| T7 load ratio | 5 bar | 0.5 → 3.5 kg | repeat T3 with increasing load | highest load at which T3 passes |

The simulation's expectations are in `out/sim/results.json` and in the README. If the
real measurement differs a lot, that is useful information in itself, for example about
the cylinder's friction.

**After T7:** fit the flow restrictors between the tee and the fill valves and repeat T3
with the restrictors ¼, ½ and ¾ closed. This shows what a smaller valve does to speed and
precision. Mark each screw so you can find a setting again.

---

## 12. Troubleshooting

| What you see | Likely cause | What to do |
|---|---|---|
| Valve does not click | polarity reversed, or e-stop pressed | red to +24 V after e-stop, black to OUT; release the e-stop |
| Valve always open | R port not plugged, or P and A swapped | blanking plug on R; see the table in step 7 |
| Pressure slowly drops (T0) | leaking fitting | soapy-water test, cut the tube square again |
| Pressure reads 0 while the gauge shows 3 bar | sensor without +5 V or wrong wire | measure 5 V on the red wire; signal on yellow/green |
| Angle jumps or is noisy | loose potentiometer wire, or no 100 nF on GP26 | check the connections |
| Arm oscillates around the target | friction differs from the simulation | lower `KP_FORCE` or raise `KD_FORCE` in `params.py`, run `python gen_config.py`, copy config.py again |
| `ERROR,over-pressure` | regulator above 6 bar | turn the regulator down |
| `ERROR,no contact with the PC` | logger stopped or USB unplugged | normal behaviour; start again |
| The Pico keeps restarting | watchdog after stopping in Thonny | normal: after 2 s it runs again, with all valves closed |

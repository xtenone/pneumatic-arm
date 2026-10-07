# Bill of materials — test 1

Generated from `docs/order-list.json` (repository root) by `build.py`. Prices in euro, * = estimate. Also as [CSV](bom.csv).


## 1. Valves (AliExpress)

Status: ordered (2026-10-04)

| # | Part | Variant | Price | Link |
|---|---|---|---|---|
| 1 | 5× fast 3/2 valve — Including shipping (store with 11 pages of reviews) | VQ110U-5M-M5 | €130.53 | [link](https://www.aliexpress.com/item/1005013133472109.html) |

## 2. Pneumatics, sensors and driver IC (AliExpress)

Status: ordered (2026-10-04)

| # | Part | Variant | Price | Link |
|---|---|---|---|---|
| 1 | Cylinder MAL20×150 | bore 20, stroke 150, standard (not CA), no magnet | €12.99 | [link](https://www.aliexpress.com/item/1005010583152545.html) |
| 1 | Linear potentiometer KTC | 175 mm, plain resistive 5 kΩ version (not 4–20 mA / LWF), type B (ball joint) | €28.19 | [link](https://www.aliexpress.com/item/1005006230077162.html) |
| 2 | Pressure sensor | #4 0–100 psi, output 0.5–4.5 V | €29.78 | [link](https://www.aliexpress.com/item/1005010385122677.html) |
| 1 | Filter + regulator AFR-2000 | G1/4, with gauge | €7.69 | [link](https://www.aliexpress.com/item/1005005324116810.html) |
| 1 | Shut-off slide valve HSV-08 | HSV-08 (G1/4), not HSV-06 | €4.09 | [link](https://www.aliexpress.com/item/1005010563686803.html) |
| 1 | Main valve 3V210-08 | NC, DC24V | €8.19 | [link](https://www.aliexpress.com/item/1005007341961878.html) |
| 1 | Emergency stop, mounted in a box | plastic box with yellow STOP label, no lid or guard; NC contact (or 1NO+1NC) | €8.29* | [link](https://www.aliexpress.com/item/1005005858101621.html) |
| 8 | Straight push-in fitting, per piece (4000+ sold) — 6 for the valves, 2 spare | 4 mm – M5 (PC4-M5) | €3.92 | [link](https://www.aliexpress.com/item/1005002796005278.html) |
| 3 | Straight push-in fitting, per piece — 2 needed, 1 spare | 4 mm – 1/8 (PC4-01) | €1.83 | [link](https://www.aliexpress.com/item/1005002796005278.html) |
| 5 | Straight push-in fitting, per piece — Regulator, slide valve, main valve (3–5 needed) | 4 mm – 1/4 (PC4-02) | €3.45 | [link](https://www.aliexpress.com/item/1005002796005278.html) |
| 1 | M5 blanking plug (10 pieces) | M5 | €3.05 | [link](https://www.aliexpress.com/item/1005004886533500.html) |
| 1 | Tee 4 mm | PE4, 10 pieces | €2.80 | [link](https://www.aliexpress.com/item/1005006534920138.html) |
| 1 | Push-in fitting, female 1/4" → 4 mm (bag of 10, for the pressure sensors) — Rc 1/4 (tapered); seal the G1/4 sensor with PTFE tape | PCF4-02 | €6.49 | [link](https://www.aliexpress.com/item/32830226405.html) |
| 2 | PU tube 5 m — Everything in 4 mm tube; 6 mm is not needed | 4×2.5 mm, 5 m (clear) | €4.84 | [link](https://www.aliexpress.com/item/1005007992615899.html) |
| 2 | Foot mount (LB) for MAL20 — Not needed for test 1 (the cylinder pivots); spare for a fixed set-up | LB, 20 mm | €8.98 | [link](https://www.aliexpress.com/item/1005007235783406.html) |
| 1 | Nut M22×1.5 — For the rear cover; the cylinder usually comes with one nut only | M22×1.5 (MAL20/25) | €3.11 | [link](https://www.aliexpress.com/item/1005007235783406.html) |
| 1 | ULN2803A Darlington array (DIP-18), 10 pieces — Only the ULN2803 in this listing, no mix-up with 2802/2804 (the 2804 does not switch on 3.3 V) | ULN2803APG DIP-18 | €2.23 | [link](https://www.aliexpress.com/item/1005006852404177.html) |
| 1 | Inline flow restrictor 4 mm (2 pieces) — Used after T7 to mimic a smaller valve | 4 mm | €3.36 | [link](https://www.aliexpress.com/item/1005008810108635.html) |
| 1 | Rod clevis (Y) for MAL20 — Connects the cylinder rod to the arm (test 1) | Y/MA MAL20 | €3.85 | [link](https://www.aliexpress.com/item/1005007235783406.html) |
| 1 | M5 exhaust silencer (5 pieces) | Short M5/5PCS | €1.64 | [link](https://www.aliexpress.com/item/1005004014973967.html) |

## 3. Electronics (Tinytronics, NL)

Status: received (2026-10-07)

| # | Part | Variant | Price | Link |
|---|---|---|---|---|
| 1 | Raspberry Pi Pico 2W (RP2350, Wi-Fi) — headers soldered on yourself | SKU 006795 | €9.25 | [link](https://www.tinytronics.nl/) |
| 4 | 40-pin male header strip (2× 20 pins needed for the Pico) | SKU 000160 | €1.60 |  |
| 2 | LM7805C 5 V voltage regulator (TO-220) — 1 spare | SKU 000236 | €1.00 |  |
| 2 | Ceramic capacitor 1 µF, 50 V — 7805 input (1 + 1 spare) | SKU 007096 | €0.40 |  |
| 6 | Ceramic capacitor 100 nF, 50 V — 7805 output + 3 ADC inputs + 2 spare | SKU 000226 | €0.60 |  |
| 1 | DC jack female 5.5 mm (5.5/2.1) to screw terminal — Check that the 24 V adapter plug is 5.5/2.1 | SKU 000287 | €1.00 |  |
| 1 | Breadboard 830 points (EIC premium) | SKU 006327 | €5.00 |  |
| 1 | Resistor 10 kΩ 1/4 W, 10 pieces — Top of the pressure sensor dividers (2 needed) | SKU 007625 | €0.50 |  |
| 3 | Resistor 47 kΩ 1/4 W, 10 pieces — 3 in parallel = 15.7 kΩ, bottom of each divider (6 needed) | SKU 007626 | €1.50 |  |
| 1 | Micro-USB cable (data), 1 m | Goobay 72227 | €2.75 |  |
| 2 | Stranded wire 0.5 mm², black, 1 m — 24 V, e-stop, valves (screw terminals) | SKU 003430 | €2.00 |  |
| 2 | Stranded wire 0.5 mm², red, 1 m | SKU 003427 | €2.00 |  |
| 3 | DuPont jumper wires male-male 10 cm, 100 pieces (blue, black, red) — Breadboard wiring: red = plus, black = ground, blue = signal | SKU 002978/002980/002977 | €13.50 |  |

## 4. DIY store

Status: still to buy

| # | Part | Variant | Price | Link |
|---|---|---|---|---|
| 1 | Plywood 18 mm: base plate 400×300, 2 cheeks 450×120, 2 blocks 60×60 (spacer block) | DIY stores often cut to size | €15.00* |  |
| 1 | Aluminium flat bar 40×5 mm (or 40×4), 50 cm — the arm |  | €8.00* |  |
| 1 | Aluminium strip 20×3 mm (or 20×2), 30 cm — potentiometer bracket + mounting strip |  | €3.00* |  |
| 1 | Aluminium tube 10×1 mm (8 mm inside), 50 cm — spacer sleeves |  | €4.00* |  |
| 2 | Ball bearing 608-2RS (8×22×7) — arm hinge | skateboard bearing | €3.00* |  |
| 2 | Bolt M8×80 + 2 washers + M8 lock nut — hinge and rear pivot |  | €2.00* |  |
| 2 | Nut M8 (standard M8 = M8×1.25) — potentiometer bracket on the rod |  | €0.40* |  |
| 2 | Bolt M5×16 + nut — potentiometer rod to the bracket |  | €0.40* |  |
| 2 | Hose clamp 20–32 mm — potentiometer on the cylinder |  | €1.60* |  |
| 4 | Angle bracket 40×40 + wood screws 4×30 / 4×40 | cheeks and block onto the base plate | €3.20* |  |
| 2 | F-clamp — clamp the rig to the table edge |  | €12.00* |  |
| 1 | 1.5 l water bottle + S-hook or string — the load; for T7 extra bottles or bags of sand |  | €1.50* |  |
| 1 | Plug nipple G1/4 male, matching the compressor coupler | buy after the compressor arrives | €3.00* |  |
| 1 | Tube cutter |  | €5.00* |  |
| 1 | PTFE tape |  | €1.50* |  |
| 1 | Multimeter (if you do not have one) — Needed for the incoming inspection, coil checks and calibration |  | €20.00* |  |

## 5. Compressor (bol.com)

Status: received (2026-10-06)

| # | Part | Variant | Price | Link |
|---|---|---|---|---|
| 1 | Stanley silent compressor DST 100/8/6 — Quiet enough for indoor testing. For the full arm a 6 l tank may be small; add a buffer tank later. Check the coupler type before buying the plug nipple. | 6 l, 8 bar, 105 l/min (intake), 59 dB, oil-free, 750 W | €160.00* | [link](https://www.bol.com/nl/nl/p/stanley-silent-compressor-dst-100-8-6-olievrij/9200000106192675/) |

**Total approx. €564** (excluding shipping and import duty).

## Tools

- Jigsaw or hand saw (wood)
- Hacksaw and file (aluminium)
- Drill with wood bits 5 and 8.5 mm, metal bits 5.5 and 8.5 mm, 22 mm Forstner bit
- Screwdrivers, spanners 8, 10, 13 mm, hex keys
- Wire stripper, small screwdriver for screw terminals
- Soldering iron (only if the Pico comes without header pins)
- Safety glasses
- Tape measure, try square, awl or centre punch

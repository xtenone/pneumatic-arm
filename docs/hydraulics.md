# Hydraulics as an option

For when the arm needs more force than pneumatics can give, or turns out to be too soft.
The joint layout stays the same (plain hinge, lever, a cylinder that only pushes), so the
joints, levers, sensors and control structure carry over; only the medium and the valves
change.

## When to consider it

- Forces much larger than the 15 kg arm (for example 50 kg or more, or heavy tools).
- Pneumatics too soft or not precise enough under load (tests T6 and T7).

For 15 kg at 1 m pneumatics is enough (Ø63 at 5 bar, see
[full-arm-sizing.md](full-arm-sizing.md)) and simpler, cleaner and safer.

## Comparison

| | Pneumatics | Hydraulics |
|---|---|---|
| Pressure | 5–6 bar | 50–200 bar |
| Force of a Ø20 cylinder | ≈ 160 N at 5 bar | ≈ 1600 N at 50 bar, ≈ 3100 N at 100 bar |
| Stiffness | air is a spring | oil hardly compresses: stiff, holds position under load |
| On a collision | gives way | does not give way |
| Control | pressure and flow, compressible | flow sets the speed, closer to a motor |
| Supply | compressor | power unit (motor, pump, tank, relief valve, accumulator) |
| Risks | low | oil leaks; a jet under high pressure can penetrate the skin |

A Ø20 hydraulic cylinder at 50 bar already carries the full-size shoulder (162 Nm on a
150 mm lever needs ≈ 540 N per cylinder), at the size of the test 1 cylinder.

## Valves (AliExpress, October 2026)

Proportional hydraulic valves are made in large numbers in China for agricultural and
construction machinery (mobile hydraulics), so they are much cheaper than pneumatic
proportional valves.

| Type | Price | Notes |
|---|---|---|
| Proportional cartridge valve, 2/2 (HydraForce SP08-20 type) | €90–115 | PWM current control; screwed into a manifold block (cavity VC08-2, 3/4-16 UNF). [SP08-20](https://nl.aliexpress.com/item/1005012186210270.html), [unbranded SP08-20](https://nl.aliexpress.com/item/1005009810937484.html) |
| Proportional pressure-reducing cartridge (HydraForce EHPR98 type) | ≈ €140 | sets a pressure per chamber (force control) |
| On/off cartridge valve, 2/2 poppet (Eaton/Vickers SV3-10-C type) | €35–60 | **not proportional**; switches in tens of ms, too slow and too harsh for PWM. Useful as a load-holding or safety valve. [SV3-10-C](https://nl.aliexpress.com/item/1005010718333141.html) |
| Proportional relief valve (Yuken EBG type) | ≈ €150 | sets the system pressure |
| Proportional directional valve NG6 (4WRA type) | ≈ €480 | one per cylinder, onboard electronics in some versions. [4WRA6E](https://nl.aliexpress.com/item/1005012391911557.html); original Rexroth via Chinese sellers €800–2000 |
| On/off directional valve NG6 (4WE6) | ≈ €67 | switches too slowly for PWM control |

Most promising: **four proportional cartridges per cylinder** in one block (fill and drain
per chamber, the same structure as the four VQ110U valves of test 1), about €400–500 per
cylinder including the block, or one proportional NG6 directional valve (≈ €480). Watch
the type code: many cartridges in the same family (SV…) are on/off valves, the
proportional ones are marked separately (SP…, EHPR…, EPV…). The Pico drives them with
a PWM current driver (MOSFET with current measurement).

Before buying an unbranded cartridge, ask the seller for:
- the type plate or datasheet (SP = proportional, SV = on/off; they look the same);
- coil voltage (12 or 24 V), maximum pressure and flow;
- the recommended PWM frequency (typically 100–300 Hz, often with dither);
- the flow direction it meters and the direction it blocks.

## System

| Part | Price (estimate) | Notes |
|---|---|---|
| Power unit: gear pump, continuous-duty motor, tank, relief valve | €400–800 | The cheap 12 V units (€140–300, e.g. [18 MPa](https://nl.aliexpress.com/item/1005012484978639.html)) are dump-trailer pumps for short duty, not for continuous control |
| Accumulator | | smooths the pressure, covers peaks |
| Filter (≈ 10 µm) | | proportional valves need clean oil |
| High-pressure hoses and fittings | | more expensive than pneumatic tube |
| Cylinders | Ø20–25 at 50–100 bar | small for the force |

## Points for the control

- Cheap cartridges have a dead band (spool overlap) and hysteresis; the controller has to
  compensate for them (dither on the PWM, dead-band compensation).
- Flow ∝ opening × √(pressure drop): the speed depends on the load, as with air, but
  without the spring of compressed air.
- Pressure sensors per chamber, as in test 1 (rated for the higher pressure).

## Safety

- Relief valve on the power unit, set to the lowest pressure that does the job.
- Hoses rated well above the system pressure, protected and fixed.
- Check valves (pilot-operated) on the cylinders so the arm does not drop when a hose
  breaks.
- Never feel for leaks by hand.
- Limit force and speed in software. The arm does not give way by itself.

# Plan

Wat er gedaan is en wat er nog moet gebeuren. Bijgewerkt: 2026-10-05.

Afkortingen: **K** = klant (bouwt, koopt, meet), **E** = engineering (ontwerp, software,
documentatie, controle).

## Fase 0 — Intake en doel ✅

- [x] Intake: doel, eisen (15 kg per arm, muur bouwen, veilig, gewone onderdelen) — [doel.md](../doel.md)
- [x] Keuze aandrijving: cilinders, pneumatiek als eerste kandidaat
- [x] Schets 2-DOF-gewricht ontvangen en eerste analyse — [2dof-gewricht.md](2dof-gewricht.md)

## Fase 1 — Proefopstelling ontwerpen ✅

- [x] Principe: één cilinder, 4 snelle 2/2-functies (vullen/legen per kamer) met PWM — [test1/docs/ontwerp.md](../test1/docs/ontwerp.md)
- [x] Ventielkeuze: SMC VQ110U (grote doorstroming), los aansluitblok (geen eiland: dat verbindt de kamers)
- [x] Sensoren: lineaire potmeter KTC 175 mm, 2 druksensoren G1/4
- [x] Elektronica: Pico 2, ULN2803A, LM7805C voor de sensoren, noodstop die de 24 V onderbreekt
- [x] Aansluitschema pneumatiek, alles in 4 mm slang
- [x] Proeven T0–T7 met meetbare criteria
- [x] Kosten per DOF — [kosten-per-dof.md](kosten-per-dof.md)

## Fase 2 — Inkopen (bezig)

- [x] AliExpress: ventielen, pneumatiek, sensoren, ULN2803A — besteld 2026-10-04 (K)
- [ ] Tinytronics: Pico 2, LM7805C, condensatoren, weerstanden 10k/15k, breadboard, DC-bus passend op de eigen adapter, USB-kabel, draad (K)
- [ ] Eigen 24 V-adapter controleren: DC (geen AC), minimaal 0,5 A, plugmaat (5,5/2,1 of 5,5/2,5) (K)
- [ ] Lidl: compressor Parkside PSKO 248 B1 (K)
- [ ] Bouwmarkt, ná de compressor: insteeknippel G1/4 passend op de compressorkoppeling, slangschaar, PTFE-tape, multiplex, aluminium hoekje, eventueel multimeter (K)

Bestellijst: [bestellijst.json](bestellijst.json), klikbaar op
`http://192.168.1.22:8200/pneumatic-arm/bestellijst.html`.

## Fase 3a — Test 1 als compleet pakket ✅

- [x] Test 1 = arm met één vrijheidsgraad (cilinder tilt een arm met last) — [test1/](../test1/README.md)
- [x] Eén parameterbestand (`test1/params.py`) voor CAD, simulatie, firmware en tekeningen
- [x] CAD (CadQuery): STEP, STL, DXF, GLB
- [x] MuJoCo-simulatie met pneumatiekmodel; regeling afgesteld, T3 geslaagd in simulatie
- [x] Firmware (MicroPython, Pico 2) en pc-programma's (logger, proeven T0–T7), getest met nagebootste hardware
- [x] Tekeningen: zijaanzicht, wang, arm, elektrisch schema, aansluitlijst, pneumatisch schema
- [x] Handleiding, ontwerp, stuklijst; bundel `dist/test1-pakket.zip` en HTML op de webmap

## Fase 3 — Voorbereiden terwijl de pakketten onderweg zijn

- [x] Ontvangstcontrole per onderdeel — in de handleiding, hoofdstuk 1 (E)
  - ventielen: etiket VQ110U-5M-M5, spoelweerstand (alle vijf gelijk), klikken op 24 V, lektest
  - druksensoren: uitgang op 0 bar (0,5 V of 0 V), draad G1/4
  - potmeter: weerstand 5 kΩ over de uiteinden, loper loopt gelijkmatig mee
  - cilinder: poorten PT1/8, stang loopt soepel
  - ULN2803A: elke uitgang los testen met een LED of ventiel
- [x] Bouwhandleiding stap voor stap, met foto-controlemomenten (E)
- [x] Pico-software, eerste versie (E)
  - sensoren uitlezen en kalibreren (0 bar + manometer)
  - ventielen los aansturen, verboden standen geblokkeerd, alles uit bij fout of USB-verlies
  - meetgegevens naar de pc (CSV)
- [x] Pc-kant: logger, proevenscript en grafiek per proef (E)

## Fase 4 — Bouwen (K, met controle door E)

- [ ] Staander, arm op lagers, cilinder scharnierend tussen staander en arm, potmeter op de cilinder (handleiding 3–6)
- [ ] Pneumatiek volgens het aansluitschema; slangen tussen ventiel en cilinder < 30 cm
- [ ] Elektronica op het breadboard; eerst zonder lucht testen (ventielen klikken, sensoren lezen)
- [ ] Veiligheid: noodstop, afsluitschuif, eerst op 2–3 bar

## Fase 5 — Proeven en meten

- [ ] T0 lektest
- [ ] T1 reactietijd ventielen, PWM-frequentie kiezen
- [ ] T2 aan/uit-regeling
- [ ] T3 PWM-regeling (sprong 20 → 80 mm)
- [ ] T4 herhaalbaarheid
- [ ] T5 staand met last
- [ ] T6 stijfheid
- [ ] T7 belastingsgraad (hoeveel van de statische kracht de regeling kan gebruiken)
- [ ] Vergelijking met smoorventielen: kleinere doorstroming tegenover snelheid en precisie

## Fase 6 — Beslissen

- [ ] Werkt pneumatiek met terugkoppeling goed genoeg voor de arm? Op basis van T3–T7.
- [ ] Zo ja: cilindermaten schouder en elleboog vastleggen met de uitkomst van T7
- [ ] Ventielen voor de grote cilinders kiezen (doorstroming, eventueel grof + fijn)

## Daarna

- 2-DOF-gewricht uitwerken (kruiskoppeling, kogelgewrichten, ontgrendelbare
  terugslagkleppen tegen wegzakken bij slangbreuk), eerst virtueel volgens de
  [werkwijze](../../werkwijze-fysieke-projecten/CLAUDE.md), dan bouwen
- Hoeksensoren op de gewrichten (bijv. AS5600) in plaats van lineaire potmeters

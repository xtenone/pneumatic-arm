# Proefopstelling 1: één cilinder met vier snelle ventielen

## Wat deze proef moet bewijzen

Kan een gewone pneumatische cilinder met goedkope aan/uit-ventielen en een
microcontroller naar een gekozen positie gestuurd worden en daar blijven staan? En hoe
precies lukt dat? Elke kamer van de cilinder krijgt een eigen druksensor. Daarmee kan
het programma naast de positie ook de stijfheid regelen: hoe hard de cilinder
terugduwt als je eraan trekt.

## Het idee

Een dubbelwerkende cilinder heeft twee kamers, A (stang naar buiten) en B (stang naar
binnen). Elke kamer krijgt twee ventielen:

- een **vulventiel**: als het open is, stroomt er lucht de kamer in;
- een **leegventiel**: als het open is, stroomt er lucht uit de kamer naar buiten.

Zijn beide ventielen van een kamer dicht, dan blijft de lucht in die kamer zitten. De
ventielen gaan tientallen keren per seconde open en dicht (PWM). Door ze langer of
korter open te zetten, regelt het programma hoe snel een kamer vult of leegloopt.

```
compressor ── filter + drukregelaar ── afsluitschuif ──┬──────────────────┐
                                                       │                  │
                                                  [V1 vul A]         [V3 vul B]
                                                       │                  │
                       druksensor pA ── kamer A ═══ CILINDER ═══ kamer B ── druksensor pB
                                                       │                  │
                                                  [V2 leeg A]        [V4 leeg B]
                                                       │                  │
                                                   demper             demper

             lineaire potmeter langs de stang ── positie x
```

| V1 | V2 | Kamer A | 
|----|----|---------|
| uit | uit | houdt druk vast |
| aan | uit | vult |
| uit | aan | loopt leeg |
| aan | aan | **verboden**: blaast lucht rechtstreeks weg. De software blokkeert dit. |

Voor kamer B gelden V3 en V4 op dezelfde manier.

## De ventielen

**Keuze: SMC VQ110 (of een kloon ervan), 5 stuks: 4 plus 1 reserve.**

- 3/2-ventiel, direct bediend (poppet), normaal gesloten
- Reactietijd: aan 3,5 ms, uit 2 ms. Snel genoeg voor PWM op 20–50 Hz.
- Maximaal 0,7 MPa (7 bar), 24 V DC
- Klein, en op AliExpress verkrijgbaar als origineel en als kloon

Een 3/2-ventiel wordt een 2/2-ventiel door één poort dicht te draaien met een M5-blindplug:

- **Vulventiel:** P ← perslucht, A → kamer, R dicht. Uit = dicht, aan = vullen.
- **Leegventiel:** P ← kamer, A → demper, R dicht. Uit = P dicht, aan = leeglopen.

Zo zijn alle vier de ventielen hetzelfde onderdeel, wat met de reserve goed uitkomt.
Bij de lektest (T0) controleren we of de dichte stand echt dicht blijft.

**Typenummer:** zoals ik de SMC-codering lees, betekent het volgende. Controleer het bij de verkoper:

- `-5` = 24 V DC
- `M` of `L` = stekker *met* kabel; `MO`/`LO` = zonder kabel, die varianten niet nemen
- `-M5` = losse klep op een aansluitblok met M5-draad. Zonder `-M5` is het een
  klep voor een ventieleiland, en dan heb je er nog een blok bij nodig.

Bedoeld typenummer: **VQ110-5M-M5** of **VQ110-5L-M5**.

**Waarom geen goedkopere 2/2-klep?** Gewone magneetkleppen zoals de 2V025 en 2W-serie
(€5) reageren in 20–50 ms. Daarmee is PWM boven ongeveer 10 Hz niet mogelijk en wordt
de regeling grof. De kleine "hoogfrequente" miniventielen van 10 mm zijn goedkoop
(€5–8), maar opgegeven voor 30 Hz en met heel weinig doorstroming. Voor een eerste test
zijn ze bruikbaar, maar voor een armgewricht niet.

**Vooruitblik:** de VQ110 is groot genoeg voor deze proefcilinder (Ø20), niet voor de
cilinders van de uiteindelijke arm. Die worden Ø40–63, omdat 15 kg op armlengte
honderden tot meer dan duizend newton aan cilinderkracht vraagt. Daar komen grotere
snelle ventielen voor, of meerdere ventielen naast elkaar. Deze proef levert de
regelsoftware en de meetgegevens om die keuze te maken.

## Onderdelenlijst

Prijzen zijn een indicatie (AliExpress, oktober 2026).

| # | Onderdeel | Zoekterm / type | Ca. prijs |
|---|---|---|---|
| 5 | Snel 3/2-ventiel 24 V | SMC VQ110-5M-M5 | €8–30 per stuk |
| 1 | Dubbelwerkende minicilinder Ø20, slag 150 mm | MAL20x150 | €15–25 |
| 1 | Lineaire potmeter 150 mm | KTC-150 / KPM-150 linear potentiometer | €20–40 |
| 2 | Druksensor 0–1 MPa, 5 V, uitgang 0,5–4,5 V | pressure transducer 0-1.2MPa 5V G1/4 | €8–15 per stuk |
| 1 | Raspberry Pi Pico 2 | | €6 |
| 1 | 4-kanaals MOSFET-module, logic level (werkt op 3,3 V) | 4 channel MOSFET module AOD4184 | €4 |
| 4 | Vrijloopdiode (als die niet op de module zit) | 1N4007 of SS34 | €1 |
| 1 | Voeding 24 V, 2–3 A | | €15 |
| 1 | Filter + drukregelaar met manometer | AFR2000 | €15–25 |
| 1 | Afsluitschuif die de leiding achter zich drukloos maakt | HSV-08 hand slide valve | €8 |
| 6 | M5-blindplug | | €3 |
| 2 | M5-geluiddemper | | €2 |
| – | Steekkoppelingen M5→4 mm, 1/8"→4 mm, T-stukken 4 mm, adapter G1/4→4 mm voor de druksensoren, PU-slang 4 mm en 6 mm | | €25 |
| – | Weerstanden voor spanningsdeler (2× 10 kΩ + 2× 20 kΩ), breadboard, draadjes | | €5 |
| 1 | Compressor met tank, ±8 bar (als je er nog geen hebt) | | €100–150 |

**Totaal zonder compressor: ongeveer €200–300.**

## Elektrisch

- **Pico 2 → MOSFET-module:** 4 PWM-pinnen, één per ventiel.
- **24 V-voeding → ventielspoelen:** de MOSFET's schakelen de min-kant. Over elke spoel
  komt een vrijloopdiode, anders gaat de MOSFET kapot.
  - Een diode vertraagt het dichtgaan van het ventiel een beetje. Als dat in T1
    meetbaar is, voegen we per spoel een zenerdiode toe.
- **Potmeter:** aan 3,3 V van de Pico, loper op ADC0 (GP26).
- **Druksensoren:** aan 5 V (VBUS van de Pico). De uitgang gaat via een spanningsdeler
  10 kΩ/20 kΩ naar ADC1 (GP27) en ADC2 (GP28). Zo wordt 4,5 V omgezet naar 3,0 V, en
  dat kan de Pico aan.
- **De pc via USB:** levert stroom aan de Pico en ontvangt de meetgegevens
  (positie, twee drukken, ventielstanden). Dat gebeurt honderden keren per seconde.

## Mechanisch

- **Eerst liggend:** cilinder en potmeter evenwijdig op een plank, stang en potmeter
  aan elkaar gekoppeld met een beugeltje.
- **Daarna staand:** de cilinder tilt een gewicht van 2–5 kg. Zo moet de regeling
  ook tegen de zwaartekracht in werken, net als straks in de arm.
  - Rekenvoorbeeld: Ø20 op 3 bar duwt 94 N, ongeveer 9,5 kg. Dat geeft genoeg
    reserve.

## Proeven en wanneer ze geslaagd zijn

Elke proef levert een logbestand op (CSV) en de getallen hieronder. Een proef is pas
geslaagd als het getal gemeten is, niet als het er goed uitziet. De grenswaarden zijn
een voorstel en worden na T1 bijgesteld als dat nodig is.

| Proef | Wat | Geslaagd als |
|---|---|---|
| T0 Lektest | Kamer vullen tot 3 bar, alle ventielen dicht, 60 s wachten | Drukval < 0,1 bar in 60 s |
| T1 Ventielen | Eén ventiel 10 ms aan; drukverloop in de kamer meten | Druk begint < 10 ms na het signaal te stijgen; PWM-frequentie gekozen |
| T2 Aan/uit-regeling | Naar 75 mm sturen met alleen vol open/dicht, met dode zone | Komt tot stilstand binnen ±3 mm |
| T3 PWM-regeling | Sprong van 20 → 80 mm en terug | Doorschot < 5 mm, stil binnen 1 s, restfout < ±1 mm |
| T4 Herhaalbaarheid | 10× van wisselende kanten naar 50 mm | Spreiding < ±1 mm |
| T5 Last | Staand, 2–5 kg, sprong 20 → 80 mm, dan vasthouden | Zelfde als T3; zakt < 1 mm in 60 s |
| T6 Stijfheid | Op 50 mm, stijfheid laag/hoog, met de hand of een gewicht duwen | Meetbaar verschil in uitwijking bij dezelfde kracht |

## Veiligheid

- **Druk:** begin op 2–3 bar en ga nooit boven de 6 bar (de grens van de ventielen
  is 7 bar).
- **Afsluitschuif:** binnen handbereik. Na het dichtschuiven is alles achter de schuif
  drukloos.
- **Bij elke opstart:** draag een veiligheidsbril, houd je handen weg van de stang en
  het beugeltje, en zet de slangen vast. Een losschietende slang zwiept.
- **Software:** zet bij een fout, bij het opstarten en als het USB-contact wegvalt
  alle ventielen uit. In uit-stand houdt de cilinder zijn lucht vast. Ontluchten gaat
  met de afsluitschuif.
- **Pneumatiek is niet ongevaarlijk:** Ø20 op 6 bar duwt bijna 19 kg, en de cilinders
  van de arm worden vele malen sterker. De veiligheid van de arm moet uit het ontwerp
  komen: begrensde druk, begrensde snelheid en meegeven. Het medium zelf maakt hem
  niet veilig.

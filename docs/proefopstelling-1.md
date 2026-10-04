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
compressor ── filter + drukregelaar ── afsluitschuif ── hoofdventiel ──┬──────────────────┐
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

**Keuze: SMC VQ110, 5 stuks: 3× standaard (VQ110) en 2× grote doorstroming (VQ110U).**

- 3/2-ventiel, direct bediend (poppet), normaal gesloten
- Reactietijd: aan 3,5 ms, uit 2 ms. Snel genoeg voor PWM op 20–50 Hz.
- Maximaal 0,7 MPa (7 bar), 24 V DC
- Klein, en op AliExpress verkrijgbaar
- Doorstroming: Cv 0,02 (standaard) of 0,04 (VQ110U, grote doorstroming).

| | Standaard (VQ110) | Grote doorstroming (VQ110U) |
|---|---|---|
| Volle slag Ø20-cilinder, ruwweg | 0,5–1 s | 0,25–0,5 s |
| Kleinste krachtstap per puls (ca. 4 ms) | 1–2 N | 3–4 N |

**Indeling:** de twee VQ110U's zitten op de snelle richting, de drie standaard
ventielen op de andere richting en als reserve.

| Ventiel | Functie | Type |
|---|---|---|
| V1 | vul kamer A (stang uit, heffen) | VQ110U |
| V4 | leeg kamer B (stang uit, heffen) | VQ110U |
| V2 | leeg kamer A (stang in, zakken) | VQ110 |
| V3 | vul kamer B (stang in, zakken) | VQ110 |
| – | reserve | VQ110 |

Staand gemonteerd tilt de snelle richting de last omhoog, tegen de zwaartekracht in.
Omlaag helpt de zwaartekracht mee en is de standaard doorstroming genoeg. In één
opstelling zijn zo beide ventielmaten te meten: snelheid en precisie bij heffen
(groot) tegenover zakken (standaard). Die metingen sturen de ventielkeuze voor de arm.
De reserve past alleen op de standaardplekken; valt een VQ110U uit, dan draait de
proef tijdelijk met een standaard ventiel op die plek.
- SMC vervangt de VQ100-serie door de V100-serie. Distributeurs hebben nog voorraad.
  Voor de arm kiezen we hoe dan ook een ander, groter ventiel.

Een 3/2-ventiel wordt een 2/2-ventiel door één poort dicht te draaien met een M5-blindplug:

- **Vulventiel:** P ← perslucht, A → kamer, R dicht. Uit = dicht, aan = vullen.
- **Leegventiel:** P ← kamer, A → demper, R dicht. Uit = P dicht, aan = leeglopen.

Bij de lektest (T0) controleren we of de dichte stand echt dicht blijft.

**Typenummer:** zoals ik de SMC-codering lees, betekent het volgende. Controleer het bij de verkoper:

- `-5` = 24 V DC
- `M` of `L` = stekker *met* kabel; `MO`/`LO` = zonder kabel, die varianten niet nemen
- `-M5` = losse klep op een aansluitblok met M5-draad. Zonder `-M5` is het een
  klep voor een ventieleiland, en dan heb je er nog een blok bij nodig.

Bedoelde typenummers: **VQ110-5M-M5** (3×) en **VQ110U-5M-M5** (2×).

De goedkopere versie zonder `-M5` (los ventiel voor een ventieleiland) past hier niet.
Een ventieleiland heeft een gezamenlijke P-aansluiting voor alle ventielen. De
leegventielen hebben juist een eigen P nodig, want daar zit de kamer op.

Twee eilanden lossen dat niet op: een vulblok met VQ110's en dichte gezamenlijke R, en
een leegblok met VQ120's (normaal open) en dichte gezamenlijke P. Staan de ventielen
uit, dan zijn kamer A en kamer B allebei met dat dichte gezamenlijke kanaal verbonden,
en dus met elkaar. De drukken lopen gelijk en de cilinder zakt weg. Elk ventiel heeft
een eigen dichte poort nodig, en dat kan alleen met een eigen aansluitblok.

**Hoe een spoel 50 Hz haalt.** De VQ110 is *direct bediend*: de spoel trekt een klein,
licht ankertje een paar tienden van een millimeter op, en dat ankertje is zelf de klep.
Grote ventielen zoals de 4V210 zijn *voorgestuurd*: de spoel opent een klein
luchtkanaal en die lucht duwt dan een grote schuif om. Dat duurt 20–50 ms. Bij 50 Hz
duurt één puls 20 ms en heeft de VQ110 ongeveer 5,5 ms nodig om open en weer dicht te
gaan. Dat past ruim.

Er zijn twee soorten PWM:

- **Langzaam (20–50 Hz), wat deze opstelling doet.** De klep volgt elke puls: helemaal
  open, helemaal dicht. De cilinder en de slangen werken als buffer en middelen de
  stoten uit, zoals een emmer die je met korte scheuten vult. De pulsbreedte bepaalt
  hoeveel lucht er gemiddeld doorgaat.
  - Een puls korter dan de opentijd (ca. 3,5 ms) opent de klep niet. Bij 50 Hz is
    daardoor ruwweg 20–85% pulsbreedte bruikbaar. De software compenseert die dode
    zone.
  - Een lagere frequentie geeft fijnere stappen, maar meer drukrimpel. T1 bepaalt de
    frequentie.
- **Snel (kHz) op de spoel.** De klep volgt dit niet. De spoel middelt de stroom
  uit. Dit wordt gebruikt voor "peak-and-hold": vol aan om te openen, daarna minder
  stroom om open te houden. Dat geeft minder warmte en de klep gaat sneller dicht.
  Een aan/uit-klep kun je hiermee **niet** half open zetten; dat kan alleen een
  proportioneel ventiel, dat anders gebouwd is (schuif tegen een veer). Voor nu niet
  nodig.

Varianten `M`/`L` hebben een ingebouwd lampje en een overspanningsbeveiliging. Die zijn
gevoelig voor plus en min: rood aan +24 V, zwart aan de MOSFET.

**Levensduur.** Bij 50 Hz schakelt een klep 180.000 keer per uur. Dat gebeurt alleen
tijdens bewegen; bij stilstaan zijn de kleppen dicht. Voor de proef is dit geen
probleem. Voor de arm wordt de levensduur een keuzecriterium bij de ventielen.

**Waarom geen goedkopere 2/2-klep?** Gewone magneetkleppen zoals de 2V025 en 2W-serie
(€5) reageren in 20–50 ms. Daarmee is PWM boven ongeveer 10 Hz niet mogelijk en wordt
de regeling grof. De kleine "hoogfrequente" miniventielen van 10 mm zijn goedkoop
(€5–8), maar opgegeven voor 30 Hz en met heel weinig doorstroming. Voor een eerste test
zijn ze bruikbaar, maar voor een armgewricht niet.

**Waarom geen VT307?** Ook SMC, direct bediend, met veel meer doorstroming en
"universele poorten": druk mag op elke poort staan, dus dezelfde klep kan als
normaal gesloten, normaal open of verdeelventiel gebruikt worden. Maar de reactietijd
is ongeveer 20 ms, ruim vijf keer trager dan de VQ110. PWM gaat daarmee tot ongeveer
10 Hz, te grof voor deze regeling. Voor de arm is hij wel een kandidaat als *grof*
ventiel voor snelle bewegingen, naast een klein snel ventiel voor de fijne regeling.

**Vooruitblik:** de VQ110 is groot genoeg voor deze proefcilinder (Ø20), niet voor de
cilinders van de uiteindelijke arm. Die worden Ø40–63, omdat 15 kg op armlengte
honderden tot meer dan duizend newton aan cilinderkracht vraagt. Daar komen grotere
snelle ventielen voor, of meerdere ventielen naast elkaar. Deze proef levert de
regelsoftware en de meetgegevens om die keuze te maken.

## Onderdelenlijst

Prijzen zijn een indicatie (AliExpress, oktober 2026).

| # | Onderdeel | Zoekterm / type | Ca. prijs |
|---|---|---|---|
| 3 + 2 | Snel 3/2-ventiel 24 V | SMC VQ110-5M-M5 (3×) en VQ110U-5M-M5 (2×) | €134,80 samen, incl. verzending |
| 1 | Dubbelwerkende minicilinder Ø20, slag 150 mm | MAL20x150 | €15–25 |
| 1 | Lineaire potmeter 150 mm | KTC-150 / KPM-150 linear potentiometer | €20–40 |
| 2 | Druksensor 0–1 MPa, 5 V, uitgang 0,5–4,5 V | pressure transducer 0-1.2MPa 5V G1/4 | €8–15 per stuk |
| 1 | Raspberry Pi Pico 2 | | €6 |
| 1 | 4-kanaals MOSFET-module, logic level (werkt op 3,3 V) | 4 channel MOSFET module AOD4184 | €4 |
| 4 | Vrijloopdiode (als die niet op de module zit) | 1N4007 of SS34 | €1 |
| 1 | Voeding 24 V, 2–3 A | | €15 |
| 1 | Filter + drukregelaar met manometer | AFR2000 | €15–25 |
| 1 | Afsluitschuif die de leiding achter zich drukloos maakt | HSV-08 hand slide valve | €8 |
| 1 | Hoofdventiel 3/2, normaal gesloten, 24 V (hoeft niet snel te zijn) | 3V210-08 | €10 |
| 1 | Noodstopknop met verbreekcontact | emergency stop button NC | €5 |
| 6 | M5-blindplug | | €3 |
| 2 | M5-geluiddemper | | €2 |
| – | Steekkoppelingen M5→4 mm, 1/8"→4 mm, T-stukken 4 mm, adapter G1/4→4 mm voor de druksensoren, PU-slang 4 mm en 6 mm | | €25 |
| – | Weerstanden voor spanningsdeler (2× 10 kΩ + 2× 20 kΩ), breadboard, draadjes | | €5 |
| 1 | Compressor met tank, ±8 bar (als je er nog geen hebt) | | €100–150 |

**Totaal zonder compressor: ongeveer €230–330.**

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

## Regeling in lagen

- **Snelle laag, op de Pico:** leest positie en drukken en stuurt de ventielen, 200–500
  keer per seconde. Deze laag houdt de cilinder op de gevraagde positie en stijfheid.
  - Vertragingen in deze lus: klep 2–3,5 ms, een drukgolf door 1 m slang ca. 3 ms,
    en het vullen van de kamer (tientallen ms).
  - Bij deze snelheden is alleen terugkoppeling nodig, geen feedforward.
- **Langzame laag, op de pc (programma of AI):** geeft ongeveer 10 keer per seconde
  een nieuwe doelpositie en stijfheid door.

Ter vergelijking: bij een mens komt een bewuste reactie na ongeveer 0,1–0,2 s, een
reflex via het ruggenmerg na enkele tientallen ms. Spieren geven daarbij van nature
mee. De stijfheidsregeling, met druk in beide kamers tegelijk, doet hetzelfde.

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
- **Afsluitschuif:** binnen handbereik. Na het dichtschuiven is de toevoerleiding
  drukloos. De cilinderkamers niet: daar zit de lucht achter dichte ventielen.
- **Noodstop:** onderbreekt de 24 V naar alle ventielen. Alle vul- en leegventielen
  gaan dicht, dus de cilinder houdt zijn lucht vast en zakt niet weg. Het hoofdventiel
  sluit de toevoer af en ontlucht die. Blijft een vulventiel hangen, dan komt er toch
  geen lucht meer bij.
- **Bij elke opstart:** draag een veiligheidsbril, houd je handen weg van de stang en
  het beugeltje, en zet de slangen vast. Een losschietende slang zwiept.
- **Software:** zet bij een fout, bij het opstarten en als het USB-contact wegvalt
  alle ventielen uit. In uit-stand houdt de cilinder zijn lucht vast.
- **Cilinder drukloos maken:** eerst de afsluitschuif dicht, dan de leegventielen V2 en
  V4 openen, via de software of met de handbediening (drukknopje) op het ventiel zelf.
  Pas daarna aan de opstelling sleutelen.
- **Pneumatiek is niet ongevaarlijk:** Ø20 op 6 bar duwt bijna 19 kg, en de cilinders
  van de arm worden vele malen sterker. De veiligheid van de arm moet uit het ontwerp
  komen: begrensde druk, begrensde snelheid en meegeven. Het medium zelf maakt hem
  niet veilig.

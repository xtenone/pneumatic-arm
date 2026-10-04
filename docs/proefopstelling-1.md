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
compressor ── filter + drukregelaar ── afsluitschuif ── hoofdventiel ──┐
                                                                       │
                                     ┌─────────────────────────────────┤
                                     │                                 │
                                [V1 vul A]                        [V3 vul B]
                                     │                                 │
          druksensor pA ──── kamer A ═══════ CILINDER ═══════ kamer B ──── druksensor pB
                                     │                                 │
                                [V2 leeg A]                       [V4 leeg B]
                                     │                                 │
                                  demper                            demper

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

**Keuze: SMC VQ110U (grote doorstroming), 5 stuks: 4 plus 1 reserve.**

- 3/2-ventiel, direct bediend (poppet), normaal gesloten
- Reactietijd: aan 3,5 ms, uit 2 ms. Snel genoeg voor PWM op 20–50 Hz.
- Maximaal 0,7 MPa (7 bar), 24 V DC
- Klein, en op AliExpress verkrijgbaar
- Doorstroming: Cv 0,02 (standaard) of 0,04 (VQ110U, grote doorstroming).

| | Standaard (VQ110) | Grote doorstroming (VQ110U) |
|---|---|---|
| Volle slag Ø20-cilinder, ruwweg | 0,5–1 s | 0,25–0,5 s |
| Kleinste krachtstap per puls (ca. 4 ms) | 1–2 N | 3–4 N |

Alle vier de plekken krijgen de VQ110U. Een cilinder is zo snel als het langzaamste
ventiel in de lus: bij elke beweging vult de ene kamer en loopt de andere leeg. Eén
standaard ventiel in die lus remt de hele beweging. Met vier grote ventielen is de
cilinder in beide richtingen snel. De grotere krachtstappen (3–4 N) liggen naar
verwachting onder de wrijving van de afdichtingen (5–10 N), die de precisie toch al
begrenst.

Om toch een kleiner ventiel te kunnen nabootsen, komt er op elk vulventiel een
smoorventiel in serie. Dichtgedraaid gedraagt het vulventiel zich als een kleiner
ventiel, traploos instelbaar. Zo is te meten bij welke doorstroming snelheid en
precisie het best samengaan; die meting stuurt de ventielkeuze voor de arm.

Een 3/2-ventiel wordt een 2/2-ventiel door één poort dicht te draaien met een M5-blindplug:

- **Vulventiel:** P ← perslucht, A → kamer, R dicht. Uit = dicht, aan = vullen.
- **Leegventiel:** P ← kamer, A → demper, R dicht. Uit = P dicht, aan = leeglopen.

Bij de lektest (T0) controleren we of de dichte stand echt dicht blijft.

**Typenummer:** zoals ik de SMC-codering lees, betekent het volgende. Controleer het bij de verkoper:

- `-5` = 24 V DC
- `M` of `L` = stekker *met* kabel; `MO`/`LO` = zonder kabel, die varianten niet nemen
- `-M5` = losse klep op een aansluitblok met M5-draad. Zonder `-M5` is het een
  klep voor een ventieleiland, en dan heb je er nog een blok bij nodig.

Bedoeld typenummer: **VQ110U-5M-M5** (5×).

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

Prijzen zijn een indicatie (oktober 2026). Ingedeeld per bestelling.

### 1. Ventielen (AliExpress, winkel met 11 pagina's beoordelingen)

| # | Onderdeel | Type | Prijs |
|---|---|---|---|
| 5 | Snel 3/2-ventiel 24 V, grote doorstroming | SMC VQ110U-5M-M5 | €130,53 samen, incl. verzending |

### 2. Pneumatiek en sensoren (AliExpress)

Gekozen artikelen (AliExpress-artikelnummers):

| Onderdeel | Artikel | Te kiezen variant |
|---|---|---|
| Ventielen (bestelling 1) | 1005013133472109 | VQ110U-5M-M5 (met aansluitblok) |
| Lineaire potmeter | 1005006230077162 | 175 mm |
| Druksensoren | 1005010385122677 | G1/4, 100 psi, 5 V, 0,5–4,5 V |
| Cilinder | 1005010583152545 | Ø20, slag 150 mm (draadsoort poorten nog bevestigen) |

Houd de productwaarde (zonder verzending) onder €150. Komt het erboven, haal dan
slang en koppelingen eruit en koop die in Nederland (bijv. M5-koppelingen bij
domoticx.net, €0,87 per stuk).

| # | Onderdeel | Zoekterm / type | Ca. prijs |
|---|---|---|---|
| 1 | Dubbelwerkende rondcilinder volgens **ISO 6432**, Ø20, slag 150 mm. De norm legt de maten vast: poorten G1/8, stang M8×1,25, deksels M22×1,5 | ISO 6432 / DSNU-20-150 (Festo-compatibel) / AirTAC MI20x150 | €14–25 |
| 2 | Voetbevestiging voor Ø20 ISO 6432 (voor en achter, op de M22-draad) | foot mount ISO 6432 20 / HBN-20 | €3 per stuk |
| 1 | Stangkop (vorkkop) M8×1,25 | rod clevis M8x1.25 / SG-M8 | €3 |
| 1 | Lineaire potmeter, slag 175 mm (langer dan de cilinderslag, zodat hij nooit op zijn eindaanslag komt), 5 kΩ, met kogelkopjes aan de uiteinden | KTC-175 linear displacement sensor | €16–25 |
| 2 | Druksensor 0–100 psi (0–6,9 bar), 5 V, uitgang 0,5–4,5 V, G1/4 buitendraad (geen NPT) | pressure transducer 5V G1/4 0.5-4.5V 100psi | €12–16 per stuk |
| 1 | Filter + drukregelaar met manometer, G1/4, handmatige aftap | AFR-2000 | €8–9 |
| 1 | Afsluitschuif, G1/4, bij voorkeur één kant buitendraad (direct in de drukregelaar) | HSV-08 hand slide valve | €4–10 |
| 1 | Hoofdventiel 3/2, normaal gesloten (NC), 24 V DC, G1/4. Voorgestuurd: schakelt pas vanaf ca. 1,5 bar | 3V210-08 NC DC24V | €8–9 |
| 1 | Noodstopknop 22 mm, paddenstoel, vergrendelend (draaien om te ontgrendelen), verbreekcontact (NC), in een kastje | emergency stop button 22mm NC with box | €5–8 |
| 2 | Smoorventiel voor 4 mm slang | inline flow control valve 4mm | €3 per stuk |
| 10 | Steekkoppeling recht M5 → 4 mm (6 nodig) | PC4-M5 | €6–9 samen |
| 6 | M5-blindplug (4 nodig) | M5 blanking plug | €3 |
| 3 | M5-geluiddemper (2 nodig) | M5 silencer | €3 |
| 2 | Steekkoppeling recht G1/8 → 4 mm (cilinderpoorten) | PC4-01 | €2 |
| 6 | T-stuk 4 mm (4 nodig) | PE4 union tee | €4 |
| 2 | Steekkoppeling binnendraad G1/4 → 4 mm (voor de druksensoren) | PCF4-02 | €3 |
| 6 | Steekkoppeling recht G1/4 → 6 mm (5 nodig) | PC6-02 | €6 |
| 1 | Y-stuk 6 mm → 2× 4 mm (toevoer naar de vulventielen) | PW6-4 Y reducer | €2 |
| 1 | G1/4-geluiddemper (uitlaat hoofdventiel) | G1/4 silencer | €2 |
| 1 | Insteeknippel G1/4 buitendraad, Euro-type (voor de compressorslang) | 1/4 male plug Euro coupler | €2 |
| 5 m | PU-slang 4×2,5 mm | PU tube 4mm | €5 |
| 5 m | PU-slang 6×4 mm | PU tube 6mm | €6 |
| 1 | Slangschaar (rechte snede, anders lekt de koppeling) | tube cutter | €3 |

**Subtotaal: ongeveer €120–160.**

### 3. Elektronica (Tinytronics, Eindhoven)

| # | Onderdeel | Ca. prijs |
|---|---|---|
| 1 | Raspberry Pi Pico 2 (met headers, of headers zelf solderen) | €7,25 |
| 1 | Micro-USB-kabel (data, niet alleen laden) | €3 |
| 1 | ULN2803A, 8-kanaals schakel-IC met ingebouwde vrijloopdiodes | €1 |
| 1 | Breadboard 830 gaten + set jumperdraden | €9 |
| 2+2 | Weerstand 10 kΩ en 20 kΩ (spanningsdeler druksensoren) | €1 |
| 3 | Condensator 100 nF (ruisfilter ADC-ingangen) | €1 |
| 1 | Stekkeradapter 24 V DC, 1–2 A, 5,5×2,1 mm plug | €12 |
| 1 | DC-bus 5,5×2,1 mm naar schroefklem | €1 |
| 1 | Step-down-module 24 V → 5 V (voeding druksensoren), instelbaar of vast 5 V | €2–4 |
| – | Montagedraad 0,5 mm² (rood/zwart) | €3 |

**Subtotaal: ongeveer €35–40 plus verzending.**

### 4. Bouwmarkt

| # | Onderdeel | Ca. prijs |
|---|---|---|
| 1 | Multiplex 18 mm, ca. 60×30 cm (grondplaat) | €8 |
| – | Aluminium hoekprofiel, M4-boutjes, houtschroeven (beugel potmeter) | €7 |
| 1 | DIN-rail 35 mm, 30 cm (optioneel, om de ventielen netjes op te zetten) | €3 |
| 1 | Multimeter (als je er nog geen hebt) | €15–25 |
| 1 | PTFE-tape (voor de insteeknippel) | €1 |

**Subtotaal: ongeveer €20, met multimeter €35–45.**

### 5. Compressor

| # | Onderdeel | Ca. prijs |
|---|---|---|
| 1 | Stille compressor 24 l, 8 bar, olievrij, bijv. Stanley Silent 24 l (59 dB, Gamma) | €195 |

Een gewone compressor (ca. €100–130) werkt ook, maar maakt ruim 85 dB. Dat is
vervelend bij urenlang testen binnen. Een olievrije compressor geeft condenswater
af; daarvoor zit de waterafscheider in de drukregelaar.

### Totaal

| Bestelling | Ca. prijs |
|---|---|
| 1. Ventielen | €130,53 |
| 2. Pneumatiek en sensoren | €120–160 |
| 3. Elektronica | €35–45 |
| 4. Bouwmarkt | €20–45 |
| **Zonder compressor** | **€305–380** |
| 5. Compressor | €195 |
| **Met compressor** | **€500–575** |

**Waarom geen afstandssensor met licht (VL6180X, VL53L-serie)?** Die meet zonder
contact, en dat is aantrekkelijk. Maar de VL6180X is opgegeven tot 100 mm, de slag is
150 mm. De ruis is enkele millimeters bij een doel van ±1 mm. Een meting duurt ongeveer
10 ms: bij 0,6 m/s is de cilinder dan al 6 mm verder voordat de meting binnen is. Voor
een snelle regellus is dat te traag.

## Aansluitschema pneumatiek

Elke regel is één verbinding. De aantallen in de onderdelenlijst komen hieruit.

**Toevoer**

| Van | Koppeling | Slang | Naar | Koppeling |
|---|---|---|---|---|
| Compressorslang (Euro-koppeling) | – | – | drukregelaar IN | insteeknippel G1/4 + PTFE-tape |
| Drukregelaar UIT | – | – | afsluitschuif IN | buitendraad van de schuif direct in de regelaar (anders PC6-02 + slang + PC6-02) |
| Afsluitschuif UIT | PC6-02 | 6 mm | hoofdventiel P | PC6-02 |
| Hoofdventiel A | PC6-02 | 6 mm | Y-stuk 6 → 2× 4 | – |
| Hoofdventiel R | G1/4-demper | – | – | – |
| Y-stuk tak 1 | – | 4 mm, via smoorventiel | V1 P (vul A) | PC4-M5 |
| Y-stuk tak 2 | – | 4 mm, via smoorventiel | V3 P (vul B) | PC4-M5 |

**Per kamer (A met V1/V2, B met V3/V4)**

| Van | Koppeling | Slang | Naar | Koppeling |
|---|---|---|---|---|
| Vulventiel, poort A | PC4-M5 | 4 mm | T-stuk 1 | – |
| T-stuk 1 | – | 4 mm | leegventiel, poort P | PC4-M5 |
| T-stuk 1 | – | 4 mm | T-stuk 2 | – |
| T-stuk 2 | – | 4 mm | cilinderpoort | PC4-01 |
| T-stuk 2 | – | 4 mm | druksensor | PCF4-02 |
| Leegventiel, poort A | M5-demper | – | – | – |
| Poort R van vul- en leegventiel | M5-blindplug | – | – | – |

- **Korte slangen:** houd alle slangen tussen ventielen en cilinder korter dan
  ongeveer 30 cm, en zet de druksensor dicht bij de cilinderpoort.
- **Smoorventielen:** heeft het smoorventiel een pijl (eenrichtingsversie), laat die
  dan naar het vulventiel wijzen. Helemaal open staat de klep op volle doorstroming.

**Draadsoorten**

- G1/8 en G1/4 zijn BSP-draad (ook PT of BSPT op AliExpress). Die passen in elkaar,
  met PTFE-tape bij PT.
- **Geen NPT kopen:** NPT heeft een andere spoed (27 in plaats van 28 gangen per inch)
  en loopt vast of lekt in een G-poort. Let daar vooral op bij de druksensoren; die
  worden vaak met 1/8 NPT verkocht.
- M5 is overal M5×0,8.
- **Slang:** 4 mm buitenmaat (4×2,5 of 4×2) en 6 mm buitenmaat (6×4) passen allebei op
  de steekkoppelingen.

## Elektrisch

- **Pico 2 → ULN2803A:** 4 PWM-pinnen, één per ventiel. De ULN2803A schakelt de
  min-kant van elke spoel. Een VQ110-spoel trekt maar ongeveer 40–60 mA, ruim binnen
  wat de chip aankan (500 mA per kanaal). De vrijloopdiodes zitten in de chip: pin 10
  (COM) aan +24 V.
  - Een diode vertraagt het dichtgaan van het ventiel een beetje. Als dat in T1
    meetbaar is, voegen we per spoel een zenerdiode toe.
- **Spoelen:** rood aan +24 V, zwart aan een uitgang van de ULN2803A. Let op plus en
  min: het ingebouwde lampje en de beveiliging werken maar in één richting.
- **Noodstop en hoofdventiel:** de +24 V van de adapter gaat eerst door de noodstop.
  Daarachter hangen het hoofdventiel (rechtstreeks, dus altijd aan zolang de noodstop
  niet is ingedrukt) en de plus van de vier VQ110U-spoelen. Ingedrukt: alles valt af,
  ook als de software vastloopt.
- **Potmeter:** aan 3,3 V van de Pico, loper op ADC0 (GP26).
- **Druksensoren:** aan 5 V uit een step-down-module die op de 24 V zit, niet aan de
  USB-5 V. De uitgang van deze sensoren schaalt mee met hun voedingsspanning, en de
  USB-spanning schommelt tot ±5%. Dat zou direct ±5% meetfout geven. De uitgang gaat via
  een spanningsdeler 10 kΩ/20 kΩ naar ADC1 (GP27) en ADC2 (GP28). Zo wordt 4,5 V omgezet
  naar 3,0 V, en dat kan de Pico aan. De step-down-module zit vóór de noodstop, zodat de
  sensoren blijven meten als de noodstop is ingedrukt.
- **Ruis:** een condensator van 100 nF van elke ADC-ingang naar GND.
- **Massa:** de min van de 24 V-adapter, pin 9 (GND) van de ULN2803A en GND van de
  Pico aan elkaar.
- **De pc via USB:** levert stroom aan de Pico en ontvangt de meetgegevens
  (positie, twee drukken, ventielstanden). Dat gebeurt honderden keren per seconde.
- **Geen 230 V aan de opstelling:** een gesloten stekkeradapter, geen losse
  netvoeding met schroefklemmen.

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
| T7 Belastingsgraad | Staand, 5 bar, gewicht stap voor stap verhogen (Ø20 kan statisch ca. 16 kg tillen) | Bij elke stap T3 herhalen. Uitkomst: het hoogste percentage van de statische kracht waarbij T3 nog slaagt. Dat getal bepaalt de cilindermaten van de arm. |

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

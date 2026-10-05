# Test 1 — ontwerp: arm met één vrijheidsgraad, één cilinder, vier snelle ventielen

Dit document legt uit wat er gekozen is en waarom. Hoe je het bouwt en test staat in
[handleiding.md](handleiding.md); alle maten staan in `../params.py`.

## Wat deze proef moet bewijzen

Kan een gewone pneumatische cilinder met goedkope aan/uit-ventielen en een
microcontroller een arm naar een gekozen hoek sturen en daar laten blijven, ook met een
last eraan? En hoe
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
gevoelig voor plus en min: rood aan +24 V, zwart aan een uitgang van de ULN2803A.

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

De actuele lijst met artikelen, varianten, aantallen en prijzen staat in
[bestellijst.json](../../docs/bestellijst.json). `tools/bestellijst.py` maakt daar een klikbare pagina
van in de gedeelde webmap (`hosted/pneumatic-arm/bestellijst.html`).

Samengevat:

- **Pneumatiek (AliExpress):** 5× VQ110U-5M-M5, cilinder MAL20×150 (poorten PT1/8) met
  2 voetbevestigingen, moer M22×1,5 en vorkkop M8, drukregelaar AFR-2000 met vezelfilter,
  afsluitschuif HSV-08, hoofdventiel 3V210-08 (NC, 24 V DC), noodstop in kastje,
  steekkoppelingen 4 mm (M5, 1/8, 1/4), PCF4-02 voor de druksensoren, T-stukken 4 mm,
  M5-blindpluggen, M5-dempers, 2 smoorventielen, 10 m PU-slang 4×2,5 mm.
- **Sensoren (AliExpress):** lineaire potmeter KTC 175 mm (5 kΩ, type B), 2 druksensoren
  0–100 psi G1/4 (uitgang 0,5–4,5 V of 0–5 V; de deler 10k/15k is voor beide veilig).
- **Elektronica:** ULN2803A (AliExpress, 10 stuks); Pico 2, LM7805C, condensatoren
  1 µF en 100 nF, weerstanden 10 kΩ en 15 kΩ, breadboard, DC-bus, USB-kabel en draad
  (Tinytronics); eigen 24 V-adapter.
- **Bouwmarkt:** insteeknippel G1/4 passend op de compressor, slangschaar, PTFE-tape,
  multiplex grondplaat, aluminium hoekje, eventueel een multimeter.
- **Compressor:** Parkside PSKO 248 B1 (Lidl), 24 l, 8 bar, 71,9 dB.

Invoerheffing (sinds 1 juli 2026): €3 + btw per productcategorie per zending. Artikelen die
AliExpress zelf verzendt, worden samen in categorieën ingedeeld.

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
| Drukregelaar UIT | – | – | afsluitschuif IN | buitendraad van de schuif direct in de regelaar (anders PC4-02 + slang + PC4-02) |
| Afsluitschuif UIT | PC4-02 | 4 mm | hoofdventiel P | PC4-02 |
| Hoofdventiel A | PC4-02 | 4 mm | T-stuk 4 mm | – |
| Hoofdventiel R | open laten (blaast alleen bij een noodstop de toevoerleiding leeg) | – | – | – |
| T-stuk tak 1 | – | 4 mm (later via smoorventiel) | V1 P (vul A) | PC4-M5 |
| T-stuk tak 2 | – | 4 mm (later via smoorventiel) | V3 P (vul B) | PC4-M5 |

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
- **Slang:** alles in 4 mm (4×2,5). Bij één bewegingsrichting staat maar één vulventiel
  open (ca. 40 Nl/min); daarvoor is 4 mm slang ruim genoeg.
- **Invoerheffing:** €3 + btw per productcategorie per zending. Daarom zo min mogelijk
  verschillende soorten: geen 6 mm slang en geen Y-stuk.

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
- **Druksensoren:** aan 5 V uit een LM7805C die op de 24 V zit, niet aan de USB-5 V.
  - De uitgang van deze sensoren schaalt mee met hun voedingsspanning. De USB-spanning
    schommelt tot ±5%, en dat zou direct ±5% meetfout geven.
  - De twee sensoren trekken samen ca. 20 mA; de 7805 verstookt dan (24 − 5) V × 0,02 A
    ≈ 0,4 W. Dat kan zonder koelplaatje. Een lineaire regelaar geeft een rustigere
    spanning dan een schakelende step-down, en dat is beter voor analoge metingen.
  - Condensatoren: 1 µF tussen IN en GND, 100 nF tussen OUT en GND, dicht bij de pootjes.
  - De 7805 zit vóór de noodstop, zodat de sensoren blijven meten als de noodstop is
    ingedrukt.
  - Elke sensoruitgang gaat via een spanningsdeler 10 kΩ (boven) / 15 kΩ (onder) naar
    ADC1 (GP27) en ADC2 (GP28). Zo wordt 5,0 V omgezet naar 3,0 V. Dat is veilig voor de
    Pico, of de sensor nu 0,5–4,5 V of 0–5 V geeft.
  - Welke uitgang het is, blijkt bij de eerste meting: op 0 bar geeft hij ongeveer 0,5 V
    of ongeveer 0 V. De software kalibreert op 0 bar en op een bekende druk (de
    manometer van de drukregelaar).
- **Ruis:** een condensator van 100 nF van elke ADC-ingang naar GND.
- **Massa:** de min van de 24 V-adapter, pin 9 (GND) van de ULN2803A en GND van de
  Pico aan elkaar.
- **De pc via USB:** levert stroom aan de Pico en ontvangt de meetgegevens
  (positie, twee drukken, ventielstanden). Dat gebeurt honderden keren per seconde.
- **Voeding:** een gesloten 24 V-stekkeradapter (minimaal 0,5 A, liever 1–2 A), geen
  losse netvoeding met schroefklemmen. Zo zit er geen 230 V aan de opstelling.
  Verbruik: 4 ventielspoelen max. ~250 mA, hoofdventiel ~125 mA, 7805 + sensoren
  ~25 mA; samen ~400 mA in het slechtste geval.

## Mechanisch: de arm

De cilinder tilt een arm, zoals straks in de schouder. Zo test je meteen wat er in de
echte arm gebeurt: een kracht die met de hoek verandert, een last aan het eind, en de
omrekening van cilinderlengte naar hoek. Zie `out/tekeningen/zijaanzicht.pdf`.

- **Staander:** twee wangen van multiplex 18 mm met een afstandsblok van 36 mm (twee lagen
  hetzelfde multiplex) ertussen, op een grondplaat van 40 × 30 cm. De opstelling staat
  op de tafelrand met twee lijmklemmen; de last hangt naast de tafel.
- **Scharnier:** bout M8 door twee kogellagers 608 (skatelagers) in de wangen, 420 mm
  boven de grondplaat. Goedkoop, overal te krijgen, en zonder speling.
- **Arm:** aluminium strip 40×5 mm, 450 mm. De vorkkop van de cilinder grijpt aan op
  150 mm van het scharnier, de last hangt op 400 mm.
- **Cilinder:** draait achter op een bout M8, 320 mm recht onder het scharnier. Pen-pen
  311–461 mm geeft een armhoek van −17° tot +66°.
- **Potmeter:** met slangklemmen op de cilinderbuis, de stang via een beugeltje aan de
  cilinderstang. Hij meet de cilinderlengte; de software rekent die om naar de hoek.

| Armhoek | Hefboom cilinder | Max. koppel bij 5 bar | Zwaartekracht (arm + 1,5 kg) | Belasting |
|---|---|---|---|---|
| −17° | 148 mm | 23,2 Nm | 6,1 Nm | 26% |
| 0° | 136 mm | 21,3 Nm | 6,4 Nm | 30% |
| 40° | 85 mm | 13,4 Nm | 4,9 Nm | 37% |
| 66° | 43 mm | 6,7 Nm | 2,6 Nm | 39% |

Hoe hoger de arm, hoe kleiner de hefboom van de cilinder: dat is hetzelfde effect als
straks in het 2-DOF-gewricht (zie `docs/2dof-gewricht.md` in de hoofdmap).

## Regeling

Het algoritme staat in `firmware/control.py` en draait **ongewijzigd** op de Pico én in de
simulatie. De afstelling uit de simulatie is dus precies wat er op de Pico komt.

**Lagen:**

- **Snelle laag, op de Pico (500 keer per seconde):** leest positie en drukken en stuurt
  de ventielen.
  1. **Doel met begrensde snelheid:** het doel loopt met maximaal 250 mm/s naar de
     gevraagde stand. Een volle slag duurt zo ca. 0,6 s, zonder sprong in de regelfout.
  2. **Positieregelaar (PID) → gewenste kracht.**
     - De integrerende term werkt alleen dicht bij het doel (binnen 6 mm) of als de arm
       stilstaat. Zo overwint hij wrijving en last zonder doorschot.
  3. **Kracht → kamerdrukken:** de gewenste kracht wordt verdeeld over kamer A en B, met de
     som van beide drukken als **stijfheid** (instelbaar, standaard 4 bar).
  4. **Drukregelaar per kamer → PWM-duty:** vullen, legen of vasthouden. Vullen en legen
     van dezelfde kamer tegelijk kan niet. Een minimale pulsduur zorgt dat het ventiel
     echt opent.
  5. **In positie:** fout < 0,3 mm, de arm staat stil en de drukken zitten op hun doel.
     Dan gaan alle ventielen dicht en houdt de opgesloten lucht de arm vast. Dat spaart
     lucht en ventielen; pas bij > 0,6 mm regelt hij weer.
  6. **Ontlasten:** komt een kamer boven 6 bar (bijv. lucht die bij doorschieten wordt
     samengedrukt), dan gaat het leegventiel van die kamer open. Duurt het langer dan
     0,5 s, dan volgt een fout: de drukregelaar staat te hoog.
- **Langzame laag, op de pc (programma of AI):** geeft doelhoek en stijfheid door, en
  stuurt elke 0,2 s een `ping`. Mist de Pico die een halve seconde, dan gaan alle
  ventielen dicht.

Er is geen feedforward nodig. De vertragingen in de lus zijn klein: klep 2–3,5 ms, een
drukgolf door 30 cm slang ca. 1 ms, en het vullen van een kamer tientallen ms.

## Simulatie

`sim/run.py` simuleert de arm in MuJoCo, met een model van de pneumatiek:
- doorstroming van de ventielen volgens ISO 6358
- opening- en sluitvertraging van de ventielen
- kamerdrukken, wrijving van de afdichtingen
- ruis en ADC-stappen van de sensoren

Uitkomst met de huidige afstelling (`out/sim/resultaten.json`, grafieken in `out/sim/`):

| Proef (simulatie) | Uitkomst |
|---|---|
| T3 sprong 0° → 30° | doorschot 1,0 mm, ingesteld in 0,9 s, restfout 0,3 mm — geslaagd |
| T3 sprong 30° → −5° | doorschot 1,2 mm, ingesteld in 0,5 s, restfout 0,1 mm — geslaagd |
| T2 aan/uit-regeling (3 bar) | slingert 20–30 mm rond het doel: de PWM-regeling is nodig |
| T6 stijfheid (15 N extra, ventielen dicht) | 14° uitwijking bij 2 bar kamerdruk, 10° bij 5 bar |
| T7 belasting | doel gehaald tot 3,5 kg (78% belasting), maar alleen rond de afstellast (1,5 kg) binnen 1 s; bij 100% niet meer |

Exacte getallen per run: [`../out/sim/resultaten.md`](../out/sim/resultaten.md).
Uit T7 blijkt al dat de afstelling bij de last hoort. Voor de arm is waarschijnlijk een
afstelling nodig die meeschaalt met de last of de stand.

Het model is een schatting. Wrijving, dode volumes en de doorstroming van deze
ventielen worden in T1–T4 gemeten; daarna wordt het model bijgesteld en de regeling
opnieuw afgesteld.

## Proeven

De proeven T0–T7, met criteria, staan in [handleiding.md](handleiding.md), hoofdstuk 11.
`host/proeven.py` voert ze uit en beoordeelt ze met dezelfde analyse als de simulatie
(`host/analyse.py`).

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
- **Arm:** handen weg tussen arm en staander. Zet de grondplaat met twee lijmklemmen op
  de tafelrand; de last hangt naast de tafel.
- **Ontlasten:** boven 6 bar opent de software het leegventiel van die kamer.
- **Pneumatiek is niet ongevaarlijk:** Ø20 op 6 bar duwt bijna 19 kg, en de cilinders
  van de arm worden vele malen sterker. De veiligheid van de arm moet uit het ontwerp
  komen: begrensde druk, begrensde snelheid en meegeven. Het medium zelf maakt hem
  niet veilig.

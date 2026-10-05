# Handleiding test 1 — arm met één vrijheidsgraad

Deze handleiding neemt je stap voor stap mee: onderdelen controleren, bouwen,
aansluiten, software installeren, kalibreren en de proeven T0–T7 doen.

Bij 📷 maak je een foto en stuur je die op, voordat je verdergaat. Dan kijkt iemand
mee voordat er lucht of stroom op komt.

Alle maten komen uit `params.py` en staan ook in de tekeningen in `out/tekeningen/`.

---

## 0. Veiligheid — eerst lezen

- **Veiligheidsbril op** zodra er perslucht op de opstelling staat. Een losschietende
  slang zwiept en kan je oog raken.
- **Begin op 2–3 bar.** Pas naar 5 bar als T0 tot en met T2 goed zijn gegaan. Nooit
  boven de 6 bar: de ventielen kunnen 7 bar aan, de druksensoren 6,9 bar.
- **Handen weg tussen arm en staander.** De cilinder duwt op 5 bar 157 N, en bij het
  scharnier is dat genoeg om vingers te pletten.
- **Noodstop binnen handbereik.** Ingedrukt: de 24 V gaat eraf, alle ventielen gaan
  dicht en het hoofdventiel laat de toevoerleiding leeglopen. De cilinder houdt dan
  zijn lucht vast; de arm blijft staan en valt niet.
- **Drukloos maken voordat je sleutelt:**
  1. afsluitschuif dicht (toevoer drukloos);
  2. in de software `klep 0 1 0 1` (beide kamers leeg laten lopen), of het knopje
     (handbediening) op de leegventielen V2 en V4 indrukken;
  3. de manometers van de drukregelaar en de meting van de druksensoren moeten 0 bar
     tonen.
- **Opstelling vastzetten.** De arm steekt over de tafelrand. Zet de grondplaat met twee
  lijmklemmen vast, anders kan het geheel kantelen bij een snelle beweging.
- **Geen 230 V aan de opstelling.** Alleen de gesloten 24 V-stekkeradapter.

---

## 1. Ontvangstcontrole

Doe dit per pakket, **voordat** je op AliExpress "ontvangst bevestigen" drukt. Is er
iets mis, open dan een geschil met foto's.

| Onderdeel | Controle | Goed als |
|---|---|---|
| 5× VQ110U-5M-M5 | etiket | er staat VQ110U-5M-M5 op, met aansluitblok (wit blokje met poorten) |
| | spoelweerstand (multimeter Ω, rode en zwarte draad) | alle vijf ongeveer gelijk: ca. 380–600 Ω (1–1,5 W op 24 V) |
| | 24 V er kort op (rood +, zwart −) | duidelijke tik, het lampje in de stekker brandt |
| | blazen op P (fietspomp of mond), spoel uit/aan | uit: dicht, aan: lucht komt uit A |
| Cilinder MAL20×150 | stang met de hand in- en uitschuiven | loopt gelijkmatig, zonder haperen |
| | poorten | draad 1/8; een PC4-01 draait er met de hand soepel een paar slagen in |
| | maten (meten!) | pen-pen-lengte ingeschoven noteren — zie stap 5 |
| Potmeter KTC-175 | weerstand tussen de pinnen | twee pinnen geven vast ca. 5 kΩ (de uiteinden); de derde is de loper |
| | loper bewegen | weerstand loper–uiteinde verandert gelijkmatig met de stang |
| 2× druksensor | 5 V erop (rood +, zwart −), signaal meten | 0 bar: ca. 0,5 V (of ca. 0 V bij een 0–5 V-type) |
| | draad | buitendraad G1/4 (past in de PCF4-02) |
| ULN2803A | — | test volgt in stap 8 |
| Drukregelaar, schuif, hoofdventiel | draadmaten | G1/4 (de PC4-02-koppelingen passen) |
| Noodstop | multimeter op piep, op de NC-aansluitingen | piept als de knop uit is, stil als hij is ingedrukt |

📷 Foto van alle onderdelen naast elkaar, met de etiketten van de ventielen leesbaar.

---

## 2. Gereedschap

- decoupeerzaag of handzaag (hout), ijzerzaag en vijl (aluminium)
- boormachine met houtboren 5 en 8,5 mm, metaalboren 5,5 en 8,5 mm, Forstnerboor 22 mm
- schroevendraaiers, steeksleutels 8, 10, 13 mm, inbussleutels
- striptang, kleine schroevendraaier voor schroefklemmen
- rolmaat, winkelhaak, priem of centerpons
- multimeter
- veiligheidsbril

---

## 3. Houtwerk: grondplaat, wangen en afstandsblok

Tekeningen: `out/tekeningen/wang.pdf` en `out/tekeningen/zijaanzicht.pdf`.

1. **Zagen** uit multiplex 18 mm. De bouwmarkt zaagt vaak gratis op maat.
   - grondplaat 400 × 300 mm
   - 2 wangen 450 × 120 mm
   - 2 blokjes 60 × 60 mm (samen het afstandsblok van 36 mm)
2. **Gaten aftekenen op beide wangen.** Leg ze precies op elkaar en zet ze vast met
   een klem. Zo komen de gaten in beide wangen exact recht tegenover elkaar.
   - scharnier: midden van de breedte (60 mm), 420 mm vanaf de onderkant
   - draaipunt cilinder: midden (60 mm), 100 mm vanaf de onderkant
   - 2 schroefgaatjes voor het blok: 30 mm van de achterkant, 20 en 45 mm hoog
3. **Boren,** met de wangen nog op elkaar geklemd:
   - Ø10 mm door, bij het scharnier
   - Ø8,5 mm door, bij het draaipunt van de cilinder
   - Ø5 mm door, bij de schroefgaatjes
4. **Lagerzittingen.** Haal de wangen uit elkaar. Boor aan de **buitenkant** van elke
   wang bij het scharnier met de Forstnerboor Ø22 mm een gat van **7 mm diep**. De
   twee wangen zijn dus elkaars spiegelbeeld.
   - Druk een lager 608 erin. Het moet strak zitten: tik het er met een blokje hout in.
   - Zit het los, zet het dan vast met een druppel tweecomponentenlijm.
5. **Afstandsblok:** lijm de twee blokjes van 60 × 60 op elkaar (36 mm dik).
6. **In elkaar zetten:**
   - zet het afstandsblok achter-onder tussen de wangen en schroef het vast met
     4 schroeven 4×40 door de Ø5-gaatjes;
   - zet de wangen met 4 hoekijzers op de grondplaat. De achterkant van de wangen staat
     90 mm van de achterrand van de grondplaat (de voorkant 190 mm van de voorrand); de
     wangen staan midden op de breedte.
   - Controleer met de winkelhaak dat de wangen recht staan.

📷 Foto van de staander op de grondplaat, van opzij en van voren.

---

## 4. De arm

Tekening: `out/tekeningen/arm.pdf`.

1. Zaag de aluminium strip 40×5 op **450 mm** en vijl de randen glad.
2. **Gaten aftekenen,** op de hartlijn (20 mm van de rand):
   - scharnier: 20 mm van het ene einde
   - vorkkop: 150 mm vanaf het scharniergat
   - last: 400 mm vanaf het scharniergat
3. Pons de gaten voor, boor eerst Ø5, dan **Ø8,5**, en ontbraam ze.
4. **Afstandsbusjes:** zaag van het buisje 10×1 vier stukjes:
   - 2× **15,5 mm** voor de arm in het scharnier (36 − 5 = 31, verdeeld over 2 kanten)
   - 2× **7 mm** voor het achterste draaipunt van de cilinder (36 − 22 = 14, verdeeld)
5. **Monteren:** steek een bout M8×80 door de lagers en wangen. Zet onderweg de busjes en
   de arm ertussen: lager — busje 15,5 — arm — busje 15,5 — lager. Draai de borgmoer
   aan tot er geen speling is, maar de arm nog vrij draait.

📷 Foto van het scharnier van boven. De arm moet midden tussen de wangen zitten en vrij
op en neer draaien.

---

## 5. De cilinder

1. **Pen-pen-lengte meten** met de stang helemaal ingeschoven: van het hart van het
   gat achterop tot het hart van de pen van de vorkkop. Zet daarvoor eerst de vorkkop
   op de stang, zie stap 2.
   - In de berekening staat **311 mm**.
   - Wijkt het meer dan 5 mm af, geef het door: dan wordt `params.py` aangepast. Dat
     verandert het bewegingsbereik en de kalibratie.
2. **Vorkkop op de stang,** in deze volgorde: moer M8 — beugeltje van de potmeter
   (gat 8,5) — moer M8 — vorkkop. Draai de vorkkop ongeveer 12 mm op de stang en
   zet hem vast met de moeren.
3. **Achterste draaipunt:** steek de tweede bout M8×80 door de wang, een busje van 7 mm,
   het gat achterop de cilinder, nog een busje van 7 mm en de andere wang. De
   luchtpoorten wijzen naar de **voorkant** (weg van de staander). Zet de borgmoer
   vast, maar laat de cilinder vrij draaien.
4. **Aan de arm:** zet de vorkkop met zijn pen vast in het gat op 150 mm. Zet de borgveer
   of het splitpennetje erop.
5. Beweeg de arm met de hand helemaal op en neer. Er mag niets aanlopen.
   - Onderste stand: ongeveer −17°, cilinder helemaal in.
   - Bovenste stand: ongeveer +66°, cilinder helemaal uit.

📷 Foto van opzij, met de arm horizontaal.

---

## 6. De potmeter

1. Buig van de strip 20×3 een montagestrip die op de cilinderbuis past.
2. Zet de potmeter daarop met zijn eigen klemmetjes.
3. Zet de montagestrip met twee slangklemmen op de cilinderbuis, aan de **onderkant**
   (weg van het scharnier). De potmeter ligt evenwijdig aan de cilinder.
4. Zet de kogelkop van de potmeterstang met een boutje M5 vast aan het beugeltje op de
   cilinderstang.
5. Beweeg de arm helemaal op en neer.
   - De potmeter mag nooit op zijn eigen eindaanslag komen: zijn slag is 175 mm, die
     van de cilinder 150 mm. Schuif hem zo dat er aan beide kanten speling blijft.
   - Niets mag klemmen; de kogelkop vangt kleine scheefstand op.

📷 Foto van de potmeter op de cilinder, in de onderste en de bovenste stand.

---

## 7. Pneumatiek

Schema: `out/tekeningen/pneumatiek.pdf`. De aansluitregels staan ook in
`docs/ontwerp.md` (hoofdstuk "Aansluitschema pneumatiek").

**Steekkoppelingen:**
- **Slang inschuiven:** recht afsnijden met de slangschaar, en er stevig in duwen
  tot de aanslag (ca. 15 mm). Daarna even aan de slang trekken.
- **Slang eruit halen:** het blauwe ringetje indrukken en dan trekken.

**Schroefdraad:**
- G1/4 en 1/8: PTFE-tape, 3–4 slagen met de draairichting mee. Stevig met de hand
  aandraaien, dan een kwartslag met de sleutel.
- M5 aan de ventielen: niet te vast, het aansluitblok is van kunststof. Het rubber
  ringetje van de koppeling dicht af.

**Opbouw:**
1. **Ventielen voorbereiden** (zie de tabel in het ontwerp):
   - **vulventielen V1, V3:** P = voeding, A = naar de kamer, **R = blindplug**
   - **leegventielen V2, V4:** P = vanuit de kamer, A = demper, **R = blindplug**
   - Plak een label op elk ventiel: V1 vul A, V2 leeg A, V3 vul B, V4 leeg B.
2. **Zet de ventielen dicht bij de cilinder,** op het afstandsblok of op een strookje
   hout. Houd elke slang tussen ventiel en cilinder **korter dan 30 cm**.
3. **Kamer A** is de poort aan de achterkant van de cilinder (zuigerzijde), **kamer B**
   de poort voorin (stangzijde).
4. **Per kamer:** één T-stuk naar het vulventiel, het leegventiel en de cilinderpoort,
   en een tweede T-stuk naar de druksensor (in een PCF4-02 geschroefd).
5. **Toevoer:** compressor — drukregelaar — afsluitschuif — hoofdventiel P → A —
   T-stuk — naar P van V1 en V3. De R-poort van het hoofdventiel blijft open: daar
   blaast de toevoer leeg bij de noodstop.
6. Zet de smoorventielen er **nog niet** tussen. Die zijn voor later (de vergelijking).

📷 Foto van de complete pneumatiek, met de labels leesbaar.

**Eerste lektest met zeepsop** (pas na stap 8 en 9, als de noodstop werkt):
1. Drukregelaar op 2 bar, afsluitschuif open.
2. Hoofdventiel aan: de noodstop is uitgetrokken en de 24 V staat aan.
3. Kwast met zeepsop over elke koppeling. Belletjes = lek. Opnieuw afsnijden en
   insteken, of de draad opnieuw tapen.

---

## 8. Elektronica

Schema: `out/tekeningen/bedrading.png`. Aansluitlijst: `out/tekeningen/bedrading_lijst.png`.

**Werk in deze volgorde en test na elke stap.** Steek de 24 V-adapter pas in het
stopcontact als dat in de stappen staat.

1. **Pico en ULN2803A** op het breadboard. Zet de ULN2803A over de middengleuf, met
   de inkeping naar links. Pin 1 zit dan linksonder (vaak met een puntje); pin 1–9 lopen
   langs de onderkant, pin 10–18 terug langs de bovenkant.
2. **Massa:** Pico GND, ULN2803A pin 9, LM7805C pin 2 en de min van de adapter samen
   op de blauwe railstrip van het breadboard.
3. **Stuurdraden:** GP2 → IN1 (pin 1), GP3 → IN2 (pin 2), GP4 → IN3 (pin 3),
   GP5 → IN4 (pin 4).
4. **24 V en noodstop:**
   - Plus van de adapter via de DC-bus naar het **NC-contact** van de noodstop.
   - Andere kant van de noodstop: dit is "+24 V ná noodstop". Die gaat naar
     ULN2803A pin 10 (COM) en naar de rode draad van alle vier de VQ110-spoelen.
   - Aan "+24 V ná noodstop" hangt ook één kant van het hoofdventiel. De andere kant
     van het hoofdventiel gaat naar GND.
5. **Spoelen:** zwart van V1 → OUT1 (pin 18), V2 → OUT2 (pin 17), V3 → OUT3 (pin 16),
   V4 → OUT4 (pin 15). **Let op plus en min:** in de stekker van de spoelen zitten een
   lampje en een beveiliging, en die werken maar in één richting.
6. **LM7805C:**
   - IN (pin 1) aan de 24 V **vóór** de noodstop, met de 1 µF van IN naar GND.
   - OUT (pin 3) wordt de +5 V, met de 100 nF van OUT naar GND.
   - Pinvolgorde, met de tekst naar je toe en de pootjes naar beneden: IN – GND – OUT.
7. **Druksensoren:**
   - rood aan +5 V, zwart aan GND
   - signaal via **10 kΩ** naar GP27 (sensor A) en GP28 (sensor B)
   - van GP27 en GP28 elk **15 kΩ** naar GND, en een **100 nF** naar GND
8. **Potmeter:**
   - uiteinden aan **3V3** (Pico pin 36) en **GND**
   - loper aan **GP26**, met een 100 nF naar GND

📷 Foto van het breadboard van bovenaf, scherp genoeg om de draden te volgen.

**Eerste test, zónder perslucht** (afsluitschuif dicht):
1. **5 V meten:** adapter erin, noodstop uitgetrokken. Meet OUT van de 7805: 4,9–5,1 V.
2. **Sensorspanning op de Pico-pinnen:** meet GP27 en GP28 ten opzichte van GND. Dat moet
   onder de 3,1 V liggen, anders klopt de deler niet. Op 0 bar is het ca. 0,3 V.
3. **Ventielen laten klikken:** zie stap 9 (software), commando `klep 1 0 0 0`. Je
   hoort V1 tikken en ziet zijn lampje. Test zo alle vier, en daarna de noodstop:
   indrukken = alles stil.

---

## 9. Software

### Op de Pico (MicroPython)

1. **MicroPython erop zetten:**
   - download MicroPython voor de **Raspberry Pi Pico 2** (RP2350) van
     micropython.org (bestand `.uf2`);
   - houd de BOOTSEL-knop ingedrukt en steek de USB-kabel erin. De Pico verschijnt als
     USB-schijf;
   - sleep het `.uf2`-bestand erop. De Pico herstart vanzelf.
2. **Thonny** installeren (thonny.org). Kies rechtsonder "MicroPython (Raspberry Pi Pico)".
3. **Firmware kopiëren:** zet de vier bestanden uit `firmware/` op de Pico:
   `main.py`, `control.py`, `config.py` en `hw.py`. In Thonny: open het bestand, dan
   "Opslaan als…" → "Raspberry Pi Pico".
4. Druk op Stop/Herstart in Thonny. Onderin zie je `OK,gestart`. Typ `help` voor de
   commando's.

`config.py` wordt gegenereerd uit `params.py` (`python gen_config.py`). Pas hem dus niet
met de hand aan.

### Op de pc (Python 3.10 of nieuwer)

```
cd test1/host
pip install -r requirements.txt
python logger.py              # zoekt de Pico zelf; anders: --poort COM5 of /dev/ttyACM0
```

Sluit Thonny eerst af: er kan maar één programma tegelijk met de Pico praten.

**Belangrijke commando's** (ook in `help`):

| Commando | Wat |
|---|---|
| `off` | alle ventielen dicht |
| `klep 1 0 0 0` | V1 open (handmatig, duty 0..1 per ventiel) |
| `druk 2 2` | beide kamers op 2 bar regelen |
| `hoek 20` | arm naar 20° |
| `bang 20` | aan/uit-regeling naar 20° (T2) |
| `som 4` | stijfheid: som van de kamerdrukken |
| `nul`, `kal_druk 3`, `kal_pos in`, `kal_pos uit`, `opslaan` | kalibratie (stap 10) |

**Veiligheid in de software:**
- Stuurt de pc een halve seconde niets, dan gaan alle ventielen dicht. De logger en
  het proevenscript sturen daarom elke 0,2 s `ping`.
- Bij het eerste bewegingscommando start de hardware-watchdog. Loopt het programma
  vast, dan herstart de Pico vanzelf, met alle ventielen dicht.

---

## 10. Kalibreren

Doe dit één keer, en opnieuw na het verplaatsen van de potmeter of een andere sensor.

1. **Nulpunt druk:** afsluitschuif dicht. Typ `klep 0 1 0 1` (beide leegventielen open) en
   laat dat zo tot en met stap 3. Typ **`nul`**.
2. **Potmeter, onderkant:** arm met de hand helemaal omlaag (cilinder helemaal in). De arm
   beweegt vrij, want beide kamers staan open naar buiten. Typ **`kal_pos in`**.
3. **Potmeter, bovenkant:** arm met de hand helemaal omhoog (cilinder helemaal uit).
   Typ **`kal_pos uit`**, laat de arm rustig zakken en typ `off`.
4. **Druk, versterking:**
   - drukregelaar op **3,0 bar**, afsluitschuif open;
   - typ **`klep 1 0 1 0`**: beide kamers vullen tot 3 bar. Met de last eraan blijft de
     arm liggen of beweegt hij een beetje; dat geeft niet. Wacht 3 seconden;
   - kijk op de manometer en typ **`kal_druk 3.0`** (of wat de manometer aangeeft);
   - typ **`off`**.
5. **`opslaan`**: de kalibratie gaat naar `cal.json` op de Pico.
6. **Controle:**
   - arm met de hand naar horizontaal. De logger moet een hoek van ca. 0° tonen; meet
     na met een waterpas;
   - de druk op de manometer en de gemeten druk moeten binnen 0,1 bar van elkaar zitten.

📷 Schermafdruk van de logger met de arm horizontaal.

---

## 11. De proeven

Start: `python proeven.py T0` (en zo verder), of `python proeven.py alle`.
Elke proef bewaart zijn meting, grafiek en uitkomst in `host/resultaten/`. Stuur die map
op na elke proef.

| Proef | Druk | Last | Wat | Geslaagd als |
|---|---|---|---|---|
| T0 lektest | 3 bar | 1,5 kg | arm naar 20°, alle ventielen dicht, 60 s meten | drukval < 0,1 bar |
| T1 ventielen | 3 bar | – | elk ventiel 10 ms open, druk snel meten | reactie < 10 ms |
| T2 aan/uit | 3 bar | 1,5 kg | 0° → 30° → −5° met alleen vol open/dicht | stilstand binnen ±3 mm |
| T3 PWM-regeling | 5 bar | 1,5 kg | 0° → 30° → −5° | doorschot < 5 mm, stil binnen 1 s, restfout < 1 mm |
| T4 herhaalbaarheid | 5 bar | 1,5 kg | 10× naar 20°, afwisselend van boven en onder | spreiding < ±1 mm |
| T5 vasthouden | 5 bar | 1,5 kg | 60 s op 30° | afwijking < 1 mm |
| T6 stijfheid | 5 bar | 1,5 + 1 kg | op 20°, ventielen dicht, 1 kg erbij; kamerdruk 2 en 5 bar | duidelijk minder uitwijking bij 5 bar |
| T7 belastingsgraad | 5 bar | 0,5 → 3,5 kg | T3 herhalen met oplopende last | hoogste last waarbij T3 slaagt |

De verwachting uit de simulatie staat in `out/sim/resultaten.json` en in het
README-bestand. Wijkt de echte meting sterk af, dan is dat juist nuttige informatie,
bijvoorbeeld over de wrijving van de cilinder.

**Na T7:** zet de smoorventielen tussen het T-stuk en de vulventielen en herhaal T3 met
de smoorventielen ¼, ½ en ¾ dicht. Zo zie je wat een kleiner ventiel doet met snelheid
en precisie. Zet een streepje op elke schroef, zodat je een stand terugvindt.

---

## 12. Problemen oplossen

| Wat je ziet | Waarschijnlijke oorzaak | Wat te doen |
|---|---|---|
| Ventiel tikt niet | plus/min omgedraaid, of noodstop ingedrukt | rood aan +24 V ná noodstop, zwart aan OUT; noodstop uittrekken |
| Ventiel blijft altijd open | R-poort niet dicht, of P en A verwisseld | blindplug op R; zie de tabel in stap 7 |
| Druk loopt langzaam weg (T0) | lekkende koppeling | zeepsoptest, slang opnieuw recht afsnijden |
| Druk leest 0 terwijl de manometer 3 bar toont | sensor zonder +5 V of verkeerde draad | 5 V meten op de rode draad; signaal op geel/groen |
| Hoek springt of ruist | potmeterdraad los, of geen 100 nF op GP26 | aansluitingen nalopen |
| Arm slingert rond het doel | wrijving anders dan in de simulatie | `KP_FORCE` lager of `KD_FORCE` hoger in `params.py`, `python gen_config.py`, config.py opnieuw kopiëren |
| `FOUT,overdruk` | drukregelaar boven 6 bar | regelaar lager zetten |
| `FOUT,geen contact met de pc` | logger gestopt of USB los | normaal gedrag; opnieuw starten |
| De Pico herstart steeds | watchdog na stoppen in Thonny | normaal: na 2 s draait hij weer, met alle ventielen dicht |

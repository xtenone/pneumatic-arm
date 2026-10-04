# Kosten per DOF

Een DOF (vrijheidsgraad) is hier één cilinder met zijn ventielen, sensoren en
besturing. Gedeelde onderdelen (compressor, drukregelaar, voeding) tellen niet mee.

## Proefopstelling (oktober 2026)

| Onderdeel | Prijs |
|---|---|
| 4× SMC VQ110U | €104 |
| Cilinder MAL20 | €10 |
| Lineaire potmeter KTC-175 | €16–25 |
| 2× druksensor (roestvrij, G1/4) | €25–32 |
| Koppelingen, slang, dempers | ~€10 |
| Raspberry Pi Pico 2 | €7 |
| **Totaal** | **ca. €175–190** |

De ventielen zijn ongeveer 58% van het bedrag. De proef houdt alle sensoren en vier
ventielen, omdat hij moet uitwijzen wat de arm echt nodig heeft.

## Mogelijke besparingen voor de arm

Elke besparing hangt af van een meting in de proef:

| Besparing | Van → naar | Beslist door |
|---|---|---|
| Hoeksensor AS5600 op het gewricht in plaats van een lineaire potmeter | €16–25 → ~€3 | Nauwkeurigheid van de AS5600 op het gewricht (bij het scharnier) |
| Losse druksensorchips (bijv. XGZP6847A, 0–1000 kPa, 0,5–4,5 V) in plaats van roestvrije transducers | €25–32 → ~€6–10 | Of de druksensoren nodig zijn (T3/T6 met en zonder drukterugkoppeling) |
| 2 ventielen per cilinder in plaats van 4 | €104 → €52 | T8: is de vasthoudstand het waard? |
| VQ110-klonen (€7–13) in plaats van originelen | €104 → ~€40 | T0/T1 met een kloon naast een origineel |

Met alle besparingen samen: ongeveer €80–120 per DOF, plus de grotere cilinders voor
schouder en elleboog.

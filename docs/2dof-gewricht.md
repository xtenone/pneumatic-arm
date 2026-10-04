# 2-DOF-gewricht met twee cilinders

![Schets van de klant](schetsen/2dof-gewricht-klant-2026-10-04.jpg)

## Het principe

Een kruiskoppeling (cardan) in het midden draagt de arm. Aan weerszijden van het
midden zit een hefboom, en aan het eind van elke hefboom een cilinder.

- **Beide cilinders dezelfde kant op:** de arm kantelt op en neer (pitch).
- **Eén cilinder uit, de andere in:** de arm draait om de as die van de kijker af
  loopt in de onderste schetsen (roll).

Hetzelfde principe zit in de enkels en polsen van veel humanoïde robots: twee lineaire
actuatoren naast elkaar op een kruiskoppeling.

## Eigenschappen

- **Voor op en neer werken de cilinders samen:** samen leveren ze het koppel tegen de
  zwaartekracht. De zware as krijgt dus de kracht van twee cilinders.
- **Koppel:** pitch = (F1 + F2) · r, roll = (F1 − F2) · b. Daarbij is r de afstand
  van de pitch-as tot de aangrijppunten, en b de halve afstand tussen de twee
  aangrijppunten.
- **Draaien onder last:** de cilinders delen het werk. Bij maximale last voor op en
  neer blijft er minder over om te draaien.
- **Bewegingen zijn gekoppeld en niet-lineair:** de gewenste hoeken worden in software
  omgerekend naar twee cilinderlengtes (inverse kinematica).

## Wat in het ontwerp opgelost moet worden

1. **Middelste gewricht:** een kruiskoppeling, met de twee assen elkaar snijdend. Die
   draagt al het gewicht en alle zijkrachten van de arm en moet dus stevig zijn.
2. **Cilinderuiteinden:** de aangrijppunten bewegen in drie dimensies. Beide uiteinden
   van elke cilinder hebben dus een kogelgewricht of kruiskoppeling nodig. Gewone
   kogelkoppen (rod end bearings) halen maar ongeveer ±13–15° scheefstand. Bij grote
   hoeken lopen ze vast; dan zijn kogelkoppen voor grote hoeken of kleine
   kruiskoppelingen nodig.
3. **Hefboomwerking aan de randen:** het koppel is het grootst als cilinder en hefboom
   haaks op elkaar staan, en neemt af naarmate ze in één lijn komen. Het
   bewegingsbereik wordt zo gekozen dat ze binnen ongeveer ±30–40° van haaks blijven.
4. **Geen zijkracht op de stangen:** de kruiskoppeling vangt de zijkrachten op, niet
   de cilinders.

## Open vragen

- Waar komt dit gewricht in de arm: schouder, elleboog of pols?
- Is "draaien" bedoeld als draaien om de eigen as van de arm (zoals een pols die een
  sleutel omdraait), of als zijwaarts zwaaien (links-rechts)? De schets geeft het
  eerste. Voor zijwaarts zwaaien moet de tweede as van de kruiskoppeling anders staan.
- Gewenst bereik in graden voor op en neer en voor draaien.
- Afmetingen: lengte van de hefbomen, en waar de cilinders aan de onderkant vastzitten.

## Status

Schets ontvangen op 2026-10-04. Nog niet uitgewerkt of doorgerekend.

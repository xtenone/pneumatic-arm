# Doel

Stap 1 t/m 4 van [werkwijze-fysieke-projecten](../werkwijze-fysieke-projecten/CLAUDE.md),
voor dit project. Eerste versie, wordt aangevuld na de intake.

## 1. Doel-tekst

Een toegankelijke robotarm maken: met algemeen verkrijgbare onderdelen te bouwen, en
met terugkoppeling (feedback) aangestuurd door een programma of AI. Hij hoeft geen
industriële snelheid of precisie te halen: de helft van wat een mens met zijn arm kan,
is genoeg.

## 2. Aanpak-keuze

De gewrichten worden bewogen door cilinders of lineaire actuatoren, zoals spieren een
menselijke arm bewegen, in plaats van door motoren met tandwielkasten in het gewricht.
De eerste kandidaat is pneumatiek: perslucht geeft mee bij een botsing en de kracht is
te begrenzen met de druk.

Eerst wordt met een simpele proefopstelling bewezen dat een cilinder met terugkoppeling
te regelen is. Daarna komen er stap voor stap gewrichten bij, te beginnen met een
scharnier met twee vrijheidsgraden (2-DOF) dat door cilinders bewogen wordt.

## 3. Doel-keuze

Een arm die stenen oppakt en tot een muur stapelt.

## 4. Doelpresentatie

Ik wil met een zelfgebouwde, door cilinders bewogen arm stenen van ongeveer 15 kg
oppakken en er een muur mee bouwen.

## Eisen

- Last: ongeveer 15 kg per arm.
- Veiligheid: een fout mag geen levensgevaarlijke klap opleveren; kracht en snelheid
  moeten begrensd zijn.
- Onderdelen zijn gewoon te koop (webshops, AliExpress), geen speciale industriële
  motoren of op maat gemaakte aandrijvingen.

## Open vragen

- Reikwijdte en nauwkeurigheid van de arm: hoe ver moet hij reiken, en hoe precies moet
  een steen geplaatst worden?
- Budget voor de proefopstelling (wordt zo laag mogelijk gehouden).
- Verhouding tot [robotic-arm-sim](../robotic-arm-sim/): hetzelfde einddoel (muur
  bouwen), maar een apart project met een eigen arm.

## Status (bijgewerkt zodra dit verandert)

- **Proefopstelling 1 (één cilinder, 4 snelle ventielen met PWM)**: ontwerp in
  [docs/proefopstelling-1.md](docs/proefopstelling-1.md), nog niet besteld.
- **2-DOF-scharnier**: ontwerp bestaat bij de klant, nog niet ontvangen of besproken.

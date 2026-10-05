# pneumatic-arm

Een toegankelijke robotarm die werkt met cilinders, zoals spieren, en met
terugkoppeling wordt aangestuurd door een programma of AI. Te bouwen met gewone,
overal verkrijgbare onderdelen. Het einddoel is een arm die stenen van ongeveer 15 kg
oppakt en er een muur mee bouwt.

![Test 1](test1/out/sim/render_arm_horizontaal_schuin.png)

## Stand van zaken

| Stap | Stand |
|---|---|
| Doel en eisen | [doel.md](doel.md) |
| **Test 1 — arm met één vrijheidsgraad** | ontwerp, CAD, simulatie, firmware en handleiding klaar; onderdelen besteld, nog niet gebouwd — [test1/](test1/README.md) |
| 2-DOF-gewricht (schouder, elleboog) | eerste analyse — [docs/2dof-gewricht.md](docs/2dof-gewricht.md) |
| Plan: wat gedaan is en wat er nog moet | [docs/plan.md](docs/plan.md) |
| Kosten per vrijheidsgraad | [docs/kosten-per-dof.md](docs/kosten-per-dof.md) |

## Zelf bouwen

Begin bij [test1/README.md](test1/README.md) en de
[handleiding](test1/docs/handleiding.md). Alle maten staan in `test1/params.py`;
`python test1/build.py` maakt daaruit opnieuw de CAD, simulatie, firmware-instellingen,
tekeningen en stuklijst.

## Meedoen

Vragen, metingen, foto's van je eigen opstelling en verbeteringen zijn welkom via issues
en pull requests. Meetresultaten van de proeven T0–T7 zijn extra waardevol: daarmee
wordt het simulatiemodel beter.

De documentatie is in het Nederlands; codecommentaar ook.

## Licentie

Copyleft: hardware onder **CERN-OHL-S-2.0**, software onder **GPL-3.0-or-later**.
Zie [LICENSE](LICENSE).

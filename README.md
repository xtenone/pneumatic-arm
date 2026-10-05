# pneumatic-arm

An accessible robot arm that works with cylinders, like muscles, and is controlled with
feedback by a program or AI. Built from ordinary, widely available parts. The end goal
is an arm that picks up blocks of about 15 kg and builds a wall with them.

![Test 1](test1/out/sim/render_arm_horizontal_oblique.png)

## Status

| Step | Status |
|---|---|
| Goal and requirements | [goal.md](goal.md) |
| **Test 1 — arm with one degree of freedom** | design, CAD, simulation, firmware and manual done; parts ordered, not built yet — [test1/](test1/README.md) |
| 2-DOF joint (shoulder, elbow) | first analysis — [docs/2dof-joint.md](docs/2dof-joint.md) |
| Plan: what is done and what is left | [docs/plan.md](docs/plan.md) |
| Cost per degree of freedom | [docs/cost-per-dof.md](docs/cost-per-dof.md) |

## Build it yourself

Start at [test1/README.md](test1/README.md) and the
[manual](test1/docs/manual.md). All dimensions are in `test1/params.py`;
`python test1/build.py` regenerates the CAD, simulation, firmware settings, drawings and
bill of materials from it.

## Contributing

Questions, measurements, photos of your own build and improvements are welcome through
issues and pull requests. Measurements from tests T0–T7 are especially valuable: they
make the simulation model better.

## License

Copyleft: hardware under **CERN-OHL-S-2.0**, software under **GPL-3.0-or-later**.
See [LICENSE](LICENSE).

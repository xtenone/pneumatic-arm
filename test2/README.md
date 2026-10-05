# Test 2 — 2-DOF joint (concept)

First concept of the joint from [docs/2dof-joint.md](../docs/2dof-joint.md), built on
test 1: the hinge becomes a universal joint (pitch + roll) and a second cylinder is added
next to the first. Same Ø20 × 150 cylinders, same upright.

![Concept](out/render_neutral_oblique.png)

- **Both cylinders out:** the arm pitches up. **One out, one in:** the arm rolls about
  its own axis.
- The cylinders attach to the ends of a crossbar under the arm (150 mm from the joint,
  ±70 mm to the sides) and to brackets on the outside of the cheeks, with ball joints at
  both ends.
- Reachable range (cylinder stroke only, ball-joint limits not yet included): pitch
  −15° to +40°, roll up to ±45° around horizontal.

Files: `t2params.py` (dimensions), `cad/model.py` (CadQuery), `render.py` (renders and
`out/test2_concept.step`).

Status: concept for discussion, not yet worked out or simulated.

"""Render the test 2 concept in a few poses (MuJoCo, static scene) and export STEP.

    python render.py                 # concept B (bar + sleeve)
    python render.py --cross-block   # variant with a cross block on a fixed bar
Output: out/[cross_block/]render_<pose>_<camera>.png and a STEP file
"""
import os
import sys
import tempfile

os.environ.setdefault("MUJOCO_GL", "egl")
import cadquery as cq  # noqa: E402
import mujoco  # noqa: E402
from PIL import Image  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "cad"))
import model  # noqa: E402
import cross_block  # noqa: E402

OUT = os.path.join(HERE, "out")
POSES = {"neutral": (0.0, 0.0), "pitch_down": (-60.0, 0.0), "pitch_up": (75.0, 0.0),
         "roll": (0.0, 65.0), "pitch_up_roll": (45.0, 65.0)}
CAMERAS = {
    "oblique": '<camera name="oblique" pos="1.25 -1.15 0.95" xyaxes="0.67 0.74 0 -0.32 0.29 0.9"/>',
    "front": '<camera name="front" pos="1.25 0 0.42" xyaxes="0 1 0 -0.1 0 1"/>',
    "side": '<camera name="side" pos="0.15 -1.45 0.4" xyaxes="1 0 0 0 0 1"/>',
    "close": '<camera name="close" pos="0.55 -0.35 0.62" xyaxes="0.54 0.84 0 -0.35 0.22 0.91"/>',
    "bottom": '<camera name="bottom" pos="0.2 -0.24 0.16" xyaxes="0.773 0.634 0 -0.254 0.309 0.917"/>',
}


def scene_xml(items, meshdir):
    assets, geoms = [], []
    for name, shape, rgba in items:
        path = os.path.join(meshdir, f"{name}.stl")
        cq.exporters.export(cq.Workplane().add(shape), path, tolerance=0.2, angularTolerance=0.2)
        assets.append(f'<mesh name="{name}" file="{path}" scale="0.001 0.001 0.001"/>')
        geoms.append(f'<geom type="mesh" mesh="{name}" rgba="{" ".join(map(str, rgba))}"/>')
    return f"""<mujoco><visual><global offwidth="1280" offheight="960"/><quality shadowsize="4096"/></visual>
<asset>{''.join(assets)}
<texture type="skybox" builtin="gradient" rgb1="0.97 0.97 1" rgb2="0.72 0.76 0.84" width="512" height="512"/>
<texture name="grid" type="2d" builtin="checker" rgb1="0.92 0.92 0.92" rgb2="0.85 0.85 0.85" width="512" height="512"/>
<material name="floor" texture="grid" texrepeat="8 8"/></asset>
<worldbody><light pos="0.6 -0.8 1.4" dir="-0.4 0.5 -1" diffuse="0.8 0.8 0.8"/>
<light pos="-0.5 0.6 1.2" dir="0.3 -0.4 -1" diffuse="0.4 0.4 0.4"/>
<geom type="plane" size="2 2 0.01" pos="0 0 -0.019" material="floor"/>
{''.join(CAMERAS.values())}{''.join(geoms)}</worldbody></mujoco>"""


CROSS_POSES = {"neutral": (0.0, 0.0), "pitch_down": (-45.0, 0.0), "pitch_up": (45.0, 0.0),
               "roll": (0.0, 55.0), "pitch_up_roll": (30.0, 65.0)}


def main():
    cross = "--cross-block" in sys.argv
    out = os.path.join(OUT, "cross_block") if cross else OUT
    os.makedirs(out, exist_ok=True)
    for pose, (pitch, roll) in (CROSS_POSES if cross else POSES).items():
        items, lengths = (cross_block if cross else model).pose(pitch, roll)
        with tempfile.TemporaryDirectory() as tmp:
            mdl = mujoco.MjModel.from_xml_string(scene_xml(items, tmp))
        d = mujoco.MjData(mdl)
        mujoco.mj_forward(mdl, d)
        r = mujoco.Renderer(mdl, 960, 1280)
        for cam in (c for c in CAMERAS if cross or c != "bottom"):   # bottom joint: variant only
            r.update_scene(d, camera=cam)
            Image.fromarray(r.render()).save(os.path.join(out, f"render_{pose}_{cam}.png"))
        r.close()
        print(pose, f"pitch {pitch}°, roll {roll}°, cylinders {[round(L) for L in lengths]} mm")
        if pose == "neutral":
            asm = cq.Assembly(name="test2_concept")
            for name, shape, rgba in items:
                asm.add(cq.Workplane().add(shape), name=name, color=cq.Color(*rgba))
            asm.export(os.path.join(out, "test2_concept.step"))


if __name__ == "__main__":
    main()

"""Render of the elbow joint on its own (CadQuery parts from elbow_cad.py, MuJoCo scene).

    python full-arm/render_elbow.py [layout] [bend]     # default: triceps_down, 60°
Output: out/render_elbow_<layout>_<view>.png

Shows the end of the upper arm, the elbow fork and yoke, the forearm with the lever and
cross blocks, and the two elbow cylinders with rod forks and rear U-joints, held in the
arm's attitude (upper arm hanging 50° down for the elbow-down layouts).
"""
import math
import os
import sys
import tempfile

os.environ.setdefault("MUJOCO_GL", "egl")
import cadquery as cq  # noqa: E402
import mujoco  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import elbow as K  # noqa: E402
import elbow_cad as C  # noqa: E402

OUT = os.path.join(HERE, "out")
COLOURS = {"cyl_body": (0.80, 0.82, 0.85, 1), "cyl_rod": (0.45, 0.46, 0.50, 1), "cyl_fork": (0.3, 0.3, 0.33, 1),
           "low_block": (0.2, 0.4, 0.75, 1), "fore_block": (0.2, 0.4, 0.75, 1), "yoke": (0.75, 0.25, 0.2, 1),
           "fork": (0.35, 0.37, 0.40, 1), "post": (0.6, 0.62, 0.66, 1)}
ALU = (0.78, 0.80, 0.83, 1)


def colour(name):
    return next((c for k, c in COLOURS.items() if name.startswith(k)), ALU)


def camera(name, pos, target):
    pos, target = np.array(pos, float), np.array(target, float)
    f = (target - pos) / np.linalg.norm(target - pos)
    x = np.cross(f, [0, 0, 1])
    x /= np.linalg.norm(x)
    y = np.cross(x, f)
    return f'<camera name="{name}" pos="{" ".join(f"{v:.3f}" for v in pos)}" xyaxes="{" ".join(f"{v:.3f}" for v in [*x, *y])}"/>'


def main():
    layout = sys.argv[1] if len(sys.argv) > 1 else "triceps_down"
    bend = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0
    K.set_layout(layout)
    C.CYL = C.CYLS.get(layout, dict(bore=50, body_d=60.0, rod_d=20.0, stroke=100.0, dead=105.0))
    pitch = bend if K.DOWN else -bend
    parts = {k: v for k, v in C.upper_parts().items() if not k.startswith("shoulder")}
    parts.update(C.forearm_parts(pitch, 0.0))
    cyl, lengths = C.cylinders(pitch, 0.0)
    parts.update(cyl)
    # place the upper-arm frame in the world: elbow at the origin, upper arm 50° down (or up)
    tilt = math.radians(-50 if K.DOWN else 25)
    c, s = math.cos(tilt), math.sin(tilt)
    m = cq.Matrix([[c, 0, -s, 0], [0, 1, 0, 0], [s, 0, c, 0]])
    shift = cq.Vector(*(-np.array([c * C.L1, 0, s * C.L1])))
    with tempfile.TemporaryDirectory() as tmp:
        assets, geoms = [], []
        for name, shape in parts.items():
            p = os.path.join(tmp, f"{name}.stl")
            cq.exporters.export(cq.Workplane().add(shape.transformGeometry(m).translate(shift)), p, tolerance=0.05, angularTolerance=0.1)
            assets.append(f'<mesh name="{name}" file="{p}" scale="0.001 0.001 0.001"/>')
            geoms.append(f'<geom type="mesh" mesh="{name}" rgba="{" ".join(map(str, colour(name)))}"/>')
        cams = {"oblique": camera("oblique", (0.40, -0.80, 0.42), (-0.06, 0.0, 0.07)),
                "side": camera("side", (-0.04, -0.95, 0.09), (-0.04, 0.0, 0.07))}
        xml = f"""<mujoco><visual><global offwidth="1280" offheight="960"/><quality shadowsize="4096"/>
<headlight ambient="0.4 0.4 0.4"/></visual>
<asset>{''.join(assets)}<texture type="skybox" builtin="gradient" rgb1="0.97 0.97 1" rgb2="0.72 0.76 0.84" width="512" height="512"/></asset>
<worldbody><light pos="0.6 -0.8 1.2" dir="-0.4 0.6 -1" diffuse="0.7 0.7 0.7"/>
{''.join(cams.values())}{''.join(geoms)}</worldbody></mujoco>"""
        mdl = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(mdl)
    mujoco.mj_forward(mdl, d)
    os.makedirs(OUT, exist_ok=True)
    r = mujoco.Renderer(mdl, 960, 1280)
    for cam in cams:
        r.update_scene(d, camera=cam)
        path = os.path.join(OUT, f"render_elbow_{layout}_{cam}.png")
        Image.fromarray(r.render()).save(path)
        print(path)
    r.close()
    print(f"{layout}, bend {bend:.0f}°: cylinders {[round(x) for x in lengths]} mm pin to pin")


if __name__ == "__main__":
    main()

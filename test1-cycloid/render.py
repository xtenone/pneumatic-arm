"""Renders of the printed cycloidal drive (MuJoCo, static scenes) and a short video.

    python render.py            # out/render_<view>.png
    python render.py --video    # also out/video_cycloid.mp4 (input turning, housing see-through)
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
sys.path.insert(0, os.path.join(HERE, "cad"))
import cycloid as C  # noqa: E402

OUT = os.path.join(HERE, "out")


def camera(name, pos, target):
    pos, target = np.array(pos), np.array(target)
    f = target - pos
    f /= np.linalg.norm(f)
    x = np.cross(f, [0, 0, 1])
    x /= np.linalg.norm(x)
    y = np.cross(x, f)
    return (f'<camera name="{name}" pos="{" ".join(f"{v:.3f}" for v in pos)}" '
            f'xyaxes="{" ".join(f"{v:.3f}" for v in [*x, *y])}"/>')


CAMERAS = {
    "oblique": camera("oblique", (0.24, -0.26, 0.17), (0.0, 0.0, -0.01)),
    "top": camera("top", (0.03, -0.07, 0.17), (0.0, 0.0, 0.035)),
    "section": camera("section", (0.13, -0.19, 0.10), (0.0, 0.0, 0.02)),
    "exploded": camera("exploded", (0.34, -0.37, 0.18), (0.0, 0.0, 0.05)),
}
EXPLODE = [("motor", -90), ("standoff", -60), ("coupling", -50), ("bearing_6808_rear", -22),
           ("housing_pin", 18), ("bearing_608_rear", 22), ("carrier_rear", 36), ("output_pin", 55),
           ("shaft", 60), ("cam", 75), ("bearing_6804_0", 92), ("disc_0", 92), ("bearing_6804_1", 112),
           ("disc_1", 112), ("bearing_608_front", 132), ("carrier_front", 140), ("cover", 165),
           ("bearing_6808_front", 185), ("housing", 0)]


def scene_xml(items, meshdir, floor_z):
    assets, geoms = [], []
    for name, shape, rgba in items:
        path = os.path.join(meshdir, f"{name}.stl")
        cq.exporters.export(cq.Workplane().add(shape), path, tolerance=0.05, angularTolerance=0.1)
        assets.append(f'<mesh name="{name}" file="{path}" scale="0.001 0.001 0.001"/>')
        geoms.append(f'<geom type="mesh" mesh="{name}" rgba="{" ".join(map(str, rgba))}"/>')
    return f"""<mujoco><visual><global offwidth="1280" offheight="960"/><quality shadowsize="4096"/></visual>
<asset>{''.join(assets)}
<texture type="skybox" builtin="gradient" rgb1="0.97 0.97 1" rgb2="0.72 0.76 0.84" width="512" height="512"/>
<texture name="grid" type="2d" builtin="checker" rgb1="0.92 0.92 0.92" rgb2="0.85 0.85 0.85" width="512" height="512"/>
<material name="floor" texture="grid" texrepeat="16 16"/></asset>
<worldbody><light pos="0.3 -0.4 0.8" dir="-0.3 0.4 -1" diffuse="0.8 0.8 0.8"/>
<light pos="-0.3 0.3 0.6" dir="0.3 -0.3 -1" diffuse="0.4 0.4 0.4"/>
<geom type="plane" size="1 1 0.01" pos="0 0 {floor_z}" material="floor"/>
{''.join(CAMERAS.values())}{''.join(geoms)}</worldbody></mujoco>"""


def render(items, path, cam, floor_z=-0.135):
    with tempfile.TemporaryDirectory() as tmp:
        mdl = mujoco.MjModel.from_xml_string(scene_xml(items, tmp, floor_z))
    d = mujoco.MjData(mdl)
    mujoco.mj_forward(mdl, d)
    r = mujoco.Renderer(mdl, 960, 1280)
    r.update_scene(d, camera=cam)
    Image.fromarray(r.render()).save(path)
    r.close()
    print(path)


def see_through(items, alpha=0.25):
    return [(n, s, (*rgba[:3], alpha) if n in ("housing", "cover") else rgba) for n, s, rgba in items]


def without(items, *prefixes):
    return [it for it in items if not it[0].startswith(prefixes)]


def section(items):
    """Cut everything away at y < 0."""
    box = cq.Workplane("XY").box(400, 200, 600).translate((0, -100, 0)).val()
    out = []
    for n, s, rgba in items:
        c = s.cut(box)
        if c.Volume() > 1:
            out.append((n, c, rgba))
    return out


def exploded(items):
    out = []
    for n, s, rgba in items:
        dz = next(v for k, v in EXPLODE if n.startswith(k))
        out.append((n, s.translate(cq.Vector(0, 0, dz)), rgba))
    return out


def video(path, turns=3, seconds_per_turn=2.0, fps=30):
    import imageio.v2 as imageio
    shapes = C.shapes()
    first = C.placements(0.0)
    with tempfile.TemporaryDirectory() as tmp:
        assets, world, moving = [], [], []
        for key, shape in shapes.items():
            p = os.path.join(tmp, f"{key}.stl")
            cq.exporters.export(cq.Workplane().add(shape), p, tolerance=0.05, angularTolerance=0.1)
            assets.append(f'<mesh name="{key}" file="{p}" scale="0.001 0.001 0.001"/>')
        for name, key, R, t, rgba in first:
            if name in ("cover", "carrier_front", "bearing_608_front", "bearing_6808_front"):
                continue                                    # open from the top
            if name == "housing":
                rgba = (*rgba[:3], 0.25)
            g = f'<geom type="mesh" mesh="{key}" rgba="{" ".join(map(str, rgba))}" contype="0" conaffinity="0"/>'
            moving.append(f'<body name="{name}" mocap="true">{g}</body>')
        xml = scene_xml([], tmp, -0.135).replace("<asset>", "<asset>" + "".join(assets)).replace(
            "</worldbody>", "".join(world + moving) + "</worldbody>")
        mdl = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(mdl)
    r = mujoco.Renderer(mdl, 960, 1280)
    w = imageio.get_writer(path, fps=fps, codec="libx264", quality=8, macro_block_size=8)
    q = np.zeros(4)
    n = int(turns * seconds_per_turn * fps)
    for i in range(n):
        phi = 2 * math.pi * turns * i / n
        for name, _, R, t, _ in C.placements(phi):
            bid = mujoco.mj_name2id(mdl, mujoco.mjtObj.mjOBJ_BODY, name)
            if bid < 0:
                continue
            m = mdl.body_mocapid[bid]
            d.mocap_pos[m] = np.asarray(t) / 1000.0
            mujoco.mju_mat2Quat(q, np.ascontiguousarray(R, dtype=float).flatten())
            d.mocap_quat[m] = q
        mujoco.mj_forward(mdl, d)
        r.update_scene(d, camera="top")
        w.append_data(r.render())
    w.close()
    r.close()
    print(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    items = C.pose(0.0)
    render(items, os.path.join(OUT, "render_assembled.png"), "oblique")
    render(without(see_through(items), "cover", "bearing_6808_front", "carrier_front", "bearing_608_front"),
           os.path.join(OUT, "render_inside.png"), "top")
    render(section(items), os.path.join(OUT, "render_section.png"), "section")
    render(exploded(items), os.path.join(OUT, "render_exploded.png"), "exploded", floor_z=-0.23)
    if "--video" in sys.argv:
        video(os.path.join(OUT, "video_cycloid.mp4"))


if __name__ == "__main__":
    main()

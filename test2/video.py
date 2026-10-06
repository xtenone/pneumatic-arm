"""Animate the cross block variant through its range (MuJoCo, kinematic only) and write MP4s.

    python video.py            # out/cross_block/video_<camera>.mp4
    python video.py --fast     # half the frame rate, for a quick look

The parts are meshed once; every frame only moves them (mocap bodies), using the same
placement as the renders (cad/cross_block.placements). No physics, no pressures: this shows
the motion, not the control.
"""
import math
import os
import sys
import tempfile

os.environ.setdefault("MUJOCO_GL", "egl")
import cadquery as cq  # noqa: E402
import imageio.v2 as imageio  # noqa: E402
import mujoco  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "cad"))
import cross_block as X  # noqa: E402
from render import CAMERAS  # noqa: E402

OUT = os.path.join(HERE, "out", "cross_block")
VIDEO_CAMERAS = ("oblique", "close", "bottom")
# (pitch, roll) key poses, all clash-free; the arm moves between them in SEGMENT seconds
KEYS = [(0, 0), (-45, 0), (45, 0), (0, 0), (0, 55), (0, -55), (0, 0),
        (30, 0), (30, 65), (30, -65), (30, 0), (-45, 0), (-45, 65), (-45, -65), (0, 0)]
SEGMENT = 1.6
PAUSE = 0.3


def trajectory(fps):
    """(pitch, roll) per frame: smooth (cosine) moves between the key poses, short pauses."""
    frames = []
    for (p0, r0), (p1, r1) in zip(KEYS, KEYS[1:]):
        n = int(SEGMENT * fps)
        for k in range(n):
            s = 0.5 - 0.5 * math.cos(math.pi * k / n)
            frames.append((p0 + s * (p1 - p0), r0 + s * (r1 - r0)))
        frames += [(p1, r1)] * int(PAUSE * fps)
    return frames


def scene_xml(meshdir):
    """Static parts in the world, moving parts on mocap bodies."""
    shapes = X.shapes()
    out, _ = X.placements(0.0, 0.0)
    assets, world, moving = [], [], []
    for key, shape in shapes.items():
        path = os.path.join(meshdir, f"{key}.stl")
        cq.exporters.export(cq.Workplane().add(shape), path, tolerance=0.1, angularTolerance=0.15)
        assets.append(f'<mesh name="{key}" file="{path}" scale="0.001 0.001 0.001"/>')
    for name, key, R, t, rgba in out:
        geom = f'<geom type="mesh" mesh="{key}" rgba="{" ".join(map(str, rgba))}" contype="0" conaffinity="0"/>'
        if np.allclose(R, np.eye(3)) and np.allclose(t, 0) and not name.startswith(("arm", "yoke")):
            world.append(geom)
        else:
            moving.append(f'<body name="{name}" mocap="true">{geom}</body>')
    return f"""<mujoco><visual><global offwidth="1280" offheight="960"/><quality shadowsize="4096"/></visual>
<asset>{''.join(assets)}
<texture type="skybox" builtin="gradient" rgb1="0.97 0.97 1" rgb2="0.72 0.76 0.84" width="512" height="512"/>
<texture name="grid" type="2d" builtin="checker" rgb1="0.92 0.92 0.92" rgb2="0.85 0.85 0.85" width="512" height="512"/>
<material name="floor" texture="grid" texrepeat="8 8"/></asset>
<worldbody><light pos="0.6 -0.8 1.4" dir="-0.4 0.5 -1" diffuse="0.8 0.8 0.8"/>
<light pos="-0.5 0.6 1.2" dir="0.3 -0.4 -1" diffuse="0.4 0.4 0.4"/>
<geom type="plane" size="2 2 0.01" pos="0 0 -0.019" material="floor"/>
{''.join(CAMERAS.values())}{''.join(world)}{''.join(moving)}</worldbody></mujoco>"""


def set_pose(mdl, d, pitch, roll):
    out, lengths = X.placements(pitch, roll)
    q = np.zeros(4)
    for name, _, R, t, _ in out:
        bid = mujoco.mj_name2id(mdl, mujoco.mjtObj.mjOBJ_BODY, name)
        if bid < 0:
            continue
        m = mdl.body_mocapid[bid]
        d.mocap_pos[m] = np.asarray(t) / 1000.0
        mujoco.mju_mat2Quat(q, np.ascontiguousarray(R, dtype=float).flatten())
        d.mocap_quat[m] = q
    mujoco.mj_forward(mdl, d)
    return lengths


def main():
    fps = 15 if "--fast" in sys.argv else 30
    os.makedirs(OUT, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        mdl = mujoco.MjModel.from_xml_string(scene_xml(tmp))
    d = mujoco.MjData(mdl)
    frames = trajectory(fps)
    r = mujoco.Renderer(mdl, 960, 1280)
    writers = {cam: imageio.get_writer(os.path.join(OUT, f"video_{cam}.mp4"), fps=fps,
                                       codec="libx264", quality=8, macro_block_size=8)
               for cam in VIDEO_CAMERAS}
    for i, (pitch, roll) in enumerate(frames):
        set_pose(mdl, d, pitch, roll)
        for cam, w in writers.items():
            r.update_scene(d, camera=cam)
            w.append_data(r.render())
        if i % fps == 0:
            print(f"{i / fps:5.1f} s  pitch {pitch:6.1f}°  roll {roll:6.1f}°")
    for w in writers.values():
        w.close()
    r.close()
    print(f"{len(frames)} frames, {len(frames) / fps:.1f} s → {OUT}/video_*.mp4")


if __name__ == "__main__":
    main()

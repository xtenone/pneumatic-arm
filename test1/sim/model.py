"""MuJoCo model of test 1, generated from params.py and the CAD meshes.

Closed chain: arm (hinge) — cylinder (rear hinge) — rod (slide) — attached to the
arm with an equality connect at the clevis pin. Contacts are off; the pneumatic
force acts as an actuator on the slide.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "cad"))
import params as P  # noqa: E402

MESH_DIR = os.path.join(ROOT, "out", "meshes")


def m(x):
    return x / 1000.0


def quat_about_neg_y(deg):
    h = math.radians(deg) / 2
    return f"{math.cos(h):.8f} 0 {-math.sin(h):.8f} 0"


def build_xml(tip_mass=P.TIP_MASS, theta0=0.0, rigid_load=False):
    """rigid_load: the bottle strapped under the arm end (T8) instead of hanging on the hook."""
    from parts import pose
    p = pose(theta0)
    arm_mass = P.ARM["length"] * P.ARM["height"] * P.ARM["thickness"] * P.ALU_DENSITY
    arm_com = P.ARM["length"] / 2 - P.ARM_BEHIND
    hx, hz = P.HINGE
    rx, rz = P.REAR_PIVOT
    ext0 = p["ext"]
    return f"""
<mujoco model="test1_arm_1dof">
  <compiler angle="degree" meshdir="{MESH_DIR}"/>
  <option timestep="0.0005" integrator="implicitfast" gravity="0 0 -9.81">
    <flag contact="disable"/>
  </option>
  <visual><global offwidth="1280" offheight="960"/><quality shadowsize="4096"/></visual>
  <asset>
    <mesh name="upright" file="upright.stl" scale="0.001 0.001 0.001"/>
    <mesh name="arm" file="arm.stl" scale="0.001 0.001 0.001"/>
    <mesh name="cylinder" file="cylinder.stl" scale="0.001 0.001 0.001"/>
    <mesh name="potentiometer" file="potentiometer.stl" scale="0.001 0.001 0.001"/>
    <mesh name="rod" file="rod.stl" scale="0.001 0.001 0.001"/>
    <mesh name="bottle" file="bottle.stl" scale="0.001 0.001 0.001"/>
    <material name="wood" rgba="0.82 0.68 0.47 1"/>
    <material name="alu" rgba="0.75 0.77 0.80 1"/>
    <material name="steel" rgba="0.45 0.45 0.48 1"/>
    <material name="blue" rgba="0.15 0.35 0.75 1"/>
    <material name="water" rgba="0.6 0.8 0.95 0.7"/>
    <texture name="grid" type="2d" builtin="checker" rgb1="0.92 0.92 0.92" rgb2="0.85 0.85 0.85" width="512" height="512"/>
    <material name="floor" texture="grid" texrepeat="8 8"/>
    <texture type="skybox" builtin="gradient" rgb1="0.97 0.97 1" rgb2="0.72 0.76 0.84" width="512" height="512"/>
  </asset>
  <worldbody>
    <light pos="0.6 0.8 1.4" dir="-0.4 -0.5 -1" diffuse="0.8 0.8 0.8"/>
    <light pos="-0.5 -0.6 1.2" dir="0.3 0.4 -1" diffuse="0.4 0.4 0.4"/>
    <geom type="plane" size="2 2 0.01" pos="0 0 {m(-P.BASE['thickness']) - 0.75}" material="floor" contype="0" conaffinity="0"/>
    <geom name="table" type="box" size="0.45 0.5 0.015" pos="{m(P.BASE_X[1] + 10) - 0.45} 0 {m(-P.BASE['thickness']) - 0.0155}" rgba="0.55 0.42 0.3 1" contype="0" conaffinity="0"/>
    <geom type="box" size="0.02 0.02 0.36" pos="{m(P.BASE_X[1] + 10) - 0.04} 0.46 {m(-P.BASE['thickness']) - 0.39}" rgba="0.4 0.3 0.2 1" contype="0" conaffinity="0"/>
    <geom type="box" size="0.02 0.02 0.36" pos="{m(P.BASE_X[1] + 10) - 0.04} -0.46 {m(-P.BASE['thickness']) - 0.39}" rgba="0.4 0.3 0.2 1" contype="0" conaffinity="0"/>
    <geom type="mesh" mesh="upright" material="wood" contype="0" conaffinity="0"/>
    <camera name="side" pos="{m(150)} -1.25 {m(220)}" xyaxes="1 0 0 0 0 1"/>
    <camera name="oblique" pos="1.1 -1.05 0.75" xyaxes="0.69 0.72 0 -0.3 0.29 0.91"/>

    <body name="arm" pos="{m(hx)} 0 {m(hz)}" quat="{quat_about_neg_y(theta0)}">
      <joint name="arm" type="hinge" axis="0 -1 0" damping="0.02" range="{P.THETA_MIN - theta0 - 2} {P.THETA_MAX - theta0 + 2}"/>
      <inertial pos="{m(arm_com)} 0 0" mass="{arm_mass:.4f}" diaginertia="1e-5 {arm_mass * m(P.ARM['length'])**2 / 12:.6f} {arm_mass * m(P.ARM['length'])**2 / 12:.6f}"/>
      <geom type="mesh" mesh="arm" material="alu" contype="0" conaffinity="0" mass="0"/>
      <site name="attach" pos="{m(P.ARM_ATTACH)} 0 0" size="0.004"/>
      <body name="load" pos="{m(P.ARM_TIP)} 0 0">
        {'' if rigid_load else '<joint name="load" type="hinge" axis="0 -1 0" damping="0.05"/>'}
        <inertial pos="0 0 {-0.04 if rigid_load else -0.15}" mass="{tip_mass:.3f}" diaginertia="0.002 0.002 0.001"/>
        <geom type="capsule" fromto="0 0 0 0 0 -0.06" size="0.002" material="steel" contype="0" conaffinity="0" mass="0"/>
        <geom type="mesh" mesh="bottle" pos="0 0 -0.06" material="water" contype="0" conaffinity="0" mass="0"/>
      </body>
    </body>

    <body name="cylinder" pos="{m(rx)} 0 {m(rz)}" quat="{quat_about_neg_y(p['phi'])}">
      <joint name="cyl_rear" type="hinge" axis="0 -1 0" damping="0.01"/>
      <inertial pos="0.12 0 0" mass="0.35" diaginertia="1e-4 2e-3 2e-3"/>
      <geom type="mesh" mesh="cylinder" material="alu" contype="0" conaffinity="0" mass="0"/>
      <geom type="mesh" mesh="potentiometer" material="blue" contype="0" conaffinity="0" mass="0"/>
      <body name="rod" pos="{m(ext0)} 0 0">
        <joint name="stroke" type="slide" axis="1 0 0" range="{m(-ext0)} {m(P.CYL['stroke'] - ext0)}"
               damping="{P.CYL['friction_viscous']}" frictionloss="{P.CYL['friction_coulomb']}" armature="0.05"/>
        <inertial pos="0.2 0 0" mass="0.12" diaginertia="1e-5 1e-4 1e-4"/>
        <geom type="mesh" mesh="rod" material="steel" contype="0" conaffinity="0" mass="0"/>
      </body>
    </body>
  </worldbody>
  <equality>
    <connect name="clevis" body1="rod" body2="arm" anchor="{m(P.PIN_TO_PIN_MIN)} 0 0" solref="0.002 1"/>
  </equality>
  <actuator>
    <general name="pneumatics" joint="stroke" gainprm="1" ctrllimited="false"/>
  </actuator>
  <sensor>
    <jointpos name="stroke" joint="stroke"/>
    <jointpos name="arm" joint="arm"/>
  </sensor>
</mujoco>
"""


def ext0(theta0=0.0):
    from parts import pose
    return pose(theta0)["ext"]


if __name__ == "__main__":
    import mujoco
    mdl = mujoco.MjModel.from_xml_string(build_xml())
    print("bodies", mdl.nbody, "joints", mdl.njnt, "nq", mdl.nq)

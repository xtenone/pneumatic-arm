"""MuJoCo-model van test 1, gegenereerd uit params.py en de CAD-meshes.

Gesloten keten: arm (scharnier) — cilinder (scharnier achter) — stang (schuif) —
vastgemaakt aan de arm met een equality-connect op de pen van de vorkkop.
Contacten staan uit; de pneumatische kracht komt als actuator op de schuif.
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


def build_xml(tip_mass=P.TIP_MASS, theta0=0.0):
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
    <mesh name="staander" file="staander.stl" scale="0.001 0.001 0.001"/>
    <mesh name="arm" file="arm.stl" scale="0.001 0.001 0.001"/>
    <mesh name="cilinder" file="cilinder.stl" scale="0.001 0.001 0.001"/>
    <mesh name="potmeter" file="potmeter.stl" scale="0.001 0.001 0.001"/>
    <mesh name="stang" file="stang.stl" scale="0.001 0.001 0.001"/>
    <mesh name="fles" file="fles.stl" scale="0.001 0.001 0.001"/>
    <material name="hout" rgba="0.82 0.68 0.47 1"/>
    <material name="alu" rgba="0.75 0.77 0.80 1"/>
    <material name="staal" rgba="0.45 0.45 0.48 1"/>
    <material name="blauw" rgba="0.15 0.35 0.75 1"/>
    <material name="water" rgba="0.6 0.8 0.95 0.7"/>
    <texture name="grid" type="2d" builtin="checker" rgb1="0.92 0.92 0.92" rgb2="0.85 0.85 0.85" width="512" height="512"/>
    <material name="vloer" texture="grid" texrepeat="8 8"/>
    <texture type="skybox" builtin="gradient" rgb1="0.97 0.97 1" rgb2="0.72 0.76 0.84" width="512" height="512"/>
  </asset>
  <worldbody>
    <light pos="0.6 0.8 1.4" dir="-0.4 -0.5 -1" diffuse="0.8 0.8 0.8"/>
    <light pos="-0.5 -0.6 1.2" dir="0.3 0.4 -1" diffuse="0.4 0.4 0.4"/>
    <geom type="plane" size="2 2 0.01" pos="0 0 {m(-P.BASE['thickness']) - 0.75}" material="vloer" contype="0" conaffinity="0"/>
    <geom name="tafel" type="box" size="0.45 0.5 0.015" pos="{m(P.BASE_X[1] + 10) - 0.45} 0 {m(-P.BASE['thickness']) - 0.0155}" rgba="0.55 0.42 0.3 1" contype="0" conaffinity="0"/>
    <geom type="box" size="0.02 0.02 0.36" pos="{m(P.BASE_X[1] + 10) - 0.04} 0.46 {m(-P.BASE['thickness']) - 0.39}" rgba="0.4 0.3 0.2 1" contype="0" conaffinity="0"/>
    <geom type="box" size="0.02 0.02 0.36" pos="{m(P.BASE_X[1] + 10) - 0.04} -0.46 {m(-P.BASE['thickness']) - 0.39}" rgba="0.4 0.3 0.2 1" contype="0" conaffinity="0"/>
    <geom type="mesh" mesh="staander" material="hout" contype="0" conaffinity="0"/>
    <camera name="zij" pos="{m(150)} -1.25 {m(220)}" xyaxes="1 0 0 0 0 1"/>
    <camera name="schuin" pos="1.1 -1.05 0.75" xyaxes="0.69 0.72 0 -0.3 0.29 0.91"/>

    <body name="arm" pos="{m(hx)} 0 {m(hz)}" quat="{quat_about_neg_y(theta0)}">
      <joint name="arm" type="hinge" axis="0 -1 0" damping="0.02" range="{P.THETA_MIN - theta0 - 2} {P.THETA_MAX - theta0 + 2}"/>
      <inertial pos="{m(arm_com)} 0 0" mass="{arm_mass:.4f}" diaginertia="1e-5 {arm_mass * m(P.ARM['length'])**2 / 12:.6f} {arm_mass * m(P.ARM['length'])**2 / 12:.6f}"/>
      <geom type="mesh" mesh="arm" material="alu" contype="0" conaffinity="0" mass="0"/>
      <site name="aanhecht" pos="{m(P.ARM_ATTACH)} 0 0" size="0.004"/>
      <body name="last" pos="{m(P.ARM_TIP)} 0 0">
        <joint name="last" type="hinge" axis="0 -1 0" damping="0.05"/>
        <inertial pos="0 0 -0.15" mass="{tip_mass:.3f}" diaginertia="0.002 0.002 0.001"/>
        <geom type="capsule" fromto="0 0 0 0 0 -0.06" size="0.002" material="staal" contype="0" conaffinity="0" mass="0"/>
        <geom type="mesh" mesh="fles" pos="0 0 -0.06" material="water" contype="0" conaffinity="0" mass="0"/>
      </body>
    </body>

    <body name="cilinder" pos="{m(rx)} 0 {m(rz)}" quat="{quat_about_neg_y(p['phi'])}">
      <joint name="cil_achter" type="hinge" axis="0 -1 0" damping="0.01"/>
      <inertial pos="0.12 0 0" mass="0.35" diaginertia="1e-4 2e-3 2e-3"/>
      <geom type="mesh" mesh="cilinder" material="alu" contype="0" conaffinity="0" mass="0"/>
      <geom type="mesh" mesh="potmeter" material="blauw" contype="0" conaffinity="0" mass="0"/>
      <body name="stang" pos="{m(ext0)} 0 0">
        <joint name="slag" type="slide" axis="1 0 0" range="{m(-ext0)} {m(P.CYL['stroke'] - ext0)}"
               damping="{P.CYL['friction_viscous']}" frictionloss="{P.CYL['friction_coulomb']}" armature="0.05"/>
        <inertial pos="0.2 0 0" mass="0.12" diaginertia="1e-5 1e-4 1e-4"/>
        <geom type="mesh" mesh="stang" material="staal" contype="0" conaffinity="0" mass="0"/>
      </body>
    </body>
  </worldbody>
  <equality>
    <connect name="vorkkop" body1="stang" body2="arm" anchor="{m(P.PIN_TO_PIN_MIN)} 0 0" solref="0.002 1"/>
  </equality>
  <actuator>
    <general name="pneumatiek" joint="slag" gainprm="1" ctrllimited="false"/>
  </actuator>
  <sensor>
    <jointpos name="slag" joint="slag"/>
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

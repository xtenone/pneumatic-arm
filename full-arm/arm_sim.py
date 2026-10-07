"""Dynamic simulation of the light arm doing stage 1b of the small wall (docs/small-wall.md).

    python full-arm/arm_sim.py --tune            # step tests, prints the gain scale per joint
    python full-arm/arm_sim.py                   # stage 1b with 0.3, 1.5 and 3 kg blocks → out/sim/results.md
    python full-arm/arm_sim.py --video N         # video of case N of CASES (MP4 not kept in git)

The arm follows the fast plan of small_wall.py, but now as a physical arm: MuJoCo for the
links and the load, the pneumatics model of test 1 (ISO 6358 flow, chamber pressures,
VQ110U valves with their switching times) for the cylinders, and the test 1 controller
(firmware/control.py) for each cylinder joint. Before gripping or releasing, the program
waits until the gripper is within ±2 mm of its target and nearly still: that wait is
where a heavier load costs time.

- Shoulder and elbow pitch: two cylinders per joint with the same command (rolls at 0),
  modelled as one cylinder with twice the area, valve flow and dead volume; the force acts
  on the joint through the lever of the real pin geometry (cylinder mass in the links).
- Base yaw and wrist pitch: motors, modelled as stiff position servos; the wrist keeps the
  gripper vertical from the measured shoulder and elbow angles.
- Blocks: the load body at the gripper gets the block's mass when it is gripped.
"""
import math
import os
import sys

os.environ.setdefault("MUJOCO_GL", "egl")
import mujoco  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
for sub in ("test1", "test1/sim", "test1/firmware"):
    sys.path.insert(0, os.path.join(ROOT, sub))
import small_wall as W  # noqa: E402
import control  # noqa: E402
import gen_config  # noqa: E402
import params as P1  # noqa: E402
from pneumatics import mass_flow  # noqa: E402

C, K = W.C, W.K
OUT = os.path.join(HERE, "out", "sim")
DT = 0.0005
CTRL_EVERY = 4                                  # 500 Hz control loop
BAR = 1e5
P_ATM = P1.P_ATM * BAR

L1 = L2 = 0.5
M_UPPER, M_FORE, M_WRIST = 1.2, 0.5, 1.1         # kg; wrist = wrist motor + gripper rotation motor + gripper
GRASP = C.GRIP                                   # wrist → grasp centre
BLOCK_DROP = W.BLOCK[2] / 2 - W.GRIP_DEPTH       # grasp centre → block centre

CYLS = {  # per joint: bore, rod (mm), cylinders, shortest pin-to-pin, stroke (mm)
    "shoulder": dict(bore=32, rod=12, n=2, L_min=160.0, stroke=200.0),
    "elbow": dict(bore=25, rod=10, n=2, L_min=220.0, stroke=80.0),
}
ELBOW_32 = dict(bore=32, rod=12, n=2, L_min=220.0, stroke=80.0)   # for the 3 kg blocks
DEAD_CM3 = 3.0                                   # per chamber and cylinder: tube + fittings
FRICTION = (0.4, 2.0)                            # N per mm of bore: Coulomb, viscous (N·s/m), scaled from test 1 (Ø20: 8 N, 40 N·s/m)
TOL, V_STILL, WAIT_MAX = 0.003, 0.02, 3.0        # m, m/s, s: "in place" before gripping or releasing
ANGLE_NOISE = math.radians(0.05)                 # joint angle sensor (AS5600 class), 1 sigma
HOLD_TIP = 0.001                                 # m at the gripper: valves closed when this close (test 1 deadband scaled)
GAINS = {  # force gains per joint: kp N/mm, ki N/(mm·s), kd N/(mm/s) on the cylinder length (tuned with --tune)
    "shoulder": dict(kp=45.0, ki=337.5, kd=6.0),
    "elbow": dict(kp=100.0, ki=750.0, kd=5.0),
}
GAINS_3KG = {  # retuned for 3 kg with the Ø32 elbow (the program knows when it holds a heavy block)
    "shoulder": dict(kp=45.0, ki=337.5, kd=9.0),
    "elbow": dict(kp=70.0, ki=525.0, kd=8.0),
}
REACH = {"shoulder": 0.6, "elbow": 0.5}           # m, joint → gripper, for the deadbands


# --- cylinder geometry (m, rad) ------------------------------------------------------
def shoulder_L(p1):
    """Pin-to-pin length and dL/dp1 of the shoulder cylinders (hub 0.10 m on the upper arm)."""
    h = C.SH_HUB * np.array([math.cos(p1), math.sin(p1)])
    d = h - np.array(C.SH_LOW)
    L = float(np.linalg.norm(d))
    return L, float(d @ (C.SH_HUB * np.array([-math.sin(p1), math.cos(p1)]))) / L


def elbow_L(p2):
    """Pin-to-pin length and dL/dp2 of the elbow cylinders (rear pivot 0.229 m along the upper
    arm, lever 0.05 m behind the elbow)."""
    lever = np.array([L1 - C.ELBOW_LEVER * math.cos(p2), -C.ELBOW_LEVER * math.sin(p2)])
    d = lever - np.array([C.ELBOW_REAR, 0.0])
    L = float(np.linalg.norm(d))
    return L, float(d @ (C.ELBOW_LEVER * np.array([math.sin(p2), -math.cos(p2)]))) / L


GEOM = {"shoulder": shoulder_L, "elbow": elbow_L}


# --- pneumatics: test 1 model with the cylinder as parameters ---------------------------
class Chambers:
    def __init__(self, cyl, p_supply=P1.P_SUPPLY):
        n = cyl["n"]
        self.aa = n * math.pi * (cyl["bore"] / 2) ** 2 * 1e-6          # m²
        self.ab = self.aa - n * math.pi * (cyl["rod"] / 2) ** 2 * 1e-6
        self.stroke = cyl["stroke"] * 1e-3
        self.dead = n * DEAD_CM3 * 1e-6
        self.Cv = n * P1.VALVE["sonic_conductance"]                     # one VQ110U per chamber per cylinder
        self.p_sup = (p_supply + P1.P_ATM) * BAR
        self.pa = self.pb = P_ATM
        self.valves = [[False, False, 0.0] for _ in range(4)]           # cmd, open, t_change
        self.air = 0.0

    def _valve(self, v, t, cmd):
        if cmd != v[0]:
            v[0], v[2] = cmd, t
        delay = P1.VALVE["t_on"] if v[0] else P1.VALVE["t_off"]
        if v[1] != v[0] and t - v[2] >= delay:
            v[1] = v[0]

    def step(self, t, dt, ext, vel, cmds):
        for v, c in zip(self.valves, cmds):
            self._valve(v, t, c)
        b = P1.VALVE["critical_ratio"]
        fa, va, fb, vb = (v[1] for v in self.valves)
        ina = mass_flow(self.p_sup, self.pa, self.Cv, b) if fa else 0.0
        inb = mass_flow(self.p_sup, self.pb, self.Cv, b) if fb else 0.0
        mA = ina - (mass_flow(self.pa, P_ATM, self.Cv, b) if va else 0.0)
        mB = inb - (mass_flow(self.pb, P_ATM, self.Cv, b) if vb else 0.0)
        self.air += (ina + inb) * dt
        ext = min(max(ext, 0.0), self.stroke)
        Va, Vb = self.dead + self.aa * ext, self.dead + self.ab * (self.stroke - ext)
        n, RT = P1.POLYTROPIC, 287.0 * P1.T_AIR
        self.pa = max(self.pa + n / Va * (RT * mA - self.pa * self.aa * vel) * dt, 0.2 * BAR)
        self.pb = max(self.pb + n / Vb * (RT * mB + self.pb * self.ab * vel) * dt, 0.2 * BAR)

    def force(self):
        return (self.pa - P_ATM) * self.aa - (self.pb - P_ATM) * self.ab

    def gauge(self):
        return (self.pa - P_ATM) / BAR, (self.pb - P_ATM) / BAR


def controller_cfg(joint, cyl, gains):
    """Test 1 controller settings for this cylinder and joint. Test 1 is tuned for about
    13 kg effective mass at the rod; here it is 100–460 kg at 1.0–1.6 Hz air-spring
    frequency, so the force gains are set per joint (kp about twice the air spring)."""
    cfg = gen_config.config_dict()
    n = cyl["n"]
    aa = n * math.pi * (cyl["bore"] / 2) ** 2
    lever = abs(GEOM[joint](-1.4 if joint == "shoulder" else 1.6)[1])
    db = HOLD_TIP * lever / REACH[joint] * 1000                       # mm of cylinder
    cfg.update(area_a=aa, area_b=aa - n * math.pi * (cyl["rod"] / 2) ** 2,
               L_min=cyl["L_min"], L_max=cyl["L_min"] + cyl["stroke"], soft_limit=2.0,
               v_max=2000.0, kp_force=gains["kp"], ki_force=gains["ki"], kd_force=gains["kd"],
               i_limit=2.0, pos_deadband=db, pos_deadband_out=2 * db)
    return cfg


# --- MuJoCo model -------------------------------------------------------------------------
def build_xml(cyls):
    S = C.S
    fr = {}
    for j, cyl in cyls.items():
        L, dL = GEOM[j](-1.4 if j == "shoulder" else 1.6)
        fc, fv = FRICTION[0] * cyl["bore"] * cyl["n"], FRICTION[1] * cyl["bore"] * cyl["n"]
        fr[j] = (fc * abs(dL), fv * dL * dL)       # joint friction torque, joint damping
    return f"""
<mujoco model="light_arm">
  <option timestep="{DT}" integrator="implicitfast" gravity="0 0 -9.81"><flag contact="disable"/></option>
  <worldbody>
    <body name="yaw" pos="0 0 {S[2]}">
      <joint name="yaw" type="hinge" axis="0 0 1" armature="0.05"/>
      <geom type="cylinder" fromto="0 0 -0.05 0 0 0.05" size="0.06" mass="2.0"/>
      <body name="upper" pos="{C.SH_OFF} 0 0">
        <joint name="shoulder" type="hinge" axis="0 -1 0" frictionloss="{fr['shoulder'][0]:.3f}" damping="{fr['shoulder'][1]:.3f}"/>
        <geom type="capsule" fromto="0 0 0 {L1} 0 0" size="0.02" mass="{M_UPPER}"/>
        <body name="fore" pos="{L1} 0 0">
          <joint name="elbow" type="hinge" axis="0 -1 0" frictionloss="{fr['elbow'][0]:.3f}" damping="{fr['elbow'][1]:.3f}"/>
          <geom type="capsule" fromto="0 0 0 {L2} 0 0" size="0.016" mass="{M_FORE}"/>
          <body name="wrist" pos="{L2} 0 0">
            <joint name="wrist" type="hinge" axis="0 -1 0" damping="0.5"/>
            <geom type="box" pos="0 0 -0.07" size="0.03 0.06 0.06" mass="{M_WRIST}"/>
            <site name="grasp" pos="0 0 {-GRASP}"/>
            <body name="load" pos="0 0 {-GRASP - BLOCK_DROP}">
              <inertial pos="0 0 0" mass="1e-4" diaginertia="1e-7 1e-7 1e-7"/>
            </body>
          </body>
        </body>
      </body>
    </body>
  </worldbody>
  <actuator>
    <motor name="yaw" joint="yaw"/>
    <motor name="wrist" joint="wrist"/>
  </actuator>
</mujoco>"""


class ArmSim:
    def __init__(self, cyls, gains, q0, block_mass=0.0, seed=1):
        self.cyls = cyls
        self.mdl = mujoco.MjModel.from_xml_string(build_xml(cyls))
        self.d = mujoco.MjData(self.mdl)
        self.block_mass = block_mass
        self.jid = {n: self.mdl.joint(n).id for n in ("yaw", "shoulder", "elbow", "wrist")}
        self.dof = {n: self.mdl.joint(n).dofadr[0] for n in self.jid}
        self.qadr = {n: self.mdl.joint(n).qposadr[0] for n in self.jid}
        self.load = self.mdl.body("load").id
        self.site = self.mdl.site("grasp").id
        self.pn = {j: Chambers(c) for j, c in cyls.items()}
        self.ctl = {j: control.Controller(controller_cfg(j, c, gains[j])) for j, c in cyls.items()}
        self.rng = np.random.default_rng(seed)
        self.t, self.i = 0.0, 0
        self.duty = {j: (0.0, 0.0, 0.0, 0.0) for j in cyls}
        self.set_q(q0)
        self._preload()
        for j in cyls:
            self.ctl[j].set_mode(control.POSITION, self.L_mm(j))

    # state
    def q(self):
        return np.array([self.d.qpos[self.qadr[n]] for n in ("yaw", "shoulder", "elbow")])

    def set_q(self, q):
        for n, v in zip(("yaw", "shoulder", "elbow"), q):
            self.d.qpos[self.qadr[n]] = v
        self.d.qpos[self.qadr["wrist"]] = -q[1] - q[2]
        self.last_ref = np.array(q, float)
        mujoco.mj_forward(self.mdl, self.d)

    def L_mm(self, j):
        return GEOM[j](self.d.qpos[self.qadr[j]])[0] * 1000

    def grasp(self):
        return self.d.site_xpos[self.site].copy()

    def grasp_vel(self):
        v = np.zeros(6)
        mujoco.mj_objectVelocity(self.mdl, self.d, mujoco.mjtObj.mjOBJ_SITE, self.site, v, 0)
        return v[3:]

    def set_block(self, mass):
        m = max(mass, 1e-4)
        a, b, c = W.BLOCK
        self.mdl.body_mass[self.load] = m
        self.mdl.body_inertia[self.load] = [m / 12 * (b * b + c * c), m / 12 * (a * a + c * c), m / 12 * (a * a + b * b)]

    def _preload(self):
        """Chamber pressures that hold the start pose (as after a slow start-up)."""
        mujoco.mj_forward(self.mdl, self.d)
        for j, pn in self.pn.items():
            tau = self.d.qfrc_bias[self.dof[j]]
            F = tau / GEOM[j](self.d.qpos[self.qadr[j]])[1]
            pa, pb = self.ctl[j]._pressures_for_force(F)
            pn.pa, pn.pb = (pa + P1.P_ATM) * BAR, (pb + P1.P_ATM) * BAR

    def step(self, q_ref):
        """One time step towards the joint reference q_ref (yaw, shoulder, elbow)."""
        d = self.d
        if self.i % CTRL_EVERY == 0:
            for j, ctl in self.ctl.items():
                ctl.ref = GEOM[j](q_ref[("shoulder", "elbow").index(j) + 1])[0] * 1000
                pa, pb = self.pn[j].gauge()
                L = self.L_mm(j) + self.rng.normal(0, ANGLE_NOISE) * abs(GEOM[j](self.d.qpos[self.qadr[j]])[1]) * 1000
                self.duty[j] = ctl.update(CTRL_EVERY * DT, L, pa + self.rng.normal(0, 0.01), pb + self.rng.normal(0, 0.01))
        # motors (stepper class: they follow the commanded position): stiff PD with the
        # reference speed; the wrist keeps the gripper vertical from the measured angles
        v_ref = (np.asarray(q_ref) - self.last_ref) / DT
        self.last_ref = np.array(q_ref, float)
        y, wy = self.qadr["yaw"], self.dof["yaw"]
        d.ctrl[0] = 3000.0 * (q_ref[0] - d.qpos[y]) + 150.0 * (v_ref[0] - d.qvel[wy])
        w, ww = self.qadr["wrist"], self.dof["wrist"]
        w_ref = -d.qpos[self.qadr["shoulder"]] - d.qpos[self.qadr["elbow"]]
        w_vel = -d.qvel[self.dof["shoulder"]] - d.qvel[self.dof["elbow"]]
        d.ctrl[1] = 400.0 * (w_ref - d.qpos[w]) + 12.0 * (w_vel - d.qvel[ww])
        period = 1.0 / P1.PWM_HZ
        phase = (self.t % period) / period
        d.qfrc_applied[:] = 0
        for j, pn in self.pn.items():
            L, dL = GEOM[j](d.qpos[self.qadr[j]])
            ext = L - self.cyls[j]["L_min"] / 1000
            vel = dL * d.qvel[self.dof[j]]
            cmds = [phase < du for du in self.duty[j]]
            for k in range(2):
                pn.step(self.t + k * DT / 2, DT / 2, ext, vel, cmds)
            d.qfrc_applied[self.dof[j]] = pn.force() * dL
        mujoco.mj_step(self.mdl, d)
        self.t += DT
        self.i += 1


# --- tuning: step tests -----------------------------------------------------------------
def step_test(gains, joint, block_mass, q0, dq=0.12, seconds=3.0, cyls=CYLS):
    """Step of one joint; returns (settling time to ±TOL at the gripper or None, end error, peak overshoot) in s, m."""
    sim = ArmSim(cyls, gains, q0)
    sim.set_block(block_mass)
    sim._preload()
    for _ in range(int(0.3 / DT)):
        sim.step(q0)
    q1 = q0.copy()
    q1[("yaw", "shoulder", "elbow").index(joint)] += dq
    start, target = sim.grasp(), W.tool(q1, 0.0)[6]
    axis = (target - start) / np.linalg.norm(target - start)
    settled, over, e = None, 0.0, 0.0
    for i in range(int(seconds / DT)):
        sim.step(q1)
        g = sim.grasp()
        e = float(np.linalg.norm(g - target))
        over = max(over, float((g - target) @ axis))
        if e > TOL:
            settled = None
        elif settled is None:
            settled = (i + 1) * DT
    return settled, e, over


def tune():
    q0 = W.pose(np.array([W.WALL_X, 0.0, W.TABLE_TOP + 0.15]), 0.0, np.array([0.0, -1.4, 1.5]))[0]
    grids = {"shoulder": [(kp, kd) for kp in (10, 20, 40) for kd in (1.5, 3, 6)],
             "elbow": [(kp, kd) for kp in (17, 35, 70) for kd in (2.5, 5.5, 11)]}
    best = {j: dict(g) for j, g in GAINS.items()}
    for j in ("shoulder", "elbow"):
        rows = []
        for kp, kd in grids[j]:
            gains = {k: dict(v) for k, v in best.items()}
            gains[j] = dict(kp=kp, ki=kp * 7.5, kd=kd)
            r = step_test(gains, j, 1.5, q0)
            score = r[0] if r[0] is not None else 10 + r[1] * 100
            rows.append((score, kp, kd, r))
            print(f"{j:8s} kp {kp:4.0f} kd {kd:5.1f}: settled {('%.2f s' % r[0]) if r[0] is not None else '   no':>7}, "
                  f"end {r[1] * 1000:5.1f} mm, overshoot {r[2] * 1000:5.1f} mm", flush=True)
        _, kp, kd, _ = min(rows)
        best[j] = dict(kp=kp, ki=kp * 7.5, kd=kd)
        print("best", j, best[j], flush=True)


# --- stage 1b ------------------------------------------------------------------------------
def run_task(cyls, gains, block_mass, mode="fast", record=False, quiet=False, seed=1):
    """Stage 1 with the physical arm. Returns a result dict; with record=True also the
    video frames (actual and planned joints, gripper yaw, jaw, block states)."""
    segs = W.segments(mode)
    q0 = segs[0]["qs"][0]
    sim = ArmSim(cyls, gains, q0, seed=seed)
    blocks = W.stack_blocks()
    held, offset = None, None
    res = dict(waits=[], errors=[], track=0.0)
    frames = []
    next_frame = [0.0]
    a_now = [segs[0]["a0"]]
    jaw_now = [segs[0]["jaw0"]]

    def tick(q_ref):
        sim.step(q_ref)
        if held is not None:
            Rt = K.Rz(sim.q()[0] + a_now[0] - q_ref[0])
            blocks[held][0] = sim.grasp() + Rt @ offset
            blocks[held][1] = a_now[0] - q_ref[0] + sim.q()[0]
        if record and sim.t >= next_frame[0]:
            next_frame[0] += 1.0 / W.FPS
            frames.append((sim.q(), q_ref.copy(), a_now[0] - q_ref[0], jaw_now[0],
                           [(b[0].copy(), b[1], b[2]) for b in blocks]))

    for _ in range(int(0.5 / DT)):
        tick(q0)
    t_start = sim.t
    for si, sg in enumerate(segs):
        qs, n = sg["qs"], len(sg["qs"]) - 1
        steps = int(round(sg["dur"] / DT))
        for i in range(steps):
            x = (i + 1) / steps * n
            k = min(int(x), n - 1)
            q_ref = qs[k] + (x - k) * (qs[k + 1] - qs[k])
            u = W.C.smooth((i + 1) / steps)
            a_now[0] = sg["a0"] + u * (sg["a1"] - sg["a0"])
            jaw_now[0] = sg["jaw0"] + u * (sg["jaw1"] - sg["jaw0"])
            tick(q_ref)
            if sg["kind"] == "travel":
                res["track"] = max(res["track"], float(np.linalg.norm(sim.grasp() - W.tool(q_ref, 0.0)[6])))
        # before gripping or releasing: wait until the gripper is in place and nearly still
        if sg["kind"] == "short" and si + 1 < len(segs):
            if segs[si + 1]["kind"] == "grip":
                t0 = sim.t
                while sim.t - t0 < WAIT_MAX:
                    if np.linalg.norm(sim.grasp() - sg["G"]) < TOL and np.linalg.norm(sim.grasp_vel()) < V_STILL:
                        break
                    tick(qs[-1])
                res["waits"].append(sim.t - t0)
        ev = sg["event"]
        if ev and ev[0] == "grab":
            held = ev[1]
            sim.set_block(block_mass)
            offset = K.Rz(sim.q()[0] + a_now[0] - qs[-1][0]).T @ (blocks[held][0] - sim.grasp())
        elif ev and ev[0] == "release":
            place = W.WALL_Y[W.STACK_N - 1 - held]
            want = np.array([W.WALL_X, place, W.TABLE_TOP + W.BLOCK[2] / 2])
            err = blocks[held][0] - want
            res["errors"].append((float(np.hypot(err[0], err[1])), float(err[2]),
                                  float(math.degrees(blocks[held][1] - math.pi / 2))))
            blocks[held][0] = blocks[held][0].copy()
            blocks[held][0][2] = W.TABLE_TOP + W.BLOCK[2] / 2          # it lands on the table
            held = None
            sim.set_block(0.0)
    for _ in range(int(1.0 / DT)):
        tick(segs[-1]["qs"][-1])
    res["time"] = sim.t - t_start - 1.0
    res["air"] = sum(pn.air for pn in sim.pn.values()) / 1.2e-3       # kg → litres of free air (ρ ≈ 1.2 g/l)
    if not quiet:
        print(f"{block_mass} kg: {res['time']:.1f} s, waits {[round(w, 2) for w in res['waits']]}, "
              f"placement {[round(e[0] * 1000, 1) for e in res['errors']]} mm, travel lag ≤ {res['track'] * 1000:.0f} mm, "
              f"air {res['air']:.1f} l", flush=True)
    return (res, frames) if record else res


CASES = [  # label, block mass, cylinders, gains, speeds
    ("0.3 kg, elbow 2 × Ø25", 0.3, CYLS, GAINS, "fast"),
    ("1.5 kg, elbow 2 × Ø25", 1.5, CYLS, GAINS, "fast"),
    ("3 kg, elbow 2 × Ø25", 3.0, CYLS, GAINS, "fast"),
    ("3 kg, elbow 2 × Ø32", 3.0, dict(CYLS, elbow=ELBOW_32), GAINS, "fast"),
    ("3 kg, elbow 2 × Ø32, retuned", 3.0, dict(CYLS, elbow=ELBOW_32), GAINS_3KG, "fast"),
    ("1.5 kg, elbow 2 × Ø25", 1.5, CYLS, GAINS, "controlled"),
    ("3 kg, elbow 2 × Ø32, retuned", 3.0, dict(CYLS, elbow=ELBOW_32), GAINS_3KG, "controlled"),
]


def results(seeds=(1, 2, 3)):
    """Stage 1b for every case, averaged over a few sensor-noise seeds → out/sim/results.md."""
    plan = {m: sum(sg["dur"] for sg in W.segments(m)) for m in ("fast", "controlled")}
    rows = []
    for label, mass, cyls, gains, mode in CASES:
        rs = [run_task(cyls, gains, mass, mode=mode, quiet=True, seed=sd) for sd in seeds]
        rows.append((f"{label} ({'1b, fast' if mode == 'fast' else '1a, controlled'})", np.mean([r["time"] for r in rs]), np.mean([sum(r["waits"]) for r in rs]),
                     max(max(r["waits"]) for r in rs), max(r["track"] for r in rs),
                     max(max(e[0] for e in r["errors"]) for r in rs), np.mean([r["air"] for r in rs])))
        print(label, [round(x, 3) for x in rows[-1][1:]], flush=True)
    lines = ["# Light arm, stage 1 — dynamic simulation", "",
             f"Generated by `python full-arm/arm_sim.py`. Plan (moves only, no waiting): {plan['fast']:.1f} s fast, "
             f"{plan['controlled']:.1f} s controlled. "
             f"Mean of {len(seeds)} runs with different sensor noise. The gains are tuned for 1.5 kg and the "
             "same for every load, except in the rows marked “retuned”.", "",
             "| Case | Time | Waiting in total | Longest wait | Largest lag while moving | Largest placement error | Air |",
             "|---|---|---|---|---|---|---|"]
    for label, t, wsum, wmax, lag, err, air in rows:
        lines.append(f"| {label} | {t:.1f} s | {wsum:.1f} s | {wmax:.1f} s{' (gave up)' if wmax >= WAIT_MAX - 1e-6 else ''} | "
                     f"{lag * 1000:.0f} mm | {err * 1000:.1f} mm | {air:.0f} l |")
    lines += ["", f"Waiting = after a move down, until the gripper is within ±{TOL * 1000:.0f} mm of its target and "
              f"slower than {V_STILL * 1000:.0f} mm/s (at most {WAIT_MAX:.0f} s, then it grips or releases anyway). "
              "Placement error = horizontal distance of the block from its place. Air in litres of free air."]
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "results.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def video(case):
    """Video of one case: the arm as simulated, the planned gripper as a ghost."""
    import imageio.v2 as imageio
    from PIL import Image, ImageDraw, ImageFont
    label, mass, cyls, gains, mode = CASES[case]
    res, frames = run_task(cyls, gains, mass, mode=mode, record=True)
    ttf = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"            # has Ø and ×
    font = ImageFont.truetype(ttf, 24) if os.path.exists(ttf) else ImageFont.load_default(size=26)
    C.CAMS = W.CAMS
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"video_sim_{label.split(',')[0].replace(' ', '').replace('.', 'p')}"
                             f"{'_elbow32' if cyls['elbow'] is ELBOW_32 else ''}{'_retuned' if gains is GAINS_3KG else ''}_{mode}.mp4")
    writer = imageio.get_writer(path, fps=W.FPS, codec="libx264", quality=8, macro_block_size=8)
    solid = {k: getattr(C, k) for k in ("ALU", "STEEL", "DARK", "RED", "BLUE")}
    for n, (q, q_ref, psi, jaw, blocks) in enumerate(frames):
        C.GEOMS.clear()
        for k, v in solid.items():                  # ghost: the planned gripper
            setattr(C, k, (0.2, 0.8, 0.3, 0.30))
        _, _, _, Rt_r, _, W_r, _ = W.tool(q_ref, psi)
        W.draw_gripper(W_r - 0.07 * Rt_r[:, 2], Rt_r, jaw)
        for k, v in solid.items():
            setattr(C, k, v)
        C.draw_arm(q, psi + q_ref[0] - q[0], jaw)
        W.draw_scene([list(b) for b in blocks])
        img = Image.fromarray(C.render_frame(None, "main"))
        lag = np.linalg.norm(W.tool(q, 0)[6] - W.tool(q_ref, 0)[6]) * 1000
        d = ImageDraw.Draw(img)
        d.text((24, 18), f"Simulated, stage {'1b (fast)' if mode == 'fast' else '1a (controlled)'}: {label}", fill=(30, 30, 30), font=font)
        d.text((24, 52), f"t = {n / W.FPS:4.1f} s    lag = {lag:4.0f} mm    green = planned gripper", fill=(30, 30, 30), font=font)
        writer.append_data(np.asarray(img))
    writer.close()
    print(path, len(frames), "frames")


if __name__ == "__main__":
    if "--tune" in sys.argv:
        tune()
    elif "--video" in sys.argv:
        video(int(sys.argv[sys.argv.index("--video") + 1]))
    else:
        results()

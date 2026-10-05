"""Simulate test 1 with the real controller (firmware/control.py).

The scenarios follow the tests in the manual:
  step       T3: 0° → 30° → -5°, measures overshoot, settling time and error
  onoff      T2: the same steps with fully open/closed valves only
  load       T7: step 0° → 30° with increasing load, until the criteria fail
  stiffness  T6: push on the arm at low and high chamber pressure
Output: plots and results.md in out/sim/.
"""
import json
import math
import os
import random
import sys

import mujoco
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "firmware"))
sys.path.insert(0, os.path.join(ROOT, "cad"))
import params as P  # noqa: E402
import model  # noqa: E402
from pneumatics import Pneumatics  # noqa: E402
import control  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "host"))
from analysis import plot, step_metrics  # noqa: E402,F401
import gen_config  # noqa: E402
from parts import pose  # noqa: E402

OUT = os.path.join(ROOT, "out", "sim")

class Sim:
    def __init__(self, tip_mass=P.TIP_MASS, p_sum=None, p_supply=P.P_SUPPLY, seed=1):
        self.mdl = mujoco.MjModel.from_xml_string(model.build_xml(tip_mass=tip_mass))
        self.d = mujoco.MjData(self.mdl)
        self.ext0 = model.ext0()
        self.pn = Pneumatics(p_supply)
        cfg = gen_config.config_dict()
        cfg["p_supply"] = p_supply
        if p_sum is not None:
            cfg["p_sum"] = p_sum
        self.ctl = control.Controller(cfg)
        self.cfg = cfg
        self.rng = random.Random(seed)
        self.t = 0.0
        self.duty = (0.0, 0.0, 0.0, 0.0)
        self.log = []
        self.ext_force = None
        self._start_at(P.THETA_MIN + 0.3)

    def _start_at(self, theta):
        """Start at rest at arm angle theta."""
        p0, p = pose(0.0), pose(theta)
        self.d.qpos[self.mdl.joint("arm").qposadr[0]] = math.radians(theta)
        self.d.qpos[self.mdl.joint("cyl_rear").qposadr[0]] = math.radians(p["phi"] - p0["phi"])
        self.d.qpos[self.mdl.joint("stroke").qposadr[0]] = (p["ext"] - p0["ext"]) / 1000
        self.d.qpos[self.mdl.joint("load").qposadr[0]] = -math.radians(theta)   # load hangs straight
        mujoco.mj_forward(self.mdl, self.d)

    # measurements as the Pico sees them
    def ext_mm(self):
        return self.ext0 + self.d.qpos[self.mdl.joint("stroke").qposadr[0]] * 1000

    def theta(self):
        return math.degrees(self.d.qpos[self.mdl.joint("arm").qposadr[0]])

    def measure(self):
        L = P.PIN_TO_PIN_MIN + self.ext_mm() + self.rng.gauss(0, 0.08)
        L = round(L / 0.05) * 0.05                       # ADC step ~0.05 mm
        pa, pb = self.pn.gauge()
        return L, pa + self.rng.gauss(0, 0.01), pb + self.rng.gauss(0, 0.01)

    def run(self, seconds, ref_fn=None):
        dt = self.mdl.opt.timestep
        ctrl_every = int(round(1.0 / P.LOOP_HZ / dt))
        period = 1.0 / self.cfg["pwm_hz"]
        slide = self.mdl.joint("stroke")
        steps = int(round(seconds / dt))
        for i in range(steps):
            if ref_fn is not None:
                ref_fn(self, self.t)
            if i % ctrl_every == 0:
                L, pa, pb = self.measure()
                self.duty = self.ctl.update(ctrl_every * dt, L, pa, pb)
                self.log.append((self.t, L, self.theta(), pa, pb, *self.duty,
                                 self.ctl.ref if self.ctl.ref is not None else float("nan"),
                                 self.ctl.p_des[0], self.ctl.p_des[1]))
            phase = (self.t % period) / period
            cmds = [phase < du for du in self.duty]
            ext = self.ext_mm() / 1000
            vel = self.d.qvel[slide.dofadr[0]]
            for k in range(5):
                self.pn.step(self.t + k * dt / 5, dt / 5, ext, vel, cmds)
            self.d.ctrl[0] = self.pn.force()
            self.d.xfrc_applied[:] = 0
            if self.ext_force is not None:
                body, f = self.ext_force
                self.d.xfrc_applied[self.mdl.body(body).id, :3] = f
            mujoco.mj_step(self.mdl, self.d)
            self.t += dt
        return np.array(self.log)


def L_of(theta):
    return P.cylinder_length(theta)


def scenario_step(mode=control.POSITION, tip_mass=P.TIP_MASS, plot_name="step", p_supply=P.P_SUPPLY):
    s = Sim(tip_mass=tip_mass, p_supply=p_supply)
    s.ctl.set_mode(mode, L_of(0.0))
    plan = [(0.0, 0.0), (2.0, 30.0), (4.0, -5.0)]

    def ref(sim, t):
        th = [a for (ts, a) in plan if t >= ts][-1]
        if sim.ctl.ref != L_of(th):
            sim.ctl.ref = L_of(th)
    log = s.run(6.0, ref)
    m1 = step_metrics(log, 2.0, 4.0, L_of(30.0))
    m2 = step_metrics(log, 4.0, 6.0, L_of(-5.0))
    plot(log, os.path.join(OUT, f"{plot_name}.png"),
         f"{'PWM control' if mode == control.POSITION else 'On/off control'} — load {tip_mass} kg, {p_supply} bar")
    return dict(up_0_to_30=m1, down_30_to_minus5=m2,
                air_used_g=round(s.pn.air_used * 1000, 2)), log


def scenario_load():
    rows = []
    for mass in (0.5, 1.5, 2.5, 3.5, 4.5, 5.5):
        s = Sim(tip_mass=mass)
        s.ctl.set_mode(control.POSITION, L_of(0.0))

        def ref(sim, t):
            sim.ctl.ref = L_of(30.0 if t >= 2.0 else 0.0)
        log = s.run(4.0, ref)
        m = step_metrics(log, 2.0, 4.0, L_of(30.0))
        arm_mass = P.ARM["length"] * P.ARM["height"] * P.ARM["thickness"] * P.ALU_DENSITY
        torque = 9.81 * (arm_mass * (P.ARM["length"] / 2 - P.ARM_BEHIND) + mass * P.ARM_TIP) / 1000 * math.cos(math.radians(30))
        avail = P.P_SUPPLY * 0.1 * P.AREA_A * P.moment_arm(30.0) / 1000
        rows.append(dict(load_kg=mass, load_pct=round(100 * torque / avail), **m))
    return rows


def scenario_stiffness():
    """T6: go to 20°, then close all valves (air trapped) and pull 15 N extra down on
    the load. The deflection measures only the stiffness of the air spring."""
    rows = []
    for p_sum in (2.0, 5.0):
        s = Sim(p_sum=p_sum)
        s.ctl.set_mode(control.POSITION, L_of(20.0))
        s.run(3.0)
        s.ctl.set_mode(control.OFF)
        s.run(0.3)
        th0 = s.theta()
        s.ext_force = ("load", np.array([0.0, 0.0, -15.0]))
        log = s.run(0.6)
        s.ext_force = None
        dip = th0 - min(log[-int(0.6 * P.LOOP_HZ):, 2])
        rows.append(dict(pressure_sum_bar=p_sum, deflection_deg=round(float(dip), 2)))
    return rows


def render_stills():
    """Still images: arm low, horizontal and high, from two cameras."""
    os.environ.setdefault("MUJOCO_GL", "egl")
    from PIL import Image
    paths = []
    for name, th in (("arm_low", P.THETA_MIN + 1), ("arm_horizontal", 0.0), ("arm_high", 50.0)):
        s = Sim()
        s._start_at(th)
        r = mujoco.Renderer(s.mdl, 960, 1280)
        for cam in ("side", "oblique"):
            r.update_scene(s.d, camera=cam)
            p = os.path.join(OUT, f"render_{name}_{cam}.png")
            Image.fromarray(r.render()).save(p)
            paths.append(p)
        r.close()
    return paths


def write_markdown(res):
    """Readable summary of the simulation (out/sim/results.md)."""
    def row(name, m):
        return (f"| {name} | {m['overshoot_mm']} | {m['settling_s']} | {m['error_mm']} | "
                f"{'yes' if m['passed'] else 'no'} |")
    lines = ["# Simulation of test 1 — results", "",
             f"Load {P.TIP_MASS} kg, supply {P.P_SUPPLY} bar, tuning from `params.py`. "
             "T3 criteria: overshoot < 5 mm, settled (within ±1 mm) within 1 s, error < 1 mm.", "",
             "## T3 PWM control and T2 on/off control", "",
             "| Step | Overshoot (mm) | Settling (s) | Error (mm) | Passed |", "|---|---|---|---|---|"]
    for key, label in (("T3_pwm", "PWM"), ("T2_onoff", "on/off (3 bar)")):
        lines.append(row(f"{label}: 0° → 30°", res[key]["up_0_to_30"]))
        lines.append(row(f"{label}: 30° → −5°", res[key]["down_30_to_minus5"]))
    lines += ["", "![PWM control](step.png)", "", "![on/off control](onoff.png)", "",
              "## T7 load ratio", "",
              "| Load (kg) | Load (%) | Overshoot (mm) | Settling (s) | Error (mm) | Passed |",
              "|---|---|---|---|---|---|"]
    for r in res["T7_load"]:
        lines.append(f"| {r['load_kg']} | {r['load_pct']} | {r['overshoot_mm']} | {r['settling_s']} | "
                     f"{r['error_mm']} | {'yes' if r['passed'] else 'no'} |")
    lines += ["", "## T6 stiffness (valves closed, 15 N extra on the load)", "",
              "| Sum of chamber pressures (bar) | Deflection (degrees) |", "|---|---|"]
    for r in res["T6_stiffness"]:
        lines.append(f"| {r['pressure_sum_bar']} | {r['deflection_deg']} |")
    with open(os.path.join(OUT, "results.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {}
    res["T3_pwm"], _ = scenario_step(control.POSITION)
    res["T2_onoff"], _ = scenario_step(control.BANGBANG, plot_name="onoff", p_supply=3.0)
    res["T7_load"] = scenario_load()
    res["T6_stiffness"] = scenario_stiffness()
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(res, f, indent=2)
    write_markdown(res)
    print(json.dumps(res, indent=2))
    if "--render" in sys.argv:
        render_stills()


if __name__ == "__main__":
    main()

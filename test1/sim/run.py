"""Simuleer test 1 met het echte regelalgoritme (firmware/control.py).

Scenario's volgen de proeven uit de handleiding:
  sprong     T3: 0° → 30° → -5°, meet doorschot, insteltijd en restfout
  aanuit     T2: dezelfde sprongen met alleen vol open/dicht
  belasting  T7: sprong 0° → 30° bij oplopende last, tot de criteria niet meer halen
  stijfheid  T6: duw tegen de arm bij lage en hoge kamerdruk
Uitvoer: grafieken en resultaten.md in out/sim/.
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
import gen_config  # noqa: E402
from parts import pose  # noqa: E402

OUT = os.path.join(ROOT, "out", "sim")

# criteria uit de handleiding (T3)
OVERSHOOT_MM = 5.0
SETTLE_S = 1.0
ERROR_MM = 1.0


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
        """Begin in rust met de arm (bijna) op de onderste aanslag."""
        p0, p = pose(0.0), pose(theta)
        self.d.qpos[self.mdl.joint("arm").qposadr[0]] = math.radians(theta)
        self.d.qpos[self.mdl.joint("cil_achter").qposadr[0]] = math.radians(p["phi"] - p0["phi"])
        self.d.qpos[self.mdl.joint("slag").qposadr[0]] = (p["ext"] - p0["ext"]) / 1000
        self.d.qpos[self.mdl.joint("last").qposadr[0]] = -math.radians(theta)   # last hangt recht
        mujoco.mj_forward(self.mdl, self.d)

    # metingen zoals de Pico ze ziet
    def ext_mm(self):
        return self.ext0 + self.d.qpos[self.mdl.joint("slag").qposadr[0]] * 1000

    def theta(self):
        return math.degrees(self.d.qpos[self.mdl.joint("arm").qposadr[0]])

    def measure(self):
        L = P.PIN_TO_PIN_MIN + self.ext_mm() + self.rng.gauss(0, 0.08)
        L = round(L / 0.05) * 0.05                       # ADC-stap ~0,05 mm
        pa, pb = self.pn.gauge()
        return L, pa + self.rng.gauss(0, 0.01), pb + self.rng.gauss(0, 0.01)

    def run(self, seconds, ref_fn=None):
        dt = self.mdl.opt.timestep
        ctrl_every = int(round(1.0 / P.LOOP_HZ / dt))
        period = 1.0 / self.cfg["pwm_hz"]
        slide = self.mdl.joint("slag")
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


def step_metrics(log, t0, t1, target):
    """Doorschot (mm), insteltijd (s) en restfout (mm) van een sprong op t0."""
    sel = (log[:, 0] >= t0) & (log[:, 0] < t1)
    t, L = log[sel, 0], log[sel, 1]
    start = L[0]
    direction = 1 if target > start else -1
    over = max(0.0, max((L - target) * direction))
    outside = np.where(np.abs(L - target) > ERROR_MM)[0]
    settle = (t[outside[-1]] - t0) if len(outside) else 0.0
    tail = (t > t1 - 0.5)
    err = float(np.mean(np.abs(L[tail] - target)))
    return dict(doorschot_mm=round(float(over), 2), insteltijd_s=round(float(settle), 3),
                restfout_mm=round(err, 2),
                geslaagd=bool(over < OVERSHOOT_MM and settle < SETTLE_S and err < ERROR_MM))


def scenario_sprong(mode=control.POSITION, tip_mass=P.TIP_MASS, plot_name="sprong", p_supply=P.P_SUPPLY):
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
         f"{'PWM-regeling' if mode == control.POSITION else 'Aan/uit-regeling'} — last {tip_mass} kg, {p_supply} bar")
    return dict(omhoog_0_naar_30=m1, omlaag_30_naar_min5=m2,
                luchtverbruik_g=round(s.pn.air_used * 1000, 2)), log


def scenario_belasting():
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
        rows.append(dict(last_kg=mass, belasting_pct=round(100 * torque / avail), **m))
    return rows


def scenario_stijfheid():
    """T6: regel naar 20°, sluit dan alle ventielen (lucht opgesloten) en duw 15 N
    extra omlaag aan de last. De uitwijking meet alleen de stijfheid van de luchtveer."""
    rows = []
    for p_sum in (2.0, 5.0):
        s = Sim(p_sum=p_sum)
        s.ctl.set_mode(control.POSITION, L_of(20.0))
        s.run(3.0)
        s.ctl.set_mode(control.OFF)
        s.run(0.3)
        th0 = s.theta()
        s.ext_force = ("last", np.array([0.0, 0.0, -15.0]))
        log = s.run(0.6)
        s.ext_force = None
        dip = th0 - min(log[-int(0.6 * P.LOOP_HZ):, 2])
        rows.append(dict(kamerdruk_som_bar=p_sum, uitwijking_graden=round(float(dip), 2)))
    return rows


def plot(log, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = log[:, 0]
    fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    ax[0].plot(t, log[:, 1], label="lengte cilinder (gemeten)")
    ax[0].plot(t, log[:, 9], "--", label="doel")
    ax[0].set_ylabel("mm")
    ax2 = ax[0].twinx()
    ax2.plot(t, log[:, 2], color="gray", alpha=0.4, label="armhoek")
    ax2.set_ylabel("graden")
    ax[0].legend(loc="upper left")
    ax[1].plot(t, log[:, 3], label="kamer A")
    ax[1].plot(t, log[:, 4], label="kamer B")
    ax[1].plot(t, log[:, 10], ":", color="C0", alpha=0.7, label="doel A")
    ax[1].plot(t, log[:, 11], ":", color="C1", alpha=0.7, label="doel B")
    ax[1].set_ylabel("bar overdruk")
    ax[1].legend(loc="upper left")
    for k, name in enumerate(("vul A", "leeg A", "vul B", "leeg B")):
        ax[2].plot(t, log[:, 5 + k] + k * 1.2, label=name)
    ax[2].set_yticks([0.5 + 1.2 * k for k in range(4)], ["vul A", "leeg A", "vul B", "leeg B"])
    ax[2].set_xlabel("tijd (s)")
    ax[2].set_ylabel("duty")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def render_stills():
    """Twee stilstaande beelden: arm laag en arm hoog."""
    os.environ.setdefault("MUJOCO_GL", "egl")
    from PIL import Image
    paths = []
    for name, th in (("arm_laag", P.THETA_MIN + 1), ("arm_horizontaal", 0.0), ("arm_hoog", 50.0)):
        s = Sim()
        s._start_at(th)
        r = mujoco.Renderer(s.mdl, 960, 1280)
        for cam in ("zij", "schuin"):
            r.update_scene(s.d, camera=cam)
            p = os.path.join(OUT, f"render_{name}_{cam}.png")
            Image.fromarray(r.render()).save(p)
            paths.append(p)
        r.close()
    return paths


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {}
    res["T3_pwm"], _ = scenario_sprong(control.POSITION)
    res["T2_aanuit"], _ = scenario_sprong(control.BANGBANG, plot_name="aanuit", p_supply=3.0)
    res["T7_belasting"] = scenario_belasting()
    res["T6_stijfheid"] = scenario_stijfheid()
    with open(os.path.join(OUT, "resultaten.json"), "w") as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res, indent=2))
    if "--render" in sys.argv:
        render_stills()


if __name__ == "__main__":
    main()

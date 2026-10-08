"""Controller for one pneumatic cylinder with 4 on/off valves.

Runs unchanged on the Pico (MicroPython) and in the simulation (CPython):
no numpy, no dataclasses, plain floats only.

Structure:
  position PID (mm)        ->  desired force (N)
  force + stiffness        ->  desired pressure per chamber (bar gauge)
  pressure loop per chamber ->  PWM duty for fill and vent valve (0..1)
A chamber fills, vents or holds; filling and venting at the same time is impossible.

MOVE (T8) differs from POSITION in two ways: the target follows a smooth profile
(quintic, continuous acceleration) instead of a constant-speed ramp, and the force gets
a feedforward of the planned acceleration, gravity and friction, so the cylinder already
pushes when the move starts instead of waiting for an error.
"""

import math

OFF, MANUAL, PRESSURE, POSITION, BANGBANG, MOVE = "off", "manual", "pressure", "position", "bangbang", "move"


def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


class Profile:
    """Quintic from (x0, v0, a0) to (x1, 0, 0) in T seconds: position, speed and
    acceleration are continuous, also when a new target interrupts a move."""

    def __init__(self, x0, v0, a0, x1, v_max, a_max, j_max, t_min=0.05):
        self.x1 = x1
        d = abs(x1 - x0)
        # rest to rest the peak speed is 1.875 d/T and the peak acceleration 5.77 d/T²
        T = max(1.875 * d / v_max, (5.77 * d / a_max) ** 0.5, t_min)
        # the jerk (how fast the force must change) is limited by how fast the valves can
        # change the pressures; starting while moving (new target during a move) can need
        # more time too: lengthen until the profile stays within all limits
        for _ in range(16):
            self._fit(x0, v0, a0, T)
            v_pk = a_pk = j_pk = 0.0
            c3, c4, c5 = self.c[3], self.c[4], self.c[5]
            for k in range(17):
                t = T * k / 16
                _, v, a = self.at(t - 1e-9)
                v_pk, a_pk = max(v_pk, abs(v)), max(a_pk, abs(a))
                j_pk = max(j_pk, abs(6 * c3 + t * (24 * c4 + t * 60 * c5)))
            if (v_pk <= 1.05 * max(v_max, abs(v0)) and a_pk <= 1.05 * max(a_max, abs(a0))
                    and j_pk <= 1.05 * j_max):
                break
            T *= 1.1

    def _fit(self, x0, v0, a0, T):
        self.T = T
        h = self.x1 - x0 - v0 * T - 0.5 * a0 * T * T     # what is left after coasting
        dv, da = -v0 - a0 * T, -a0
        T2 = T * T
        self.c = (x0, v0, 0.5 * a0,
                  (10 * h - 4 * dv * T + 0.5 * da * T2) / (T2 * T),
                  (-15 * h + 7 * dv * T - da * T2) / (T2 * T2),
                  (6 * h - 3 * dv * T + 0.5 * da * T2) / (T2 * T2 * T))

    def at(self, t):
        """(x, v, a) at time t after the start."""
        if t >= self.T:
            return self.x1, 0.0, 0.0
        c0, c1, c2, c3, c4, c5 = self.c
        x = c0 + t * (c1 + t * (c2 + t * (c3 + t * (c4 + t * c5))))
        v = c1 + t * (2 * c2 + t * (3 * c3 + t * (4 * c4 + t * 5 * c5)))
        a = 2 * c2 + t * (6 * c3 + t * (12 * c4 + t * 20 * c5))
        return x, v, a


class Controller:
    def __init__(self, cfg):
        self.cfg = cfg              # dict from config.py
        self.mode = OFF
        self.ref = None             # mm (POSITION, BANGBANG)
        self.p_ref = (0.0, 0.0)     # bar (PRESSURE)
        self.p_sum = cfg["p_sum"]   # bar, stiffness
        self.manual = (0.0, 0.0, 0.0, 0.0)
        self.integral = 0.0
        self.v_filt = 0.0
        self.last_L = None
        self.fault = ""
        self.force = 0.0
        self.p_des = (0.0, 0.0)
        self.ref_now = None         # mm, target that moves towards ref at limited speed
        self.over_t = 0.0           # s that the pressure has been too high
        self.holding = False        # in position, all valves closed
        self.plan = None            # Profile (MOVE)
        self.plan_t = 0.0           # s since the start of the profile
        self.v_ref_filt = 0.0       # mm/s, planned speed through the same filter as v_filt

    # --- helpers --------------------------------------------------------------
    def set_mode(self, mode, value=None):
        if mode == MOVE and self.mode == MOVE:
            self.ref = value        # new target during a move: replanned from the current profile state
            return
        self.mode = mode
        self.plan = None
        self.integral = 0.0
        self.ref_now = None
        self.holding = False
        if mode in (POSITION, BANGBANG, MOVE):
            self.ref = value
        elif mode == PRESSURE:
            self.p_ref = value
        elif mode == MANUAL:
            self.manual = value
        if mode == OFF:
            self.fault = ""

    def _chamber(self, p_des, p):
        """Duty (fill, vent) for one chamber."""
        c = self.cfg
        e = p_des - p
        if e > c["p_deadband"]:
            return clamp(c["d_min"] + c["kp_pressure"] * e, 0.0, 1.0), 0.0
        if e < -c["p_deadband"]:
            return 0.0, clamp(c["d_min"] - c["kp_pressure"] * e, 0.0, 1.0)
        return 0.0, 0.0

    def _pressures_for_force(self, force):
        """Chamber pressures (bar gauge) that together give `force` with sum p_sum."""
        c = self.cfg
        aa, ab = c["area_a"] * 0.1, c["area_b"] * 0.1   # N per bar
        pa = (force + self.p_sum * ab) / (aa + ab)
        pa = clamp(pa, 0.0, c["p_supply"])
        pb = clamp(self.p_sum - pa, 0.0, c["p_supply"])
        return pa, pb

    # --- arm geometry (angle in radians, lengths in mm) ---------------------------
    def length(self, th):
        r, b = self.cfg["hinge_to_rear"], self.cfg["hinge_to_attach"]
        return (r * r + b * b + 2 * r * b * math.sin(th)) ** 0.5

    def angle(self, L):
        r, b = self.cfg["hinge_to_rear"], self.cfg["hinge_to_attach"]
        return math.asin(clamp((L * L - r * r - b * b) / (2 * r * b), -1.0, 1.0))

    def feedforward(self, th, w, al, v):
        """Force (N) for the planned angle th, angular speed w (rad/s) and acceleration al
        (rad/s²): gravity of arm + load, inertia, and the cylinder's friction at rod
        speed v (mm/s)."""
        c = self.cfg
        load = c["load_kg"]
        moment = c["arm_moment"] + load * c["tip_dist"]                 # kg·mm
        inertia = c["arm_inertia"] + load * c["tip_dist"] ** 2          # kg·mm²
        lever = c["hinge_to_rear"] * c["hinge_to_attach"] * math.cos(th) / self.length(th)   # mm
        torque = (9.81 * moment * math.cos(th) + inertia * al / 1000.0) / 1000.0           # N·m
        f = torque * 1000.0 / lever
        f += c["ff_friction"] * clamp(v / 5.0, -1.0, 1.0) + c["ff_viscous"] * v / 1000.0
        return f

    # --- main -------------------------------------------------------------------
    def update(self, dt, L, pa, pb):
        """One control step. L in mm (pin to pin), pressures in bar gauge.

        Returns (fill_a, vent_a, fill_b, vent_b) as duty 0..1.
        """
        fa, va, fb, vb = self._update(dt, L, pa, pb)
        c = self.cfg
        if pa > c["p_max"]:
            fa, va = 0.0, 1.0
        if pb > c["p_max"]:
            fb, vb = 0.0, 1.0
        return fa, va, fb, vb

    def _update(self, dt, L, pa, pb):
        """Mode logic; update() adds the over-pressure relief on top."""
        c = self.cfg
        # velocity (filtered), tracked in every mode
        if self.last_L is not None and dt > 0:
            v = (L - self.last_L) / dt
            self.v_filt += (v - self.v_filt) * clamp(dt * c["v_filter_hz"] * 6.283, 0.0, 1.0)
        self.last_L = L

        # over-pressure: open the vent valve of that chamber (relief). Short peaks happen
        # when the cylinder compresses air, e.g. when overshooting. If it lasts longer
        # than p_max_time, the pressure regulator is set too high: fault.
        relief_a = pa > c["p_max"]
        relief_b = pb > c["p_max"]
        if relief_a or relief_b:
            self.over_t += dt
            if self.over_t > c["p_max_time"]:
                self.fault = "over-pressure (regulator set too high?)"
        else:
            self.over_t = 0.0
        if L < c["L_min"] - 20 or L > c["L_max"] + 20:
            self.fault = "position sensor out of range"
        if self.fault:
            self.mode = OFF
            # on a fault: everything closed (the cylinder keeps its air)
            return 0.0, 0.0, 0.0, 0.0

        if self.mode == OFF:
            return 0.0, 0.0, 0.0, 0.0
        if self.mode == MANUAL:
            fa, va, fb, vb = self.manual
            if fa > 0 and va > 0:
                va = 0.0
            if fb > 0 and vb > 0:
                vb = 0.0
            return fa, va, fb, vb
        if self.mode == PRESSURE:
            self.p_des = self.p_ref
            fa, va = self._chamber(self.p_ref[0], pa)
            fb, vb = self._chamber(self.p_ref[1], pb)
            return fa, va, fb, vb

        lo, hi = c["L_min"] + c["soft_limit"], c["L_max"] - c["soft_limit"]
        target = clamp(self.ref, lo, hi)
        v_ref = a_ref = 0.0
        if self.mode == MOVE:
            # smooth profile of the arm angle; a new target starts a new profile from the
            # current one. Planned in degrees, so the limits mean the same at every angle.
            th1 = math.degrees(self.angle(target))
            if self.plan is None:
                self.plan = Profile(math.degrees(self.angle(L)), 0.0, 0.0, th1, c["move_w_max"], c["move_alpha_max"], c["move_jerk_max"])
                self.plan_t = 0.0
            elif self.plan.x1 != th1:
                x, v, a = self.plan.at(self.plan_t)
                self.plan = Profile(x, v, a, th1, c["move_w_max"], c["move_alpha_max"], c["move_jerk_max"])
                self.plan_t = 0.0
            else:
                self.plan_t += dt
            th, w, al = self.plan.at(self.plan_t)
            th, w, al = math.radians(th), math.radians(w), math.radians(al)
            # the same motion in cylinder length: L(th), L' w, L'' w² + L' al
            self.ref_now = self.length(th)
            r, b = c["hinge_to_rear"], c["hinge_to_attach"]
            d1 = r * b * math.cos(th) / self.ref_now
            d2 = (-r * b * math.sin(th) - d1 * d1) / self.ref_now
            v_ref, a_ref = d1 * w, d2 * w * w + d1 * al
            ff_args = (th, w, al, v_ref)
            arrived = self.plan_t >= self.plan.T
        else:
            # let the target follow at limited speed (no step in the control error)
            if self.ref_now is None:
                self.ref_now = L
            step = c["v_max"] * dt
            self.ref_now += clamp(target - self.ref_now, -step, step)
            arrived = abs(self.ref_now - target) < 1e-6
        self.v_ref_filt += (v_ref - self.v_ref_filt) * clamp(dt * c["v_filter_hz"] * 6.283, 0.0, 1.0)
        ref = self.ref_now if self.mode in (POSITION, MOVE) else target
        e = ref - L
        if self.mode == BANGBANG:
            # T2: fully open/closed with a deadband, no PWM fine control
            db = c["bangbang_deadband"]
            if e > db:
                return 1.0, 0.0, 0.0, 1.0
            if e < -db:
                return 0.0, 1.0, 1.0, 0.0
            return 0.0, 0.0, 0.0, 0.0

        # POSITION, MOVE
        # In position and still: all valves closed, the trapped air holds the arm.
        # Saves air and valve wear. Control resumes when the error exceeds pos_deadband_out.
        hold_in, hold_out = c["pos_deadband"], c["pos_deadband_out"]
        if self.holding:
            if abs(e) < hold_out and arrived:
                return 0.0, 0.0, 0.0, 0.0
            self.holding = False
        elif (abs(e) < hold_in and abs(self.v_filt) < c["v_hold"]
              and arrived
              and abs(self.p_des[0] - pa) < 2 * c["p_deadband"]
              and abs(self.p_des[1] - pb) < 2 * c["p_deadband"]):
            self.holding = True
            return 0.0, 0.0, 0.0, 0.0
        f_max = c["p_supply"] * c["area_a"] * 0.1
        f_min = -c["p_supply"] * c["area_b"] * 0.1
        # integrate close to the target, or when the arm is stalled short of it
        # (heavy load): overcomes friction and gravity without overshoot
        if abs(e) < c["i_zone"] or abs(self.v_filt) < c["v_hold"]:
            self.integral = clamp(self.integral + e * dt, -c["i_limit"], c["i_limit"])
        if self.mode == MOVE:
            force = (c["kp_force"] * e + c["ki_force"] * self.integral
                     + c["kd_force"] * (self.v_ref_filt - self.v_filt) + self.feedforward(*ff_args))
        else:
            force = c["kp_force"] * e + c["ki_force"] * self.integral - c["kd_force"] * self.v_filt
        self.force = clamp(force, f_min, f_max)
        self.p_des = self._pressures_for_force(self.force)
        fa, va = self._chamber(self.p_des[0], pa)
        fb, vb = self._chamber(self.p_des[1], pb)
        return fa, va, fb, vb

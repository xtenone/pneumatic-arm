"""Controller for one pneumatic cylinder with 4 on/off valves.

Runs unchanged on the Pico (MicroPython) and in the simulation (CPython):
no numpy, no dataclasses, plain floats only.

Structure:
  position PID (mm)        ->  desired force (N)
  force + stiffness        ->  desired pressure per chamber (bar gauge)
  pressure loop per chamber ->  PWM duty for fill and vent valve (0..1)
A chamber fills, vents or holds; filling and venting at the same time is impossible.
"""

OFF, MANUAL, PRESSURE, POSITION, BANGBANG = "off", "manual", "pressure", "position", "bangbang"


def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


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

    # --- helpers --------------------------------------------------------------
    def set_mode(self, mode, value=None):
        self.mode = mode
        self.integral = 0.0
        self.ref_now = None
        self.holding = False
        if mode in (POSITION, BANGBANG):
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
        # let the target follow at limited speed (no step in the control error)
        if self.ref_now is None:
            self.ref_now = L
        step = c["v_max"] * dt
        self.ref_now += clamp(target - self.ref_now, -step, step)
        ref = self.ref_now if self.mode == POSITION else target
        e = ref - L
        if self.mode == BANGBANG:
            # T2: fully open/closed with a deadband, no PWM fine control
            db = c["bangbang_deadband"]
            if e > db:
                return 1.0, 0.0, 0.0, 1.0
            if e < -db:
                return 0.0, 1.0, 1.0, 0.0
            return 0.0, 0.0, 0.0, 0.0

        # POSITION
        # In position and still: all valves closed, the trapped air holds the arm.
        # Saves air and valve wear. Control resumes when the error exceeds pos_deadband_out.
        hold_in, hold_out = c["pos_deadband"], c["pos_deadband_out"]
        if self.holding:
            if abs(e) < hold_out and abs(self.ref_now - target) < 1e-6:
                return 0.0, 0.0, 0.0, 0.0
            self.holding = False
        elif (abs(e) < hold_in and abs(self.v_filt) < c["v_hold"]
              and abs(self.ref_now - target) < 1e-6
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
        force = c["kp_force"] * e + c["ki_force"] * self.integral - c["kd_force"] * self.v_filt
        self.force = clamp(force, f_min, f_max)
        self.p_des = self._pressures_for_force(self.force)
        fa, va = self._chamber(self.p_des[0], pa)
        fb, vb = self._chamber(self.p_des[1], pb)
        return fa, va, fb, vb

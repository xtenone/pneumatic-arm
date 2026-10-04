"""Regelalgoritme voor één pneumatische cilinder met 4 aan/uit-ventielen.

Draait ongewijzigd op de Pico (MicroPython) en in de simulatie (CPython):
geen numpy, geen dataclasses, alleen gewone floats.

Opbouw:
  positie-PID (mm)  ->  gewenste kracht (N)
  kracht + stijfheid ->  gewenste druk per kamer (bar overdruk)
  drukregelaar per kamer -> PWM-duty voor vul- en leegventiel (0..1)
Een kamer vult óf loopt leeg óf houdt vast; vullen en legen tegelijk kan niet.
"""

OFF, MANUAL, PRESSURE, POSITION, BANGBANG = "off", "manual", "pressure", "position", "bangbang"


def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


class Controller:
    def __init__(self, cfg):
        self.cfg = cfg              # dict uit config.py
        self.mode = OFF
        self.ref = None             # mm (POSITION, BANGBANG)
        self.p_ref = (0.0, 0.0)     # bar (PRESSURE)
        self.p_sum = cfg["p_sum"]   # bar, stijfheid
        self.manual = (0.0, 0.0, 0.0, 0.0)
        self.integral = 0.0
        self.v_filt = 0.0
        self.last_L = None
        self.fault = ""
        self.force = 0.0
        self.p_des = (0.0, 0.0)
        self.ref_now = None         # mm, doel dat met maximale snelheid naar ref beweegt
        self.over_t = 0.0           # s dat de druk al te hoog is
        self.holding = False        # in positie, alle ventielen dicht

    # --- hulpfuncties ---------------------------------------------------------
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
        """Duty (vul, leeg) voor één kamer."""
        c = self.cfg
        e = p_des - p
        if e > c["p_deadband"]:
            return clamp(c["d_min"] + c["kp_pressure"] * e, 0.0, 1.0), 0.0
        if e < -c["p_deadband"]:
            return 0.0, clamp(c["d_min"] - c["kp_pressure"] * e, 0.0, 1.0)
        return 0.0, 0.0

    def _pressures_for_force(self, force):
        """Kamerdrukken (bar overdruk) die samen `force` geven bij som p_sum."""
        c = self.cfg
        aa, ab = c["area_a"] * 0.1, c["area_b"] * 0.1   # N per bar
        pa = (force + self.p_sum * ab) / (aa + ab)
        pa = clamp(pa, 0.0, c["p_supply"])
        pb = clamp(self.p_sum - pa, 0.0, c["p_supply"])
        return pa, pb

    # --- hoofdfunctie ------------------------------------------------------------
    def update(self, dt, L, pa, pb):
        """Eén regelstap. L in mm (pen-pen), drukken in bar overdruk.

        Geeft (vul_a, leeg_a, vul_b, leeg_b) als duty 0..1.
        """
        fa, va, fb, vb = self._update(dt, L, pa, pb)
        c = self.cfg
        if pa > c["p_max"]:
            fa, va = 0.0, 1.0
        if pb > c["p_max"]:
            fb, vb = 0.0, 1.0
        return fa, va, fb, vb

    def _update(self, dt, L, pa, pb):
        """Eén regelstap. L in mm (pen-pen), drukken in bar overdruk.

        Geeft (vul_a, leeg_a, vul_b, leeg_b) als duty 0..1.
        """
        c = self.cfg
        # snelheid (gefilterd), ook buiten POSITION bijhouden
        if self.last_L is not None and dt > 0:
            v = (L - self.last_L) / dt
            self.v_filt += (v - self.v_filt) * clamp(dt * c["v_filter_hz"] * 6.283, 0.0, 1.0)
        self.last_L = L

        # overdruk: het leegventiel van die kamer openen (ontlasten). Korte pieken ontstaan
        # als de cilinder lucht samendrukt, bijv. bij doorschieten. Houdt het langer dan
        # p_max_time aan, dan staat de drukregelaar te hoog: fout.
        relief_a = pa > c["p_max"]
        relief_b = pb > c["p_max"]
        if relief_a or relief_b:
            self.over_t += dt
            if self.over_t > c["p_max_time"]:
                self.fault = "overdruk (drukregelaar te hoog?)"
        else:
            self.over_t = 0.0
        if L < c["L_min"] - 20 or L > c["L_max"] + 20:
            self.fault = "positiesensor buiten bereik"
        if self.fault:
            self.mode = OFF
            # bij een fout: alles dicht (cilinder houdt zijn lucht vast)
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
        # doel met begrensde snelheid laten meelopen (geen sprong in de regelfout)
        if self.ref_now is None:
            self.ref_now = L
        step = c["v_max"] * dt
        self.ref_now += clamp(target - self.ref_now, -step, step)
        ref = self.ref_now if self.mode == POSITION else target
        e = ref - L
        if self.mode == BANGBANG:
            # T2: vol open/dicht met dode zone, zonder PWM-fijnregeling
            db = c["bangbang_deadband"]
            if e > db:
                return 1.0, 0.0, 0.0, 1.0
            if e < -db:
                return 0.0, 1.0, 1.0, 0.0
            return 0.0, 0.0, 0.0, 0.0

        # POSITION
        # In positie en stil: alle ventielen dicht, de opgesloten lucht houdt de arm vast.
        # Dat spaart lucht en ventielen. Pas bij een fout > pos_deadband_out weer regelen.
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
        # integreren vlak bij het doel, of als de arm stilstaat zonder het doel te halen
        # (zware last): overwint wrijving en zwaartekracht zonder doorschot
        if abs(e) < c["i_zone"] or abs(self.v_filt) < c["v_hold"]:
            self.integral = clamp(self.integral + e * dt, -c["i_limit"], c["i_limit"])
        force = c["kp_force"] * e + c["ki_force"] * self.integral - c["kd_force"] * self.v_filt
        self.force = clamp(force, f_min, f_max)
        self.p_des = self._pressures_for_force(self.force)
        fa, va = self._chamber(self.p_des[0], pa)
        fb, vb = self._chamber(self.p_des[1], pb)
        return fa, va, fb, vb

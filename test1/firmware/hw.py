"""Pico 2 hardware: valves (PWM through the ULN2803A) and sensors (ADC).

MicroPython on the Pico only. The simulation does not use this file.
"""
import json

from machine import ADC, PWM, Pin

VREF = 3.3
CAL_FILE = "cal.json"


class Valves:
    """Four valves: fill A, vent A, fill B, vent B. Duty 0..1."""

    def __init__(self, pins, freq):
        self.pwm = []
        for name in ("fill_a", "vent_a", "fill_b", "vent_b"):
            p = PWM(Pin(pins[name]))
            p.freq(freq)
            p.duty_u16(0)
            self.pwm.append(p)
        self.duty = [0.0, 0.0, 0.0, 0.0]

    def set(self, duties):
        fa, va, fb, vb = duties
        # never fill and vent the same chamber at the same time
        if fa > 0 and va > 0:
            va = 0.0
        if fb > 0 and vb > 0:
            vb = 0.0
        self.duty = [fa, va, fb, vb]
        for p, d in zip(self.pwm, self.duty):
            p.duty_u16(int(max(0.0, min(1.0, d)) * 65535))

    def off(self):
        self.set((0.0, 0.0, 0.0, 0.0))


class Sensors:
    """Potentiometer (position) and two pressure sensors, with calibration."""

    def __init__(self, cfg):
        self.cfg = cfg
        pins = cfg["pins"]
        self.adc_pos = ADC(Pin(pins["adc_pos"]))
        self.adc_pa = ADC(Pin(pins["adc_pa"]))
        self.adc_pb = ADC(Pin(pins["adc_pb"]))
        r1, r2 = cfg["divider"]
        self.div = (r1 + r2) / r2
        self.cal = dict(pot_v_retracted=cfg["pot_v_retracted"], pot_v_per_mm=cfg["pot_v_per_mm"],
                        p_v_zero=list(cfg["p_v_zero"]), p_v_per_bar=list(cfg["p_v_per_bar"]))
        self.load()

    @staticmethod
    def _volts(adc, n=4):
        s = 0
        for _ in range(n):
            s += adc.read_u16()
        return s / n / 65535 * VREF

    def raw(self):
        """Voltages: potentiometer, sensor A, sensor B (sensor voltage before the divider)."""
        return (self._volts(self.adc_pos),
                self._volts(self.adc_pa) * self.div,
                self._volts(self.adc_pb) * self.div)

    def read(self):
        """(L in mm pin to pin, pa, pb in bar gauge)."""
        vpos, va, vb = self.raw()
        c = self.cal
        ext = (vpos - c["pot_v_retracted"]) / c["pot_v_per_mm"]
        L = self.cfg["L_min"] + ext
        pa = (va - c["p_v_zero"][0]) / c["p_v_per_bar"][0]
        pb = (vb - c["p_v_zero"][1]) / c["p_v_per_bar"][1]
        return L, pa, pb

    def load(self):
        try:
            with open(CAL_FILE) as f:
                self.cal.update(json.load(f))
        except OSError:
            pass

    def save(self):
        with open(CAL_FILE, "w") as f:
            json.dump(self.cal, f)

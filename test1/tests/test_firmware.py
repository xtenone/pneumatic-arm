"""Run the Pico firmware on the PC with simulated hardware (a fake machine module).

Checks that main.py, hw.py, control.py and config.py work together: commands,
safety (fill+vent at the same time, PC watchdog, over-pressure) and calibration.
Usage:  python tests/test_firmware.py
"""
import io
import os
import sys
import time
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FW = os.path.join(ROOT, "firmware")


def install_fakes(adc_values):
    m = types.ModuleType("machine")

    class Pin:
        def __init__(self, n, *a, **k):
            self.n = n

    class PWM:
        log = {}

        def __init__(self, pin):
            self.pin = pin.n
            PWM.log[self.pin] = 0

        def freq(self, f):
            self.f = f

        def duty_u16(self, d):
            PWM.log[self.pin] = d

    class ADC:
        def __init__(self, pin):
            self.pin = pin.n

        def read_u16(self):
            return int(adc_values[self.pin] / 3.3 * 65535)

    class WDT:
        started = False

        def __init__(self, timeout):
            WDT.started = True

        def feed(self):
            pass

    m.Pin, m.PWM, m.ADC, m.WDT = Pin, PWM, ADC, WDT
    sys.modules["machine"] = m
    # MicroPython time functions on top of CPython's time module
    time.ticks_ms = lambda: int(time.monotonic() * 1000)
    time.ticks_us = lambda: int(time.monotonic() * 1e6)
    time.ticks_diff = lambda a, b: a - b
    time.ticks_add = lambda a, b: a + b
    time.sleep_us = lambda us: time.sleep(us / 1e6)
    return PWM, WDT


def main():
    adc = {26: 1.0, 27: 0.5 * 15 / 25, 28: 0.5 * 15 / 25}   # potentiometer 1 V, sensors 0 bar
    PWM, WDT = install_fakes(adc)
    sys.path.insert(0, FW)
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    os.chdir(os.path.join(ROOT, "out"))                       # cal.json ends up here
    src = open(os.path.join(FW, "main.py")).read().replace("\ntry:\n    run()\nfinally:\n    valves.off()\n", "\n")
    out = io.StringIO()
    real_stdout = sys.stdout
    g = {"__name__": "firmware_main"}
    sys.stdout = out
    try:
        exec(compile(src, "main.py", "exec"), g)
    finally:
        sys.stdout = real_stdout
    ctl, valves, sensors, handle, control = g["ctl"], g["valves"], g["sensors"], g["handle"], g["control"]
    ok = True

    def check(cond, text):
        nonlocal ok
        print(("OK   " if cond else "FAIL ") + text)
        ok &= bool(cond)

    # 1. everything closed after start-up
    check(all(v == 0 for v in PWM.log.values()), "all valves closed after start-up")
    # 2. manual fill and vent at the same time is refused
    handle("valve 1 1 0 0")
    duty = ctl.update(0.002, *sensors.read())
    valves.set(duty)
    check(duty[0] > 0 and duty[1] == 0, "fill A and vent A together: vent A stays closed")
    check(WDT.started, "hardware watchdog starts at the first motion command")
    # 3. position control targets above the current position when the arm is too low
    handle("angle 30")
    duty = ctl.update(0.002, *sensors.read())
    check(ctl.mode == control.POSITION and ctl.ref > sensors.read()[0], "angle 30: target above the current position")
    # 4. over-pressure: the vent valve of that chamber opens
    adc[27] = 7.0 * 0.58 * 15 / 25 + 0.3                     # well above p_max
    duty = ctl.update(0.002, *sensors.read())
    check(duty[1] == 1.0 and duty[0] == 0.0, "over-pressure in chamber A: vent valve A open")
    adc[27] = 0.5 * 15 / 25
    # 5. calibration
    handle("zero")
    L, pa, pb = sensors.read()
    check(abs(pa) < 0.01 and abs(pb) < 0.01, "after 'zero' the pressure sensors read 0 bar")
    handle("cal_pos in")
    check(abs(sensors.read()[0] - g["CFG"]["L_min"]) < 0.01, "after 'cal_pos in' the length is L_min")
    # 6. move (T8): smooth profile from the current position, speed and load commands
    handle("load 2")
    check(g["CFG"]["load_kg"] == 2.0, "load 2: feedforward uses 2 kg")
    handle("speed 0.9")
    w0, a0, j0 = g["MOVE_LIMITS"]
    cfg = g["CFG"]
    check(abs(cfg["move_w_max"] - 0.9 * w0) < 1e-6 and abs(cfg["move_alpha_max"] - 0.81 * a0) < 1e-6
          and abs(cfg["move_jerk_max"] - 0.729 * j0) < 1e-6, "speed 0.9: speed × 0.9, acceleration × 0.81, jerk × 0.729")
    sys.stdout = io.StringIO()
    handle("speed 3")
    msg = sys.stdout.getvalue()
    sys.stdout = real_stdout
    check("ERROR" in msg and abs(cfg["move_w_max"] - 0.9 * w0) < 1e-6, "speed 3 is refused")
    L0 = sensors.read()[0]
    handle("move 30")
    refs = []
    for _ in range(50):
        ctl.update(0.002, *sensors.read())
        refs.append(ctl.ref_now)
    check(ctl.mode == control.MOVE and abs(refs[0] - L0) < 0.05, "move 30: the profile starts at the current position")
    check(all(b >= a for a, b in zip(refs, refs[1:])) and L0 < refs[-1] < ctl.ref,
          "move 30: the profile rises smoothly towards the target")
    handle("speed 1")
    handle("load 1")
    # 7. PC watchdog
    g["last_msg"] = time.ticks_ms() - 10_000
    handle("angle 10")
    g["last_msg"] = time.ticks_ms() - 10_000
    sys.stdout = io.StringIO()
    g["pc_watchdog"]()
    sys.stdout = real_stdout
    check(ctl.mode == control.OFF, "no ping from the PC: valves closed")
    # 8. an unknown command breaks nothing
    sys.stdout = io.StringIO()
    handle("fly")
    msg = sys.stdout.getvalue()
    sys.stdout = real_stdout
    check("ERROR" in msg, "unknown command gives ERROR")
    print("\nall good" if ok else "\nthere are failures")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

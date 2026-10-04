"""Draai de Pico-firmware op de pc met nagebootste hardware (machine-module).

Controleert dat main.py, hw.py, control.py en config.py samen werken:
commando's, veiligheid (vullen+legen tegelijk, watchdog van de pc, overdruk)
en de kalibratie. Gebruik:  python tests/test_firmware.py
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
    # MicroPython-tijdfuncties op de CPython-time-module
    time.ticks_ms = lambda: int(time.monotonic() * 1000)
    time.ticks_us = lambda: int(time.monotonic() * 1e6)
    time.ticks_diff = lambda a, b: a - b
    time.ticks_add = lambda a, b: a + b
    time.sleep_us = lambda us: time.sleep(us / 1e6)
    return PWM, WDT


def main():
    adc = {26: 1.0, 27: 0.5 * 15 / 25, 28: 0.5 * 15 / 25}   # potmeter 1 V, sensoren 0 bar
    PWM, WDT = install_fakes(adc)
    sys.path.insert(0, FW)
    os.chdir(os.path.join(ROOT, "out"))                       # cal.json komt hier terecht
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
        print(("OK   " if cond else "FOUT ") + text)
        ok &= bool(cond)

    # 1. na het opstarten alles dicht
    check(all(v == 0 for v in PWM.log.values()), "na opstarten alle ventielen dicht")
    # 2. handmatig vullen en legen tegelijk wordt geweigerd
    handle("klep 1 1 0 0")
    duty = ctl.update(0.002, *sensors.read())
    valves.set(duty)
    check(duty[0] > 0 and duty[1] == 0, "vul A en leeg A tegelijk: leeg A blijft dicht")
    check(WDT.started, "hardware-watchdog start bij het eerste bewegingscommando")
    # 3. positieregeling geeft een kracht naar boven als de arm te laag staat
    handle("hoek 30")
    duty = ctl.update(0.002, *sensors.read())
    check(ctl.mode == control.POSITION and ctl.ref > sensors.read()[0], "hoek 30: doel boven de huidige stand")
    # 4. overdruk: leegventiel van die kamer gaat open
    adc[27] = 7.0 * 0.58 * 15 / 25 + 0.3                     # ruim boven p_max
    duty = ctl.update(0.002, *sensors.read())
    check(duty[1] == 1.0 and duty[0] == 0.0, "overdruk in kamer A: leegventiel A open")
    adc[27] = 0.5 * 15 / 25
    # 5. kalibratie
    handle("nul")
    L, pa, pb = sensors.read()
    check(abs(pa) < 0.01 and abs(pb) < 0.01, "na 'nul' lezen de druksensoren 0 bar")
    handle("kal_pos in")
    check(abs(sensors.read()[0] - g["CFG"]["L_min"]) < 0.01, "na 'kal_pos in' is de lengte L_min")
    # 6. watchdog van de pc
    g["last_msg"] = time.ticks_ms() - 10_000
    handle("hoek 10")
    g["last_msg"] = time.ticks_ms() - 10_000
    sys.stdout = io.StringIO()
    g["pc_watchdog"]()
    sys.stdout = real_stdout
    check(ctl.mode == control.OFF, "geen ping van de pc: ventielen dicht")
    # 7. onbekend commando breekt niets
    sys.stdout = io.StringIO()
    handle("vlieg")
    msg = sys.stdout.getvalue()
    sys.stdout = real_stdout
    check("FOUT" in msg, "onbekend commando geeft FOUT")
    print("\nalles in orde" if ok else "\ner zijn fouten")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

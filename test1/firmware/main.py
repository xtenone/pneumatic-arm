"""Firmware test 1: arm met één vrijheidsgraad, pneumatische cilinder met 4 ventielen.

Bediening via USB (seriële poort, 115200, regels tekst). Zie de handleiding voor alle
commando's; 'help' toont ze ook. De Pico stuurt meetregels:
  D,tijd_ms,L_mm,hoek_graden,pa_bar,pb_bar,vul_a,leeg_a,vul_b,leeg_b,modus,doel_mm,fout

Veiligheid:
- Na het opstarten en bij elke fout staan alle ventielen dicht.
- Krijgt de Pico in een actieve modus langer dan watchdog_ms geen bericht van de pc
  (de pc stuurt 'ping'), dan gaan alle ventielen dicht.
- Loopt het programma vast, dan herstart de hardware-watchdog de Pico (ventielen dicht).
  De watchdog start bij het eerste bewegingscommando, zodat je de Pico daarvoor rustig
  met Thonny kunt bijwerken.
- De noodstop onderbreekt de 24 V in hardware, los van deze software.
"""
import math
import select
import sys
import time

from machine import WDT

import control
from config import CFG
from hw import Sensors, Valves

valves = Valves(CFG["pins"], CFG["pwm_hz"])
valves.off()
sensors = Sensors(CFG)
ctl = control.Controller(CFG)
wdt = None   # hardware-watchdog, start bij het eerste actieve commando (zie start_watchdog)

poll = select.poll()
poll.register(sys.stdin, select.POLLIN)
line_buf = ""
last_msg = time.ticks_ms()
stream_every = max(1, CFG["loop_hz"] // 100)     # standaard 100 meetregels per seconde


def angle(L):
    a, b = CFG["hinge_to_rear"], CFG["hinge_to_attach"]
    s = (L * L - a * a - b * b) / (2 * a * b)
    return math.degrees(math.asin(max(-1.0, min(1.0, s))))


def length(theta):
    a, b = CFG["hinge_to_rear"], CFG["hinge_to_attach"]
    return math.sqrt(a * a + b * b + 2 * a * b * math.sin(math.radians(theta)))


def start_watchdog():
    """Start de hardware-watchdog. Eenmaal gestart kan hij niet meer uit: na stoppen in
    Thonny herstart de Pico binnen 2 s vanzelf (met alle ventielen dicht)."""
    global wdt
    if wdt is None:
        wdt = WDT(timeout=2000)


def say(*parts):
    print(",".join(str(p) for p in parts))


def pulse_capture(channel, ms):
    """T1: één ventiel `ms` milliseconden open en de druk snel meten (≈ 5 kHz, 80 ms)."""
    valves.off()
    adc = sensors.adc_pa if channel in (0, 1) else sensors.adc_pb
    samples = []
    t0 = time.ticks_us()
    duty = [0.0, 0.0, 0.0, 0.0]
    duty[channel] = 1.0
    opened = False
    while time.ticks_diff(time.ticks_us(), t0) < 80_000:
        t = time.ticks_diff(time.ticks_us(), t0)
        if not opened and t >= 5_000:
            valves.set(duty)
            opened = True
        if opened and t >= 5_000 + ms * 1000:
            valves.off()
        samples.append((t, adc.read_u16()))
    valves.off()
    for t, v in samples:
        say("P", t, round(v / 65535 * 3.3 * sensors.div, 4))
    say("PEINDE", channel, ms)


HELP = """commando's:
  off                     alle ventielen dicht
  hoek <graden>           arm naar hoek (positieregeling)
  pos <mm>                cilinder naar lengte pen-pen
  bang <graden>           aan/uit-regeling (T2)
  druk <pa> <pb>          kamerdrukken regelen (bar overdruk)
  klep <va> <la> <vb> <lb>  duty per ventiel 0..1 (handmatig)
  puls <0-3> <ms>         één ventiel kort open, druk snel meten (T1)
  som <bar>               som kamerdrukken = stijfheid
  nul                     druksensoren op 0 bar zetten (geen druk op de cilinder!)
  kal_druk <bar>          versterking druksensoren (beide kamers op die druk, zie manometer)
  kal_pos in|uit          potmeter: cilinder helemaal in / helemaal uit
  opslaan                 kalibratie bewaren (cal.json)
  stream <hz>             meetregels per seconde (0 = uit)
  info                    instellingen en kalibratie
  ping                    'ik leef nog' van de pc"""


def handle(cmd):
    global stream_every
    p = cmd.split()
    if not p:
        return
    c = p[0]
    try:
        if c == "ping":
            return
        if c in ("hoek", "pos", "bang", "druk", "klep", "puls"):
            start_watchdog()
        if c == "off":
            ctl.set_mode(control.OFF)
        elif c == "hoek":
            ctl.set_mode(control.POSITION, length(float(p[1])))
        elif c == "pos":
            ctl.set_mode(control.POSITION, float(p[1]))
        elif c == "bang":
            ctl.set_mode(control.BANGBANG, length(float(p[1])))
        elif c == "druk":
            ctl.set_mode(control.PRESSURE, (float(p[1]), float(p[2])))
        elif c == "klep":
            ctl.set_mode(control.MANUAL, tuple(float(x) for x in p[1:5]))
        elif c == "puls":
            ctl.set_mode(control.OFF)
            pulse_capture(int(p[1]), float(p[2]))
        elif c == "som":
            ctl.p_sum = float(p[1])
        elif c == "nul":
            _, va, vb = sensors.raw()
            sensors.cal["p_v_zero"] = [va, vb]
            say("OK", "nul", round(va, 4), round(vb, 4))
        elif c == "kal_druk":
            bar = float(p[1])
            _, va, vb = sensors.raw()
            z = sensors.cal["p_v_zero"]
            sensors.cal["p_v_per_bar"] = [(va - z[0]) / bar, (vb - z[1]) / bar]
            say("OK", "kal_druk", sensors.cal["p_v_per_bar"])
        elif c == "kal_pos":
            vpos, _, _ = sensors.raw()
            if p[1] == "in":
                sensors.cal["pot_v_retracted"] = vpos
            else:
                # helemaal uit = volle cilinderslag (L_max - L_min)
                sensors.cal["pot_v_per_mm"] = (vpos - sensors.cal["pot_v_retracted"]) / (CFG["L_max"] - CFG["L_min"])
            say("OK", "kal_pos", p[1], round(vpos, 4))
        elif c == "opslaan":
            sensors.save()
            say("OK", "opslaan")
        elif c == "stream":
            hz = float(p[1])
            stream_every = 0 if hz <= 0 else max(1, int(CFG["loop_hz"] / hz))
        elif c == "info":
            say("INFO", CFG)
            say("CAL", sensors.cal)
        elif c == "help":
            print(HELP)
        else:
            say("FOUT", "onbekend commando", c)
            return
        say("OK", c)
    except Exception as e:  # noqa: BLE001 — verkeerde invoer mag de lus niet stoppen
        say("FOUT", c, e)


def read_commands():
    global line_buf, last_msg
    while poll.poll(0):
        ch = sys.stdin.read(1)
        if ch in ("\n", "\r"):
            if line_buf:
                last_msg = time.ticks_ms()
                handle(line_buf.strip())
            line_buf = ""
        else:
            line_buf += ch


def pc_watchdog():
    """Ventielen dicht als de pc in een actieve modus te lang niets stuurt."""
    if ctl.mode != control.OFF and time.ticks_diff(time.ticks_ms(), last_msg) > CFG["watchdog_ms"]:
        ctl.set_mode(control.OFF)
        say("FOUT", "geen contact met de pc: ventielen dicht")


def run():
    period_us = 1_000_000 // CFG["loop_hz"]
    t_next = time.ticks_us()
    t_start = time.ticks_ms()
    n = 0
    say("OK", "gestart", "typ 'help'")
    while True:
        if wdt is not None:
            wdt.feed()
        read_commands()
        pc_watchdog()
        L, pa, pb = sensors.read()
        duty = ctl.update(period_us / 1e6, L, pa, pb)
        valves.set(duty)
        n += 1
        if stream_every and n % stream_every == 0:
            ref = ctl.ref if ctl.ref is not None else 0.0
            d = valves.duty
            say("D", time.ticks_diff(time.ticks_ms(), t_start), round(L, 2), round(angle(L), 2),
                round(pa, 3), round(pb, 3), round(d[0], 2), round(d[1], 2), round(d[2], 2), round(d[3], 2),
                ctl.mode, round(ref, 2), ctl.fault)
        t_next = time.ticks_add(t_next, period_us)
        wait = time.ticks_diff(t_next, time.ticks_us())
        if wait > 0:
            time.sleep_us(wait)
        else:
            t_next = time.ticks_us()


try:
    run()
finally:
    valves.off()

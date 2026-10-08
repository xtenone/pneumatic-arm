"""Firmware for test 1: arm with one degree of freedom, pneumatic cylinder with 4 valves.

Control over USB (serial port, 115200 baud, lines of text). See the manual for all
commands; 'help' lists them too. The Pico sends data lines:
  D,time_ms,L_mm,angle_deg,pa_bar,pb_bar,fill_a,vent_a,fill_b,vent_b,mode,target_mm,fault,profile_mm
(profile_mm: where the target is now, along the profile of `move` or the ramp of `angle`)

Safety:
- After start-up and on every fault all valves are closed.
- If the Pico gets no message from the PC for longer than watchdog_ms while in an
  active mode (the PC sends 'ping'), all valves close.
- If the program hangs, the hardware watchdog resets the Pico (valves closed).
  The watchdog starts at the first motion command, so you can update the Pico with
  Thonny before that without it resetting.
- The emergency stop cuts the 24 V in hardware, independent of this software.
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
wdt = None   # hardware watchdog, started at the first active command (see start_watchdog)

poll = select.poll()
poll.register(sys.stdin, select.POLLIN)
line_buf = ""
last_msg = time.ticks_ms()
stream_every = max(1, CFG["loop_hz"] // 100)     # default about 100 data lines per second (125 at 250 Hz)
MOVE_LIMITS = (CFG["move_w_max"], CFG["move_alpha_max"], CFG["move_jerk_max"])   # at speed 1
GAINS = (CFG["kp_force"], CFG["ki_force"], CFG["kd_force"])                        # at gain 1
loop_stats = [0, 0, 0]      # steps, steps longer than the period, longest step (µs); shown and reset by 'info'


def angle(L):
    a, b = CFG["hinge_to_rear"], CFG["hinge_to_attach"]
    s = (L * L - a * a - b * b) / (2 * a * b)
    return math.degrees(math.asin(max(-1.0, min(1.0, s))))


def length(theta):
    a, b = CFG["hinge_to_rear"], CFG["hinge_to_attach"]
    return math.sqrt(a * a + b * b + 2 * a * b * math.sin(math.radians(theta)))


def start_watchdog():
    """Start the hardware watchdog. Once started it cannot be stopped: after stopping in
    Thonny the Pico resets itself within 2 s (with all valves closed)."""
    global wdt
    if wdt is None:
        wdt = WDT(timeout=2000)


def say(*parts):
    print(",".join(str(p) for p in parts))


def pulse_capture(channel, ms):
    """T1: open one valve for `ms` milliseconds and sample the pressure fast (≈ 5 kHz, 80 ms)."""
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
    say("PEND", channel, ms)


HELP = """commands:
  off                         close all valves
  angle <deg>                 move the arm to an angle (position control)
  move <deg>                  move the arm to an angle fast and smoothly (profile + feedforward, T8)
  load <kg>                   load on the arm, for the feedforward of move
  speed <factor>              speed of move, 1 = as tuned (0.9 = 10% slower)
  gain <factor>               strength of the position control, 1 = as tuned (0.5 without load)
  pos <mm>                    move the cylinder to a pin-to-pin length
  bang <deg>                  on/off control (T2)
  pressure <pa> <pb>          control the chamber pressures (bar gauge)
  valve <fa> <va> <fb> <vb>   duty per valve 0..1 (manual)
  pulse <0-3> <ms>            open one valve briefly, sample the pressure fast (T1)
  stiffness <bar>             sum of the chamber pressures
  zero                        set the pressure sensors to 0 bar (no pressure on the cylinder!)
  cal_pressure <bar>          pressure sensor gain (both chambers at that pressure, see gauge)
  cal_pos in|out              potentiometer: cylinder fully in / fully out
  save                        store the calibration (cal.json)
  stream <hz>                 data lines per second (0 = off)
  info                        settings and calibration
  ping                        'still alive' from the PC"""


def handle(cmd):
    global stream_every
    p = cmd.split()
    if not p:
        return
    c = p[0]
    try:
        if c == "ping":
            return
        if c in ("angle", "move", "pos", "bang", "pressure", "valve", "pulse"):
            start_watchdog()
        if c == "off":
            ctl.set_mode(control.OFF)
        elif c == "angle":
            ctl.set_mode(control.POSITION, length(float(p[1])))
        elif c == "move":
            ctl.set_mode(control.MOVE, length(float(p[1])))
        elif c == "load":
            ctl.cfg["load_kg"] = float(p[1])
        elif c == "speed":
            k = float(p[1])
            if not 0.1 <= k <= 1.2:
                raise ValueError("speed between 0.1 and 1.2")
            w, al, j = MOVE_LIMITS
            ctl.cfg["move_w_max"], ctl.cfg["move_alpha_max"], ctl.cfg["move_jerk_max"] = w * k, al * k * k, j * k ** 3
        elif c == "gain":
            k = float(p[1])
            if not 0.2 <= k <= 1.5:
                raise ValueError("gain between 0.2 and 1.5")
            kp, ki, kd = GAINS
            ctl.cfg["kp_force"], ctl.cfg["ki_force"], ctl.cfg["kd_force"] = kp * k, ki * k, kd * k
        elif c == "pos":
            ctl.set_mode(control.POSITION, float(p[1]))
        elif c == "bang":
            ctl.set_mode(control.BANGBANG, length(float(p[1])))
        elif c == "pressure":
            ctl.set_mode(control.PRESSURE, (float(p[1]), float(p[2])))
        elif c == "valve":
            ctl.set_mode(control.MANUAL, tuple(float(x) for x in p[1:5]))
        elif c == "pulse":
            ctl.set_mode(control.OFF)
            pulse_capture(int(p[1]), float(p[2]))
        elif c == "stiffness":
            ctl.p_sum = float(p[1])
        elif c == "zero":
            _, va, vb = sensors.raw()
            sensors.cal["p_v_zero"] = [va, vb]
            say("OK", "zero", round(va, 4), round(vb, 4))
        elif c == "cal_pressure":
            bar = float(p[1])
            _, va, vb = sensors.raw()
            z = sensors.cal["p_v_zero"]
            sensors.cal["p_v_per_bar"] = [(va - z[0]) / bar, (vb - z[1]) / bar]
            say("OK", "cal_pressure", sensors.cal["p_v_per_bar"])
        elif c == "cal_pos":
            vpos, _, _ = sensors.raw()
            if p[1] == "in":
                sensors.cal["pot_v_retracted"] = vpos
            else:
                # fully out = full cylinder stroke (L_max - L_min)
                sensors.cal["pot_v_per_mm"] = (vpos - sensors.cal["pot_v_retracted"]) / (CFG["L_max"] - CFG["L_min"])
            say("OK", "cal_pos", p[1], round(vpos, 4))
        elif c == "save":
            sensors.save()
            say("OK", "save")
        elif c == "stream":
            hz = float(p[1])
            stream_every = 0 if hz <= 0 else max(1, int(CFG["loop_hz"] / hz))
        elif c == "info":
            say("INFO", CFG)
            say("CAL", sensors.cal)
            say("LOOP", "steps", loop_stats[0], "too_long", loop_stats[1], "longest_us", loop_stats[2])
            loop_stats[:] = [0, 0, 0]
        elif c == "help":
            print(HELP)
        else:
            say("ERROR", "unknown command", c)
            return
        say("OK", c)
    except Exception as e:  # noqa: BLE001 — bad input must not stop the loop
        say("ERROR", c, e)


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
    """Close the valves if the PC sends nothing for too long while in an active mode."""
    if ctl.mode != control.OFF and time.ticks_diff(time.ticks_ms(), last_msg) > CFG["watchdog_ms"]:
        ctl.set_mode(control.OFF)
        say("ERROR", "no contact with the PC: valves closed")


def run():
    period_us = 1_000_000 // CFG["loop_hz"]
    t_next = time.ticks_us()
    t_last = t_next
    t_start = time.ticks_ms()
    n = 0
    say("OK", "started", "type 'help'")
    while True:
        t_loop = time.ticks_us()
        if wdt is not None:
            wdt.feed()
        read_commands()
        pc_watchdog()
        L, pa, pb = sensors.read()
        now = time.ticks_us()
        dt = time.ticks_diff(now, t_last) / 1e6      # real time since the last step (memory clean-up can pause the loop)
        t_last = now
        duty = ctl.update(min(max(dt, 1e-4), 0.05), L, pa, pb)
        valves.set(duty)
        n += 1
        if stream_every and n % stream_every == 0:
            ref = ctl.ref if ctl.ref is not None else 0.0
            prof = ctl.ref_now if ctl.ref_now is not None else ref
            d = valves.duty
            # % formatting: about 3× faster than joining str() of every field
            print("D,%d,%.2f,%.2f,%.3f,%.3f,%.2f,%.2f,%.2f,%.2f,%s,%.2f,%s,%.2f" % (
                time.ticks_diff(time.ticks_ms(), t_start), L, angle(L), pa, pb, d[0], d[1], d[2], d[3],
                ctl.mode, ref, ctl.fault, prof))
        busy = time.ticks_diff(time.ticks_us(), t_loop)
        loop_stats[0] += 1
        if busy > period_us:
            loop_stats[1] += 1
        if busy > loop_stats[2]:
            loop_stats[2] = busy
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

"""Pneumatics model: 2 cylinder chambers, 4 on/off valves, supply and exhaust.

Flow according to ISO 6358 (sonic conductance C, critical pressure ratio b).
Chamber pressure, polytropic: dp/dt = n/V · (R·T·ṁ − p·dV/dt).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import params as P  # noqa: E402

R = 287.0
RHO0 = 1.185          # kg/m³, standard air (ISO 8778)
BAR = 1e5


def mass_flow(p_up, p_down, C_dm3, b):
    """kg/s from p_up to p_down (Pa absolute); 0 if p_up <= p_down."""
    if p_up <= p_down:
        return 0.0
    r = p_down / p_up
    C = C_dm3 * 1e-3 / BAR      # m³/(s·Pa)
    if r <= b:
        phi = 1.0
    else:
        phi = math.sqrt(max(0.0, 1.0 - ((r - b) / (1.0 - b)) ** 2))
    return C * p_up * RHO0 * phi * math.sqrt(293.15 / P.T_AIR)


class Valve:
    """On/off valve with opening and closing delay."""

    def __init__(self):
        self.cmd = False
        self.open = False
        self.t_change = 0.0

    def step(self, t, cmd):
        if cmd != self.cmd:
            self.cmd = cmd
            self.t_change = t
        delay = P.VALVE["t_on"] if self.cmd else P.VALVE["t_off"]
        if self.open != self.cmd and t - self.t_change >= delay:
            self.open = self.cmd


class Pneumatics:
    def __init__(self, p_supply_bar=P.P_SUPPLY):
        self.p_sup = (p_supply_bar + P.P_ATM) * BAR
        self.p_atm = P.P_ATM * BAR
        self.pa = self.p_atm
        self.pb = self.p_atm
        self.valves = [Valve() for _ in range(4)]   # fill A, vent A, fill B, vent B
        self.air_used = 0.0                           # kg taken from the supply

    def volumes(self, ext_m):
        """Chamber volumes (m³) at extension ext (m)."""
        dead = P.DEAD_VOLUME * 1e-6
        aa = P.AREA_A * 1e-6
        ab = P.AREA_B * 1e-6
        s = P.CYL["stroke"] * 1e-3
        return dead + aa * ext_m, dead + ab * (s - ext_m)

    def step(self, t, dt, ext_m, vel_ms, cmds):
        for v, c in zip(self.valves, cmds):
            v.step(t, c)
        C, b = P.VALVE["sonic_conductance"], P.VALVE["critical_ratio"]
        fa, va, fb, vb = (v.open for v in self.valves)
        mA = (mass_flow(self.p_sup, self.pa, C, b) if fa else 0.0) - (mass_flow(self.pa, self.p_atm, C, b) if va else 0.0)
        mB = (mass_flow(self.p_sup, self.pb, C, b) if fb else 0.0) - (mass_flow(self.pb, self.p_atm, C, b) if vb else 0.0)
        self.air_used += ((mass_flow(self.p_sup, self.pa, C, b) if fa else 0.0)
                          + (mass_flow(self.p_sup, self.pb, C, b) if fb else 0.0)) * dt
        Va, Vb = self.volumes(ext_m)
        aa = P.AREA_A * 1e-6
        ab = P.AREA_B * 1e-6
        n = P.POLYTROPIC
        self.pa += n / Va * (R * P.T_AIR * mA - self.pa * aa * vel_ms) * dt
        self.pb += n / Vb * (R * P.T_AIR * mB + self.pb * ab * vel_ms) * dt
        self.pa = max(self.pa, 0.2 * BAR)
        self.pb = max(self.pb, 0.2 * BAR)

    def force(self):
        """Force on the rod (N), positive = extending."""
        return ((self.pa - self.p_atm) * P.AREA_A - (self.pb - self.p_atm) * P.AREA_B) * 1e-6

    def gauge(self):
        return (self.pa - self.p_atm) / BAR, (self.pb - self.p_atm) / BAR

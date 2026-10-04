"""Schrijf firmware/config.py uit params.py (de Pico kent params.py niet)."""
import os

import params as P

HERE = os.path.dirname(os.path.abspath(__file__))


def config_dict():
    return dict(
        # regeling
        p_sum=P.P_SUM, p_deadband=P.P_DEADBAND, kp_pressure=P.KP_PRESSURE,
        d_min=round(P.VALVE["t_on"] * P.PWM_HZ * 1.15, 3),   # kortste puls die het ventiel echt opent
        kp_force=P.KP_FORCE, ki_force=P.KI_FORCE, kd_force=P.KD_FORCE, i_limit=3.0, i_zone=4.0,
        v_filter_hz=10.0, bangbang_deadband=3.0, soft_limit=P.SOFT_LIMIT,
        p_supply=P.P_SUPPLY, p_max=P.P_MAX, p_max_time=0.5,
        v_max=P.V_MAX, pos_deadband=0.3, pos_deadband_out=0.6, v_hold=5.0,
        area_a=round(P.AREA_A, 3), area_b=round(P.AREA_B, 3),
        L_min=round(P.PIN_TO_PIN_MIN, 2), L_max=round(P.PIN_TO_PIN_MAX, 2),
        # geometrie (hoek uit lengte)
        hinge_to_rear=P.HINGE[1] - P.REAR_PIVOT[1], hinge_to_attach=P.ARM_ATTACH,
        # hardware
        pwm_hz=P.PWM_HZ, loop_hz=P.LOOP_HZ, pins=P.PINS,
        divider=P.DIVIDER, adc_vref=P.ADC_VREF,
        pot_stroke=P.POT["stroke"],
        # kalibratie (wordt overschreven door het 'cal'-commando, opgeslagen in cal.json)
        pot_v_retracted=0.30, pot_v_per_mm=3.3 / P.POT["stroke"],
        p_v_zero=(0.5, 0.5), p_v_per_bar=(4.0 / 6.895, 4.0 / 6.895),
        watchdog_ms=500,
    )


def write():
    cfg = config_dict()
    lines = ['"""Gegenereerd door gen_config.py uit params.py — niet met de hand wijzigen."""', "", "CFG = {"]
    for k, v in cfg.items():
        lines.append(f"    {k!r}: {v!r},")
    lines.append("}")
    path = os.path.join(HERE, "firmware", "config.py")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


if __name__ == "__main__":
    print(write())

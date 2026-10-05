"""Tests T0–T7 of test 1, run and assessed automatically.

    python tests_t0_t7.py T3 --port COM5
    python tests_t0_t7.py all --port COM5

Each test writes a folder results/<date>_<test>/ with the run (CSV), a plot (PNG) and
the outcome (JSON). Where you need to do something (set the pressure, hang a weight)
the script asks for it.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

import analysis
from pico import Pico

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "firmware"))
from config import CFG  # noqa: E402


def length(theta):
    a, b = CFG["hinge_to_rear"], CFG["hinge_to_attach"]
    return math.sqrt(a * a + b * b + 2 * a * b * math.sin(math.radians(theta)))


def ask(text):
    input(f"\n>>> {text}\n    Press Enter when ready... ")


def save(name, data, result, title=None):
    d = os.path.join(HERE, "results", time.strftime("%Y%m%d_%H%M%S_") + name)
    os.makedirs(d, exist_ok=True)
    if data is not None and len(data):
        np.savetxt(os.path.join(d, "run.csv"), data, delimiter=",", fmt="%.4f",
                   header="time_s,L_mm,angle,pa_bar,pb_bar,fill_a,vent_a,fill_b,vent_b,target_mm,target_pa,target_pb",
                   comments="")
        analysis.plot(data - np.r_[data[0, 0], np.zeros(data.shape[1] - 1)], os.path.join(d, "plot.png"), title or name)
    with open(os.path.join(d, "outcome.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    print(f"Saved in {d}")
    return result


def steps(p, plan, cmd="angle"):
    """Run (wait time, angle) steps and return the run and the step start times."""
    t_begin = p.now()
    marks = []
    for hold, theta in plan:
        p.send(f"{cmd} {theta}")
        marks.append((p.now() - t_begin, theta))
        p.wait(hold)
    data = p.take(since=t_begin)
    data[:, 0] -= t_begin
    return data, marks


def t0(p):
    ask("T0 leak test. Regulator at 3 bar, load on the arm.")
    p.send("angle 20")
    p.wait(3)
    p.send("off")
    p.wait(0.5)
    t_begin = p.now()
    p.wait(60)
    d = p.take(since=t_begin)
    drop_a = float(np.mean(d[:20, 3]) - np.mean(d[-20:, 3]))
    drop_b = float(np.mean(d[:20, 4]) - np.mean(d[-20:, 4]))
    drift = float(np.max(np.abs(d[:, 1] - d[0, 1])))
    ok = max(drop_a, drop_b) < 0.1
    return save("T0_leak", d, dict(drop_a_bar=round(drop_a, 3), drop_b_bar=round(drop_b, 3),
                                   sag_mm=round(drift, 2), criterion="pressure drop < 0.1 bar in 60 s",
                                   passed=ok))


def t1(p):
    ask("T1 valves. Regulator at 3 bar.")
    res = {}
    for ch, name in enumerate(("fill_a", "vent_a", "fill_b", "vent_b")):
        if name.startswith("vent"):
            p.send("pressure 2 2")
            p.wait(2)
            p.send("off")
            p.wait(0.3)
        p.messages()
        p.send(f"pulse {ch} 10")
        p.wait(1.5)
        pts = [m.split(",") for m in p.messages() if m.startswith("P,")]
        t = np.array([int(x[1]) for x in pts]) / 1000.0     # ms
        v = np.array([float(x[2]) for x in pts])
        if len(t) < 10:
            res[name] = "no data"
            continue
        base = np.mean(v[t < 4.5])
        moved = np.where(np.abs(v - base) > 0.05)[0]
        delay = float(t[moved[0]] - 5.0) if len(moved) else float("nan")
        res[name] = dict(response_ms=round(delay, 2))
    ok = all(isinstance(r, dict) and r["response_ms"] < 10 for r in res.values())
    res["criterion"] = "pressure starts to change < 10 ms after the signal"
    res["passed"] = ok
    return save("T1_valves", None, res)


def t2(p):
    ask("T2 on/off control. Regulator at 3 bar.")
    data, marks = steps(p, [(3, 0), (3, 30), (3, -5)], cmd="bang")
    rest = {}
    for (t0_, th), (t1_, _) in zip(marks[1:], marks[2:] + [(data[-1, 0], None)]):
        sel = (data[:, 0] > t1_ - 0.5) & (data[:, 0] <= t1_)
        rest[f"to_{th}_deg"] = round(float(np.mean(np.abs(data[sel, 1] - length(th)))), 2)
    ok = all(v < 3 for v in rest.values())
    return save("T2_onoff", data, dict(deviation_mm=rest, criterion="comes to rest within ±3 mm",
                                       passed=ok), "T2 on/off control")


def t3(p, label="T3_pwm"):
    if label == "T3_pwm":
        ask("T3 PWM control. Regulator at 5 bar, load 1.5 kg.")
    data, marks = steps(p, [(3, 0), (3, 30), (3, -5)])
    m1 = analysis.step_metrics(data, marks[1][0], marks[2][0], length(30))
    m2 = analysis.step_metrics(data, marks[2][0], data[-1, 0], length(-5))
    return save(label, data, dict(up_0_to_30=m1, down_30_to_minus5=m2,
                                  passed=m1["passed"] and m2["passed"]), label)


def t4(p):
    ask("T4 repeatability. 5 bar, load 1.5 kg.")
    ends = []
    t_begin = p.now()
    for i in range(10):
        p.send(f"angle {-10 if i % 2 else 50}")
        p.wait(2.5)
        p.send("angle 20")
        p.wait(2.5)
        d = p.take(since=p.now() - 0.3)
        ends.append(float(np.mean(d[:, 1])))
    data = p.take(since=t_begin)
    data[:, 0] -= t_begin
    spread = (max(ends) - min(ends)) / 2
    return save("T4_repeatability", data, dict(end_positions_mm=[round(e, 2) for e in ends],
                                               spread_mm=round(spread, 2), criterion="spread < ±1 mm",
                                               passed=spread < 1.0), "T4 repeatability")


def t5(p):
    ask("T5 holding with load. 5 bar, load 1.5 kg (or heavier).")
    p.send("angle 30")
    p.wait(3)
    t_begin = p.now()
    p.wait(60)
    d = p.take(since=t_begin)
    d[:, 0] -= t_begin
    sag = float(np.max(np.abs(d[:, 1] - length(30))))
    return save("T5_hold", d, dict(max_deviation_mm=round(sag, 2), criterion="< 1 mm in 60 s",
                                   passed=sag < 1.0), "T5 hold")


def t6(p):
    res = {}
    for s in (2, 5):
        ask(f"T6 stiffness, chamber pressure sum {s} bar. Regulator at 5 bar, load 1.5 kg; have 1 kg extra ready.")
        p.send(f"stiffness {s}")
        p.send("angle 20")
        p.wait(3)
        p.send("off")
        p.wait(0.5)
        a0 = float(np.mean(p.take(since=p.now() - 0.3)[:, 2]))
        ask("Now hang the extra 1 kg on the arm (gently, do not drop it).")
        p.wait(1)
        a1 = float(np.mean(p.take(since=p.now() - 0.3)[:, 2]))
        res[f"sum_{s}_bar"] = dict(deflection_deg=round(a0 - a1, 2))
        ask("Remove the extra 1 kg.")
    p.send(f"stiffness {CFG['p_sum']}")
    res["criterion"] = "clear difference in deflection between 2 and 5 bar"
    a, b = res["sum_2_bar"]["deflection_deg"], res["sum_5_bar"]["deflection_deg"]
    res["passed"] = a > b * 1.2
    return save("T6_stiffness", None, res)


def t7(p):
    rows = []
    for kg in (0.5, 1.5, 2.5, 3.5):
        ask(f"T7 load: hang {kg} kg on the arm. 5 bar.")
        r = t3(p, label=f"T7_{kg}kg")
        rows.append(dict(load_kg=kg, passed=r["passed"]))
        if not r["passed"]:
            break
    return save("T7_load", None, dict(per_load=rows))


TESTS = dict(T0=t0, T1=t1, T2=t2, T3=t3, T4=t4, T5=t5, T6=t6, T7=t7)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("test", choices=list(TESTS) + ["all"])
    ap.add_argument("--port")
    a = ap.parse_args()
    with Pico(a.port) as p:
        p.send("stream 100")
        p.wait(0.5)
        for name in (TESTS if a.test == "all" else [a.test]):
            print(f"\n===== {name} =====")
            TESTS[name](p)
            p.send("off")
    return 0


if __name__ == "__main__":
    sys.exit(main())

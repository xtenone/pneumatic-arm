"""De proeven T0–T7 van test 1, automatisch uitgevoerd en beoordeeld.

    python proeven.py T3 --poort COM5
    python proeven.py alle --poort COM5

Per proef komt er een map resultaten/<datum>_<proef>/ met de meetreeks (CSV),
grafiek (PNG) en de uitkomst (JSON). Waar je iets moet doen (druk instellen,
gewicht ophangen) vraagt het script erom.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

import analyse
from pico import Pico

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "firmware"))
from config import CFG  # noqa: E402


def length(theta):
    a, b = CFG["hinge_to_rear"], CFG["hinge_to_attach"]
    return math.sqrt(a * a + b * b + 2 * a * b * math.sin(math.radians(theta)))


def ask(text):
    input(f"\n>>> {text}\n    Druk op Enter als het klaar is... ")


def save(name, data, result, title=None):
    d = os.path.join(HERE, "resultaten", time.strftime("%Y%m%d_%H%M%S_") + name)
    os.makedirs(d, exist_ok=True)
    if data is not None and len(data):
        np.savetxt(os.path.join(d, "meting.csv"), data, delimiter=",", fmt="%.4f",
                   header="tijd_s,L_mm,hoek,pa_bar,pb_bar,vul_a,leeg_a,vul_b,leeg_b,doel_mm,doel_pa,doel_pb",
                   comments="")
        analyse.plot(data - np.r_[data[0, 0], np.zeros(data.shape[1] - 1)], os.path.join(d, "grafiek.png"), title or name)
    with open(os.path.join(d, "uitkomst.json"), "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Opgeslagen in {d}")
    return result


def steps(p, plan, cmd="hoek"):
    """Voer (wachttijd, hoek)-stappen uit en geef de meetreeks + starttijden terug."""
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
    ask("T0 lektest. Drukregelaar op 3 bar, last aan de arm.")
    p.send("hoek 20")
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
    return save("T0_lektest", d, dict(drukval_a_bar=round(drop_a, 3), drukval_b_bar=round(drop_b, 3),
                                      zakken_mm=round(drift, 2), criterium="drukval < 0,1 bar in 60 s",
                                      geslaagd=ok))


def t1(p):
    ask("T1 ventielen. Drukregelaar op 3 bar.")
    res = {}
    for ch, name in enumerate(("vul_a", "leeg_a", "vul_b", "leeg_b")):
        if name.startswith("leeg"):
            p.send("druk 2 2" if ch == 1 else "druk 2 2")
            p.wait(2)
            p.send("off")
            p.wait(0.3)
        p.messages()
        p.send(f"puls {ch} 10")
        p.wait(1.5)
        pts = [m.split(",") for m in p.messages() if m.startswith("P,")]
        t = np.array([int(x[1]) for x in pts]) / 1000.0     # ms
        v = np.array([float(x[2]) for x in pts])
        if len(t) < 10:
            res[name] = "geen data"
            continue
        base = np.mean(v[t < 4.5])
        moved = np.where(np.abs(v - base) > 0.05)[0]
        delay = float(t[moved[0]] - 5.0) if len(moved) else float("nan")
        res[name] = dict(reactietijd_ms=round(delay, 2))
    ok = all(isinstance(r, dict) and r["reactietijd_ms"] < 10 for r in res.values())
    res["criterium"] = "druk begint < 10 ms na het signaal te veranderen"
    res["geslaagd"] = ok
    return save("T1_ventielen", None, res)


def t2(p):
    ask("T2 aan/uit-regeling. Drukregelaar op 3 bar.")
    data, marks = steps(p, [(3, 0), (3, 30), (3, -5)], cmd="bang")
    rest = {}
    for (t0_, th), (t1_, _) in zip(marks[1:], marks[2:] + [(data[-1, 0], None)]):
        sel = (data[:, 0] > t1_ - 0.5) & (data[:, 0] <= t1_)
        rest[f"naar_{th}_graden"] = round(float(np.mean(np.abs(data[sel, 1] - length(th)))), 2)
    ok = all(v < 3 for v in rest.values())
    return save("T2_aanuit", data, dict(afwijking_mm=rest, criterium="komt tot stilstand binnen ±3 mm",
                                        geslaagd=ok), "T2 aan/uit-regeling")


def t3(p, label="T3_pwm"):
    if label == "T3_pwm":
        ask("T3 PWM-regeling. Drukregelaar op 5 bar, last 1,5 kg.")
    data, marks = steps(p, [(3, 0), (3, 30), (3, -5)])
    m1 = analyse.step_metrics(data, marks[1][0], marks[2][0], length(30))
    m2 = analyse.step_metrics(data, marks[2][0], data[-1, 0], length(-5))
    return save(label, data, dict(omhoog_0_naar_30=m1, omlaag_30_naar_min5=m2,
                                   geslaagd=m1["geslaagd"] and m2["geslaagd"]), label)


def t4(p):
    ask("T4 herhaalbaarheid. 5 bar, last 1,5 kg.")
    ends = []
    t_begin = p.now()
    for i in range(10):
        p.send(f"hoek {-10 if i % 2 else 50}")
        p.wait(2.5)
        p.send("hoek 20")
        p.wait(2.5)
        d = p.take(since=p.now() - 0.3)
        ends.append(float(np.mean(d[:, 1])))
    data = p.take(since=t_begin)
    data[:, 0] -= t_begin
    spread = (max(ends) - min(ends)) / 2
    return save("T4_herhaalbaarheid", data, dict(eindposities_mm=[round(e, 2) for e in ends],
                                                 spreiding_mm=round(spread, 2), criterium="spreiding < ±1 mm",
                                                 geslaagd=spread < 1.0), "T4 herhaalbaarheid")


def t5(p):
    ask("T5 vasthouden met last. 5 bar, last 1,5 kg (of zwaarder).")
    p.send("hoek 30")
    p.wait(3)
    t_begin = p.now()
    p.wait(60)
    d = p.take(since=t_begin)
    d[:, 0] -= t_begin
    sag = float(np.max(np.abs(d[:, 1] - length(30))))
    return save("T5_vasthouden", d, dict(max_afwijking_mm=round(sag, 2), criterium="< 1 mm in 60 s",
                                         geslaagd=sag < 1.0), "T5 vasthouden")


def t6(p):
    res = {}
    for som in (2, 5):
        ask(f"T6 stijfheid, kamerdruk {som} bar. 5 bar op de regelaar, last 1,5 kg; houd 1 kg extra klaar.")
        p.send(f"som {som}")
        p.send("hoek 20")
        p.wait(3)
        p.send("off")
        p.wait(0.5)
        L0 = float(np.mean(p.take(since=p.now() - 0.3)[:, 2]))
        ask("Hang nu de extra 1 kg aan de arm (rustig, niet laten vallen).")
        p.wait(1)
        L1 = float(np.mean(p.take(since=p.now() - 0.3)[:, 2]))
        res[f"som_{som}_bar"] = dict(uitwijking_graden=round(L0 - L1, 2))
        ask("Haal de extra 1 kg er weer af.")
    p.send(f"som {CFG['p_sum']}")
    res["criterium"] = "meetbaar verschil in uitwijking tussen 2 en 5 bar"
    a, b = res["som_2_bar"]["uitwijking_graden"], res["som_5_bar"]["uitwijking_graden"]
    res["geslaagd"] = a > b * 1.2
    return save("T6_stijfheid", None, res)


def t7(p):
    rows = []
    for kg in (0.5, 1.5, 2.5, 3.5):
        ask(f"T7 belasting: hang {kg} kg aan de arm. 5 bar.")
        r = t3(p, label=f"T7_{kg}kg")
        rows.append(dict(last_kg=kg, geslaagd=r["geslaagd"]))
        if not r["geslaagd"]:
            break
    return save("T7_belasting", None, dict(per_last=rows))


TESTS = dict(T0=t0, T1=t1, T2=t2, T3=t3, T4=t4, T5=t5, T6=t6, T7=t7)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proef", choices=list(TESTS) + ["alle"])
    ap.add_argument("--poort")
    a = ap.parse_args()
    with Pico(a.poort) as p:
        p.send("stream 100")
        p.wait(0.5)
        for name in (TESTS if a.proef == "alle" else [a.proef]):
            print(f"\n===== {name} =====")
            TESTS[name](p)
            p.send("off")
    return 0


if __name__ == "__main__":
    sys.exit(main())

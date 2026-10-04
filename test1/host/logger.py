"""Handbediening met opname: typ commando's voor de Pico, alles wordt in een CSV bewaard.

    python logger.py --poort COM5 --uit meting.csv
Typ 'help' voor de commando's van de Pico, 'stop' om af te sluiten (ventielen dicht).
"""
import argparse
import csv
import sys
import time

from pico import Pico

COLS = ["tijd_s", "L_mm", "hoek", "pa_bar", "pb_bar", "vul_a", "leeg_a", "vul_b", "leeg_b", "doel_mm"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--poort")
    ap.add_argument("--uit", default=time.strftime("meting_%Y%m%d_%H%M%S.csv"))
    a = ap.parse_args()
    with Pico(a.poort) as p:
        print("Verbonden. Typ 'help' of 'stop'.")
        try:
            while True:
                for m in p.messages():
                    print("  <", m)
                cmd = input("> ").strip()
                if cmd in ("stop", "exit", "quit"):
                    break
                if cmd:
                    p.send(cmd)
                time.sleep(0.2)
                for m in p.messages():
                    print("  <", m)
                if p.rows:
                    r = p.rows[-1]
                    print(f"  L={r[1]:.1f} mm  hoek={r[2]:.1f}°  pa={r[3]:.2f}  pb={r[4]:.2f} bar")
        except (KeyboardInterrupt, EOFError):
            pass
        data = p.take()
    with open(a.uit, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for r in data:
            w.writerow([round(x, 4) for x in list(r[:9]) + [r[9]]])
    print(f"{len(data)} meetregels bewaard in {a.uit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

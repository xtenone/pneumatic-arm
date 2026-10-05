"""Manual control with recording: type commands for the Pico, everything is saved to CSV.

    python logger.py --port COM5 --out run.csv
Type 'help' for the Pico's commands, 'quit' to stop (valves closed).
"""
import argparse
import csv
import sys
import time

from pico import Pico

COLS = ["time_s", "L_mm", "angle", "pa_bar", "pb_bar", "fill_a", "vent_a", "fill_b", "vent_b", "target_mm"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port")
    ap.add_argument("--out", default=time.strftime("run_%Y%m%d_%H%M%S.csv"))
    a = ap.parse_args()
    with Pico(a.port) as p:
        print("Connected. Type 'help' or 'quit'.")
        try:
            while True:
                for m in p.messages():
                    print("  <", m)
                cmd = input("> ").strip()
                if cmd in ("quit", "exit", "stop"):
                    break
                if cmd:
                    p.send(cmd)
                time.sleep(0.2)
                for m in p.messages():
                    print("  <", m)
                if p.rows:
                    r = p.rows[-1]
                    print(f"  L={r[1]:.1f} mm  angle={r[2]:.1f}°  pa={r[3]:.2f}  pb={r[4]:.2f} bar")
        except (KeyboardInterrupt, EOFError):
            pass
        data = p.take()
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for r in data:
            w.writerow([round(x, 4) for x in list(r[:9]) + [r[9]]])
    print(f"{len(data)} data lines saved to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

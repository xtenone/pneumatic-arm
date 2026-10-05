"""Connection to the Pico over USB (pyserial). Works on Windows (COM3...) and Linux (/dev/ttyACM0).

    from pico import Pico
    with Pico("COM5") as p:
        p.send("angle 20")
        p.wait(3)
        data = p.take()     # numpy array, columns as in analysis.py
"""
import threading
import time

import numpy as np
import serial
import serial.tools.list_ports


def find_port():
    """First port that looks like a Raspberry Pi Pico (USB VID 0x2E8A)."""
    for p in serial.tools.list_ports.comports():
        if p.vid == 0x2E8A:
            return p.device
    return None


class Pico:
    def __init__(self, port=None, baud=115200):
        port = port or find_port()
        if port is None:
            raise SystemExit("No Pico found. Give the port with --port (e.g. COM5 or /dev/ttyACM0).")
        self.ser = serial.Serial(port, baud, timeout=0.1)
        self.rows = []
        self.lines = []           # other lines (OK, ERROR, INFO, P, ...)
        self.lock = threading.Lock()
        self.stop = False
        self.t_offset = None
        self.ref_target = float("nan")
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()
        self.pinger = threading.Thread(target=self._ping, daemon=True)
        self.pinger.start()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        try:
            self.send("off")
            time.sleep(0.2)
        finally:
            self.stop = True
            self.ser.close()

    def send(self, cmd):
        self.ser.write((cmd.strip() + "\n").encode())

    def _ping(self):
        while not self.stop:
            try:
                self.send("ping")
            except Exception:  # noqa: BLE001
                return
            time.sleep(0.2)

    def _read(self):
        buf = b""
        while not self.stop:
            try:
                buf += self.ser.read(4096)
            except Exception:  # noqa: BLE001
                return
            while b"\n" in buf:
                raw, buf = buf.split(b"\n", 1)
                line = raw.decode(errors="replace").strip()
                if line.startswith("D,"):
                    f = line.split(",")
                    try:
                        t = int(f[1]) / 1000.0
                        row = [t, float(f[2]), float(f[3]), float(f[4]), float(f[5]),
                               float(f[6]), float(f[7]), float(f[8]), float(f[9]),
                               float(f[11]), float("nan"), float("nan")]
                    except (ValueError, IndexError):
                        continue
                    with self.lock:
                        self.rows.append(row)
                        if len(f) > 12 and f[12]:
                            self.lines.append("ERROR," + f[12])
                elif line:
                    with self.lock:
                        self.lines.append(line)

    def wait(self, seconds):
        time.sleep(seconds)

    def take(self, since=None):
        """All data lines since the start (or since time `since`) as an array."""
        with self.lock:
            a = np.array(self.rows) if self.rows else np.zeros((0, 12))
        if len(a) and since is not None:
            a = a[a[:, 0] >= since]
        return a

    def now(self):
        with self.lock:
            return self.rows[-1][0] if self.rows else 0.0

    def messages(self):
        with self.lock:
            out, self.lines = self.lines, []
        return out

"""Analysis of recorded runs, shared by the simulation and the real tests.

A run is a numpy array with columns:
  0 time_s, 1 L_mm, 2 angle, 3 pa, 4 pb, 5-8 duty (fill A, vent A, fill B, vent B),
  9 target_mm, 10 target pa, 11 target pb  (10-11 only in the simulation, NaN otherwise)
"""
import numpy as np

# T3 criteria (see the manual)
OVERSHOOT_MM = 5.0
SETTLE_S = 1.0
ERROR_MM = 1.0


def step_metrics(log, t0, t1, target):
    """Overshoot (mm), settling time (s) and steady-state error (mm) of a step at t0."""
    sel = (log[:, 0] >= t0) & (log[:, 0] < t1)
    t, L = log[sel, 0], log[sel, 1]
    start = L[0]
    direction = 1 if target > start else -1
    over = max(0.0, float(np.max((L - target) * direction)))
    outside = np.where(np.abs(L - target) > ERROR_MM)[0]
    settle = (t[outside[-1]] - t0) if len(outside) else 0.0
    tail = t > t1 - 0.5
    err = float(np.mean(np.abs(L[tail] - target)))
    return dict(overshoot_mm=round(over, 2), settling_s=round(float(settle), 3),
                error_mm=round(err, 2),
                passed=bool(over < OVERSHOOT_MM and settle < SETTLE_S and err < ERROR_MM))


def plot(log, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = log[:, 0]
    fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    ax[0].plot(t, log[:, 1], label="cylinder length (measured)")
    ax[0].plot(t, log[:, 9], "--", label="target")
    ax[0].set_ylabel("mm")
    ax2 = ax[0].twinx()
    ax2.plot(t, log[:, 2], color="gray", alpha=0.4)
    ax2.set_ylabel("arm angle (degrees)")
    ax[0].legend(loc="upper left")
    ax[1].plot(t, log[:, 3], label="chamber A")
    ax[1].plot(t, log[:, 4], label="chamber B")
    if log.shape[1] > 11 and not np.all(np.isnan(log[:, 10])):
        ax[1].plot(t, log[:, 10], ":", color="C0", alpha=0.7, label="target A")
        ax[1].plot(t, log[:, 11], ":", color="C1", alpha=0.7, label="target B")
    ax[1].set_ylabel("bar gauge")
    ax[1].legend(loc="upper left")
    for k in range(4):
        ax[2].plot(t, log[:, 5 + k] + k * 1.2)
    ax[2].set_yticks([0.5 + 1.2 * k for k in range(4)], ["fill A", "vent A", "fill B", "vent B"])
    ax[2].set_xlabel("time (s)")
    ax[2].set_ylabel("duty")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)

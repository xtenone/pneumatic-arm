"""Analysis of recorded runs, shared by the simulation and the real tests.

A run is a numpy array with columns:
  0 time_s, 1 L_mm, 2 angle, 3 pa, 4 pb, 5-8 duty (fill A, vent A, fill B, vent B),
  9 target_mm, 10 target pa, 11 target pb  (10-11 only in the simulation, NaN otherwise),
  12 profile_mm (where the target is now: the profile of `move`, the ramp of `angle`)
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


# T8: preset positions (s after the start, arm angle). The last two are 0.15 s apart: a
# new target during a move.
T8_PLAN = [(0.5, 30.0), (2.0, -5.0), (3.5, 50.0), (5.0, 10.0), (6.5, 40.0), (6.65, 20.0)]
T8_END = 8.0
T8_TRACK_MM, T8_OVERSHOOT_MM, T8_SETTLE_MM, T8_SETTLE_S, T8_ERROR_MM = 3.0, 2.0, 1.5, 0.2, 1.0
T8_REPLAN_S = 0.5            # a command this soon after the previous one changes a running move


def t8_metrics(log, commands, t_stop, target_mm):
    """Per move of T8: profile time, largest tracking error during the profile (measured −
    profile), overshoot past the target, time until within ±T8_SETTLE_MM after the
    profile ends, time from the command until settled, and the mean error at rest.

    commands: [(time, angle)] as sent; target_mm(angle) gives the cylinder length.
    A command within T8_REPLAN_S of the previous one belongs to the same move; its
    overshoot is past the new, nearer target and does not count."""
    t, L, prof = log[:, 0], log[:, 1], log[:, 12]
    rows = []
    for i, (tc, th) in enumerate(commands):
        if i + 1 < len(commands) and commands[i + 1][0] - tc < T8_REPLAN_S:
            continue                                   # replaced during the move
        replanned = i > 0 and tc - commands[i - 1][0] < T8_REPLAN_S
        t0 = commands[i - 1][0] if replanned else tc
        t_next = commands[i + 1][0] if i + 1 < len(commands) else t_stop
        target = target_mm(th)
        win = (t >= t0) & (t < t_next)
        # the profile has ended when it stays at the target
        off = np.where(win & (np.abs(prof - target) > 0.02))[0]
        t_end = t[off[-1]] if len(off) else t0
        moving = win & (t <= t_end)
        track = float(np.max(np.abs(L[moving] - prof[moving]))) if moving.any() else 0.0
        start = L[np.searchsorted(t, t0)]
        direction = 1 if target > start else -1
        over = max(0.0, float(np.max((L[win] - target) * direction)))
        after = win & (t > t_end)
        outside = np.where(np.abs(L[after] - target) > T8_SETTLE_MM)[0]
        t_settled = t[after][outside[-1]] if len(outside) else t_end
        settle_after = max(0.0, float(t_settled - t_end))
        err = float(np.mean(np.abs(L[win & (t > t_next - 0.3)] - target)))
        ok = (track < T8_TRACK_MM and (replanned or over < T8_OVERSHOOT_MM)
              and settle_after <= T8_SETTLE_S and err < T8_ERROR_MM)
        rows.append(dict(command_s=round(float(t0), 3), angle=th, profile_s=round(float(t_end - t0), 3),
                         track_mm=round(track, 2), overshoot_mm=round(over, 2),
                         settle_after_s=round(settle_after, 3), command_to_settled_s=round(float(t_settled - t0), 3),
                         error_mm=round(err, 2), new_target_during_move=replanned, passed=bool(ok)))
    return rows


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

"""Duty-cycle governor for the Stage 2 search (Will's steering 3,
2026-11-15 02:32 CST: "focus on managing duty cycles to keep the ranch
operating cleanly").

Wraps a child command in its own session/process group and governs it
by die temperature: the k10temp sensor is resolved by name under
/sys/class/hwmon (the same resolution ~/thermal/sample.sh uses) and
sampled every INTERVAL seconds -- the per-minute thermal.log is a
record, not a control signal. Work is never killed, only frozen;
frozen time is the cycle, and it is measured and reported.

CONTROL LAW — temperature smoothing (Will's ruling, 2026-11-15,
replacing the instantaneous STOP_AT/RESUME_AT gate this file
originally carried, and mirroring duty/duty_governor.py): decisions
ride an exponential moving average of Tctl (time constant
AVG_TAU_S), never a single sample, so a momentary spike moves
nothing. As the average climbs the plateau ladder (BAND_EDGES) the
duty target steps down (BAND_DUTIES), delivered as SIGSTOP/SIGCONT
slices spread evenly over time; it steps back up -- eased by
HYSTERESIS_C -- as the average falls. A sustained average at
SAFETY_AT freezes the group outright until the average falls to
SAFETY_RESUME (92 C is below TjMax on every ranch part -- 95 C
desktop, 100 C HS/HX -- yet above the 88-91 C these chassis
saturate at ungoverned, so the shed trips on cooling failure, not
on work). This governor has no wattage lever; timed slices are the
closest faithful analogue of stepping the watts down.

Outputs: a CSV of every control sample (iso, tctl, state), a stats
JSON (sample min/median/max, transitions, running/frozen seconds,
duty fraction), and transition lines on stdout.
"""
import csv
import json
import math
import os
import signal
import statistics
import subprocess
import sys
import time
from datetime import datetime

AVG_TAU_S = 60.0
BAND_EDGES = (78.0, 82.0, 86.0, 90.0)
BAND_DUTIES = (0.75, 0.50, 0.25, 0.10)
HYSTERESIS_C = 1.5
SAFETY_AT = 92.0
SAFETY_RESUME = 80.0
INTERVAL = 3.0


def sensor_path():
    base = "/sys/class/hwmon"
    for entry in sorted(os.listdir(base)):
        try:
            with open(os.path.join(base, entry, "name")) as fh:
                if fh.read().strip() == "k10temp":
                    return os.path.join(base, entry, "temp1_input")
        except OSError:
            continue
    return None


def read_tctl(path):
    try:
        with open(path) as fh:
            return int(fh.read().strip()) / 1000.0
    except (OSError, ValueError):
        return None


def duty_for_level(level):
    return ((1.0,) + BAND_DUTIES)[level]


def main():
    args = sys.argv[1:]
    sep = args.index("--")
    opts, cmd = args[:sep], args[sep + 1:]
    out_prefix = opts[opts.index("--out") + 1] if "--out" in opts \
        else "duty"
    path = sensor_path()
    if path is None:
        print("GOVERNOR: no k10temp sensor found — refusing to run "
              "ungoverned", flush=True)
        return 2
    print(f"GOVERNOR: sensor {path}; smoothing law: avg tau "
          f"{AVG_TAU_S:.0f}s, ladder {list(BAND_EDGES)} C -> duties "
          f"{list(BAND_DUTIES)}, safety freeze at avg >= {SAFETY_AT} C, "
          f"sample every {INTERVAL}s", flush=True)

    child = subprocess.Popen(cmd, start_new_session=True)
    pgid = child.pid                    # start_new_session: pid == pgid
    t0 = time.time()
    frozen = False
    freeze_start = None
    frozen_total = 0.0
    running_total = 0.0
    last_tick = t0
    transitions = 0
    samples = []
    read_failures = 0
    # smoothing-law state
    ema = None
    ema_max = None
    level = 0
    slice_acc = 0.0
    safety = False
    safety_events = 0
    avg_samples_ge_safety = 0

    csv_path = out_prefix + "-samples.csv"
    fh = open(csv_path, "w", newline="")
    writer = csv.writer(fh)
    writer.writerow(["iso", "tctl_c", "state"])

    def note_state(now):
        nonlocal running_total, frozen_total, last_tick
        dt = now - last_tick
        if frozen:
            frozen_total += dt
        else:
            running_total += dt
        last_tick = now

    def set_frozen(want_frozen, now, why):
        nonlocal frozen, freeze_start, transitions
        if want_frozen == frozen:
            return
        if want_frozen:
            os.killpg(pgid, signal.SIGSTOP)
            note_state(now)
            frozen = True
            freeze_start = now
            transitions += 1
            print(f"GOVERNOR [{now - t0:7.1f}s]: {why} — SIGSTOP "
                  f"group {pgid}", flush=True)
        else:
            os.killpg(pgid, signal.SIGCONT)
            note_state(now)
            frozen = False
            print(f"GOVERNOR [{now - t0:7.1f}s]: {why} — SIGCONT "
                  f"group {pgid} (froze {now - freeze_start:.0f}s)",
                  flush=True)

    try:
        while True:
            now = time.time()
            tctl = read_tctl(path)
            if tctl is None:
                read_failures += 1
            else:
                samples.append(tctl)
                # fold the sample into the moving average — every
                # decision below rides the average, never the sample
                if ema is None:
                    ema = tctl
                else:
                    alpha = 1.0 - math.exp(-INTERVAL / AVG_TAU_S)
                    ema += alpha * (tctl - ema)
                if ema_max is None or ema > ema_max:
                    ema_max = ema
                if safety:
                    if ema >= SAFETY_AT:
                        avg_samples_ge_safety += 1
                    if ema <= SAFETY_RESUME:
                        safety = False
                        set_frozen(False, now,
                                   f"avg Tctl {ema:.1f} C <= "
                                   f"{SAFETY_RESUME} — safety shed "
                                   f"released")
                elif ema >= SAFETY_AT:
                    avg_samples_ge_safety += 1
                    safety = True
                    safety_events += 1
                    if frozen:
                        # already frozen in a duty slice: the shed
                        # takes over the freeze (no signal needed)
                        print(f"GOVERNOR [{now - t0:7.1f}s]: avg Tctl "
                              f"{ema:.1f} C >= {SAFETY_AT} — SAFETY "
                              f"shed takes over the freeze", flush=True)
                    else:
                        set_frozen(True, now,
                                   f"avg Tctl {ema:.1f} C >= "
                                   f"{SAFETY_AT} — SAFETY freeze")
                else:
                    # plateau ladder on the average, eased on the
                    # way back up so the level cannot flap
                    while level < len(BAND_EDGES) \
                            and ema >= BAND_EDGES[level]:
                        level += 1
                    while level > 0 \
                            and ema < BAND_EDGES[level - 1] \
                            - HYSTERESIS_C:
                        level -= 1
                    duty = duty_for_level(level)
                    if duty >= 1.0:
                        slice_acc = 0.0
                        want_frozen = False
                    else:
                        # Bresenham: spread the frozen slices evenly
                        slice_acc += duty
                        if slice_acc >= 1.0:
                            slice_acc -= 1.0
                            want_frozen = False
                        else:
                            want_frozen = True
                    set_frozen(want_frozen, now,
                               f"avg Tctl {ema:.1f} C, level {level}, "
                               f"duty {duty:.2f}")
                writer.writerow(
                    [datetime.now().astimezone().isoformat(timespec="seconds"),
                     f"{tctl:.1f}", "frozen" if frozen else "running"])
                fh.flush()
            if child.poll() is not None:
                note_state(time.time())
                break
            time.sleep(INTERVAL)
    finally:
        fh.close()
        if frozen:                      # never leave a frozen group behind
            try:
                os.killpg(pgid, signal.SIGCONT)
            except OSError:
                pass
    wall = time.time() - t0
    stats = {
        "child_exit_code": child.returncode,
        "wall_seconds": round(wall, 1),
        "running_seconds": round(running_total, 1),
        "frozen_seconds": round(frozen_total, 1),
        "duty_fraction": round(running_total / wall, 4) if wall else 0,
        "transitions": transitions,
        "samples": len(samples),
        "sample_interval_s": INTERVAL,
        "avg_tau_s": AVG_TAU_S,
        "band_edges_c": list(BAND_EDGES),
        "band_duties": list(BAND_DUTIES),
        "safety_at_c": SAFETY_AT, "safety_resume_c": SAFETY_RESUME,
        "safety_events": safety_events,
        "avg_samples_ge_safety": avg_samples_ge_safety,
        "tctl_avg_max": round(ema_max, 2) if ema_max is not None else None,
        "tctl_min": min(samples) if samples else None,
        "tctl_median": statistics.median(samples) if samples else None,
        "tctl_max": max(samples) if samples else None,
        "sensor_read_failures": read_failures,
        "sensor": path,
    }
    with open(out_prefix + "-stats.json", "w") as fh:
        json.dump(stats, fh, indent=1)
    print("GOVERNOR STATS " + json.dumps(stats), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

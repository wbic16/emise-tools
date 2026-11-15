#!/usr/bin/env python3
"""probe_tctl.py — measure the Tctl rise/fall shape under step load.

The duty governor's first acceptance runs showed Tctl swinging ~55<->82 C
between 2 s samples under SIGSTOP/SIGCONT cycling: the sensor moves far
faster than the control loop. Before re-tuning, measure the actual curve:
from a cool idle, apply N soak workers, sample temp1_input every 50 ms;
then kill the load and sample the fall. Reports, per instance count:
time from load-start to cross 65/70/73/75/80 C, plateau, and fall times.

Run on the node: python3 probe_tctl.py [counts...]  (default 4 1 8)
Stdlib only.
"""
import os
import subprocess
import sys
import time

BASE = os.path.expanduser("~/nethack-solver")
VENV_PY = os.path.join(BASE, ".venv", "bin", "python")
WORKER = os.path.join(BASE, "soak_worker.py")


def tctl_path():
    for entry in sorted(os.listdir("/sys/class/hwmon")):
        d = os.path.join("/sys/class/hwmon", entry)
        try:
            with open(os.path.join(d, "name")) as f:
                if f.read().strip() == "k10temp":
                    return os.path.join(d, "temp1_input")
        except OSError:
            continue
    raise SystemExit("no k10temp")


PATH = tctl_path()


def read_c():
    with open(PATH) as f:
        return int(f.read().strip()) / 1000.0


def wait_cool(limit, cap_s=180):
    t0 = time.time()
    while time.time() - t0 < cap_s:
        if read_c() <= limit:
            return True
        time.sleep(2)
    return read_c() <= limit


def sample_for(seconds, series, t_ref):
    end = time.time() + seconds
    while time.time() < end:
        series.append((time.time() - t_ref, read_c()))
        time.sleep(0.05)


def crossings(series, t_start, thresholds):
    out = {}
    for th in thresholds:
        out[th] = None
        for t, v in series:
            if t >= t_start and v >= th:
                out[th] = round(t - t_start, 2)
                break
    return out


def main():
    counts = [int(x) for x in sys.argv[1:]] or [4, 1, 8]
    for n in counts:
        if not wait_cool(40.0):
            print(f"count={n}: node did not cool to 40 C; starting anyway "
                  f"at {read_c():.1f} C", flush=True)
        idle = read_c()
        procs = []
        series = []
        t_ref = time.time()
        sample_for(3.0, series, t_ref)  # idle baseline
        t_load = time.time() - t_ref
        for i in range(n):
            procs.append(subprocess.Popen(
                [VENV_PY, WORKER, "--duration", "30", "--seed", str(5000 + i),
                 "--progress", f"/tmp/probe-progress-{n}-{i}.txt"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        sample_for(20.0, series, t_ref)  # rise + plateau
        t_kill = time.time() - t_ref
        for p in procs:
            p.kill()
        for p in procs:
            p.wait()
        sample_for(15.0, series, t_ref)  # fall
        rise = crossings(series, t_load, (65, 70, 73, 75, 80))
        plateau = max(v for t, v in series if t_load <= t <= t_kill)
        fall = {}
        for th in (75, 70, 65, 60):
            fall[th] = None
            for t, v in series:
                if t >= t_kill and v <= th:
                    fall[th] = round(t - t_kill, 2)
                    break
        print(f"count={n} idle={idle:.1f} plateau_max={plateau:.1f} "
              f"rise_s={rise} fall_s={fall}", flush=True)


if __name__ == "__main__":
    main()

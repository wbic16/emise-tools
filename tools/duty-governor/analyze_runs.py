#!/usr/bin/env python3
"""analyze_runs.py — recompute the acceptance record for the six governed
runs from the collected primary evidence: governor summary JSONs, worker
progress files (total steps), and each node's ~/thermal/thermal.log
minute samples inside the run window. Prints one JSON record per run.
"""
import glob
import json
import os
from datetime import datetime

BASE = os.path.expanduser("~/workspace/nethack-solver/duty/collected")
NODES = ["plain-view", "free-fall", "logos-prime"]


def progress_total(run_dir):
    total = 0
    for pf in sorted(glob.glob(os.path.join(run_dir, "progress-*.txt"))):
        last = None
        with open(pf) as f:
            for line in f:
                parts = line.split()
                if len(parts) == 2:
                    last = int(parts[1])
        if last is None:
            raise SystemExit(f"no progress lines in {pf}")
        total += last
    return total


def thermal_window(path, start_epoch, end_epoch):
    samples = []
    with open(path) as f:
        for line in f:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2:
                continue
            try:
                ts = datetime.fromisoformat(parts[0]).timestamp()
                temp = float(parts[1])
            except ValueError:
                continue
            if start_epoch - 30 <= ts <= end_epoch + 30:
                samples.append((ts, temp))
    return samples


def main():
    records = []
    for node in NODES:
        for n in (4, 8):
            run_dir = os.path.join(BASE, node, f"{node}-{n}inst")
            with open(os.path.join(run_dir, "governor.log.summary.json")) as f:
                s = json.load(f)
            steps = progress_total(run_dir)
            win = thermal_window(os.path.join(BASE, node, "thermal.log"),
                                 s["start_epoch"], s["end_epoch"])
            temps = [t for _, t in win]
            rec = {
                "node": node,
                "instances": n,
                "start": s["start_iso"],
                "end": s["end_iso"],
                "wall_s": s["wall_s"],
                "duty_fraction": s["duty_fraction"],
                "cycles": s["cycles"],
                "mean_burst_s": s["mean_burst_s"],
                "mean_cool_s": s["mean_cool_s"],
                "gov_tctl_median": s["tctl_median_c"],
                "gov_tctl_p95": s["tctl_p95_c"],
                "gov_tctl_max": s["tctl_max_c"],
                "gov_samples": s["tctl_n"],
                "gov_samples_ge_75": s["samples_ge_75"],
                "gov_samples_ge_80": s["samples_ge_80"],
                "total_steps": steps,
                "effective_steps_per_s": round(steps / s["wall_s"], 1),
                "thermal_minute_samples": len(temps),
                "thermal_max": max(temps) if temps else None,
                "thermal_samples_ge_75": sum(1 for t in temps if t >= 75.0),
            }
            records.append(rec)
    print(json.dumps(records, indent=1))


if __name__ == "__main__":
    main()

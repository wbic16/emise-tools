#!/usr/bin/env python3
"""duty_governor.py — the inside-a-job thermal duty-cycle governor for the ranch.

Tonight's per-node soak sweep (~/workspace/nethack-solver/node-limits.md)
proved there is no sustained full-tilt operating point on any ranch node:
Tctl crosses 75 C within ~2-3 minutes at any instance count and saturates
at 88-91 C. Sustained work therefore runs as a governed duty cycle. The
house's between-job policy (new starts pause at >=75 C, resume <=70,
off-time to <=65 after an 80 C crossing; ranch-batchq) decides whether a
job may START; this governor is the layer inside a running job.

Control law — temperature smoothing (Will's ruling, 2026-11-15,
replacing the 73/70 instantaneous gate this file originally carried;
grounded in the AMD R9 reliability brief of the same day). AMD
validates Ryzen 9 silicon to live at TjMax (95 C desktop, 100 C
HS/HX) continuously; the wear mechanism the evidence indicts is
thermal CYCLING (fatigue damage ~ dT^2) — which a stop/go gate
manufactures. So the governor no longer decides on instantaneous
samples and no longer rides a line:

  - Sample Tctl every sample_s seconds (2-5 s) from k10temp, resolved
    BY NAME under /sys/class/hwmon (the hwmon index varies per node —
    the fleet's ~/thermal/sample.sh pattern; never hardcoded), and
    fold it into an exponential moving average with time constant
    avg_tau_s (default 60 s). EVERY decision below uses the AVERAGE;
    a momentary spike moves nothing.
  - Plateau ladder: while the average sits below band_edges[0]
    (78 C) the workload runs unthrottled. As the average climbs
    through the edges (78/82/86/90 C) the duty target steps down
    (0.75/0.50/0.25/0.10), and steps back up — eased by hysteresis_c
    (1.5 C) so the level cannot flap — as the average falls. The
    governor seeks the equilibrium duty at which the node holds its
    plateau instead of swinging between full speed and frozen.
  - Duty is delivered as SIGSTOP/SIGCONT slices spread evenly over
    time (a Bresenham accumulator over sample ticks), so the
    run/freeze grain is seconds, not minutes — the smallest thermal
    swing this lever can make. This governor has NO wattage lever:
    it cannot set PPT (RyzenAdj) or a frequency cap. Timed slices
    are the closest faithful analogue of "step the watts down";
    governing package power directly remains the recorded open
    option in results.md section 5.
  - Safety shed: if the sustained AVERAGE reaches safety_c (92 C —
    below TjMax on every ranch part, yet above the 88-91 C these
    chassis saturate at ungoverned, so it trips on cooling failure
    rather than on work), the group is frozen outright until the
    average falls to safety_resume_c (80 C).
  - The workload is never SIGKILLed by the thermal law. On governor
    exit (SIGTERM/SIGINT or --max-seconds), the group is SIGCONTed
    first — nothing is ever left frozen — then SIGTERMed as a
    shutdown, never as thermal control.

Usage:
  duty_governor.py --profile <node>.json --log <run.log> [--max-seconds S]
                   [--safety-c C] [--avg-tau-s S] [--sample-s S]
                   [--tctl-file PATH] -- <command...>

--tctl-file reads the temperature (degrees C, plain float) from a file
instead of the sensor — for smoke tests and exotic nodes.

The governor writes a timestamped cycle log (every sample, every
stop/cont event) to --log, and a machine-readable summary to
<log>.summary.json: wall/run/frozen seconds, duty fraction, cycle count,
burst/cool length stats, Tctl median/p95/max, samples >= 75 C.

Python 3, stdlib only.
"""
import argparse
import json
import math
import os
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime

DEFAULTS = {
    "sample_s": 2.0,
    # Temperature-smoothing law (Will, 2026-11-15) — see module docstring.
    "avg_tau_s": 60.0,
    "band_edges": [78.0, 82.0, 86.0, 90.0],
    "band_duties": [0.75, 0.50, 0.25, 0.10],
    "hysteresis_c": 1.5,
    "safety_c": 92.0,
    "safety_resume_c": 80.0,
}


def iso(epoch):
    return datetime.fromtimestamp(epoch).astimezone().isoformat(timespec="milliseconds")


def resolve_tctl_path():
    """Find k10temp's temp1_input by sensor NAME (hwmon index varies)."""
    base = "/sys/class/hwmon"
    try:
        entries = sorted(os.listdir(base))
    except OSError:
        return None
    for entry in entries:
        d = os.path.join(base, entry)
        try:
            with open(os.path.join(d, "name")) as f:
                if f.read().strip() == "k10temp":
                    p = os.path.join(d, "temp1_input")
                    if os.path.exists(p):
                        return p
        except OSError:
            continue
    return None


class Governor:
    def __init__(self, cfg, cmd, log_path, max_seconds=None, tctl_file=None):
        self.cfg = cfg
        self.cmd = cmd
        self.max_seconds = max_seconds
        self.tctl_file = tctl_file
        self.tctl_path = None if tctl_file else resolve_tctl_path()
        self.logf = open(log_path, "a", buffering=1)
        self.summary_path = log_path + ".summary.json"
        self.proc = None
        self.pgid = None
        self.state = "RUNNING"  # RUNNING | FROZEN | FROZEN_SAFETY
        self.shutdown = False
        self.samples = []
        # smoothing-law state: the EMA is the controlled variable
        self.avg = None
        self.avg_max = None
        self.level = 0           # plateau ladder level 0..len(band_edges)
        self.slice_acc = 0.0     # Bresenham accumulator for duty slices
        self.safety = False      # safety shed engaged
        self.safety_events = 0
        self.avg_samples_ge_safety = 0
        self.events = []
        self.run_s = 0.0
        self.frozen_s = 0.0
        self.bursts = []   # completed run intervals (s)
        self.cools = []    # completed frozen intervals (s)
        self.cycles = 0
        self._state_since = None
        self._last_tick = None

    # -- logging ------------------------------------------------------
    def log(self, event, tctl=None, extra=""):
        now = time.time()
        t = f"{tctl:.1f}" if tctl is not None else "NA"
        self.logf.write(
            f"{iso(now)} epoch={now:.3f} tctl={t} state={self.state} "
            f"event={event} {extra}\n"
        )
        if event in ("stop", "cont", "safety_stop", "safety_cont",
                     "start", "exit"):
            self.events.append((now, event))

    # -- temperature --------------------------------------------------
    def read_tctl(self):
        try:
            if self.tctl_file:
                with open(self.tctl_file) as f:
                    return float(f.read().strip())
            if self.tctl_path is None:
                self.tctl_path = resolve_tctl_path()
                if self.tctl_path is None:
                    return None
            with open(self.tctl_path) as f:
                return int(f.read().strip()) / 1000.0
        except (OSError, ValueError):
            self.tctl_path = None if not self.tctl_file else self.tctl_path
            return None

    # -- signals to the workload group --------------------------------
    def group_signal(self, sig):
        if self.pgid is None:
            return
        try:
            os.killpg(self.pgid, sig)
        except (ProcessLookupError, PermissionError):
            pass

    # -- state transitions --------------------------------------------
    def _enter(self, new_state, event, tctl, now, extra=""):
        if self._state_since is not None:
            dur = now - self._state_since
            if self.state == "RUNNING":
                self.bursts.append(dur)
            else:
                self.cools.append(dur)
        self.state = new_state
        self._state_since = now
        self.log(event, tctl, extra)

    # -- the smoothing law ---------------------------------------------
    def duty_target(self):
        """Duty fraction for the current ladder level (level 0 = 1.0)."""
        return ([1.0] + list(self.cfg["band_duties"]))[self.level]

    def _update_level(self, avg):
        edges = self.cfg["band_edges"]
        hyst = self.cfg["hysteresis_c"]
        # restrict further the moment the AVERAGE crosses an edge
        while self.level < len(edges) and avg >= edges[self.level]:
            self.level += 1
        # ease back only once the average has clearly fallen
        while self.level > 0 and avg < edges[self.level - 1] - hyst:
            self.level -= 1

    def _apply(self, want_running, tctl, now, safety=False, extra=""):
        """Drive the group to the wanted run/freeze state (signal only
        on an actual transition)."""
        if want_running == (self.state == "RUNNING"):
            return
        if want_running:
            self.group_signal(signal.SIGCONT)
            self._enter("RUNNING",
                        "safety_cont" if safety else "cont",
                        tctl, now, extra)
        else:
            self.group_signal(signal.SIGSTOP)
            self.cycles += 1
            self._enter("FROZEN_SAFETY" if safety else "FROZEN",
                        "safety_stop" if safety else "stop",
                        tctl, now, extra)

    # -- main loop ------------------------------------------------------
    def run(self):
        if not self.tctl_file and self.tctl_path is None:
            self.logf.write("# FATAL: no k10temp sensor found\n")
            return 2
        start = time.time()
        self._state_since = start
        self._last_tick = start
        self.proc = subprocess.Popen(self.cmd, start_new_session=True)
        self.pgid = self.proc.pid
        self.log("start", None,
                 f"pid={self.proc.pid} cmd={json.dumps(self.cmd)} "
                 f"profile={json.dumps(self.cfg)} host={socket.gethostname()}")
        exit_code = None
        timed_out = False
        while True:
            now = time.time()
            dt = now - self._last_tick
            self._last_tick = now
            if self.state == "RUNNING":
                self.run_s += dt
            else:
                self.frozen_s += dt

            if self.shutdown:
                self.log("governor_shutdown", None, "SIGCONT+SIGTERM group")
                self.group_signal(signal.SIGCONT)
                self.group_signal(signal.SIGTERM)
                break
            if self.max_seconds and now - start >= self.max_seconds:
                timed_out = True
                self.log("max_seconds", None, "SIGCONT+SIGTERM group")
                self.group_signal(signal.SIGCONT)
                self.group_signal(signal.SIGTERM)
                break

            rc = self.proc.poll()
            if rc is not None:
                exit_code = rc
                break

            tctl = self.read_tctl()
            if tctl is not None:
                self.samples.append(tctl)
                # fold the sample into the moving average — every
                # decision below rides the average, never the sample
                if self.avg is None:
                    self.avg = tctl
                else:
                    alpha = 1.0 - math.exp(
                        -self.cfg["sample_s"] / self.cfg["avg_tau_s"])
                    self.avg += alpha * (tctl - self.avg)
                if self.avg_max is None or self.avg > self.avg_max:
                    self.avg_max = self.avg
                extra = (f"avg={self.avg:.1f} level={self.level} "
                         f"duty={self.duty_target():.2f}")
                before = self.state
                if self.safety:
                    if self.avg >= self.cfg["safety_c"]:
                        self.avg_samples_ge_safety += 1
                    if self.avg <= self.cfg["safety_resume_c"]:
                        self.safety = False
                        self._update_level(self.avg)
                        extra = (f"avg={self.avg:.1f} level={self.level} "
                                 f"duty={self.duty_target():.2f}")
                        self._apply(True, tctl, now, safety=True,
                                    extra=extra)
                elif self.avg >= self.cfg["safety_c"]:
                    self.avg_samples_ge_safety += 1
                    self.safety = True
                    self.safety_events += 1
                    if self.state == "RUNNING":
                        self._apply(False, tctl, now, safety=True,
                                    extra=extra)
                    else:
                        # already frozen in a duty slice: the shed
                        # takes over the freeze — record the takeover
                        # (no signal; the group is already stopped)
                        self.log("safety_stop", tctl, extra)
                else:
                    self._update_level(self.avg)
                    duty = self.duty_target()
                    extra = (f"avg={self.avg:.1f} level={self.level} "
                             f"duty={duty:.2f}")
                    if duty >= 1.0:
                        self.slice_acc = 0.0
                        want_running = True
                    else:
                        # Bresenham: spread the frozen slices evenly
                        # over time so no single freeze is long
                        self.slice_acc += duty
                        if self.slice_acc >= 1.0:
                            self.slice_acc -= 1.0
                            want_running = True
                        else:
                            want_running = False
                    self._apply(want_running, tctl, now, extra=extra)
                if self.state == before:
                    self.log("sample", tctl, extra)
            else:
                self.log("sample_na", None)

            # sleep the remainder of the sample interval, waking early
            # if the child exits
            deadline = time.time() + self.cfg["sample_s"]
            while time.time() < deadline:
                if self.proc.poll() is not None or self.shutdown:
                    break
                time.sleep(0.1)

        # never leave the group frozen, whatever happened
        if self.state != "RUNNING":
            self.group_signal(signal.SIGCONT)
            self.state = "RUNNING"
        try:
            exit_code = self.proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            self.log("exit_timeout", None,
                     "child still alive 30 s after SIGTERM; governor exits")
            if exit_code is None:
                exit_code = -1
        end = time.time()
        if self._state_since is not None:
            dur = end - self._state_since
            if self.state == "RUNNING":
                pass  # trailing partial burst not counted in bursts[]
            self._trailing = dur
        self.log("exit", None, f"exit_code={exit_code} timed_out={timed_out}")
        self.write_summary(start, end, exit_code, timed_out)
        return exit_code if exit_code is not None and exit_code >= 0 else 0

    def write_summary(self, start, end, exit_code, timed_out):
        s = sorted(self.samples)

        def pct(p):
            if not s:
                return None
            return s[min(len(s) - 1, int(p * len(s)))]

        def mean(xs):
            return round(sum(xs) / len(xs), 2) if xs else None

        wall = end - start
        summary = {
            "host": socket.gethostname(),
            "cmd": self.cmd,
            "profile": self.cfg,
            "start_iso": iso(start),
            "end_iso": iso(end),
            "start_epoch": round(start, 3),
            "end_epoch": round(end, 3),
            "wall_s": round(wall, 2),
            "run_s": round(self.run_s, 2),
            "frozen_s": round(self.frozen_s, 2),
            "duty_fraction": round(self.run_s / wall, 4) if wall else None,
            "cycles": self.cycles,
            "bursts_n": len(self.bursts),
            "mean_burst_s": mean(self.bursts),
            "cools_n": len(self.cools),
            "mean_cool_s": mean(self.cools),
            "tctl_n": len(s),
            "tctl_median_c": pct(0.5),
            "tctl_p95_c": pct(0.95),
            "tctl_max_c": s[-1] if s else None,
            "tctl_min_c": s[0] if s else None,
            "samples_ge_75": sum(1 for x in s if x >= 75.0),
            "samples_ge_80": sum(1 for x in s if x >= 80.0),
            "tctl_avg_max_c": (round(self.avg_max, 2)
                               if self.avg_max is not None else None),
            "safety_events": self.safety_events,
            "avg_samples_ge_safety": self.avg_samples_ge_safety,
            "exit_code": exit_code,
            "timed_out": timed_out,
        }
        with open(self.summary_path, "w") as f:
            json.dump(summary, f, indent=1)
        self.logf.write("SUMMARY " + json.dumps(summary) + "\n")
        print(json.dumps(summary, indent=1))
        return summary


def main():
    ap = argparse.ArgumentParser(description="Thermal duty-cycle governor")
    ap.add_argument("--profile", help="per-node profile JSON")
    ap.add_argument("--log", required=True, help="cycle log path")
    ap.add_argument("--max-seconds", type=float, default=None)
    ap.add_argument("--tctl-file", default=None,
                    help="read temperature (C, float) from this file "
                         "instead of the k10temp sensor (smoke tests)")
    ap.add_argument("--safety-c", type=float, default=None)
    ap.add_argument("--avg-tau-s", type=float, default=None)
    ap.add_argument("--sample-s", type=float, default=None)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    args = ap.parse_args()

    cmd = args.cmd
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        ap.error("no command given (expected -- <command...>)")

    cfg = dict(DEFAULTS)
    if args.profile:
        with open(args.profile) as f:
            prof = json.load(f)
        for k in DEFAULTS:
            if k in prof:
                cfg[k] = (prof[k] if isinstance(DEFAULTS[k], list)
                          else float(prof[k]))
    if args.safety_c is not None:
        cfg["safety_c"] = args.safety_c
    if args.avg_tau_s is not None:
        cfg["avg_tau_s"] = args.avg_tau_s
    if args.sample_s is not None:
        cfg["sample_s"] = args.sample_s
    if not (1.0 <= cfg["sample_s"] <= 10.0):
        ap.error("sample_s should be in the 2-5 s band")
    edges, duties = cfg["band_edges"], cfg["band_duties"]
    if len(edges) != len(duties) or edges != sorted(edges):
        ap.error("band_edges must ascend and match band_duties in length")
    if (any(not (0.0 < d <= 1.0) for d in duties)
            or duties != sorted(duties, reverse=True)):
        ap.error("band_duties must descend within (0, 1]")
    if not (edges[-1] < cfg["safety_c"]
            and cfg["safety_resume_c"] < cfg["safety_c"]):
        ap.error("need top band edge < safety_c and "
                 "safety_resume_c < safety_c")
    if cfg["avg_tau_s"] < 10.0:
        ap.error("avg_tau_s should be >= 10 s "
                 "(decisions ride the average, not the sample)")

    gov = Governor(cfg, cmd, args.log,
                   max_seconds=args.max_seconds, tctl_file=args.tctl_file)

    def on_signal(signum, frame):
        gov.shutdown = True
        # unfreeze immediately; the loop sends SIGTERM and reaps
        gov.group_signal(signal.SIGCONT)

    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    return gov.run()


if __name__ == "__main__":
    sys.exit(main())

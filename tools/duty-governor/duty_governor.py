#!/usr/bin/env python3
"""duty_governor.py — the inside-a-job thermal duty-cycle governor for the ranch.

Tonight's per-node soak sweep (~/workspace/nethack-solver/node-limits.md)
proved there is no sustained full-tilt operating point on any ranch node:
Tctl crosses 75 C within ~2-3 minutes at any instance count and saturates
at 88-91 C. Sustained work therefore runs as a governed duty cycle: the
workload runs at full speed until the die approaches the ceiling, is
frozen (SIGSTOP) while it cools, and resumes (SIGCONT) — repeat. The
house's between-job policy (new starts pause at >=75 C, resume <=70,
off-time to <=65 after an 80 C crossing; ranch-batchq) decides whether a
job may START; this governor is the layer inside a running job that keeps
it from ever reaching the line.

Control law (defaults; per-node values live in the profile JSON):
  - sample Tctl every sample_s seconds (2-5 s) from k10temp, resolved BY
    NAME under /sys/class/hwmon (the hwmon index varies per node — the
    fleet's ~/thermal/sample.sh pattern; never hardcoded).
  - Tctl >= pause_c (73)  -> SIGSTOP the workload's process group.
  - Tctl <= resume_c (70) -> SIGCONT. The band sits INSIDE the 75 C
    ceiling with margin: the governor's job is that 75 is never reached,
    not that it is ridden.
  - Hard rule (preserved from the 2026-11-04 ranch policy): if Tctl ever
    crosses hard_c (80), the group stays frozen until Tctl <=
    hard_resume_c (65) — the off-time rule.
  - The workload is never SIGKILLed by the thermal law. On governor exit
    (SIGTERM/SIGINT or --max-seconds), the group is SIGCONTed first —
    nothing is ever left frozen — then SIGTERMed as a shutdown, never as
    thermal control.

Usage:
  duty_governor.py --profile <node>.json --log <run.log> [--max-seconds S]
                   [--pause-c C] [--resume-c C] [--sample-s S]
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
import os
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime

DEFAULTS = {
    "pause_c": 73.0,
    "resume_c": 70.0,
    "sample_s": 2.0,
    "hard_c": 80.0,
    "hard_resume_c": 65.0,
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
        self.state = "RUNNING"  # RUNNING | FROZEN | FROZEN_HARD
        self.shutdown = False
        self.samples = []
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
        if event in ("stop", "cont", "hard_stop", "hard_cont", "start", "exit"):
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
    def _enter(self, new_state, event, tctl, now):
        if self._state_since is not None:
            dur = now - self._state_since
            if self.state == "RUNNING":
                self.bursts.append(dur)
            else:
                self.cools.append(dur)
        self.state = new_state
        self._state_since = now
        self.log(event, tctl)

    def stop(self, tctl, now, hard=False):
        self.group_signal(signal.SIGSTOP)
        self.cycles += 1
        self._enter("FROZEN_HARD" if hard else "FROZEN",
                    "hard_stop" if hard else "stop", tctl, now)

    def cont(self, tctl, now, hard=False):
        self.group_signal(signal.SIGCONT)
        self._enter("RUNNING", "hard_cont" if hard else "cont", tctl, now)

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
                ev = "sample"
                if self.state == "RUNNING" and tctl >= self.cfg["hard_c"]:
                    self.stop(tctl, now, hard=True)
                    ev = "hard_stop"
                elif self.state == "RUNNING" and tctl >= self.cfg["pause_c"]:
                    self.stop(tctl, now)
                    ev = "stop"
                elif self.state == "FROZEN" and tctl >= self.cfg["hard_c"]:
                    self._enter("FROZEN_HARD", "hard_stop", tctl, now)
                    ev = "hard_stop"
                elif self.state == "FROZEN" and tctl <= self.cfg["resume_c"]:
                    self.cont(tctl, now)
                    ev = "cont"
                elif (self.state == "FROZEN_HARD"
                      and tctl <= self.cfg["hard_resume_c"]):
                    self.cont(tctl, now, hard=True)
                    ev = "hard_cont"
                if ev == "sample":
                    self.log("sample", tctl)
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
    ap.add_argument("--pause-c", type=float, default=None)
    ap.add_argument("--resume-c", type=float, default=None)
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
                cfg[k] = float(prof[k])
    if args.pause_c is not None:
        cfg["pause_c"] = args.pause_c
    if args.resume_c is not None:
        cfg["resume_c"] = args.resume_c
    if args.sample_s is not None:
        cfg["sample_s"] = args.sample_s
    if not (1.0 <= cfg["sample_s"] <= 10.0):
        ap.error("sample_s should be in the 2-5 s band")
    if not cfg["resume_c"] < cfg["pause_c"] < 75.0:
        ap.error("need resume_c < pause_c < 75 (the ceiling is never ridden)")

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

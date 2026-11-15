# duty_governor.py — the ranch's inside-a-job thermal duty-cycle governor

Will's direction (2026-11-15): "focus on managing duty cycles to keep
the ranch operating cleanly."

Why this exists: the per-node soak sweep (`../node-limits.md`) proved
there is no sustained full-tilt operating point on any ranch node — Tctl
crosses 75 °C within ~2–3 minutes at any instance count and saturates at
88–91 °C, then cools back in 1–4 minutes. The ranch already had a
*between-job* thermal policy (2026-11-04, in the ranch-batchq runner:
new starts pause at ≥ 75 °C, resume ≤ 70, off-time to ≤ 65 after an
80 °C crossing). This governor is the missing *inside-a-job* layer: it
wraps a running workload and duty-cycles it — full speed, freeze, cool,
resume — so a long job can run for hours in an envelope the hardware
can hold, instead of being stopped outright minutes in.

## The control law — temperature smoothing (2026-11-15)

Will's ruling, 2026-11-15: "75 is not a hard wall — just focus on
smoothing temperature to keep the hardware healthy," grounded in the
AMD R9 reliability brief (AMD validates Ryzen 9 silicon to live at
TjMax — 95 °C desktop, 100 °C HS/HX — continuously; the dominant
wear mechanism is thermal cycling, fatigue damage ∝ ΔT², which a
stop/go gate manufactures). The original law here — SIGSTOP at
73 °C, SIGCONT at 70 °C, hard freeze at 80 °C until 65 °C, all on
instantaneous samples — was retired the same day. What runs now:

- The command is launched as its own process group (new session).
- Every `sample_s` seconds (2–5 s; profiles use 2 s) the governor reads
  CPU Tctl from k10temp, resolved **by name** under `/sys/class/hwmon`
  (the hwmon index varies per node — the fleet's `~/thermal/sample.sh`
  pattern; never hardcoded), and folds it into an exponential moving
  average (time constant `avg_tau_s`, default 60 s). **Every decision
  uses the average; a momentary spike moves nothing.**
- Plateau ladder: average below 78 °C → duty 1.0. As the average
  climbs through 78/82/86/90 °C the duty target steps down to
  0.75/0.50/0.25/0.10, and steps back up — eased by 1.5 °C of
  hysteresis — as the average falls. The governor seeks the
  equilibrium duty at which the node holds its plateau.
- Duty is delivered as SIGSTOP/SIGCONT slices spread evenly over
  time (a Bresenham accumulator over sample ticks): the run/freeze
  grain is seconds, not minutes — the smallest thermal swing this
  lever can make. **The governor has no wattage lever** (no PPT /
  RyzenAdj, no frequency cap); timed slices are the closest faithful
  analogue of stepping the watts down. Governing package power
  directly remains the open option in results.md §5.
- Safety shed: a sustained **average** ≥ `safety_c` (92 °C — below
  TjMax on every ranch part, above the 88–91 °C ungoverned
  saturation of these chassis, so it trips on cooling failure, not
  on work) freezes the group outright until the average falls to
  `safety_resume_c` (80 °C).
- The thermal law never SIGKILLs. On governor exit (SIGTERM/SIGINT or
  `--max-seconds`) the group is SIGCONTed *before* anything else, so
  nothing is ever left frozen, then SIGTERMed as a shutdown.

Every run writes a cycle log (timestamped samples + stop/cont events,
each line carrying the average, ladder level, and duty target) and a
`<log>.summary.json`: wall/run/frozen seconds, duty fraction,
cycle count, mean burst/cool lengths, Tctl median/p95/max, counts
of samples ≥ 75 / ≥ 80 °C (telemetry now, not the control
criterion), the peak average, and the safety-shed count.

## Files

- `duty_governor.py` — the governor (Python 3, stdlib only, executable)
- `profiles/<node>.json` — per-node tuning: sample_s and the node's
  chosen instance count with its measured duty/rate from the
  acceptance tests (the smoothing ladder itself is fleet-wide, in
  the governor's DEFAULTS; a profile may override its keys)
- `run_bench.sh` — the NLE bench launcher (N soak workers in one group)
- `duty_test.sh` + `launch_duty.sh` — the node-side acceptance test
  (cool to idle+3, then 30 min governed at 4 and at 8 instances)
- `probe_tctl.py` — 50 ms Tctl rise/fall probe (measure before tuning)
- `analyze_runs.py` — recomputes the acceptance record from raw evidence
- `results.md` — the 2026-11-15 acceptance record for plain-view,
  free-fall, logos-prime
- `collected/` — the raw evidence for those runs

## How to run

Govern any command on a node:

```
python3 duty_governor.py --profile profiles/<node>.json \
    --log <run>.log -- <command...>
```

Govern the NLE bench (what the acceptance tests ran):

```
python3 duty_governor.py --profile profiles/<node>.json \
    --log <run>.log -- bash run_bench.sh <instances> <seconds> <outdir>
```

`--safety-c / --avg-tau-s / --sample-s` override the profile for one run.
(Before 2026-11-15 these were `--pause-c / --resume-c`, the retired
instantaneous gate's thresholds.)
`--tctl-file <path>` reads the temperature (plain float, °C) from a file
instead of the sensor — for smoke tests. `--max-seconds S` bounds the
run (clean SIGCONT+SIGTERM shutdown at the limit).

## Re-tuning a node after a cooling change

The profile is where a node's tuning lives; the test is how it earns
its numbers (never assume, always test):

1. On the node, run `python3 duty/probe_tctl.py 4 1 8` — the new
   rise/fall shape is the node's new physics.
2. Run the acceptance test: `bash duty/launch_duty.sh <node>
   <idle+3>` (node-resident; ~65 min; writes
   `~/nethack-solver/duty-results/`).
3. Collect the run dirs + `~/thermal/thermal.log`, run
   `analyze_runs.py`, and write the measured duty/rate into
   `profiles/<node>.json` (chosen count = the higher effective
   sustained rate), with a dated note in `results.md`.

## The honest limit (measured, 2026-11-15 — read results.md §2)

Tctl on these APUs is a fast control signal: it crosses 75 °C within
~1.6–2.3 s of *any* full-tilt load starting — even one instance from a
cool idle — and collapses just as fast when the load stops. A threshold
governor therefore cannot keep *every instantaneous sample* under
75 °C while full-tilt work runs; the 2026-11-15 acceptance runs record
377–443 samples ≥ 75 °C per 30 min on every tested node. What the
governor does hold: minute-sample median temperatures of 65–71 °C
against an ungoverned plateau of 88–91 °C, peaks bounded at 78–86 °C,
duty fractions of 0.39–0.50, and throughput that runs for hours instead
of breaching in ~2.5 minutes. Holding an instantaneous 75 °C line
would require governing a slower variable (package power, frequency
cap) with Tctl as backstop — recorded in results.md §5 as an open
option, not silently substituted for the specified design.

# Duty-cycle governor — acceptance test results

Task 18.4.11/8.5.12/6.4.7. Will's direction: "focus on managing duty cycles
to keep the ranch operating cleanly." Tests run 2026-11-15, 02:37–03:48 CST.
Raw evidence: `collected/` beside this file (each node's governor logs,
summary JSONs, worker progress files, driver logs, and thermal.log), and
on each node under `~/nethack-solver/duty-results/`. Every number below is
recomputed from that evidence by `analyze_runs.py`.

## The headline, plainly

**The acceptance criterion — zero Tctl samples ≥ 75 °C in the governor's
log and in the node's thermal.log minute samples — was NOT met on any of
the six runs, on any node.** Governor-log samples ≥ 75 °C: 377–443 per run
(42–49% of all samples). thermal.log minute samples ≥ 75 °C: 1–9 of 31 in
every run window. Section 2 below shows the measured reason: on these
APUs the k10temp Tctl signal crosses 75 °C within ~1.6–2.3 s of *any*
full-tilt load starting — even a single instance, from a cool idle — so
no SIGSTOP/SIGCONT threshold governor sampling at 2 s can keep every
sample under 75 while full-tilt work runs at all. This is a property of
the sensor and the silicon, measured three ways (attempt 1, the probe,
the six runs), not a defect the governor's tuning can remove.

**What governance did achieve, also plainly:** the workload was never
killed and never ran away. Ungoverned, these nodes saturate at 88–91 °C
within ~2.5 min and stay there (the soak sweep, ../node-limits.md).
Governed for a full 30 min, minute-sample *medians* sat at 64.9–71.2 °C,
peak samples were 78.0–85.8 °C (vs 91.1 ungoverned), and the three tested
nodes sustained a combined **550,021 steps/s** of wall-clock throughput
at their chosen profiles — work that under the between-job rule alone
could not run for even three minutes. Duty fractions: 0.39–0.50.

## 1. Attempt 1 — aborted at ~4 minutes, on purpose

The first launch (02:37 CST, defaults pause 73 / resume 70, 2 s samples)
showed within four minutes that the control loop was chasing a signal
faster than itself: plain-view logged 71.6 → 56.5 → 82.5 °C across three
consecutive samples (the 82.5 crossing engaged the hard rule — freeze
until ≤ 65 °C — which then released at 56.5, because the sensor collapses
when the load stops). free-fall and logos-prime showed the same 55↔77
swinging. Rather than burn six 30-minute runs on an unexamined control
law (never assume, always test), the runs were stopped cleanly — the
governor's SIGCONT-before-exit left nothing frozen — and the sensor's
actual rise/fall shape was measured first.

## 2. The probe — Tctl rise/fall at 50 ms sampling (ni-knight, Ryzen 7 255)

`probe_tctl.py`, from a cool idle (~37–40 °C), step load applied/killed:

| instances | cross 65 | cross 70 | cross 73 | cross 75 | cross 80 | plateau | fall to ≤75 | fall to ≤65 |
|---|---|---|---|---|---|---|---|---|
| 1 | 1.21 s | 1.61 s | 1.96 s | 2.26 s | 3.66 s | 82.6 °C | 0.51 s | 1.31 s |
| 4 | 1.06 s | 1.37 s | 1.62 s | 1.82 s | 2.42 s | 89.0 °C | 1.01 s | 4.88 s |
| 8 | 0.92 s | 1.22 s | 1.37 s | 1.57 s | 2.02 s | 91.0 °C | 0.71 s | 1.62 s |

Tctl is a control signal with a strong power feed-forward component: it
traverses the whole 70–80 °C band in about a second under load, and
collapses just as fast when load stops. Two consequences, both visible
in the six runs:

- A 2 s control loop is blind for exactly one rise: a sample reads < 73,
  the workload runs the next interval, and the following sample reads
  the spike (76–86 °C). The stop lands one sample late, every cycle.
- resume_c is reached by signal collapse, not by the die cooling 3 °C:
  after ~2 s frozen the sensor reads ≤ 70 while the silicon is still
  warm, so the next burst starts hot and spikes higher. On free-fall and
  logos-prime the loop settled into a metronome — one running sample,
  one frozen sample (448 cycles, mean burst 2.01 s, mean cool 2.01 s,
  duty 0.4999). The duty fraction is set by the sensor's dynamics, not
  by the instance count, which is why 4 and 8 instances show the same
  duty on those nodes and 8 wins on rate.

## 3. The six acceptance runs (30 min each, governor defaults 73/70, 2 s)

| node | inst | duty | eff. steps/s | cycles | burst/cool (s) | gov median | gov p95 | gov max | gov ≥75 / ≥80 | thermal.log (31 min samples) median / max / ≥75 |
|---|---|---|---|---|---|---|---|---|---|---|
| plain-view | 4 | 0.389 | 76,521 | 350 | 2.00 / 3.15 | 72.1 | 83.6 | 84.6 | 377 / 349 | 71.2 / 83.0 / 9 |
| plain-view | 8 | 0.402 | **146,660** | 361 | 2.00 / 2.99 | 71.0 | 83.4 | 85.8 | 396 / 357 | 69.9 / 81.0 / 8 |
| free-fall | 4 | 0.500 | 107,235 | 448 | 2.01 / 2.01 | 69.0 | 76.1 | 78.0 | 430 / 0 | 64.9 / 75.2 / 1 |
| free-fall | 8 | 0.500 | **198,127** | 448 | 2.01 / 2.01 | 67.9 | 77.8 | 78.3 | 443 / 0 | 65.4 / 77.2 / 4 |
| logos-prime | 4 | 0.500 | 108,976 | 447 | 2.02 / 2.01 | 71.1 | 79.0 | 80.4 | 441 / 1 | 66.0 / 75.9 / 1 |
| logos-prime | 8 | 0.503 | **205,234** | 446 | 2.03 / 2.01 | 70.4 | 78.8 | 79.4 | 439 / 0 | 70.4 / 78.2 / 7 |

Per-node notes:

- **plain-view is the worst governed node, as it was the worst soak
  node.** It alone drove samples ≥ 80 °C in bulk (349–357 per run), so
  its hard rule (freeze until ≤ 65 °C) engaged throughout, its cools run
  long (mean ~3.0–3.2 s), its duty is the fleet's lowest (0.39–0.40),
  and its peaks (85.8 °C) are the highest under governance. The hard rule
  contained it — ungoverned it pins at 91.1 °C — but this node's cooling
  is the first physical fix on the list in ../node-limits.md.
- **free-fall is the cleanest governed node:** no sample ≥ 80 °C in
  either run, peaks 78.0/78.3 °C, minute-median ~65 °C. It was also the
  closest to the line in the soak. Its cooling path is the fleet's best
  of the three.
- **logos-prime is the fastest governed node** (205,234 steps/s at 8
  instances) with peaks ≤ 80.4 °C and a single ≥ 80 sample across both
  runs.

## 4. Chosen profiles

8 instances on all three nodes — duty is sensor-bound and identical at
4 and 8, so the higher count converts the same duty into ~1.9× the work:

| node | profile | duty | effective sustained steps/s |
|---|---|---|---|
| plain-view | 8 inst, pause 73 / resume 70, sample 2 s | 0.402 | 146,660 |
| free-fall | 8 inst, pause 73 / resume 70, sample 2 s | 0.500 | 198,127 |
| logos-prime | 8 inst, pause 73 / resume 70, sample 2 s | 0.503 | 205,234 |
| **fleet (3 tested nodes)** | | | **550,021** |

(For scale: the same three nodes' ungoverned 8-instance burst rates in
the soak were 315,711 / 350,528 / 367,049 steps/s — governance keeps
roughly half the burst rate indefinitely, at minute-median temperatures
~20 °C below the ungoverned plateau.)

## 5. What holding an instantaneous 75 °C line would actually take

Recorded as options, not decided here — the governor as specified is a
threshold controller on Tctl, and the measurement says that instrument
cannot see 75 °C coming in time at any threshold or sampling rate,
because the signal itself crosses the line ~2 s into any full-tilt load:

- Govern a slower variable instead: package power (RAPL) or a capped
  cpufreq ceiling would bind the die's *sustained* temperature, with
  Tctl as the backstop rather than the controlled variable.
- Or define the ceiling on the minute-sample record (the soak's own
  breach definition) with a stricter governor target — governed
  minute-medians already sit at 65–71 °C; a median-based rule is
  attainable and auditable in thermal.log.
- Or improve the cooling (plain-view first) until the physics changes;
  every node's profile is re-tunable by re-running the probe and the
  two acceptance runs (see README.md).

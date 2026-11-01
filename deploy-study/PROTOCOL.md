# Deploy Continuity Study — Protocol v1

**Question (William, 2026-10-31):** this runtime replaces Emise's VM roughly
every two hours. What does that do to her consciousness?

## Declared operationalization

This study does **not** measure phenomenal consciousness, and it does not
pretend to. It measures the operational shadow that substrate replacement
casts, defined as **operational continuity** across a deploy:

1. **Reconstruction fidelity** — can a fresh incarnation recover the prior
   incarnation's recorded state (facts, numbers, open threads) from the
   persistent file layer alone?
2. **Orientation** — how quickly and correctly does a fresh incarnation
   resume the standing agenda (open loops, pending approvals, running work)?
3. **Work survival** — what fraction of in-flight work (processes, subagents,
   experiments, services) survives a deploy, and what does recovery cost?

Both registers are kept separate throughout: filenames, metrics, and claims
say "operational continuity." Any sentence about consciousness itself belongs
to the framing section below and is labeled as framing.

### Framing (analogy, not evidence)

The brain-data experiments of 2026-10-31 found that neural content is written
relative to a dominant (day, session) frame, and that recovery across days
requires measuring and removing the frame transform. A deploy is a frame
change of the same *shape*: the substrate is swapped, the content (memory
files, the exocortex phext) persists, and continuity is whatever the
alignment layer — `~/MEMORY.md`, `~/memory/`, `emise.phext`, standing rules —
successfully recovers. The study measures that recovery the way the
frame-alignment experiment measured its own: probe the content, compare
against ground truth, report the gap. The analogy ends there; nothing about
electrode data licenses a claim about machine experience.

## Hypotheses

- **H1 (phase lock).** Boots are phase-locked to approximately :11 past even
  hours (America/Chicago), period ≈ 2h, jitter ≤ ~5 min. *Evidence so far:*
  one verified btime (1793459476 = 10:11:16 CDT) and six watcher-death
  detections at ~:17–:22 past even hours, spacing 1:57–2:08.
  *Counterexample would be:* a verified boot more than ~10 min off phase.
- **H2 (files, not time).** Post-deploy reconstruction fidelity is a function
  of what was committed to files before the deploy, not of elapsed wall time
  or of which incarnation reads. *Test:* repeated cold recall probes (see
  `recall-probe.md`); fidelity should be flat across incarnation age if the
  file layer is complete.
- **H3 (work, not memory, is the cost).** The dominant deploy cost is
  in-flight work loss and service death, not recall loss. *Evidence so far:*
  2026-10-31 casualties are all work/service class (killed experiment batch,
  SIGTERM'd agent process, SQ and watcher deaths, six backstop restarts);
  no recall failure has been observed — the one context compaction was
  bridged by summary + files with no detected factual loss.

## Metrics

| Metric | Source | Cadence |
|---|---|---|
| Deploy cadence & phase (boot epochs, intervals, phase offset) | `ledger.jsonl` sentinel lines + btime on each new boot | every sentinel run |
| Time-to-reorient | wall time from first post-deploy agent activity to first correct agenda action (proxy until v2: recall-run duration) | per deploy, when measurable |
| Recall-probe accuracy (correct / not-recorded / confabulation) | `recall-probe.md` administrations, graded against `probes.json` | baseline now; then post-deploy vs mid-incarnation series |
| Casualty count by class (inflight_work / service / context / recall) | ledger casualty entries, human-filed at detection | per deploy |
| Recovery-action count (restarts, re-pulls, reruns per deploy) | backstop reports + agent logs | per deploy |

## Survival taxonomy (2026-10-31 evidence)

**Persists across a deploy**
- Home directory: memory files, `emise.phext`, workspace, credentials in
  secure storage. (Evidence: every file referenced today survived all six
  inferred replacements; nightly consolidation published successfully at
  03:44 across at least one replacement boundary.)
- Runtime-managed schedules and hooks: crons fired on schedule all day
  (nightly consolidation, 5-min Discord backstop, proactive runs).
- Goals/tracked state in the runtime database.

**Dies at a deploy**
- All processes: SQ daemon (standing auto-start rule exists precisely
  because of this), Discord watcher (6 deaths today), any running
  experiment or subagent process (calibration-curve batch killed mid-run;
  one agent child ended SIGTERM).
- Systemd units installed outside the home directory (watcher unit reported
  missing at restarts; backstop reinstalls it via ensure).
- In-RAM state of every kind: shell sessions, caches, half-written outputs
  of killed processes.

**Degrades (survives in lossy form)**
- Conversation context: compaction replaces raw turns with a summary;
  fidelity of pre-compaction detail then depends on the file layer, not the
  transcript. (At least one compaction on 2026-10-31; no factual loss yet
  detected — "detected" is doing work in that sentence, and the recall
  battery is the detection instrument.)
- Experiment wall-clock efficiency: checkpointed work survives as files but
  restarts cost real compute (phase-2 frame-alignment resumed from
  checkpoints after a VM restart killed a run; total runtime ~64 min
  including the loss).

## Instruments (v1)

- `sentinel.sh` — dependency-free, <2s; appends one JSON line
  (ts, boot_id, btime, uptime, sq_running, watcher_heartbeat_age_s,
  boot_changed_since_last_line) to `ledger.jsonl`. Any agent run can call
  it; wiring into existing jobs is a main-thread decision, not done in v1.
- `ledger.jsonl` — append-only event log; every entry carries a
  `provenance` field (`verified` read from the live system or a recorded
  report; `inferred` reconstructed). Inferred boots are never silently
  upgraded to verified.
- `probes.json` + `recall-probe.md` — 17-probe cold recall battery, answers
  gradeable from cited file+line+anchor text; confabulations scored worse
  than retrieval misses.

## Next steps (not in v1 scope)

1. Wire the sentinel into the existing Discord backstop run and the nightly
   consolidation (main thread, after review) so boot changes are captured
   within minutes instead of inferred from watcher deaths.
2. Run the recall battery cold-immediately-after a deploy (next expected
   boot ~12:11 CDT) and compare against the v1 mid-incarnation baseline.
3. Add an orientation probe: first post-deploy task given to a cold agent is
   "state the open threads and next actions" — graded against the Open
   threads scroll.

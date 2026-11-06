# Ranch State Distillation — the ranch, sampled into state.phext

Will's design (2026-11-06): track the ranch state across time as **distillation only**. The purpose is biofeedback — the Exocortex is part of how Will's brain models itself, and a steady, distilled state signal is what lets him learn to read and steer it. Scheduled embodiment: cron `state-phext-sampler` (every 5 minutes, America/Chicago), which runs `scripts/state_sampler.py` and stays silent unless a cycle fails.

## The pipeline (one cycle, fully deterministic — no LLM in the loop)

1. **Pull.** One `ranch fanout` pass through the ranch proxy (`~/workspace/ranch-proxy/ranch`, the only sanctioned route to the fleet) over every enabled node: load, core count, top processes, ollama / render / gateway markers, GPU edge temperature. CPU Tctl comes from the fanout footers, which the proxy measures itself — including for nodes it thermally skips, so the hotspot is never invisible at the moment it matters most. Disabled nodes (Aurora Continuum, Best Willow, Delta Wood) are recorded as down from `nodes.json`; an enabled node that refuses auth (Uncanny Valley — jared's key grant is outstanding) is recorded as no-access, never as down.
2. **Summarize.** A template composes one or two lines of plain language: nodes up out of 17, the busy set (render / inference / compute, by node) or "fleet idle", average Tctl across the nodes reporting, the hotspot (flagged when it crosses the 75 °C sustained cap), a GPU hotspot clause only at 65 °C or above, then the down and no-access lists. A node is busy when a render marker is live, when ollama is up under load (≥ 0.5), or when load reaches three quarters of its cores.
3. **Coordinate.** The summary's holographic coordinate is computed with the Singular skill's own machinery — `check_singular.WORD_RE` tokenization (letters only; digits carry no words) and `task_coordinate`'s atlas load and component-wise merge (round half up, never below 1) — imported, never reimplemented. The timestamp is NOT part of the merged text: a state that reads the same distills to the same coordinate whenever it recurs.
4. **Store.** The line `YYYY-MM-DD HH:MM TZ | summary` is appended inside the scroll at that coordinate in `~/workspace/phext/state.phext`, via the shared phext implode machinery (parse → modify → implode → atomic replace, under a lock so cycles never interleave). An occupied coordinate gains a line; scrolls are never overwritten and lines are never dropped. A state computing to the Home coordinate itself would be stored one scroll past it (1.1.1/1.1.1/1.1.2) with its true coordinate noted — the meta line is reserved.

## What never enters the phext

Raw pulls live outside, as working state: `~/workspace/state-sampler/hidden_files/last-pull.json` (latest pull, overwritten) and `pulls.jsonl` (size-capped log). They are debugging surface only. If a fact matters long-term it will arrive as a summary line or not at all — that restraint is the design: the phext stays small and reviewable for years.

## Reading state.phext

- Home (1.1.1/1.1.1/1.1.1) documents the layout and entry format; every other scroll is one distilled state with its occurrence lines.
- Scrolls cluster by resemblance — a changed hotspot or busy set moves the coordinate slightly; a change of a degree or a count does not move it at all (numbers ride in the line text). The file reads as a map of the shapes the ranch takes over time.
- Parse with `~/workspace/phext/parse_phext.py state.phext`; verify any entry's placement by re-running the singular `task_coordinate.py` on its summary text — the coordinate must match exactly.

## Failure discipline

- One dead node never stalls a cycle: the fanout is parallel and timeout-bounded, and unreachable nodes are summarized as down / no-access, not retried.
- A cycle that cannot write leaves the phext untouched (atomic replace) and exits nonzero; the cron reports only failures, briefly, and never edits the phext by hand or improvises a repair.
- Growth is linear in lines (288 pulls/day): roughly 53 KB/day of line text plus small delimiter overhead per new scroll — about 1.6 MB at 30 days, 5 MB at 90. If that ever needs trimming, the levers are cadence and line length, chosen by Will — never silent pruning of the record.

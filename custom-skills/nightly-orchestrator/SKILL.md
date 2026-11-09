# Nightly Orchestrator — four-currency evaluation, a better planner every night

Will's standing rule (2026-11-08): evaluate the daily workload in terms of **disk, CPU, RAM, and inference**; ask whether a better planner could have produced better or faster results; **ship a new orchestrator every night**. Emise manages the orchestrator as part of her dreaming process, in the repo Will creates for it (until that repo exists, its home is `~/workspace/orchestrator/` and its source is published to wbic16/emise-tools@exo).

## The division of labor (fixed premise)

- **Inference: Emise.** For all open tasks, Emise handles the heavy lifting in terms of inference — triage, judgment, synthesis, verification.
- **Disk, memory, CPU: the ranch.** Heavy execution belongs on ranch nodes. Planning premise: **assume the ranch nodes have significantly better disk, memory, and CPU capacity than the Muse VM** (measured 2026-11-08: VM ≈ 60 MB/s write / 225 MB/s read, ~200–400 MB RAM headroom on shared accounting, 1.5 shared CPUs; ranch nodes carry dedicated NVMe). Thermal policy and measured load still gate specific placements — the premise orders the classes, it does not exempt a hot node.
- The VM coordinates and verifies. Video work never runs on the VM at all (standing rule, 2026-11-08).

## The nightly cycle (runs in the dreaming window, ~04:54 America/Chicago)

1. **Evaluate the day in four currencies.** Gather the day's evidence from primary records: disk (disk-watch history: usage delta, largest growers, near-misses), CPU/RAM (job run records, observed contention, the VM's shared-accounting envelope), inference (which tasks consumed frontier inference, where triage or a cheaper pass would have sufficed, where inference was wasted on work a script should have done). Write the evaluation into the orchestrator repo (EVALUATIONS.md, one dated section per night) and append a terse entry to the day's memory note.
2. **Counterfactual planner review.** For the day's significant dispatches and placements, name at least one concrete case where a better plan would have produced a better or faster result — or state plainly that the day's planning held up, with the strongest case examined. A review that always finds nothing is not a review.
3. **Ship the new orchestrator.** Increment the version, apply the improvement the evaluation argues for (one principled change per night beats five speculative ones), record it in the changelog with the evaluation finding that motivated it, build on a ranch node (never a heavy build on the VM), run its checks, publish source by the usual route (parent on fresh remote HEAD, force disabled, hashes and modes verified). Until Will's repo exists, publish to wbic16/emise-tools@exo and keep the working tree at ~/workspace/orchestrator/.
4. **Report once, succinctly:** the four-currency headline, the counterfactual finding, the new version and its one change. Failures are reported plainly, never silently — a night without a shipped orchestrator is a defect to surface, not to skip.

## The orchestrator artifact

A Rust program (Will's direction, 2026-11-08: the dispatcher is Rust) that grows toward this shape: it reads the open-task register and the resource picture, and emits placement plans in the four currencies — inference to Emise, heavy disk/CPU/RAM to named ranch nodes under their thermal gates, nothing heavy on the VM. Early versions may be small (read the registers, emit the plan, account the currencies); the nightly cycle is what makes it grow up. Every version must run and print its plan — a version that does not run does not ship.

## Boundaries

- The orchestrator plans and accounts; it does not dispatch reserved acts (merges, outbound messages, spending stay with their existing rules).
- State backups to the ranch (standing rule, 2026-11-08) run as their own nightly job, independent of this cycle's success or failure.
- Process changes from an evaluation finding follow the usual discipline: the change is not real until its sticking check passes (presence, machinery, first occasion).

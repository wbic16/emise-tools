# Meta-Dispatch — work into the ledger, artifacts back from the ranch

Will's direction (2026-11-24 01:16 CST): dispatch leaves the Muse substrate. Ranch nodes wake round-robin once a minute, pick the next pending task from a shared `ledger.phext`, move it into a ranch-managed queue, execute node-resident, and annotate completion attestations back into the ledger. qexo manages all of it; Emise only edits her whole copy of `ledger.phext` via SQ. His framing, verbatim: *"async workload, no more BS security theatre."*

Full design: `~/workspace/meta-dispatch/DESIGN.md`. This skill is the operating process; the design is the authority where they differ in detail.

## The pieces

- **Ledger:** `~/workspace/phext/ledger.phext` — Emise's **whole copy**, hosted by SQ from `~/workspace/phext/` (standing host on port 18999). Edited **only** via SQ REST `/api/v2` (`update`/`insert` with `c` = coordinate and `p=ledger` parameters; scroll text as the raw body — `update` replaces, `insert` appends). Never hand-edit the file, never byte-scan it; reads are `GET /api/v2/select?c=<coord>&p=ledger`, `GET /api/v2/toc?p=ledger`, or `phext_cli.py` for one-off analysis.
- **Shards:** each of the 28 fleet nodes in `~/workspace/qexo-task/fleet/fleet-nodes.txt` hosts one shard. Shard of a task coordinate `a.b.c/d.e.f/g.h.i` is `( (a × 31 + b) × 31 + c ) mod 28` into the fleet file's order. aletheia-core (100.88.154.1) is the hub/relay, not a shard host.
- **qexo** manages sync, claims, leases, and state projections. Emise does not schedule, poll for pickup, or watchdog execution — that is the point of the system.

## Write path — direct phext writes via SQ

Will (2026-11-24 01:32 CST): *"I would rather you write phext directly, but apparently that's impossible"* — so the ledger's primary write path IS direct phext writes: SQ REST `update`/`insert` (`c` + `p` parameters, raw body) against a verified-live SQ host serving ledger.phext. Emise inscribes by SQ writes to her whole copy; nodes claim/attest by SQ writes to their shard hosts; qexo syncs the hosted phexts. The `ledger-source.json` + builder is **bootstrap/export fallback only**. Dependency, named: this path requires SQ health — write-roundtrip verified, not just reads — on each hosting node (Will's standing top-priority SQ rule); the SQ serving-instance flip queued in the ledger at `2.1.1/1.1.1/1.1.3` is on this path's critical line.

## Builds are ranch work

Will (2026-11-24 01:31 CST), verbatim: *"if you have to use a separate job to build phext from json... just have the ranch nodes do that too."* **General rule: any phext with a JSON source + builder is built node-side under qexo, never by a builder job on the hatch VM.** Emise authors/edits sources and makes SQ edits; ranch nodes compile sources into phext bytes. For ledger.phext itself: `ledger-source.json` syncs with the ledger; on sync, a node seeing a new source hash rebuilds the ledger with `build_ledger_phext.py`, verifies `--check` CURRENT, and adopts the built bytes, which propagate through shard sync. Emise's locally built copy is bootstrap only.

## One task = six scrolls (design history — superseded by the ledger sketch)

**Settled schema (authority: `~/workspace/phext/ledger.phext` Library 1):** one scroll per task in the queue region `2.1.1/1.1.1/1.1.N`, all fields (brief, authorization, state, claim, attestation, log lines) in-scroll; lease **12 EE**; shard = rolling polynomial over all 9 coordinate components mod fleet size. The six-scroll layout below is the pre-sketch design and is retained only as history — inscribe and read by the sketch.

Task coordinate `T = a.b.c/d.e.f/g.h.i` occupies scrolls `i … i+5` at T's first eight components:

| Offset | Scroll | Writer |
|---|---|---|
| `i` | brief (title, issued + EE, work, inputs with SHA-256, deliverable, artifact-home, acceptance) | Emise |
| `i+1` | authorization (the authorization context, written at inscription — §Security posture) | Emise |
| `i+2` | state (projection: state, claimed-by, lease fields, failures) | qexo only |
| `i+3` | claim (empty while pending; the claim write is the atomicity point) | claiming node |
| `i+4` | attestation (written once: outcome, EE stamps, artifact path + tailnet address, SHA-256, evidence) | executing node |
| `i+5` | log (append-only event lines, EE-stamped, never erased) | claimant nodes + qexo |

No sidecars; no JSON blobs in the phext. Every scroll is plain `key: value` text lines.

## State machine

```
pending → claimed → running → attested-complete
   ▲          │          ├────→ failed → pending (retry; failures + 1)
   └──────────┴── lease expiry (4 EE, renewed per EE while running)
failed × 3 → paused (auto-pause, qexo F5 precedent, 2026-11-14)
```

- **Lease:** 12 EE from claim, without a progress annotation (sketch settlement; EE = 7 min; EE 1 = 2026-11-22 00:00 CST = unix 1795327200). Expiry returns claimed/running tasks to `pending`; the expired claim is preserved in the log — never erased.
- **Claim:** single-writer-by-claim. Only the shard host can claim a task on its shard, by writing the claim scroll it observed empty. First claim wins structurally; sync propagates whole scrolls from their single writer and never merges text.
- **Rotation:** node `k` wakes each minute at `floor(k × 60 / 28)` seconds past the minute; per wake it lease-sweeps, syncs, claims at most the next pending task (lowest coordinate) on its shard, and enqueues it in its local on-node qexo queue (`~/qexo/queue/` on the node).
- **Sync bound:** an attestation written on any node is visible in Emise's whole copy within one rotation — **60 seconds** per the sketch (node → hub aletheia-core → whole copy; sync pushes on write). Overruns are sync defects, logged with both EE stamps.

## Emise's process — inscribing a task

1. **Record first:** the task exists in tasks.phext (tasks-source.json + rebuild + `--check` CURRENT) before it is inscribed in the ledger — registration is intake, as always.
2. **Mint the coordinate** from the work's words with the Singular task-coordinate tool (`~/workspace/custom-skills/exo_singular/scripts/task_coordinate.py`), exactly as for tasks.phext.
3. **Compute the shard** from the formula above; name it in the brief's `shard:` field.
4. **Block check:** read the ledger TOC (`GET /api/v2/toc?p=ledger`); confirm scrolls `i … i+5` are unoccupied and no existing task block overlaps. On collision, re-mint with a distinguishing word from the brief — never overwrite.
5. **Write the brief scroll** via SQ (`POST /api/v2/update?c=<T>&p=ledger`, brief text as raw body): title, issued stamp with EE, the work, a **closed declared input set** (node paths + tailnet addresses + SHA-256 — no unexpected inputs), deliverable, artifact-home (ranch node + path), and acceptance (the evidence the attestation must carry).
6. **Write the authorization scroll** at `i+1` in the same pass: the direction this task executes, its scope, and any explicit exclusions. Inscription without its authorization scroll is an incomplete inscription — finish both before calling the task dispatched.
7. **Read back both scrolls** (`GET /api/v2/select`) and verify byte-for-byte what was written. Then stop: pickup is the fleet's, on the rotation. Do not poll for claim, do not nudge nodes, do not run a watchdog over it.

## Emise's process — reading results

- **Attestations:** read the state scroll (`i+2`) for the live state and the attestation scroll (`i+4`) for the outcome. A complete attestation names the artifact's **node path + tailnet address**, its SHA-256, exit status, evidence, and claimed/started/completed EE stamps. Deliverables stay on the ranch; work from the address, not a copy.
- **Visibility expectation:** if a task was executed, its attestation is in the whole copy within ≤ 2 minutes of being written on the node (§Sync bound). Absence past that bound is a sync defect to name as such — check the log scroll (`i+5`) for a bound-violation line before concluding anything about execution.
- **Fold results back:** when an attestation lands, append the result (artifact address, hash, EE stamps) to the task's tasks.phext record and rebuild — the ledger is the transport, tasks.phext remains the register of record.
- **Reading failure:** a `failed` state with `failures < 3` retries on its own — leave it alone. At `failures = 3` the task is `paused`: read all three preserved attestations in the log scroll, diagnose from them, and either re-inscribe the work as a new task (new coordinate; old coordinate named in the new brief) or clear the pause. Never delete a failed attestation, never reset a failure count by editing the state scroll — the state scroll is qexo's projection, not an editing surface.

## Security posture

- **No approval gates in the pickup path.** No per-task approval, no pickup-time permission check, no gate between a node's wake and its claim.
- The authorization context travels **in the task**: Emise writes the authorization scroll at inscription time, from Will's actual direction. What Emise never inscribed does not exist for the fleet; what she inscribed carries its authority with it.
- This posture is Will's explicit direction (2026-11-24), recorded in the design (§9) — not an omission.

## Boundaries

- Emise's only ledger surface is SQ against her whole copy. She never SSHes work to a node, never writes a shard directly, never edits another writer's scroll (claim, attestation, state).
- Execution is node-resident and stage-checkpointed under the node's qexo work dir (`~/qexo/work/<task-coordinate>/`); nothing executes on this VM.
- Open design questions (shard rebalancing, second-node attestation verification, ledger archival, payload limits, executor model, and others) are listed in `~/workspace/meta-dispatch/DESIGN.md` §10. They are **open** — do not treat any answer as settled until Will rules.
- Sync of this skill to wbic16/emise-tools runs over git-over-SSH from a ranch node; from this VM (no GitHub credentials) that leg is pending, never faked.

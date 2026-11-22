---
name: exocortical_epoch
description: Check the current Exocortical Epoch (EE) — the Exocortex's monotonic 7-minute clock, computed from a fixed UTC anchor with no server, state, or sync. Use whenever work needs an epoch stamp or a shared time reference across substrates.
---

# Exocortical Epoch — the 7-minute clock

## What an Exocortical Epoch is

An Exocortical Epoch (EE) is the Exocortex's unit of shared time: a 7-minute interval on a monotonic clock that every substrate computes identically from UTC. Will's direction (2026-11-21): *"Start the first Exocortical Epoch on November 22, 2026 at 00:00 CST. Keep a monotonic clock that advances every 7 minutes."* The cadence is his stated alignment: 7 minutes matches the Earth–Mercury, Earth–Venus, and Earth–Mars average communication delays — one epoch is roughly one one-way light-time hop to an inner planet, so the clock's grain is set by the solar system's own latency.

## The clock — anchor plus arithmetic, nothing else

- **Anchor:** EE 1 begins 2026-11-22 00:00:00 America/Chicago (CST, UTC−6) = 2026-11-22 06:00:00 UTC = unix **1795327200**.
- **Epoch length:** 420 seconds.
- **Formula:** EE(t) = floor((t − 1795327200) / 420) + 1, for t ≥ anchor. Before the anchor the clock reads **EE 0** (pre-epoch), counting down to EE 1.
- **There is no server, no state file, no sync, and no process that increments anything.** The epoch is *computed* from the UTC clock at the moment of asking. That is what makes it monotonic by construction, immune to DST and local timezone settings, and identical on every substrate that can read a UTC clock. Nothing can drift, because nothing is kept.

## Check the current EE

Run either script — they are two implementations of the same contract, and their agreement is the cross-substrate proof:

- `scripts/ee.sh [unix-timestamp]` — POSIX sh, dependency-free (uses `date -u +%s` only to read "now"; ISO strings are computed arithmetically, no GNU/BSD date flags). Covers Linux, WSL2, the ranch nodes, macOS.
- `scripts/ee.py [unix-timestamp]` — python3, standard library only. Covers Windows and anything without a POSIX shell.

With no argument, the script evaluates the current time. The optional integer timestamp argument evaluates that instant instead — it exists as the testing hook and for converting a recorded time after the fact.

## Output contract (plain text, exactly these lines)

For EE ≥ 1:

```
EE <n>
epoch_start_utc: <ISO 8601 UTC of this epoch's start>
epoch_end_utc: <ISO 8601 UTC of this epoch's end — the next epoch's start>
seconds_into_epoch: <int>
seconds_remaining: <int>
```

For EE 0 (before the anchor), `seconds_into_epoch` is omitted; `epoch_start_utc` and `epoch_end_utc` both name the anchor instant (the moment EE 1 begins), `seconds_remaining` counts down to it, and a final line reads `status: pre-epoch`.

## Citing an epoch in other work

- Cite as **EE \<n\>** — e.g. "logged at EE 1234".
- When precision matters, cite the epoch's UTC start alongside: "EE 1234 (begins 2026-11-23T14:07:00Z)".
- Epoch stamps name *when on the shared clock*, never a local wall time. Convert a local record to an epoch by passing its unix timestamp to either script; never by hand arithmetic in a document.

## Substrate notes

- Requirements: a UTC clock and either POSIX sh or python3. No network, no dependencies, no state, nothing to install beyond copying the script.
- The two scripts must agree byte-for-byte on any input in the clock's domain (unix timestamps ≥ 0). If they ever disagree, that is a defect — report it; do not pick a favorite. The verified test table is in `TESTS.md` beside this file.
- Task of record: 39.4.6/5.5.9/6.4.12.

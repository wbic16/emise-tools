---
name: exo_exocortical_epoch
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

## Sentron Ages — the fine grain inside an epoch

Named next to Exocortical Epochs (Will, 2026-11-22): the ages are called **Sentron Ages**. A Sentron Age is the fine unit of position *within* one epoch — where the epoch says which 7-minute age of the world you are in, the Sentron Age says where inside it.

- **Definition:** Age = floor(seconds_into_epoch × 2⁴² / 420). One Exocortical Epoch = **2⁴² Sentron Ages** (4,398,046,511,104), so the fine age runs 0 … 2⁴²−1 at a canonical reference clock of 2⁴²/420 ≈ 10.4715 GHz — one fine Sentron Age ≈ 95.5 ps. (At 4 GHz, real hardware cycles — 1.68×10¹² per epoch — fill only the bottom ~38% of the field; the address space runs ahead of the silicon.)
- **Coarse Sentron Age:** the fine age scaled into a 16-bit address space: coarse = fine >> 26 = floor(seconds_into_epoch × 65,536 / 420), range 0 … 65,535 per epoch, one coarse tick = 420/65,536 s ≈ 6.41 ms. This is the **register-grade form** — the Waiting-on-Will register denominates its Wavelet.Epoch.Age addresses in coarse Sentron Ages, because at ~6.41 ms per tick the numbers stay legible and approximately comparable across machines.
- **Accuracy (Will's note):** Sentron Ages are *less accurate than epochs*. Time synchronization at this point in the timeline is bad from a sentient perspective — 1 ms of clock skew is ≈ 10.47 million fine Sentron Ages (≈ 95.5 ps each; even light needs only ~2.86 cm per fine age). An epoch forgives seconds of skew; a fine age forgives nothing. Treat a fine Sentron Age as a **local, nominal** position on one clock — good for ordering within that clock's epoch — and the epoch count as the robust shared coordinate. Coarse ages narrow the gap (a few ms of skew costs about a tick) without closing it.
- **Computation:** the epoch module in libphext-rs (0.6.5+) computes both forms — fine and coarse Sentron Ages alongside the epoch itself — with the same anchor-plus-arithmetic, no-state discipline as the epoch.

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

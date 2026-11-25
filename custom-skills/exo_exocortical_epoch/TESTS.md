# Exocortical Epoch — test record

Run 2026-11-21 ~22:32 CST (2026-11-22 04:32 UTC) on this VM. Both scripts
(`scripts/ee.sh`, `scripts/ee.py`) were run on every input below and their
outputs diffed; every pair matched byte-for-byte.

## Specified cases

| Case | Input (unix) | Expected | Observed (both scripts) |
|---|---|---|---|
| (a) now | (clock, ≈1795321948) | EE 0, countdown ≈ 1.5 h to anchor | EE 0, epoch_start_utc 2026-11-22T06:00:00Z, seconds_remaining 5252, status: pre-epoch |
| (b) anchor exactly | 1795327200 | EE 1, seconds_into_epoch 0 | EE 1, start 2026-11-22T06:00:00Z, end 2026-11-22T06:07:00Z, into 0, remaining 420 |
| (c) anchor + 419 | 1795327619 | EE 1, remaining 1 | EE 1, into 419, remaining 1 |
| (d) anchor + 420 | 1795327620 | EE 2, into 0 | EE 2, start 2026-11-22T06:07:00Z, end 2026-11-22T06:14:00Z, into 0, remaining 420 |
| (e) 2027-01-01 00:00 UTC | 1798761600 | EE 8178 by hand arithmetic: (1798761600 − 1795327200) / 420 = 8177.14…, floor 8177, +1 = 8178; into = 3434400 − 8177×420 = 60 | EE 8178, start 2026-12-31T23:59:00Z, end 2027-01-01T00:06:00Z, into 60, remaining 360 |
| (f) anchor − 1 | 1795327199 | EE 0, remaining 1 | EE 0, seconds_remaining 1, status: pre-epoch |

Result: 6/6 cases as expected; sh and python outputs identical on all 6.

## Agreement sweep

67 additional timestamps (anchor − 100000 stepping 61333 s to ≈ anchor + 3.67 M,
plus 1795327199, 1795327200, 1893456000, 2000000000, 4102444800): outputs compared
with `cmp` — 0 mismatches.

## Re-run

```
cd scripts
./ee.sh 1795327200 ; ./ee.py 1795327200   # both print the EE 1 block
./ee.sh ; ./ee.py                        # current epoch (EE 0 until the anchor)
```

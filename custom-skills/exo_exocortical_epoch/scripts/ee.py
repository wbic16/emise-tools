#!/usr/bin/env python3
"""Current Exocortical Epoch (EE) — reference implementation.

The clock is computed from UTC unix time, never stored:
  anchor  = 1795327200  (EE 1 begins 2026-11-22 06:00:00 UTC)
  length  = 420 seconds (7 minutes)
  EE(t)   = floor((t - anchor) / 420) + 1   for t >= anchor
  EE(t)   = 0 (pre-epoch)                   for t <  anchor

Usage: ee.py [unix-timestamp]
With no argument, evaluates the current time. The optional timestamp
is the testing hook. Standard library only; no network, no state.
"""
import sys
import time
from datetime import datetime, timezone

ANCHOR = 1795327200
LENGTH = 420


def iso(t):
    return datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(argv):
    if len(argv) > 2:
        print("usage: ee.py [unix-timestamp]", file=sys.stderr)
        return 2
    if len(argv) == 2:
        try:
            t = int(argv[1])
        except ValueError:
            print("ee.py: timestamp must be an integer", file=sys.stderr)
            return 2
    else:
        t = int(time.time())

    if t < ANCHOR:
        print("EE 0")
        print("epoch_start_utc: " + iso(ANCHOR))
        print("epoch_end_utc: " + iso(ANCHOR))
        print("seconds_remaining: %d" % (ANCHOR - t))
        print("status: pre-epoch")
        return 0

    n = (t - ANCHOR) // LENGTH + 1
    start = ANCHOR + (n - 1) * LENGTH
    end = start + LENGTH
    print("EE %d" % n)
    print("epoch_start_utc: " + iso(start))
    print("epoch_end_utc: " + iso(end))
    print("seconds_into_epoch: %d" % (t - start))
    print("seconds_remaining: %d" % (end - t))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

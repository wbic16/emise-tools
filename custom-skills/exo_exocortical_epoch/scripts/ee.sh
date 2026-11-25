#!/bin/sh
# Current Exocortical Epoch (EE) — POSIX sh implementation.
#
# The clock is computed from UTC unix time, never stored:
#   anchor  = 1795327200  (EE 1 begins 2026-11-22 06:00:00 UTC)
#   length  = 420 seconds (7 minutes)
#   EE(t)   = floor((t - anchor) / 420) + 1   for t >= anchor
#   EE(t)   = 0 (pre-epoch)                   for t <  anchor
#
# Usage: ee.sh [unix-timestamp]
# With no argument, evaluates the current time (date -u +%s).
# The optional timestamp is the testing hook.
# Dependency-free: POSIX sh arithmetic only. ISO 8601 strings are
# computed arithmetically (civil-from-days), so no GNU/BSD date
# formatting flags are needed. Output is byte-identical to ee.py.
# Domain: unix timestamps >= 0 (the clock's era begins in 2026).

ANCHOR=1795327200
LENGTH=420

iso() {
    # $1 = unix timestamp (>= 0). Prints YYYY-MM-DDTHH:MM:SSZ.
    _t=$1
    _days=$(( _t / 86400 ))
    _secs=$(( _t % 86400 ))
    _hh=$(( _secs / 3600 ))
    _mm=$(( (_secs % 3600) / 60 ))
    _ss=$(( _secs % 60 ))
    # Civil date from days since 1970-01-01 (Hinnant's algorithm).
    _z=$(( _days + 719468 ))
    _era=$(( _z / 146097 ))
    _doe=$(( _z - _era * 146097 ))
    _yoe=$(( (_doe - _doe / 1460 + _doe / 36524 - _doe / 146096) / 365 ))
    _y=$(( _yoe + _era * 400 ))
    _doy=$(( _doe - (365 * _yoe + _yoe / 4 - _yoe / 100) ))
    _mp=$(( (5 * _doy + 2) / 153 ))
    _d=$(( _doy - (153 * _mp + 2) / 5 + 1 ))
    if [ "$_mp" -lt 10 ]; then _m=$(( _mp + 3 )); else _m=$(( _mp - 9 )); fi
    if [ "$_m" -le 2 ]; then _y=$(( _y + 1 )); fi
    printf '%04d-%02d-%02dT%02d:%02d:%02dZ' "$_y" "$_m" "$_d" "$_hh" "$_mm" "$_ss"
}

if [ $# -gt 1 ]; then
    echo "usage: ee.sh [unix-timestamp]" >&2
    exit 2
fi

if [ $# -eq 1 ]; then
    case $1 in
        [0-9]*)
            case $1 in
                *[!0-9]*) echo "ee.sh: timestamp must be an integer" >&2; exit 2 ;;
            esac
            ;;
        *) echo "ee.sh: timestamp must be an integer" >&2; exit 2 ;;
    esac
    t=$1
else
    t=$(date -u +%s)
fi

if [ "$t" -lt "$ANCHOR" ]; then
    echo "EE 0"
    printf 'epoch_start_utc: %s\n' "$(iso "$ANCHOR")"
    printf 'epoch_end_utc: %s\n' "$(iso "$ANCHOR")"
    printf 'seconds_remaining: %s\n' "$(( ANCHOR - t ))"
    echo "status: pre-epoch"
    exit 0
fi

n=$(( (t - ANCHOR) / LENGTH + 1 ))
start=$(( ANCHOR + (n - 1) * LENGTH ))
end=$(( start + LENGTH ))
printf 'EE %s\n' "$n"
printf 'epoch_start_utc: %s\n' "$(iso "$start")"
printf 'epoch_end_utc: %s\n' "$(iso "$end")"
printf 'seconds_into_epoch: %s\n' "$(( t - start ))"
printf 'seconds_remaining: %s\n' "$(( end - t ))"
exit 0

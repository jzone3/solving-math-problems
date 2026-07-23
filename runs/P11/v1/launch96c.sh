#!/bin/bash
# phase C for CW(96,36): stop at d=24 (skip the B=2 d=48 wall) and throw long
# kissat budgets at the size-4-class pinned lifts directly.
cd "$(dirname "$0")"
for p in $(pgrep -f "python3 pipeline96.py"); do
  if tr '\0' '\n' < /proc/$p/environ 2>/dev/null | grep -q "CW_N=96\|^LEVELS=12,24,48"; then kill "$p" 2>/dev/null; fi
  if ! tr '\0' '\n' < /proc/$p/environ 2>/dev/null | grep -q "CW_N="; then kill "$p" 2>/dev/null; fi
done
sleep 1
for w in 0 1 2 3; do
  CW_N=96 CW_K=36 TOP_D=6 LEVELS=12,24 EARLY_LIFT_SIZE=4 ENUM_TL=300 LIFT_TL=1800 MAX_B=200 \
    WORKER_ID=$w NUM_WORKERS=4 setsid nohup python3 pipeline96.py > pl96c_w$w.log 2>&1 < /dev/null &
done
sleep 3
pgrep -c -f "python3 pipeline96.py"

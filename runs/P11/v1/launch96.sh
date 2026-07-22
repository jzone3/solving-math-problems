#!/bin/bash
cd "$(dirname "$0")"
for p in $(pgrep -f "python3 pipeline96.py"); do kill "$p" 2>/dev/null; done
sleep 1
for w in 0 1; do
  WORKER_ID=$w NUM_WORKERS=2 ENUM_TL=600 LIFT_TL=900 setsid nohup python3 pipeline96.py > pl96b_w$w.log 2>&1 < /dev/null &
done
sleep 3
pgrep -c -f "python3 pipeline96.py"

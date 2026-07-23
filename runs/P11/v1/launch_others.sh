#!/bin/bash
# secondary open cells: CW(112,36), CW(120,49), CW(132,81)
cd "$(dirname "$0")"
CW_N=112 CW_K=36 TOP_D=7  LEVELS=14,28,56 ENUM_TL=600 LIFT_TL=900 \
  WORKER_ID=0 NUM_WORKERS=1 setsid nohup python3 pipeline96.py > pl112_w0.log 2>&1 < /dev/null &
CW_N=120 CW_K=49 TOP_D=15 LEVELS=30,60    ENUM_TL=600 LIFT_TL=900 \
  WORKER_ID=0 NUM_WORKERS=1 setsid nohup python3 pipeline96.py > pl120_w0.log 2>&1 < /dev/null &
CW_N=132 CW_K=81 TOP_D=11 LEVELS=33,66    ENUM_TL=600 LIFT_TL=900 \
  WORKER_ID=0 NUM_WORKERS=1 setsid nohup python3 pipeline96.py > pl132_w0.log 2>&1 < /dev/null &
sleep 3
pgrep -c -f "python3 pipeline96.py"

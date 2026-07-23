#!/bin/bash
# validation: known-SAT CW(48,36); worker 2 of 8 => exactly class index 2,
# which contains the known witness's mod-6 fold (4,0,4,0,-2,0)
cd "$(dirname "$0")"
CW_N=48 CW_K=36 TOP_D=6 LEVELS=12,24 ENUM_TL=900 LIFT_TL=300 MAX_B=500 \
  WORKER_ID=2 NUM_WORKERS=8 setsid nohup python3 pipeline96.py > pl48_validate2.log 2>&1 < /dev/null &
sleep 2
pgrep -c -f "python3 pipeline96.py"

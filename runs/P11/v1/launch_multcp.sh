#!/bin/bash
cd "$(dirname "$0")"
for p in $(pgrep -f "python3 multiplier_search.py"); do kill "$p" 2>/dev/null; done
sleep 1
for spec in "96 36" "105 36" "112 36" "117 36" "120 49" "132 81"; do
  set -- $spec
  setsid nohup python3 mult_cpsat.py $1 $2 48 --affine > multcp_$1_$2.log 2>&1 < /dev/null &
done
sleep 2
pgrep -c -f mult_cpsat.py

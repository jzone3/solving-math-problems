#!/bin/bash
cd "$(dirname "$0")"
for spec in "96 36" "105 36" "112 36" "117 36" "120 49" "132 81"; do
  set -- $spec
  setsid nohup python3 multiplier_search.py $1 $2 24 > mult_$1_$2.log 2>&1 < /dev/null &
done
sleep 2
pgrep -c -f multiplier_search.py

#!/bin/bash
# Stage 2: after resumed 48-orbit sweeps finish, extend to 64 orbits (previously
# skipped classes, incl. order-2 maps like negation) for all six cells, then
# retry any UNKNOWNs with 1800s budgets.
cd "$(dirname "$0")"
# wait for current sweeps
while pgrep -f "mult_cpsat.py (112|117|120)" > /dev/null; do sleep 60; done
for spec in "132 81" "105 36" "112 36" "117 36" "120 49"; do
  set -- $spec
  setsid nohup python3 mult_cpsat.py $1 $2 64 --affine --resume=multcp_$1_$2.log \
    >> multcp_$1_$2.log 2>&1 < /dev/null &
  # run two at a time
  while [ "$(pgrep -cf mult_cpsat.py)" -ge 2 ]; do sleep 60; done
done
while pgrep -f mult_cpsat.py > /dev/null; do sleep 60; done
for spec in "105 36" "112 36" "117 36" "120 49" "132 81"; do
  set -- $spec
  setsid nohup python3 mult_retry.py $1 $2 multcp_$1_$2.log 1800 \
    > multretry_$1_stage2.log 2>&1 < /dev/null &
  while [ "$(pgrep -cf mult_retry.py)" -ge 2 ]; do sleep 120; done
done

#!/bin/bash
# Chained worker: always restart from the smallest certified witness any worker
# has produced, so all workers share one descent instead of racing on copies.
# Usage: MODE=greedy|lns SEED=n H=40 BALL=1 DROPK=2 ./chain.sh
set -u
cd "$(dirname "$0")"
export POOL=${POOL:-tuniv_1.6_1.3.pkl}
SEED=${SEED:-1}
MODE=${MODE:-lns}
H=${H:-40}
BALL=${BALL:-1}
DROPK=${DROPK:-2}
TIME=${TIME:-900}
while true; do
  BEST=$(python3 best.py --path)
  N=$(python3 -c "import pickle,sys;print(len(pickle.load(open('$BEST','rb'))))")
  echo "=== restart from $BEST ($N vertices) at $(date -u +%H:%M:%S)"
  if [ "$MODE" = greedy ]; then
    python3 greedy8.py "$((SEED + RANDOM))" "$BEST" "c$SEED"
  else
    START=$BEST H=$H BALL=$BALL DROPK=$DROPK TIME=$TIME SEED=$SEED \
      OUT=tlns_$SEED.pkl timeout 7200 python3 tlns.py
  fi
done

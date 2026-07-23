#!/bin/bash
# Balanced exhaustive sweep: single geng|directg generator, awk round-robin
# splitter into W fifos, W python checkers. Usage:
#   fifo_sweep.sh <tag> <genspec...>   e.g. fifo_sweep.sh n8 8 7:12
D=/home/ubuntu/repos/solving-math-problems/runs/P03/v2
TAG=$1; shift
W=7
cd $D
mkdir -p fifos
PIDS=()
FIFOS=()
for i in $(seq 0 $((W-1))); do
  f=fifos/${TAG}_$i; rm -f $f; mkfifo $f
  FIFOS+=($f)
  python3 $D/exhaust_small.py ${TAG}-$i < $f > $D/logs/fifo_${TAG}_$i.log 2>&1 &
  PIDS+=($!)
done
nauty-geng -c -q "$@" | nauty-directg -T 2>/dev/null | \
  awk -v w=$W -v tag=fifos/${TAG}_ '{print > (tag (NR%w))}'
for f in "${FIFOS[@]}"; do :; done
wait "${PIDS[@]}"
echo "SWEEP $TAG DONE"

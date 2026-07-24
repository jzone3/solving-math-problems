#!/bin/bash
# Repeated independent basin sampling: fresh walk descent (20 min) followed by
# LNS refinement (40 min) from the walk's best. Collects basin records in
# basins/ for later recombination.
# Usage: basin_worker.sh <worker_id>
set -u
W=$1
mkdir -p basins
i=0
while true; do
  i=$((i+1))
  seed=$((W * 1000003 + i * 7919))
  ./walk 1200 $seed > /dev/null 2>&1
  if [ -f walk_best_$seed.txt ]; then
    timeout 2400 /usr/bin/python3 lns.py walk_best_$seed.txt basins/b_${W}_${i} $seed > basins/b_${W}_${i}.log 2>&1
    rm -f walk_best_$seed.txt
  fi
done

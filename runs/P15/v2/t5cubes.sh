#!/bin/bash
# SCIP cube-and-conquer on N=1680, T=5: case split on largest value covering 0.
# Usage: t5cubes.sh <offset> <stride> <per-cube-seconds>
cd "$(dirname "$0")"
OFF=$1; STR=$2; TL=$3
CUBES=(1680 840 560 420 336 280 240 210 168 140 120 112 105 84 80 70 60 56 48 42 40 35 30 28 24 21 20 16 15 14 12 10 8 7 6 5)
i=0
for V in "${CUBES[@]}"; do
  if (( i % STR == OFF )); then
    echo "=== cube v0=$V"
    timeout $((TL+300)) python3 scip.py -N "2^4,3,5,7" -T 5 --time-limit "$TL" \
      --cube-v0 "$V" -o "covers/cube5_1680_v$V.txt" 2>&1 \
      | grep -E "^(status|SAT|UNSAT|INDETERMINATE|wrote)"
  fi
  i=$((i+1))
done
echo SHARD-DONE

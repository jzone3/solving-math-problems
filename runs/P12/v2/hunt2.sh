#!/bin/bash
# witness hunt v2: randomized restarts; binary and node-limit per worker
cd "$(dirname "$0")"
n=$1; w=$2; bin=$3; L=$4
seed=$((w*1000000 + RANDOM))
while true; do
  seed=$((seed+1))
  ./$bin $n -r $seed -1 -L $L > hunt_${n}_${w}.out 2>> hunt_${n}_${w}.log
  if [ -s hunt_${n}_${w}.out ]; then
    echo "FOUND n=$n worker=$w bin=$bin seed=$seed" >> FOUND.txt
    cp hunt_${n}_${w}.out FOUND_n${n}_w${w}_seed${seed}.txt
    exit 0
  fi
  echo "seed=$seed done $(date +%s)" >> hunt_${n}_${w}.log
done

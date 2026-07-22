#!/bin/bash
# witness hunt: randomized restarts of exhaustive DFS with node limit
n=$1; w=$2; L=${3:-3000000000}
seed=$((w*100000))
while true; do
  seed=$((seed+1))
  ./t2dfs3 $n -r $seed -1 -L $L > hunt_${n}_${w}.out 2>> hunt_${n}_${w}.log
  rc=$?
  if [ -s hunt_${n}_${w}.out ]; then
    echo "FOUND n=$n worker=$w seed=$seed" >> FOUND.txt
    cp hunt_${n}_${w}.out FOUND_n${n}_seed${seed}.txt
    exit 0
  fi
  echo "seed=$seed rc=$rc done $(date +%s)" >> hunt_${n}_${w}.log
done

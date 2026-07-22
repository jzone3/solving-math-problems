#!/bin/bash
# many short annealing restarts, args: n iters flag logfile seedbase
n=$1; iters=$2; flag=$3; log=$4; base=$5
for i in $(seq 1 400); do
  python3 localsearch.py $n $iters $((base+i)) $flag >> $log 2>&1
done

#!/bin/bash
# C-core exhaustive sweep. Usage: c_sweep.sh <tag> <n> <erange> <mod> [para]
# Runs <mod> geng|directg|checker pipelines (para at a time). Survivors ->
# surv_<tag>_<shard>.txt ; stats -> logs/c_<tag>_<shard>.log
D=/home/ubuntu/repos/solving-math-problems/runs/P03/v2
TAG=$1; N=$2; ER=$3; MOD=$4; PARA=${5:-8}
cd $D
: > jobs_c_$TAG.txt
for r in $(seq 0 $((MOD-1))); do
  echo "nauty-geng -c -q $N $ER $r/$MOD | nauty-directg -T 2>/dev/null | $D/checker 60 > $D/surv_${TAG}_$r.txt 2> $D/logs/c_${TAG}_$r.log" >> jobs_c_$TAG.txt
done
xargs -a jobs_c_$TAG.txt -P $PARA -I CMD bash -c CMD
echo "CSWEEP $TAG DONE"

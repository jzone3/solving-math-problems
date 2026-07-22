#!/bin/bash
# Long-running random stage-1 sampler over larger sparse cores.
# Usage: random_driver.sh <worker_id> <total_batches>
# Each batch: random n in 15..22, edges n+k (k in 0..5), 200k samples,
# spider_search64 keeps only connected-graph work (disconnected graphs
# never produce complete pair lists for a triple spanning components, but
# to be safe we filter connected with pickg -c ... not available; instead
# spider_search treats components fine: a triple within one component is
# still a valid core test; cross-component triples have empty pair lists
# and are skipped. A hit inside a component is a hit for that component.)
id=$1; batches=$2
for b in $(seq 1 "$batches"); do
  n=$(( 15 + RANDOM % 8 ))
  k=$(( RANDOM % 6 ))
  e=$(( n + k ))
  seed=$(( id * 100000 + b ))
  nauty-genrang -g -e"$e" -S"$seed" "$n" 200000 2>/dev/null \
    | ./spider_search64 -m >> "rand_$id.out" 2>> "rand_$id.err"
  echo "batch $b: n=$n e=$e done" >> "rand_$id.log"
done

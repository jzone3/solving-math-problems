#!/bin/bash
cd "$(dirname "$0")"
for ((r=0;r<8;r++)); do
  setsid nohup bash -c "nauty-geng -Cq 13 0:22 ${r}/8 | ./lp2 3 > lp13s_${r}.hits 2> lp13s_${r}.err" >/dev/null 2>&1 </dev/null &
done
setsid nohup bash -c 'for n in 13 14 15 16 17 18; do nauty-geng -Cq -d2 -D3 $n | ./lp2 3 > sub${n}.hits 2> sub${n}.err; done' >/dev/null 2>&1 </dev/null &
setsid nohup bash -c 'for n in 18 20 22 24; do nauty-geng -Cq -d3 -D3 $n | ./lp2 3 > cub${n}.hits 2> cub${n}.err; done' >/dev/null 2>&1 </dev/null &
setsid nohup python3 weighted.py --iters 30000 --ns 12 --nsmax 18 --wmax 6 --nmax 58 --restarts 400 --tag wsk18 >/dev/null 2>&1 </dev/null &
setsid nohup python3 search.py --seedfile t2seeds12.jsonl --iters 30000 --nmin 12 --nmax 26 --biconn --restarts 200 --tag t2n12c >/dev/null 2>&1 </dev/null &

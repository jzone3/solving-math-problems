#!/bin/bash
cd "$(dirname "$0")"
for ((r=0;r<6;r++)); do
  setsid nohup bash -c "nauty-geng -Cq 11 0:22 ${r}/6 | ./lp 3 > lp11_${r}.hits 2> lp11_${r}.err" >/dev/null 2>&1 </dev/null &
done
setsid nohup python3 weighted.py --iters 20000 --ns 8 --nsmax 12 --wmax 7 --nmax 44 --restarts 200 --tag wsk8 >/dev/null 2>&1 </dev/null &
setsid nohup python3 weighted.py --iters 20000 --ns 11 --nsmax 15 --wmax 6 --nmax 52 --restarts 200 --tag wsk11 >/dev/null 2>&1 </dev/null &

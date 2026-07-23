#!/bin/bash
cd "$(dirname "$0")"
setsid nohup python3 weighted.py --iters 30000 --ns 9 --nsmax 13 --wmax 9 --nmax 56 --restarts 300 --tag wsk9b >/dev/null 2>&1 </dev/null &
setsid nohup python3 weighted.py --iters 30000 --ns 12 --nsmax 16 --wmax 5 --nmax 56 --restarts 300 --tag wsk12b >/dev/null 2>&1 </dev/null &

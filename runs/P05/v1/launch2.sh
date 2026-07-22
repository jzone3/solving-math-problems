#!/bin/bash
cd "$(dirname "$0")"
setsid nohup python3 search.py --seed random --iters 30000 --nmin 10 --nmax 16 --biconn --restarts 100 --tag b16 >/dev/null 2>&1 </dev/null &
setsid nohup python3 search.py --seed random --iters 30000 --nmin 12 --nmax 20 --biconn --restarts 100 --tag b20 >/dev/null 2>&1 </dev/null &
setsid nohup python3 search.py --seed random --iters 20000 --nmin 14 --nmax 24 --biconn --restarts 60 --tag b24 >/dev/null 2>&1 </dev/null &
setsid nohup python3 search.py --seed random --iters 10000 --nmin 18 --nmax 30 --biconn --restarts 30 --tag b30 >/dev/null 2>&1 </dev/null &
setsid nohup python3 search.py --seed "Van Cleemput-Zamfirescu Graph 13" --iters 20000 --nmin 10 --nmax 22 --biconn --restarts 40 --tag vczb >/dev/null 2>&1 </dev/null &
setsid nohup python3 search.py --seed "Thomassen Graph 34" --iters 2000 --nmin 26 --nmax 40 --biconn --restarts 15 --tag thomb >/dev/null 2>&1 </dev/null &

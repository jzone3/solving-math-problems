#!/bin/bash
cd "$(dirname "$0")"
setsid nohup python3 search.py --seed "Van Cleemput-Zamfirescu Graph 13" --iters 20000 --nmin 8 --nmax 22 --restarts 30 --tag vcz13 >/dev/null 2>&1 </dev/null &
setsid nohup python3 search.py --seed "Zamfirescu Graph 36" --iters 1500 --nmin 24 --nmax 40 --restarts 10 --tag zam36 >/dev/null 2>&1 </dev/null &
setsid nohup python3 search.py --seed "Thomassen Graph 34" --iters 1500 --nmin 24 --nmax 40 --restarts 10 --tag thom34 >/dev/null 2>&1 </dev/null &
setsid nohup python3 search.py --seed random --iters 20000 --nmin 8 --nmax 20 --restarts 60 --tag rnd20b >/dev/null 2>&1 </dev/null &

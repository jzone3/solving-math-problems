#!/bin/bash
cd "$(dirname "$0")"
setsid nohup python3 search.py --seedfile t2seeds12.jsonl --iters 30000 --nmin 10 --nmax 20 --biconn --restarts 114 --tag t2n12 >/dev/null 2>&1 </dev/null &
setsid nohup python3 search.py --seedfile t2seeds12.jsonl --iters 20000 --nmin 12 --nmax 26 --biconn --restarts 114 --tag t2n12b >/dev/null 2>&1 </dev/null &

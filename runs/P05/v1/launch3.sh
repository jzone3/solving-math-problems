#!/bin/bash
cd "$(dirname "$0")"
setsid nohup python3 search.py --seedfile hybrids.jsonl --iters 30000 --nmin 18 --nmax 32 --restarts 80 --tag hybanneal5 >/dev/null 2>&1 </dev/null &

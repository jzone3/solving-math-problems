#!/bin/bash
# n=12 exhaustive run: 64 chunks, 8 concurrent workers, checkpointed.
cd "$(dirname "$0")"
mkdir -p out12
worker(){
  local w=$1
  for ((c=w; c<64; c+=8)); do
    if [ -s "out12/part$c.txt" ] && grep -q '^DONE' "out12/part$c.txt"; then continue; fi
    nauty-geng -q 12 $c/64 2>/dev/null | ./check 129 > "out12/part$c.txt.tmp" 2> "out12/part$c.err"
    mv "out12/part$c.txt.tmp" "out12/part$c.txt"
    echo "$(date -u +%H:%M:%S) chunk $c done" >> out12/progress.log
  done
}
for w in 0 1 2 3 4 5 6 7; do worker $w & done
wait
echo "ALL DONE $(date -u)" >> out12/progress.log

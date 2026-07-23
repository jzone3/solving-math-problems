#!/bin/bash
# Driver for the exhaustive n=12 BN sweep: 96 geng parts, 8 concurrent workers.
# Skips parts whose summary already exists (restartable).
cd "$(dirname "$0")"
mkdir -p logs12
for r in $(seq 0 95); do echo "$r"; done | xargs -P 8 -I{} sh -c '
  if grep -q SUMMARY logs12/sum_{}.txt 2>/dev/null; then exit 0; fi
  nauty-geng -cq 12 {}/96 2>/dev/null | ./sweep12 12 > logs12/cand_{}.txt 2> logs12/sum_{}.tmp
  mv logs12/sum_{}.tmp logs12/sum_{}.txt
'
echo "ALL PARTS DONE"

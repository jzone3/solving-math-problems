#!/bin/bash
# Exact LNS with *contiguous* holes: drop the H record vertices nearest a random
# record vertex, refill from the 1-hop pool under the 508-vertex budget.
w=$1; H=$2; shift 2
for sd in "$@"; do
  echo "== ball seed $sd H=$H start" >> lnsb_w$w.log
  POOL=w4x.pkl LNSFIX=rec_w4x.pkl LNSBALL=$H LNSSEED=$sd LNSHOPS=1 \
  MAXSEL=$((H-2)) SEED=$((5000+sd)) HYP=none.pkl BANK=lnsb_${H}_$sd.jsonl \
  PERIT=4 TABU=200000 timeout 2400 python3 -u cegar4.py >> lnsb_w$w.log 2>&1
done

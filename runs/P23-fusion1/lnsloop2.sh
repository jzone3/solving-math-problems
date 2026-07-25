#!/bin/bash
# Wider exact-LNS holes: freeze K of the record's 510 W4 vertices, refill from
# the 1-hop pool around the hole under the 508-vertex budget.
w=$1; K=$2; shift 2
for sd in "$@"; do
  echo "== seed $sd start" >> lnsy_w$w.log
  POOL=w4x.pkl LNSFIX=rec_w4x.pkl LNSK=$K LNSSEED=$sd LNSHOPS=1 \
  MAXSEL=$((508-K)) SEED=$((7000+sd)) HYP=none.pkl BANK=lnsy_${K}_$sd.jsonl \
  PERIT=4 TABU=200000 timeout 3600 python3 -u cegar4.py >> lnsy_w$w.log 2>&1
done

#!/bin/bash
# Exact LNS: punch a hole of (510-K) vertices in the record's W4 embedding,
# let the hitting set refill it from the 1-hop pool around the hole under a
# 508-vertex total budget, and run each neighbourhood to a definite answer
# (508 witness, or outer UNSAT = no refill of that hole exists).
w=$1; shift
for sd in "$@"; do
  echo "== seed $sd start" >> lnsx_w$w.log
  POOL=w4x.pkl LNSFIX=rec_w4x.pkl LNSK=490 LNSSEED=$sd LNSHOPS=1 \
  MAXSEL=18 SEED=$((9000+sd)) HYP=none.pkl BANK=lnsx_$sd.jsonl PERIT=4 \
  TABU=200000 timeout 1800 python3 -u cegar4.py >> lnsx_w$w.log 2>&1
done

#!/bin/bash
# Frontier descent: start from the smallest certified witness (currently 509,
# reached by greedy from the padded set) and attempt exact region trades with
# assorted hole sizes.  Any success is a 508.
w=$1
HS=(30 45 60 80)
while true; do
  best=$(python3 - <<'PY'
import pickle,glob
c=[]
for f in glob.glob('desc_*.pkl'):
    try: c.append((len(pickle.load(open(f,'rb'))),f))
    except Exception: pass
c.sort(); print(c[0][1] if c else 'rec_w4x.pkl')
PY
)
  H=${HS[$((RANDOM % 4))]}
  echo "== worker $w from $best H=$H" >> chain2_$w.log
  POOL=w4x.pkl START=$best H=$H DROPK=1 HOPS=1 TIME=420 SEED=$((w*131+RANDOM%9999)) \
  RANDHOLE=$((RANDOM % 2)) OUT=desc_f$w.pkl timeout 1800 python3 -u lnsdescend.py >> chain2_$w.log 2>&1
done

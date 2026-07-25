#!/bin/bash
# Exact-LNS descent chain: always restart from the smallest certified witness
# any worker has produced, so the workers share progress.
w=$1
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
  echo "== worker $w from $best" >> chain_$w.log
  POOL=w4x.pkl START=$best H=45 DROPK=3 HOPS=1 TIME=240 SEED=$((w*97+RANDOM%1000)) \
  RANDHOLE=1 OUT=desc_c$w.pkl timeout 1800 python3 -u lnsdescend.py >> chain_$w.log 2>&1
done

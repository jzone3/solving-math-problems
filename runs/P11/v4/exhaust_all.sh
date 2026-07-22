#!/bin/bash
# Run the C exhauster over all multiplier subgroups of a cell, cheapest first,
# with a per-subgroup timeout. Usage: exhaust_all.sh n s [timeout_s]
cd "$(dirname "$0")"
N=$1; S=$2; TO=${3:-3600}
python3 - "$N" <<'EOF' > /tmp/subs_$1.txt
import sys
from math import gcd
n=int(sys.argv[1])
subs={}
def key(n,t):
    seen=[False]*n; parts=[]
    for i in range(n):
        if not seen[i]:
            cur=[]; j=i
            while not seen[j]:
                seen[j]=True; cur.append(j); j=(j*t)%n
            parts.append(frozenset(cur))
    return frozenset(parts), len(parts)
for t in range(2,n):
    if gcd(t,n)!=1: continue
    k,m=key(n,t)
    if k not in subs: subs[k]=(t,m)
for t,m in sorted(subs.values(), key=lambda x:x[1]):
    print(t,m)
EOF
while read T M; do
  echo "--- t=$T m=$M (timeout ${TO}s)"
  timeout $TO ./exhaust $N $S $T
  rc=$?
  [ $rc -eq 124 ] && echo "TIMEOUT n=$N t=$T m=$M after ${TO}s"
  [ $rc -eq 0 ] && { echo "FOUND-STOP"; break; }
done < /tmp/subs_$N.txt
echo "ALL-DONE n=$N"

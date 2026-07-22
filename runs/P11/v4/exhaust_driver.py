#!/usr/bin/env python3
"""Run sym_exhaust.py over all multiplier subgroups of one cell, cheapest first.

Definitive per subgroup: SOLUTION or EXHAUSTED (or SKIP if too big).
Usage: exhaust_driver.py n s [max_leaves]
"""
import subprocess, sys
from math import gcd

def orbits_key(n, t):
    seen = [False]*n; parts = []
    for i in range(n):
        if not seen[i]:
            cur = []; j = i
            while not seen[j]:
                seen[j] = True; cur.append(j); j = (j*t) % n
            parts.append(frozenset(cur))
    return frozenset(parts), len(parts)

def main():
    n = int(sys.argv[1]); s = int(sys.argv[2])
    max_leaves = int(sys.argv[3]) if len(sys.argv) > 3 else 30_000_000
    subs = {}
    for t in range(2, n):
        if gcd(t, n) != 1: continue
        key, m = orbits_key(n, t)
        if key not in subs:
            subs[key] = (t, m)
    cands = sorted(subs.values(), key=lambda x: x[1])
    print(f"n={n} s={s}: {len(cands)} subgroups", flush=True)
    for (t, m) in cands:
        r = subprocess.run(['python3','sym_exhaust.py',str(n),str(s),str(t),str(max_leaves)],
                           capture_output=True, text=True)
        for l in r.stdout.strip().splitlines():
            print(f"[t={t} m={m}] {l}", flush=True)
        if 'SOLUTION' in r.stdout:
            return 0
    print("ALL-DONE", flush=True)
    return 2

if __name__ == "__main__":
    sys.exit(main())

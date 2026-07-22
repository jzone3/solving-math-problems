#!/usr/bin/env python3
"""Round-robin driver: multiplier-symmetric RRR over all cyclic multiplier
subgroups of Z_n^* for one open cell CW(n, s^2).

Enumerates one generator t per distinct subgroup <t> (deduped by orbit
partition), ordered by orbit count m descending-usefulness (small m first),
and runs rrr_sym.py on each in escalating time slices, forever (until killed
or SOLUTION).

Usage: sym_driver.py n s [slice0] [max_m]
"""
import subprocess, sys, time
from math import gcd

def orbits_key(n, t):
    seen = [False]*n
    parts = []
    for i in range(n):
        if not seen[i]:
            cur = []
            j = i
            while not seen[j]:
                seen[j] = True; cur.append(j); j = (j*t) % n
            parts.append(frozenset(cur))
    return frozenset(parts), len(parts)

def main():
    n = int(sys.argv[1]); s = int(sys.argv[2])
    slice0 = float(sys.argv[3]) if len(sys.argv) > 3 else 45.0
    max_m = int(sys.argv[4]) if len(sys.argv) > 4 else 80
    subs = {}
    for t in range(2, n):
        if gcd(t, n) != 1: continue
        key, m = orbits_key(n, t)
        if key not in subs:
            subs[key] = (t, m)
    cands = sorted(subs.values(), key=lambda x: x[1])
    cands = [(t, m) for (t, m) in cands if m <= max_m]
    print(f"n={n} s={s}: {len(cands)} distinct multiplier subgroups, m range "
          f"{cands[0][1]}..{cands[-1][1]}", flush=True)
    rnd = 0
    sl = slice0
    seed = 1000 + n
    while True:
        rnd += 1
        for (t, m) in cands:
            r = subprocess.run(['python3','rrr_sym.py',str(n),str(s),str(t),
                                str(sl),'64',str(seed+rnd)],
                               capture_output=True, text=True)
            out = r.stdout.strip().splitlines()
            last = out[-1] if out else ''
            print(f"round={rnd} t={t} m={m} slice={sl:.0f}s -> {last}", flush=True)
            if 'SOLUTION' in r.stdout:
                for l in out:
                    if 'SOLUTION' in l: print(l, flush=True)
                return 0
        sl = min(sl*1.6, 600)

if __name__ == "__main__":
    sys.exit(main())

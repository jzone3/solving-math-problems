#!/usr/bin/env python3
"""Sweep ALL multiplier subgroups of Z_n^* (not just cyclic) with the C exhauster.

Subgroups are generated as joins of cyclic subgroups (closure under pairwise
join); each is passed to ./exhaust via a small generating set. Ordered by
orbit count ascending (fewest orbits = cheapest & most symmetric first).

Usage: allsub_driver.py n s [timeout_s] [min_m_skip]
  min_m_skip: skip subgroups whose orbit count exceeds this (default 34)
"""
import subprocess, sys
from math import gcd

def cyc(n, t):
    g = {1}; x = t
    while x not in g:
        g.add(x); x = (x*t) % n
    return frozenset(g)

def orbit_count(n, H):
    seen = [False]*n; m = 0
    for i in range(n):
        if not seen[i]:
            m += 1
            stack=[i]; seen[i]=True
            while stack:
                j=stack.pop()
                for t in H:
                    v=(j*t)%n
                    if not seen[v]: seen[v]=True; stack.append(v)
    return m

def join(n, A, B):
    g = set(A) | set(B)
    frontier = list(g)
    while frontier:
        new=[]
        for a in list(g):
            for b in frontier:
                v=(a*b)%n
                if v not in g: g.add(v); new.append(v)
        frontier=new
    return frozenset(g)

def main():
    n = int(sys.argv[1]); s = int(sys.argv[2])
    to = int(sys.argv[3]) if len(sys.argv) > 3 else 7200
    max_m = int(sys.argv[4]) if len(sys.argv) > 4 else 34
    units = [t for t in range(1, n) if gcd(t, n) == 1]
    subs = set()
    gensets = {}
    for t in units[1:]:
        H = cyc(n, t)
        if H not in subs:
            subs.add(H); gensets[H] = (t,)
    changed = True
    while changed:
        changed = False
        cur = list(subs)
        for i in range(len(cur)):
            for j in range(i+1, len(cur)):
                J = join(n, cur[i], cur[j])
                if J not in subs:
                    subs.add(J)
                    gensets[J] = tuple(sorted(set(gensets[cur[i]]) | set(gensets[cur[j]])))
                    changed = True
    work = sorted(((orbit_count(n, H), gensets[H], len(H)) for H in subs))
    print(f"n={n}: {len(work)} subgroups total (incl. non-cyclic), m range {work[0][0]}..{work[-1][0]}", flush=True)
    for (m, gens, order) in work:
        if m > max_m:
            print(f"SKIP gens={gens} m={m} (> {max_m})", flush=True); continue
        cmd = ['./exhaust', str(n), str(s)] + [str(g) for g in gens]
        print(f"--- gens={gens} |H|={order} m={m} timeout={to}s", flush=True)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=to)
            print(r.stdout.strip(), flush=True)
            if r.returncode == 0:
                print("FOUND-STOP", flush=True); return 0
        except subprocess.TimeoutExpired:
            print(f"TIMEOUT gens={gens} m={m} after {to}s", flush=True)
    print(f"ALL-DONE n={n}", flush=True)
    return 2

if __name__ == "__main__":
    sys.exit(main())

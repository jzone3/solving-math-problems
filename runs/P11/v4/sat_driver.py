#!/usr/bin/env python3
"""Sweep multiplier subgroups with the orbit-SAT exhauster (orbit_sat.py).

Enumerates ALL subgroups of Z_n^* (joins of cyclic), skips those already
decided (parsed from prior asub_*.log DFS logs given via --done), orders by
orbit count ascending, and runs orbit_sat.py (adder encoding) with a timeout.

Usage: sat_driver.py n s [timeout_s] [max_m] [--done log1 log2 ...]
"""
import re
import subprocess
import sys
from math import gcd


def cyc(n, t):
    g = {1}; x = t
    while x not in g:
        g.add(x); x = (x * t) % n
    return frozenset(g)


def close(n, gens):
    g = {1}
    changed = True
    while changed:
        changed = False
        for a in list(g):
            for b in gens:
                v = (a * b) % n
                if v not in g:
                    g.add(v); changed = True
    return frozenset(g)


def orbit_count(n, H):
    seen = [False] * n; m = 0
    for i in range(n):
        if not seen[i]:
            m += 1
            stack = [i]; seen[i] = True
            while stack:
                j = stack.pop()
                for t in H:
                    v = (j * t) % n
                    if not seen[v]:
                        seen[v] = True; stack.append(v)
    return m


def join(n, A, B):
    g = set(A) | set(B)
    frontier = list(g)
    while frontier:
        new = []
        for a in list(g):
            for b in frontier:
                v = (a * b) % n
                if v not in g:
                    g.add(v); new.append(v)
        frontier = new
    return frozenset(g)


def main():
    args = sys.argv[1:]
    done_logs = []
    if '--done' in args:
        i = args.index('--done')
        done_logs = args[i + 1:]
        args = args[:i]
    n = int(args[0]); s = int(args[1])
    to = int(args[2]) if len(args) > 2 else 7200
    max_m = int(args[3]) if len(args) > 3 else 60

    # decided subgroups from prior DFS logs: lines "--- gens=(..) .." followed by EXHAUSTED
    done = set()
    for path in done_logs:
        gens_cur = None
        for line in open(path):
            mm = re.match(r'--- gens=\(([\d, ]+)\)', line)
            if mm:
                gens_cur = tuple(int(x) for x in mm.group(1).split(',') if x.strip())
            elif line.startswith('EXHAUSTED') and gens_cur:
                done.add(close(n, gens_cur))
                gens_cur = None
    print(f"n={n}: {len(done)} subgroups already decided by DFS", flush=True)

    units = [t for t in range(1, n) if gcd(t, n) == 1]
    subs = set(); gensets = {}
    for t in units[1:]:
        H = cyc(n, t)
        if H not in subs:
            subs.add(H); gensets[H] = (t,)
    changed = True
    while changed:
        changed = False
        cur = list(subs)
        for i in range(len(cur)):
            for j in range(i + 1, len(cur)):
                J = join(n, cur[i], cur[j])
                if J not in subs:
                    subs.add(J)
                    gensets[J] = tuple(sorted(set(gensets[cur[i]]) | set(gensets[cur[j]])))
                    changed = True
    work = sorted((orbit_count(n, H), gensets[H], H) for H in subs)
    print(f"n={n}: {len(work)} subgroups, m range {work[0][0]}..{work[-1][0]}", flush=True)
    for (m, gens, H) in work:
        if H in done:
            print(f"DONE-SKIP gens={gens} m={m} (DFS-exhausted)", flush=True)
            continue
        if m > max_m:
            print(f"SKIP gens={gens} m={m} (> {max_m})", flush=True)
            continue
        cmd = ['python3', 'orbit_sat.py', str(n), str(s)] + [str(g) for g in gens] + ['--enc', 'adder']
        print(f"--- gens={gens} |H|={len(H)} m={m} timeout={to}s", flush=True)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=to)
            print(r.stdout.strip(), flush=True)
            if r.returncode == 0:
                print("FOUND-STOP", flush=True)
                return 0
        except subprocess.TimeoutExpired:
            print(f"TIMEOUT gens={gens} m={m} after {to}s", flush=True)
    print(f"ALL-DONE n={n}", flush=True)
    return 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Systematic sweep over conjugacy classes of cyclic subgroups <g> of the monomial
symmetry group S3 wr S6 of the football-pool space {0,1,2}^6, searching for a
<g>-invariant covering code (radius 1) of size <= TARGET via exact orbit ILP.

Element classes up to conjugacy: coordinate-permutation cycle type (partition of 6),
plus for each cycle the conjugacy class in S3 of the composite symbol map around the
cycle (id / transposition / 3-cycle). This covers ALL cyclic groups up to conjugacy,
hence ALL codes invariant under at least one nontrivial monomial symmetry.

Usage: orbit_sweep.py TARGET [max_orbits] [time_limit_per_ilp]
"""
import itertools
import sys
import highspy
import numpy as np

TARGET = int(sys.argv[1])
MAX_ORBITS = int(sys.argv[2]) if len(sys.argv) > 2 else 400
TL = float(sys.argv[3]) if len(sys.argv) > 3 else 300.0

N = 729
def digits(w):
    return [(w // 3**i) % 3 for i in range(6)]
def undig(d):
    return sum(v * 3**i for i, v in enumerate(d))

BALL = []
for w in range(N):
    d = digits(w)
    b = [w]
    for i in range(6):
        for v in (1, 2):
            e = d[:]; e[i] = (e[i] + v) % 3
            b.append(undig(e))
    BALL.append(b)

S3 = {"id": (0, 1, 2), "tau": (1, 0, 2), "sigma": (1, 2, 0)}

def partitions(n, maxpart=None):
    if maxpart is None:
        maxpart = n
    if n == 0:
        yield []
        return
    for p in range(min(n, maxpart), 0, -1):
        for rest in partitions(n - p, p):
            yield [p] + rest

def build_g(cycles):
    """cycles: list of (length, s3name). Build perm over coords and symbol maps.
    Put the composite map on the last edge of the cycle; identity elsewhere."""
    perm = [0] * 6
    smap = [S3["id"]] * 6   # symbol map applied to digit moving FROM coordinate i
    pos = 0
    for (L, s) in cycles:
        idxs = list(range(pos, pos + L))
        for k, i in enumerate(idxs):
            perm[i] = idxs[(k + 1) % L]
        smap[idxs[-1]] = S3[s]
        pos += L
    return perm, smap

def apply_g(perm, smap, w):
    d = digits(w)
    e = [0] * 6
    for i in range(6):
        e[perm[i]] = smap[i][d[i]]
    return undig(e)

def orbits_of(perm, smap):
    seen = [False] * N
    orbits = []
    orb_id = [0] * N
    for w in range(N):
        if seen[w]:
            continue
        o = []
        x = w
        while not seen[x]:
            seen[x] = True
            o.append(x)
            orb_id[x] = len(orbits)
            x = apply_g(perm, smap, x)
        orbits.append(o)
    return orbits, orb_id

def solve(orbits, orb_id, target):
    M = len(orbits)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", TL)
    h.setOptionValue("threads", 1)
    inf = highspy.kHighsInf
    sizes = np.array([float(len(o)) for o in orbits])
    h.addVars(M, np.zeros(M), np.ones(M))
    h.changeColsIntegrality(M, np.arange(M, dtype=np.int32), np.full(M, highspy.HighsVarType.kInteger))
    h.changeColsCost(M, np.arange(M, dtype=np.int32), sizes)
    for w in range(N):
        cols = sorted(set(orb_id[b] for b in BALL[w]))
        h.addRow(1.0, inf, len(cols), np.array(cols, dtype=np.int32), np.ones(len(cols)))
    h.run()
    st = h.getModelStatus()
    if st == highspy.HighsModelStatus.kOptimal:
        obj = h.getInfo().objective_function_value
        sol = np.array(h.getSolution().col_value)
        chosen = [w for j in np.where(sol > 0.5)[0] for w in orbits[int(j)]]
        return obj, chosen, "optimal"
    return None, None, str(st)

count = 0
for lam in partitions(6):
    k = len(lam)
    # assignments of S3 classes to cycles; dedupe assignments among equal-length cycles
    seen_assign = set()
    for assign in itertools.product(S3.keys(), repeat=k):
        key = tuple(sorted(zip(lam, assign)))
        if key in seen_assign:
            continue
        seen_assign.add(key)
        # order of g: lcm over cycles of L * order(s) adjustment; skip identity
        if all(L == 1 and s == "id" for L, s in zip(lam, assign)):
            continue
        perm, smap = build_g(list(zip(lam, assign)))
        orbits, orb_id = orbits_of(perm, smap)
        M = len(orbits)
        if M > MAX_ORBITS:
            print(f"SKIP lam={lam} assign={assign} orbits={M}", flush=True)
            continue
        count += 1
        obj, chosen, st = solve(orbits, orb_id, TARGET)
        tag = f"lam={lam} assign={assign} orbits={M}"
        if obj is None:
            print(f"NOSOLVE {tag} status={st}", flush=True)
        else:
            print(f"OPT {tag} best_invariant_cover={int(round(obj))}", flush=True)
            if obj <= TARGET:
                fn = f"sweep_code_{int(round(obj))}.txt"
                with open(fn, "w") as f:
                    for w in sorted(chosen):
                        f.write("".join(str(v) for v in digits(w)) + "\n")
                print("WROTE", fn, flush=True)
print("sweep complete, classes solved:", count)

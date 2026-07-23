#!/usr/bin/env python3
"""Feasibility-only re-run for orbit_sweep classes that timed out or were skipped:
decide whether a <g>-invariant covering code of size <= TARGET exists.
Reads sweep log lines 'NOSOLVE lam=[..] assign=(..) ...' / 'SKIP lam=[..] assign=(..) ...'.
Usage: orbit_feas.py SWEEPLOG TARGET TL"""
import ast
import re
import sys
import highspy
import numpy as np
import importlib.util

spec = importlib.util.spec_from_file_location("osw", "/home/ubuntu/p25/orbit_sweep.py")
# avoid executing the sweep main loop: reimplement helpers here instead
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

def build_g(cycles):
    perm = [0] * 6
    smap = [S3["id"]] * 6
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

log, TARGET, TL = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
classes = []
for line in open(log):
    m = re.match(r"(NOSOLVE|SKIP) lam=(\[[^\]]*\]) assign=(\([^)]*\))", line)
    if m:
        lam = ast.literal_eval(m.group(2))
        assign = ast.literal_eval(m.group(3))
        if isinstance(assign, str):
            assign = (assign,)
        classes.append((lam, assign))
print(f"{len(classes)} classes to re-check at target {TARGET}", flush=True)
for lam, assign in classes:
    if all(L == 1 and s == "id" for L, s in zip(lam, assign)):
        print(f"IDENTITY-SKIP lam={lam} assign={assign} (this is the unrestricted problem)", flush=True)
        continue
    perm, smap = build_g(list(zip(lam, assign)))
    orbits, orb_id = orbits_of(perm, smap)
    M = len(orbits)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", TL)
    h.setOptionValue("threads", 2)
    inf = highspy.kHighsInf
    sizes = np.array([float(len(o)) for o in orbits])
    h.addVars(M, np.zeros(M), np.ones(M))
    h.changeColsIntegrality(M, np.arange(M, dtype=np.int32), np.full(M, highspy.HighsVarType.kInteger))
    h.changeColsCost(M, np.arange(M, dtype=np.int32), sizes)
    for w in range(N):
        cols = sorted(set(orb_id[b] for b in BALL[w]))
        h.addRow(1.0, inf, len(cols), np.array(cols, dtype=np.int32), np.ones(len(cols)))
    h.addRow(-inf, float(TARGET), M, np.arange(M, dtype=np.int32), sizes)
    h.run()
    st = h.getModelStatus()
    if st == highspy.HighsModelStatus.kOptimal:
        sol = np.array(h.getSolution().col_value)
        chosen = [w for j in np.where(sol > 0.5)[0] for w in orbits[int(j)]]
        fn = f"feas_code_{len(chosen)}.txt"
        with open(fn, "w") as f:
            for w in sorted(chosen):
                f.write("".join(str(v) for v in digits(w)) + "\n")
        print(f"FEASIBLE!!! lam={lam} assign={assign} size={len(chosen)} wrote {fn}", flush=True)
    elif st == highspy.HighsModelStatus.kInfeasible:
        print(f"INFEASIBLE lam={lam} assign={assign} orbits={M}", flush=True)
    else:
        print(f"UNDECIDED lam={lam} assign={assign} orbits={M} status={st}", flush=True)
print("feasibility recheck complete", flush=True)

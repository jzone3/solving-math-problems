#!/usr/bin/env python3
"""Structured search: covering codes of length 6 over GF(3), radius 1, invariant under a
cyclic group <g> where g is a monomial symmetry (coordinate permutation + per-coordinate
affine symbol map x -> a*x+b, a in {1,2}). For each random g, words split into orbits;
choose orbits (all-in/all-out) to cover all 729 words with total size <= TARGET via ILP.
Usage: orbit_search.py TARGET NUM_TRIALS SEED
"""
import random
import sys
import highspy
import numpy as np

TARGET = int(sys.argv[1])
TRIALS = int(sys.argv[2])
random.seed(int(sys.argv[3]))

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

def apply_g(perm, aa, bb, w):
    d = digits(w)
    e = [0] * 6
    for i in range(6):
        e[perm[i]] = (aa[i] * d[i] + bb[i]) % 3
    return undig(e)

def try_group(perm, aa, bb):
    # orbits of <g>
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
            x = apply_g(perm, aa, bb, x)
        if orb_id[x] != len(orbits):
            return None  # inconsistent (shouldn't happen for a bijection)
        orbits.append(o)
    M = len(orbits)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", 60.0)
    h.setOptionValue("threads", 1)
    inf = highspy.kHighsInf
    h.addVars(M, np.zeros(M), np.ones(M))
    h.changeColsIntegrality(M, np.arange(M, dtype=np.int32), np.full(M, highspy.HighsVarType.kInteger))
    h.changeColsCost(M, np.arange(M, dtype=np.int32), np.array([float(len(o)) for o in orbits]))
    for w in range(N):
        cols = sorted(set(orb_id[b] for b in BALL[w]))
        h.addRow(1.0, inf, len(cols), np.array(cols, dtype=np.int32), np.ones(len(cols)))
    h.addRow(-inf, float(TARGET), M, np.arange(M, dtype=np.int32),
             np.array([float(len(o)) for o in orbits]))
    h.run()
    if h.getModelStatus() == highspy.HighsModelStatus.kOptimal:
        sol = np.array(h.getSolution().col_value)
        chosen = [w for j in np.where(sol > 0.5)[0] for w in orbits[int(j)]]
        return chosen
    return None

best = 10**9
for t in range(TRIALS):
    perm = list(range(6)); random.shuffle(perm)
    aa = [random.choice([1, 2]) for _ in range(6)]
    bb = [random.randrange(3) for _ in range(6)]
    res = try_group(tuple(perm), aa, bb)
    if res is not None:
        sz = len(res)
        if sz < best:
            best = sz
            print(f"trial {t}: perm={perm} a={aa} b={bb} -> code size {sz}", flush=True)
            if sz <= TARGET:
                with open(f"orbit_code_{sz}.txt", "w") as f:
                    for w in sorted(res):
                        f.write("".join(str(v) for v in digits(w)) + "\n")
                print("WROTE", f"orbit_code_{sz}.txt", flush=True)
print("done best=", best)

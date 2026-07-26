"""Alternating exact half-minimisation (Parts' L u rho*S idea, done exactly).

Fix one half of a witness and solve the other half to optimality by implicit
hitting set: D is a hyperedge iff FIX u (CAND \\ D) is 4-colorable, so any
admissible other half must hit every D, and the minimum hitting set is the
smallest possible other half *given* FIX.  Alternating the two halves is Parts'
own scheme, but with an exact inner solve instead of greedy deletion.

Hyperedges come from a min-conflicts/tabu colouring of FIX u CAND followed by a
conflict cover restricted to CAND (sound: dropping the cover leaves a proper
4-colouring).

Env: POOL, START (pickle of the current witness), SIDE (0 = optimise the
lattice half, 1 = the rotated half), STEPS, ITERS, OUT.
"""
import json
import os
import pickle
import random
import subprocess
import time

import numpy as np
from scipy.optimize import LinearConstraint, milp

import findrot as R
from sat import color_cnf, write_cnf, KISSAT

POOL = os.environ.get('POOL', 'tasym_1.6_1.3.pkl')
START = os.environ.get('START', '')
SIDE = int(os.environ.get('SIDE', '1'))
STEPS = int(os.environ.get('STEPS', '1500000'))
ITERS = int(os.environ.get('ITERS', '10000'))
SEED = int(os.environ.get('SEED', '1'))
OUT = os.environ.get('OUT', f'halfhs_{SEED}.pkl')

pts, E = pickle.load(open(POOL, 'rb'))
N = len(pts)
adj = [[] for _ in range(N)]
for a, b in E:
    adj[a].append(b)
    adj[b].append(a)
half = [0 if R.in_lattice(p) else 1 for p in pts]
cur = sorted(pickle.load(open(START, 'rb'))) if START else list(range(N))
rng = random.Random(SEED)
print(f'pool {N}, witness {len(cur)} '
      f'(half0 {sum(1 for v in cur if half[v]==0)}, '
      f'half1 {sum(1 for v in cur if half[v]==1)})', flush=True)


def colorable(vs):
    vs = sorted(vs)
    rm = {x: i for i, x in enumerate(vs)}
    E2 = [(rm[u], rm[v]) for u, v in E if u in rm and v in rm]
    nv, cls = color_cnf(len(vs), E2, 4)
    cnf = f'/tmp/hh_{SEED}_{os.getpid()}.cnf'
    write_cnf(cnf, nv, cls)
    try:
        r = subprocess.run([KISSAT, cnf], capture_output=True, text=True)
        return 's UNSATISFIABLE' not in r.stdout
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def colour_fixed(fix):
    """A proper 4-colouring of the frozen half (it is 4-colorable on its own)."""
    vs = sorted(fix)
    rm = {x: i for i, x in enumerate(vs)}
    E2 = [(rm[u], rm[v]) for u, v in E if u in rm and v in rm]
    nv, cls = color_cnf(len(vs), E2, 4)
    cnf = f'/tmp/hhf_{SEED}_{os.getpid()}.cnf'
    write_cnf(cnf, nv, cls)
    try:
        r = subprocess.run([KISSAT, cnf], capture_output=True, text=True)
        assert 's SATISFIABLE' in r.stdout
        pos = {int(t) for line in r.stdout.splitlines()
               if line.startswith('v ') for t in line[2:].split()
               if int(t) > 0}
        return {v: c for v, i in rm.items() for c in range(4)
                if 4 * i + c + 1 in pos}
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def tabu_cover(fix, cand, fixcol):
    """A hyperedge: subset of `cand` whose removal 4-colours fix u cand.

    The frozen half keeps a proper colouring throughout, so every surviving
    conflict has an endpoint in `cand` and the cover is a valid clause.
    """
    univ = sorted(set(fix) | set(cand))
    idx = {v: i for i, v in enumerate(univ)}
    col = [fixcol[v] if v in fixcol else rng.randrange(4) for v in univ]
    free = [idx[v] for v in cand]
    freeset = set(free)
    nbr = [[idx[u] for u in adj[v] if u in idx] for v in univ]
    cnt = [[0] * 4 for _ in univ]
    for i in range(len(univ)):
        for j in nbr[i]:
            cnt[i][col[j]] += 1
    bad = [i for i in free if cnt[i][col[i]]]
    for _ in range(STEPS):
        if not bad:
            break
        i = bad[rng.randrange(len(bad))]
        if not cnt[i][col[i]]:
            bad.remove(i)
            continue
        if i not in freeset:
            bad.remove(i)
            continue
        c = (rng.randrange(4) if rng.random() < 0.02 else
             min(range(4), key=lambda k: cnt[i][k]))
        if c == col[i]:
            continue
        old, col[i] = col[i], c
        for j in nbr[i]:
            cnt[j][old] -= 1
            cnt[j][c] += 1
            if j in freeset and cnt[j][col[j]] and j not in bad:
                bad.append(j)
        if cnt[i][c] and i not in bad:
            bad.append(i)
    candset = set(cand)
    conf = [(univ[i], univ[j]) for i in range(len(univ)) for j in nbr[i]
            if univ[i] < univ[j] and col[i] == col[j]]
    if any(a not in candset and b not in candset for a, b in conf):
        return None                      # conflict inside the frozen half
    deg = {}
    for a, b in conf:
        for x in (a, b):
            if x in candset:
                deg[x] = deg.get(x, 0) + 1
    out, rest = set(), list(conf)
    while rest:
        v = max(deg, key=lambda x: deg.get(x, 0))
        out.add(v)
        rest2 = []
        for a, b in rest:
            if a == v or b == v:
                for x in (a, b):
                    if x in deg:
                        deg[x] -= 1
            else:
                rest2.append((a, b))
        rest = rest2
        deg.pop(v, None)
    return sorted(out)


def optimise(cur, side):
    fix = [v for v in cur if half[v] != side]
    cand = [v for v in range(N) if half[v] == side]
    ci = {v: i for i, v in enumerate(cand)}
    target = len([v for v in cur if half[v] == side])
    print(f'  side {side}: fix {len(fix)}, candidates {len(cand)}, '
          f'current {target}', flush=True)
    fixcol = colour_fixed(fix)
    clauses = []
    t0 = time.time()
    for it in range(ITERS):
        if clauses:
            A = np.zeros((len(clauses), len(cand)))
            for r, cl in enumerate(clauses):
                A[r, [ci[v] for v in cl]] = 1.0
            cons = [LinearConstraint(A, lb=1, ub=np.inf)]
        else:
            cons = []
        obj = 1.0 + np.array([rng.random() for _ in cand]) / (10.0 * len(cand))
        res = milp(c=obj, constraints=cons, integrality=np.ones(len(cand)),
                   bounds=(0, 1))
        sol = np.round(res.x).astype(int)
        S = [cand[i] for i in range(len(cand)) if sol[i]]
        if len(S) >= target:
            print(f'  side {side}: lower bound {len(S)} >= current {target} '
                  f'-- optimal ({round(time.time()-t0)}s, {it} its)', flush=True)
            return None
        if not colorable(set(fix) | set(S)):
            print(f'  *** side {side}: {len(fix)+len(S)} vertices '
                  f'(was {len(fix)+target})', flush=True)
            return sorted(set(fix) | set(S))
        D = tabu_cover(fix, cand, fixcol)
        if D is None:
            continue
        clauses.append(D)
        if it % 10 == 0:
            print(f'    it{it}: bound {len(S)}, |D| {len(D)} '
                  f'({round(time.time()-t0)}s)', flush=True)
    return None


def main():
    global cur
    side = SIDE
    stall = 0
    while stall < 2:
        got = optimise(cur, side)
        if got:
            cur = got
            pickle.dump(cur, open(OUT, 'wb'))
            print(f'witness now {len(cur)} vertices -> {OUT}', flush=True)
            stall = 0
        else:
            stall += 1
        side = 1 - side
    print(f'both halves optimal at {len(cur)} vertices', flush=True)


if __name__ == '__main__':
    main()

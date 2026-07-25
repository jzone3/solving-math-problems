"""Alternating half re-optimisation of a type-M graph (L u omega S).

Every earlier search moved vertices globally, so the two halves of the record
were always perturbed together and only shallowly.  Here one half is frozen and
the other is re-optimised from scratch over the *whole* candidate pool of that
half (up to a full rebuild of all 136 vertices of S), which is a far deeper
neighbourhood: the frozen half keeps the union non-4-colorable-in-principle
while the free half can move to a completely different vertex set.

pool: w4x.pkl -- P_4 u L374 in copy A, P_4 u S136 in copy B, exact edges, and it
contains the record exactly (core = 509).

Usage: POOL=w4x.pkl START=rec_w4x.pkl SEED=1 python3 altmin.py
"""
import os
import pickle
import random
import subprocess
import time

import coremin
from sat import color_cnf, write_cnf, KISSAT

POOL = os.environ.get('POOL', 'w4x.pkl')
START = os.environ.get('START', 'rec_w4x.pkl')
SEED = int(os.environ.get('SEED', '1'))
ITERS = int(os.environ.get('ITERS', '400'))
SLACK = int(os.environ.get('SLACK', '200'))
MINNB = int(os.environ.get('MINNB', '1'))
FULLP = float(os.environ.get('FULLP', '0.25'))

E, adj = coremin.E, coremin.adj
PTS = coremin.allpts
NP = len(PTS)
HALF = [0 if t == 'A' else 1 for t, _ in PTS]
rng = random.Random(SEED)


def solve(S, seed, timeout=1800):
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in E if u in remap and v in remap]
    tri = coremin.find_triangle(S)
    tri2 = tuple(remap[x] for x in tri) if tri else None
    nvars, cls = color_cnf(len(S), E2, 4, sym_clique=tri2)
    d = os.path.expanduser('~/p23/tmp')
    os.makedirs(d, exist_ok=True)
    cnf = f'{d}/am_{SEED}_{seed}.cnf'
    try:
        write_cnf(cnf, nvars, cls)
        r = subprocess.run([KISSAT, f'--seed={seed}', cnf],
                           capture_output=True, text=True, timeout=timeout)
        if 's UNSATISFIABLE' in r.stdout:
            return True, None
        pos = {int(x) for line in r.stdout.splitlines() if line.startswith('v ')
               for x in line[2:].split() if int(x) > 0}
        col = {v: c for i, v in enumerate(S) for c in range(4)
               if 4 * i + c + 1 in pos}
        return False, col
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def recreate(S, half, cap):
    """Column generation restricted to one half."""
    S = set(S)
    acc = {}
    while True:
        ok, col = solve(S, rng.randrange(10 ** 6))
        if ok:
            return S
        if len(S) > cap:
            return None
        best, bs = None, -1.0
        for w in range(NP):
            if HALF[w] != half or w in S:
                continue
            nb = adj[w] & S
            if len(nb) < MINNB:
                continue
            k = len({col[u] for u in nb})
            sc = acc.get(w, 0.0) + (1.0 if k == 4 else 0.25 * k) + 0.01 * len(nb)
            if k == 4:
                acc[w] = acc.get(w, 0.0) + 1.0
            if sc > bs:
                best, bs = w, sc
        if best is None:
            return None
        S.add(best)


def repair(S):
    S = set(S)
    for _ in range(3):
        shrunk = False
        for v in sorted(S, key=lambda v: len(adj[v] & S)):
            if v in S and solve(S - {v}, rng.randrange(10 ** 6))[0]:
                S.discard(v)
                shrunk = True
        if not shrunk:
            break
    return S


def main():
    cur = set(pickle.load(open(START, 'rb')))
    ok, _ = solve(cur, 1)
    print(f'start {len(cur)} non-4-colorable={ok}', flush=True)
    best = set(cur)
    t0 = time.time()
    for it in range(ITERS):
        half = it % 2
        inhalf = [v for v in cur if HALF[v] == half]
        if not inhalf:
            continue
        if rng.random() < FULLP:
            k = len(inhalf)
        else:
            k = rng.randint(max(2, len(inhalf) // 8), max(3, len(inhalf) // 2))
        drop = set(rng.sample(sorted(inhalf), k))
        got = recreate(cur - drop, half, len(cur) - 1 + SLACK)
        if got is None:
            print(f'  it{it} half{half} k={k}: fail '
                  f'({round(time.time()-t0)}s)', flush=True)
            continue
        S2 = repair(got)
        print(f'  it{it} half{half} k={k}: -> {len(S2)} '
              f'(cur {len(cur)} best {len(best)}) {round(time.time()-t0)}s',
              flush=True)
        if len(S2) <= len(cur):
            cur = set(S2)
        if len(S2) < len(best):
            best = set(S2)
            pickle.dump(sorted(best), open(f'altmin_best_{SEED}.pkl', 'wb'))
            print(f'*** NEW BEST {len(best)}', flush=True)
    print(f'DONE best={len(best)}', flush=True)


if __name__ == '__main__':
    main()

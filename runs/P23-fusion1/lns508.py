"""Large-neighbourhood (ruin & recreate) search for a sub-509 5-chromatic UDG.

All prior attempts (v1 and this run) were *small* neighbourhood moves: -1+0,
-2+1, -3+2, plus greedy deletion. Those cannot escape the record's basin
because it is vertex-critical. LNS destroys a whole spatial region of the
record and rebuilds it from the extended (sqrt2) pool, which is a move of
radius ~20-40 vertices.

Loop:
  1. ruin:      remove a spatial ball of k vertices from S (4-colorable now)
  2. recreate:  greedily add pool vertices maximising degree into S, testing
                non-4-colorability once |S| drops to target, then one-by-one
  3. repair:    SAT core extraction + greedy deletion passes
  4. accept if |S| < |S_best| (strict descent, random restart otherwise)

Env: POOL, SEED, BEST (start pkl of index set, optional), ITERS, KMIN, KMAX.
"""
import os, pickle, random, time, sys, math

POOL = os.environ.get('POOL', 'pool_x2big.pkl')
os.environ['POOL'] = POOL
SEED = int(os.environ.get('SEED', '0'))
ITERS = int(os.environ.get('ITERS', '200'))
KMIN = int(os.environ.get('KMIN', '12'))
KMAX = int(os.environ.get('KMAX', '45'))
NREC = 509

import coremin
import subprocess
from sat import color_cnf, write_cnf, KISSAT
from mfield import MField

allp, E, adj = coremin.allpts, coremin.E, coremin.adj
K = MField((2, 3, 5, 11))
fl = [(K.to_float(p[0]), K.to_float(p[1])) for p in allp]
rng = random.Random(SEED)
NP = len(allp)


def unsat(S, tag):
    st, core = coremin.solve_core(S, seed=rng.randrange(10**6), timeout=600, tag=tag)
    return st == 'UNSAT', core


def model_4col(S, seed, timeout=300):
    """Return a 4-coloring dict {vertex: color} or None if non-4-colorable."""
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in E if u in remap and v in remap]
    tri = coremin.find_triangle(S)
    tri2 = tuple(remap[x] for x in tri) if tri else None
    nvars, cls = color_cnf(len(S), E2, 4, sym_clique=tri2)
    tmpdir = os.path.expanduser('~/p23/tmp')
    os.makedirs(tmpdir, exist_ok=True)
    cnf = f'{tmpdir}/mdl_{SEED}_{seed}.cnf'
    try:
        write_cnf(cnf, nvars, cls)
        r = subprocess.run([KISSAT, f'--seed={seed}', cnf],
                           capture_output=True, text=True, timeout=timeout)
        if 's UNSATISFIABLE' in r.stdout:
            return None
        pos = set()
        for line in r.stdout.splitlines():
            if line.startswith('v '):
                for tok in line[2:].split():
                    x = int(tok)
                    if x > 0:
                        pos.add(x)
        col = {}
        for i, v in enumerate(S):
            for c in range(4):
                if 4 * i + c + 1 in pos:
                    col[v] = c
                    break
        return col
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def ruin(S, k):
    """Remove a spatially-localised ball of k vertices."""
    c = rng.choice(sorted(S))
    cx, cy = fl[c]
    order = sorted(S, key=lambda v: (fl[v][0]-cx)**2 + (fl[v][1]-cy)**2)
    return set(S) - set(order[:k])


SLACK = int(os.environ.get('SLACK', '40'))


def recreate(S, target, tag):
    """Conflict-driven column generation: repeatedly add the pool vertex that is
    *blocked* (sees all 4 colors) under the most sampled 4-colorings of S."""
    S = set(S)
    acc = {}
    cap = target + SLACK
    while True:
        col = model_4col(S, rng.randrange(10**6))
        if col is None:
            ok, core = unsat(S, tag)      # confirm + core-extract with proof
            return (set(core) if core else S) if ok else None
        if len(S) >= cap:
            return None
        # score candidates: blocked under this coloring == strongest
        best, bs = None, -1.0
        for w in range(NP):
            if w in S:
                continue
            nb = adj[w] & S
            if len(nb) < 3:
                continue
            k = len({col[u] for u in nb})
            s = acc.get(w, 0.0) + (1.0 if k == 4 else 0.25 * k) + 0.01 * len(nb)
            acc[w] = acc.get(w, 0.0) + (1.0 if k == 4 else 0.0)
            if s > bs:
                best, bs = w, s
        if best is None:
            return None
        S.add(best)


GLIM = int(os.environ.get('GLIM', '80'))


def greedy_pass(S, tag):
    """Deletion passes using proof-free SAT calls (fast); core-extract at the end."""
    S = set(S)
    for _ in range(3):
        shrunk = False
        order = sorted(S, key=lambda v: len(adj[v] & S))[:GLIM]
        for v in order:
            if v not in S:
                continue
            if model_4col(S - {v}, rng.randrange(10**6)) is None:
                S.discard(v)
                shrunk = True
        if not shrunk:
            break
    ok, core = unsat(S, tag)          # certify + core-extract once
    if ok and core and len(core) < len(S):
        S = set(core)
    return S


def main():
    S = set(range(NREC))
    best = set(S)
    cur = set(S)
    print(f'LNS seed={SEED} pool={POOL} start={len(S)}', flush=True)
    t0 = time.time()
    for it in range(ITERS):
        k = rng.randint(KMIN, KMAX)
        R = ruin(cur, k)
        tag = f'lns{SEED}_{it}'
        got = recreate(R, len(cur) - 1, tag)
        if got is None:
            print(f'  it{it} k={k}: recreate failed ({round(time.time()-t0)}s)', flush=True)
            continue
        S2 = greedy_pass(got, tag)
        print(f'  it{it} k={k}: -> {len(S2)} (cur {len(cur)} best {len(best)}) '
              f'{round(time.time()-t0)}s', flush=True)
        if len(S2) <= NREC:              # record every plateau (<=509) hit
            novel = len(set(S2) - set(range(NREC)))
            pickle.dump(sorted(S2), open(f'plat_{SEED}_{it}.pkl', 'wb'))
            print(f'    plateau {len(S2)}: {novel} non-record vertices', flush=True)
        if len(S2) <= len(cur):          # plateau move: accept equal sizes too
            cur = set(S2)
        if len(S2) < len(best):
            best = set(S2)
            pickle.dump(sorted(best), open(f'lns_best_{SEED}.pkl', 'wb'))
            print(f'*** NEW BEST {len(best)} seed={SEED}', flush=True)
            if len(best) < NREC:
                print(f'*** SUB-509 CANDIDATE: {len(best)} vertices', flush=True)
    print(f'DONE best={len(best)}', flush=True)


if __name__ == '__main__':
    main()

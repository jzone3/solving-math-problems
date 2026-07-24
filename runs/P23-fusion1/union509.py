"""Combine DISTINCT 509-vertex 5-chromatic graphs found by the LNS plateau walk.

Rationale: until now exactly one 509 graph was known (the record), so
"union then minimize" was impossible. The LNS plateau walk (lns508.py) emits
plat_*.pkl -- alternative 509s that differ from the record in a few vertices.
The union of two distinct 509s is a ~510-515 vertex non-4-colorable graph whose
minimum non-4-colorable subgraph need NOT be either of them: core extraction on
the union can in principle land below 509.

For every distinct pair: core-minimize the union (several seeds) and then run a
full greedy deletion pass. Any result < 509 is reported loudly (and must then be
exact-verified with verify_m.py).

Env: POOL (pool_native.pkl), NPROC.
"""
import os, glob, pickle, itertools, random, time
from multiprocessing import Pool as MPPool

POOL = os.environ.get('POOL', 'pool_native.pkl')
os.environ['POOL'] = POOL
NPROC = int(os.environ.get('NPROC', '7'))
NREC = 509

import coremin
from sat import color_cnf, write_cnf, KISSAT
import subprocess

E, adj = coremin.E, coremin.adj


def sets():
    out = {}
    for f in sorted(glob.glob('plat_*.pkl')):
        S = frozenset(pickle.load(open(f, 'rb')))
        out[S] = f
    out[frozenset(range(NREC))] = 'record'
    return list(out.items())


def fast_unsat(S, seed):
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in E if u in remap and v in remap]
    tri = coremin.find_triangle(S)
    tri2 = tuple(remap[x] for x in tri) if tri else None
    nvars, cls = color_cnf(len(S), E2, 4, sym_clique=tri2)
    d = os.path.expanduser('~/p23/tmp')
    os.makedirs(d, exist_ok=True)
    cnf = f'{d}/u509_{seed}_{os.getpid()}.cnf'
    try:
        write_cnf(cnf, nvars, cls)
        r = subprocess.run([KISSAT, '-q', f'--seed={seed}', cnf],
                           capture_output=True, text=True, timeout=600)
        return 's UNSATISFIABLE' in r.stdout
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def minimize(S, seed):
    S = set(S)
    rng = random.Random(seed)
    for _ in range(4):
        st, core = coremin.solve_core(S, seed=rng.randrange(10**6), tag=f'u{seed}')
        if st != 'UNSAT':
            return None
        if core and len(core) < len(S):
            S = set(core)
        else:
            break
    shrunk = True
    while shrunk:
        shrunk = False
        order = sorted(S, key=lambda v: len(adj[v] & S))
        for v in order:
            if v in S and fast_unsat(S - {v}, rng.randrange(10**6)):
                S.discard(v)
                shrunk = True
    return S


def job(arg):
    i, (A, fa), (B, fb) = arg
    U = set(A) | set(B)
    if len(U) <= NREC:
        return None
    S = minimize(U, 1000 + i)
    return (fa, fb, len(U), len(S) if S else -1, sorted(S) if S else None)


def main():
    L = sets()
    print(f'distinct 509-plateau graphs: {len(L)}', flush=True)
    pairs = [(i, a, b) for i, (a, b) in enumerate(itertools.combinations(L, 2))]
    print(f'pairs: {len(pairs)}', flush=True)
    t0 = time.time()
    with MPPool(NPROC) as mp:
        for res in mp.imap_unordered(job, pairs):
            if not res:
                continue
            fa, fb, nu, ns, S = res
            print(f'  {fa} + {fb}: union {nu} -> {ns} ({round(time.time()-t0)}s)', flush=True)
            if 0 < ns < NREC:
                print(f'*** SUB-509: {ns} vertices from {fa}+{fb}', flush=True)
                pickle.dump(S, open(f'sub509_{ns}_{fa}_{fb}.pkl', 'wb'))
    print('DONE', flush=True)


if __name__ == '__main__':
    main()

"""Multi-way union of ALL known distinct 509s, minimized with randomized greedy.

Pairwise unions of distinct 509s all collapse back to 509 (union509.py). This
takes the union of *all* of them at once -- record + every swap vertex found by
scan508x (a ~520-vertex non-4-colorable graph) -- and attacks it with many
independent RANDOMLY ORDERED greedy deletion runs. Degree-ordered greedy is
deterministic and always finds the same optimum; random orders explore different
minimal subgraphs of the same union, which is the only way a different (possibly
smaller) critical subgraph would show up.

Env: POOL, LOG (scan log with swaps), SEEDS, NPROC.
"""
import os, re, random, pickle, subprocess, time
from multiprocessing import Pool as MPPool

POOL = os.environ.get('POOL', 'pool_native.pkl')
os.environ['POOL'] = POOL
LOG = os.environ.get('LOG', 'scan508n.log')
SEEDS = int(os.environ.get('SEEDS', '32'))
NPROC = int(os.environ.get('NPROC', '8'))
NREC = 509

import coremin
from sat import color_cnf, write_cnf, KISSAT

E, adj = coremin.E, coremin.adj


def unsat(S, seed):
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in E if u in remap and v in remap]
    tri = coremin.find_triangle(S)
    tri2 = tuple(remap[x] for x in tri) if tri else None
    nvars, cls = color_cnf(len(S), E2, 4, sym_clique=tri2)
    d = os.path.expanduser('~/p23/tmp')
    os.makedirs(d, exist_ok=True)
    cnf = f'{d}/mu_{os.getpid()}_{seed}.cnf'
    try:
        write_cnf(cnf, nvars, cls)
        r = subprocess.run([KISSAT, '-q', f'--seed={seed}', cnf],
                           capture_output=True, text=True, timeout=900)
        return 's UNSATISFIABLE' in r.stdout
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def base_set():
    S = set(range(NREC))
    for line in open(LOG):
        m = re.search(r'w=(\d+) swap-deletable', line)
        if m:
            S.add(int(m.group(1)))
    return S


BASE = base_set()


def run(seed):
    rng = random.Random(seed)
    S = set(BASE)
    changed = True
    while changed:
        changed = False
        order = sorted(S)
        rng.shuffle(order)
        for v in order:
            if v in S and unsat(S - {v}, rng.randrange(10**6)):
                S.discard(v)
                changed = True
    return seed, sorted(S)


def main():
    print(f'union base: {len(BASE)} vertices (record + {len(BASE)-NREC} swap points)',
          flush=True)
    if not unsat(BASE, 0):
        print('base is 4-colorable?!', flush=True)
        return
    t0 = time.time()
    best = None
    with MPPool(NPROC) as mp:
        for seed, S in mp.imap_unordered(run, range(SEEDS)):
            novel = len([v for v in S if v >= NREC])
            print(f'  seed {seed}: -> {len(S)} ({novel} non-record) '
                  f'{round(time.time()-t0)}s', flush=True)
            if best is None or len(S) < best:
                best = len(S)
                pickle.dump(S, open(f'multiunion_{len(S)}_{seed}.pkl', 'wb'))
            if len(S) < NREC:
                print(f'*** SUB-509: {len(S)} vertices (seed {seed})', flush=True)
    print(f'DONE best={best}', flush=True)


if __name__ == '__main__':
    main()

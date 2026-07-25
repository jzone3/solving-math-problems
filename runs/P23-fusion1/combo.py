"""Composite multi-swap moves: combine several *independent* single swaps of the
record into one graph, then probe for a deletion (-> 508).

Enabled only now: v1 knew a handful of swaps but never combined them, and this
run's native scan (scan508x.py on pool_native.pkl) produces many
(w -> v) pairs where  509 - v + w  is still non-4-colorable.

For every pair/triple of swaps with disjoint deleted vertices:
  S = record - {v_i} + {w_i}          (still 509 vertices)
  1. check S is non-4-colorable at all (independence is NOT automatic)
  2. if yes, try deleting EVERY vertex of S (proof-free SAT), any success = 508.

Reads swaps from a log written by scan508x.py. Env: POOL, LOG, NPROC, MAXK.
"""
import os, re, sys, pickle, itertools, random, subprocess, time
from multiprocessing import Pool as MPPool

POOL = os.environ.get('POOL', 'pool_native.pkl')
os.environ['POOL'] = POOL
LOG = os.environ.get('LOG', 'scan508n.log')
NPROC = int(os.environ.get('NPROC', '3'))
MAXK = int(os.environ.get('MAXK', '3'))
NREC = 509

import coremin
from sat import color_cnf, write_cnf, KISSAT

E, adj = coremin.E, coremin.adj


def read_swaps(path):
    out = []
    for line in open(path):
        m = re.search(r'w=(\d+) swap-deletable: \[([0-9, ]+)\]', line)
        if m:
            w = int(m.group(1))
            for v in m.group(2).split(','):
                out.append((w, int(v)))
    return out


def unsat(S, seed):
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in E if u in remap and v in remap]
    tri = coremin.find_triangle(S)
    tri2 = tuple(remap[x] for x in tri) if tri else None
    nvars, cls = color_cnf(len(S), E2, 4, sym_clique=tri2)
    d = os.path.expanduser('~/p23/tmp')
    os.makedirs(d, exist_ok=True)
    cnf = f'{d}/cb_{os.getpid()}_{seed}.cnf'
    try:
        write_cnf(cnf, nvars, cls)
        r = subprocess.run([KISSAT, '-q', f'--seed={seed}', cnf],
                           capture_output=True, text=True, timeout=900)
        return 's UNSATISFIABLE' in r.stdout
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def job(arg):
    idx, combo = arg
    dels = {v for _, v in combo}
    adds = {w for w, _ in combo}
    if len(dels) != len(combo) or len(adds) != len(combo):
        return None
    S = (set(range(NREC)) - dels) | adds
    if not unsat(S, idx):
        return (combo, 'SAT', None)          # swaps interfere: not independent
    for v in sorted(S, key=lambda v: len(adj[v] & S)):
        if unsat(S - {v}, idx * 7919 + v):
            return (combo, 'R508', sorted(S - {v}))
    return (combo, 'critical', None)


def main():
    sw = read_swaps(LOG)
    print(f'{len(sw)} swaps read from {LOG}', flush=True)
    jobs = []
    for k in range(2, MAXK + 1):
        for c in itertools.combinations(sw, k):
            jobs.append(c)
    jobs = [(i, c) for i, c in enumerate(jobs)]
    print(f'{len(jobs)} composite moves (k=2..{MAXK})', flush=True)
    t0 = time.time()
    nind = 0
    with MPPool(NPROC) as mp:
        for res in mp.imap_unordered(job, jobs):
            if not res:
                continue
            combo, st, S = res
            if st == 'R508':
                print(f'*** 508 FOUND from {combo}', flush=True)
                pickle.dump(S, open('r508_combo.pkl', 'wb'))
            elif st == 'critical':
                nind += 1
                print(f'  independent 509 (still critical): {combo} '
                      f'[{nind}] {round(time.time()-t0)}s', flush=True)
    print(f'DONE {nind} independent composite 509s, none reducible', flush=True)


if __name__ == '__main__':
    main()

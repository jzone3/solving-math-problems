"""Extended-field 508 swap scan against the 509 record.

v1's scan508/scan508m/scan_fresh only ever used candidate vertices from the
NATIVE Parts field Q(sqrt3,sqrt5,sqrt11). This scans the record's substitution
neighbourhood using candidates from the sqrt2 EXTENSION pool (pool_x2big,
Q(sqrt2,sqrt3,sqrt5,sqrt11)) -- geometry that has never been tested as swap
candidates.

Phase 1 (-1+1): for each candidate w with >= MINDEG record neighbours, and each
record vertex v near w, test whether  G509 - v + w  is still non-4-colorable.
Each such (w,v) is an *alternative* 509. If some w admits TWO independent
deletions v1,v2, then  G509 - v1 - v2 + w  has 508 vertices -> WORLD RECORD.

Phase 2 (-2+1 pairs): for every w, test all pairs from its swap-deletable set.

Env: POOL (default pool_x2big.pkl), MINDEG (4), RADIUS (2.05), NPROC (8).
Writes swaps_x2.json with all hits.
"""
import os, pickle, json, math, sys, time
from multiprocessing import Pool as MPPool

POOL = os.environ.get('POOL', 'pool_x2big.pkl')
os.environ['POOL'] = POOL
MINDEG = int(os.environ.get('MINDEG', '4'))
RADIUS = float(os.environ.get('RADIUS', '2.05'))
NPROC = int(os.environ.get('NPROC', '8'))
NREC = 509

import coremin  # loads POOL, gives solve_core over the same pool
from mfield import MField

allp, E = coremin.allpts, coremin.E
adj = coremin.adj
K = MField((2, 3, 5, 11))
REC = list(range(NREC))
RECSET = set(REC)
fl = [(K.to_float(p[0]), K.to_float(p[1])) for p in allp]


def cand_list():
    out = []
    for w in range(NREC, len(allp)):
        d = len(adj[w] & RECSET)
        if d >= MINDEG:
            out.append((d, w))
    out.sort(reverse=True)
    return [w for _, w in out]


def near_record(w):
    wx, wy = fl[w]
    return [v for v in REC
            if (fl[v][0]-wx)**2 + (fl[v][1]-wy)**2 <= RADIUS*RADIUS]


def unsat(S, tag):
    st, _ = coremin.solve_core(S, seed=abs(hash(tag)) % 10**6, timeout=900, tag=tag)
    return st == 'UNSAT'


def work(w):
    """Return (w, [swap-deletable v...], [508 hits...])."""
    base = RECSET | {w}
    dels = []
    for v in near_record(w):
        S = base - {v}
        try:
            if unsat(S, f'sx{w}_{v}'):
                dels.append(v)
        except Exception:
            continue
    hits = []
    for i in range(len(dels)):
        for j in range(i+1, len(dels)):
            S = base - {dels[i], dels[j]}   # 508 vertices
            try:
                if unsat(S, f'sx8_{w}_{i}_{j}'):
                    hits.append((dels[i], dels[j]))
            except Exception:
                continue
    return w, dels, hits


def main():
    cands = cand_list()
    print(f'pool={POOL} candidates with >={MINDEG} record nbrs: {len(cands)}', flush=True)
    t0 = time.time()
    res = {'swaps': [], 'r508': []}
    with MPPool(NPROC) as mp:
        for k, (w, dels, hits) in enumerate(mp.imap_unordered(work, cands)):
            if dels:
                print(f'  w={w} swap-deletable: {dels}', flush=True)
                res['swaps'].append([w, dels])
            if hits:
                print(f'*** 508 CANDIDATE w={w} pairs={hits}', flush=True)
                res['r508'].append([w, hits])
                json.dump(res, open('swaps_x2.json', 'w'))
            if k % 25 == 0:
                print(f'  ..{k}/{len(cands)} {round(time.time()-t0)}s', flush=True)
    json.dump(res, open('swaps_x2.json', 'w'))
    print(f'DONE {len(cands)} candidates, {len(res["swaps"])} swap-deletable, '
          f'{len(res["r508"])} 508-candidates, {round(time.time()-t0)}s', flush=True)


if __name__ == '__main__':
    main()

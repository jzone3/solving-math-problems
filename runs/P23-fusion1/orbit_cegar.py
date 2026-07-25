"""Hitting-set search at the ORBIT level.

Parts' record is orbit-structured: L374 is 37 base orbits (18 of them complete)
and S136 is 14 orbits.  Searching over the 5696 individual pool vertices is
therefore hugely redundant -- the natural search space is the few hundred
orbits of the automorphism group <tau3, tau4, conj33, neg> acting on
W_4 = P u rho P.

So: selection variables per ORBIT, hyperedges lifted to orbits (an orbit is in
the lifted hyperedge iff it meets D), cardinality bound on the number of
selected orbits.  A hit gives a non-4-colorable union of whole orbits, which is
then vertex-minimised exactly (kissat + DRAT core) -- and unlike the pool-wide
deletion runs (calibrated ~3.5x off optimum) that minimisation starts from a
few hundred vertices, not from thousands.

Env: POOL, MAXORB, SEED, TABU, BANK.
"""
import json
import os
import pickle
import random
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical153

import hyperpar as H
import lattice as L

MAXORB = int(os.environ.get('MAXORB', '55'))
SEED = int(os.environ.get('SEED', '1'))
BANK = os.environ.get('BANK', 'orbbank.jsonl')
MAXVTX = int(os.environ.get('MAXVTX', '508'))
BUDGET = int(os.environ.get('BUDGET', '1'))   # PB constraint on vertex count
MINVTX = int(os.environ.get('MINVTX', '0'))   # ignore hopelessly small unions

PTS = H.PTS
rng = random.Random(SEED)


def orbits(pts):
    idx = {p: i for i, p in enumerate(pts)}
    seen, out = set(), []
    for i, (t, p) in enumerate(pts):
        if i in seen:
            continue
        cur = {(t, p)}
        while True:
            new = set(cur)
            for tt, q in cur:
                for f in (L.tau3, L.tau4, L.conj33, L.neg):
                    new.add((tt, f(q)))
            if new == cur:
                break
            cur = new
        orb = sorted(idx[x] for x in cur if x in idx)
        seen.update(orb)
        out.append(orb)
    return out


def main():
    ORB = orbits(PTS)
    sizes = sorted(len(o) for o in ORB)
    print(f'{len(ORB)} orbits over {len(PTS)} vertices, sizes '
          f'{sizes[0]}..{sizes[-1]}, bound {MAXORB} orbits', flush=True)
    where = {}
    for k, o in enumerate(ORB):
        for v in o:
            where[v] = k

    pool = IDPool(start_from=1)
    ovar = {k: pool.id(('o', k)) for k in range(len(ORB))}
    outer = Cadical153()
    if BUDGET:      # sum of orbit sizes <= MAXVTX: any hit beats the record.
        # pypblib does not build here, so the weighted budget is encoded by
        # repeating each orbit literal (size) times in a sequential counter --
        # the counter sums input positions, so repetition gives the weight.
        lits = [ovar[k] for k in range(len(ORB)) for _ in range(len(ORB[k]))]
        for cl in CardEnc.atmost(lits=lits, bound=MAXVTX, vpool=pool,
                                 encoding=EncType.seqcounter).clauses:
            outer.add_clause(cl)
        if MINVTX:      # tiny selections are trivially colourable: skip them
            for cl in CardEnc.atleast(lits=lits, bound=MINVTX, vpool=pool,
                                      encoding=EncType.seqcounter).clauses:
                outer.add_clause(cl)
    else:
        for cl in CardEnc.atmost(lits=list(ovar.values()), bound=MAXORB,
                                 vpool=pool,
                                 encoding=EncType.seqcounter).clauses:
            outer.add_clause(cl)
    seen = 0
    if os.path.exists(BANK):
        with open(BANK) as f:
            for line in f:
                outer.add_clause([ovar[k] for k in json.loads(line)])
                seen += 1
        print(f'{seen} orbit hyperedges preloaded', flush=True)

    t0, it = time.time(), 0
    while True:
        it += 1
        if not outer.solve():
            print(f'OUTER UNSAT: no union of <= {MAXORB} orbits of this pool '
                  f'is non-4-colorable ({round(time.time()-t0)}s)', flush=True)
            return
        model = set(outer.get_model())
        sel = [k for k in range(len(ORB)) if ovar[k] in model]
        V = sorted(v for k in sel for v in ORB[k])
        if len(V) > MAXVTX:                 # too big to be useful; forbid
            outer.add_clause([-ovar[k] for k in sel])
            continue
        col = H.kissat_color(V, f'ob_{SEED}')
        if col is None:
            pickle.dump(V, open(f'orbit_hit_{SEED}.pkl', 'wb'))
            print(f'*** HIT: {len(V)} vertices from {len(sel)} orbits',
                  flush=True)
            return
        movable = [v for v in H.CAND if v not in set(V)]
        D = H.tabu_hyperedge(col, movable, rng)
        if not D:
            continue
        lifted = sorted({where[v] for v in D})
        with open(BANK, 'a') as f:
            f.write(json.dumps(lifted) + '\n')
        with open(BANK) as f:
            fresh = [json.loads(line) for line in f][seen:]
        for cl in fresh:
            outer.add_clause([ovar[k] for k in cl])
        seen += len(fresh)
        if it % 5 == 0 or it < 5:
            print(f'  it{it}: {len(sel)} orbits / {len(V)} vtx, '
                  f'lifted hyperedge {len(lifted)} orbits, '
                  f'{round(time.time()-t0)}s', flush=True)


if __name__ == '__main__':
    main()

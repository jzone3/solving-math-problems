"""Minimum-hitting-set search with MAXIMAL-4-colorable-set hyperedges.

This is the modern form of the machinery Parts uses in his section 5 (critical
subgraph enumeration + minimal-graph search), and the piece that was missing
from every heuristic in this run:

  * a set D of candidates is a valid *hyperedge* iff  universe \\ D  is
    4-colorable, because any non-4-colorable witness inside universe \\ D would
    be a subgraph of a 4-colorable graph;
  * minimal hyperedges  <->  MAXIMAL 4-colorable subsets;
  * a witness is exactly a hitting set of all hyperedges, so the smallest
    witness is the minimum hitting set -- solved as SAT over selection
    variables with a cardinality bound, refined lazily.

cegar_half.py used the same loop but with *greedy-extension* hyperedges of
~850 vertices, which are far from minimal and therefore almost useless as
constraints.  Here each hyperedge is the complement of a maximal 4-colorable
set, computed with one incremental SAT solver (indicator variable per candidate,
assumption-based), which typically yields hyperedges one to two orders of
magnitude smaller.

Env: POOL, FROZEN (pkl of a vertex set; its vertices in the *other* half are
frozen in), FREEHALF (0/1, which half is searched), MAXSEL, SEED.
Setting FROZEN='' searches the whole pool with no frozen part.
"""
import os
import pickle
import random
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical153

import coremin

POOL = os.environ.get('POOL', 'w4x.pkl')
FROZEN = os.environ.get('FROZEN', 'rec_w4x.pkl')
FREEHALF = int(os.environ.get('FREEHALF', '1'))
MAXSEL = int(os.environ.get('MAXSEL', '135'))
SEED = int(os.environ.get('SEED', '1'))
REPORT = int(os.environ.get('REPORT', '10'))

E, adj, PTS = coremin.E, coremin.adj, coremin.allpts
NP = len(PTS)
HALF = [0 if t == 'A' else 1 for t, _ in PTS]
rng = random.Random(SEED)

if FROZEN:
    fro = set(pickle.load(open(FROZEN, 'rb')))
    FIX = sorted(v for v in fro if HALF[v] != FREEHALF)
    CAND = sorted(v for v in range(NP) if HALF[v] == FREEHALF)
else:
    FIX = []
    CAND = list(range(NP))
FIXS = set(FIX)
print(f'frozen {len(FIX)}, candidates {len(CAND)}, bound {MAXSEL}', flush=True)


class Extender:
    """Incremental 4-colouring solver with an indicator per candidate."""

    def __init__(self):
        self.pool = IDPool(start_from=1)
        self.s = Cadical153()
        self.x = {v: [self.pool.id(('x', v, k)) for k in range(4)]
                  for v in FIX + CAND}
        self.ind = {v: self.pool.id(('in', v)) for v in CAND}
        for v, xs in self.x.items():
            self.s.add_clause(xs)
        for u, v in E:
            if u not in self.x or v not in self.x:
                continue
            guard = [-self.ind[u]] if u in self.ind else []
            guard += [-self.ind[v]] if v in self.ind else []
            for k in range(4):
                self.s.add_clause(guard + [-self.x[u][k], -self.x[v][k]])

    def maximal(self, seed_in):
        """Greedily grow a maximal 4-colorable set containing `seed_in`."""
        M = list(seed_in)
        assump = [self.ind[v] for v in M]
        if not self.s.solve(assumptions=assump):
            return None
        order = [v for v in CAND if v not in set(M)]
        rng.shuffle(order)
        for v in order:
            if self.s.solve(assumptions=assump + [self.ind[v]]):
                M.append(v)
                assump.append(self.ind[v])
        return set(M)


def four_colorable(S, ext):
    return ext.s.solve(assumptions=[ext.ind[v] for v in S if v in ext.ind])


def main():
    ext = Extender()
    pool = IDPool(start_from=1)
    svar = {v: pool.id(('s', v)) for v in CAND}
    outer = Cadical153()
    for cl in CardEnc.atmost(lits=[svar[v] for v in CAND], bound=MAXSEL,
                             vpool=pool, encoding=EncType.totalizer).clauses:
        outer.add_clause(cl)
    # WLOG min-degree 4 (a vertex of degree <= 3 is colourable last)
    candset = set(CAND)
    for v in CAND:
        nf = len(adj[v] & FIXS)
        nb = sorted(adj[v] & candset)
        if nf + len(nb) < 4:
            outer.add_clause([-svar[v]])
            continue
        need = 4 - nf
        if need <= 0:
            continue
        for cl in CardEnc.atleast(lits=[svar[u] for u in nb], bound=need,
                                  vpool=pool,
                                  encoding=EncType.totalizer).clauses:
            outer.add_clause(cl + [-svar[v]])
    print('outer built', flush=True)

    it = 0
    t0 = time.time()
    sizes = []
    while True:
        it += 1
        if not outer.solve():
            print(f'OUTER UNSAT after {it-1} hyperedges '
                  f'({round(time.time()-t0)}s): no witness with <= {MAXSEL} '
                  f'free vertices exists over this pool', flush=True)
            return
        model = set(outer.get_model())
        sel = [v for v in CAND if svar[v] in model]
        if not four_colorable(sel, ext):
            S = sorted(set(sel) | FIXS)
            pickle.dump(S, open(f'cegar2_hit_{SEED}.pkl', 'wb'))
            print(f'*** WITNESS: {len(S)} vertices ({len(FIX)} frozen + '
                  f'{len(sel)} free)', flush=True)
            return
        M = ext.maximal(sel)
        D = [v for v in CAND if v not in M]
        if not D:
            print('the whole pool is 4-colorable -- nothing to find', flush=True)
            return
        outer.add_clause([svar[v] for v in D])
        sizes.append(len(D))
        if it % REPORT == 0:
            print(f'  it{it}: |sel|={len(sel)} hyperedge={len(D)} '
                  f'(avg {sum(sizes)//len(sizes)}) {round(time.time()-t0)}s',
                  flush=True)


if __name__ == '__main__':
    main()

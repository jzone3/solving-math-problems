"""Minimum-hitting-set search over tabu hyperedges (Parts-style, modern form).

Loads a bank of hyperedges produced by hyperpar.py (|D| ~ 35-200 rather than the
~850 of greedy extension), then runs the exact loop:

    outer SAT: pick <= MAXSEL free candidates hitting every known hyperedge
    -> if frozen half + selection is non-4-colorable: WITNESS (a 508)
    -> else fix that colouring and tabu-colour the rest to produce a new
       hyperedge disjoint from the selection, which cuts it off.

If the outer solver ever reports UNSAT, no witness of that size exists over the
pool -- a complete negative result rather than a heuristic floor.

Env: POOL, FROZEN, FREEHALF, MAXSEL, SEED, HYP, TABU, NOISE.
"""
import os
import pickle
import random
import json
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical153

import hyperpar as H

MAXSEL = int(os.environ.get('MAXSEL', '135'))
SEED = int(os.environ.get('SEED', '1'))
HYP = os.environ.get('HYP', 'hyp_w4x.pkl')
BANK = os.environ.get('BANK', 'bank.jsonl')   # shared, append-only
PERIT = int(os.environ.get('PERIT', '3'))     # hyperedges per refinement

CAND, FIX = H.CAND, H.FIX
rng = random.Random(SEED)


def main():
    pool = IDPool(start_from=1)
    svar = {v: pool.id(('s', v)) for v in CAND}
    outer = Cadical153()
    t0 = time.time()
    for cl in CardEnc.atmost(lits=[svar[v] for v in CAND], bound=MAXSEL,
                             vpool=pool, encoding=EncType.seqcounter).clauses:
        outer.add_clause(cl)
    bank = pickle.load(open(HYP, 'rb')) if os.path.exists(HYP) else []
    seen = 0
    if os.path.exists(BANK):
        with open(BANK) as f:
            for line in f:
                bank.append(json.loads(line))
                seen += 1
    for D in bank:
        outer.add_clause([svar[v] for v in D])
    print(f'frozen {len(FIX)}, candidates {len(CAND)}, bound {MAXSEL}, '
          f'{len(bank)} hyperedges preloaded ({round(time.time()-t0)}s)',
          flush=True)

    it, tot = 0, 0
    while True:
        it += 1
        ts = time.time()
        if not outer.solve():
            print(f'OUTER UNSAT after {len(bank)+it-1} hyperedges: no witness '
                  f'with <= {MAXSEL} free vertices exists over this pool '
                  f'({round(time.time()-t0)}s)', flush=True)
            return
        model = set(outer.get_model())
        sel = [v for v in CAND if svar[v] in model]
        tsolve = time.time() - ts
        col = H.kissat_color(FIX + sel, f'c4_{SEED}')
        if col is None:
            S = sorted(set(sel) | set(FIX))
            pickle.dump(S, open(f'cegar4_hit_{SEED}.pkl', 'wb'))
            print(f'*** WITNESS {len(S)} vertices ({len(FIX)} frozen + '
                  f'{len(sel)} free)', flush=True)
            return
        selset = set(sel)
        movable = [v for v in CAND if v not in selset]
        news = []
        for _ in range(PERIT):
            D = H.tabu_hyperedge(col, movable, rng)
            if D:
                news.append(sorted(D))
        if not news:
            continue
        with open(BANK, 'a') as f:      # share progress across seeds/restarts
            for D in news:
                f.write(json.dumps(D) + '\n')
        with open(BANK) as f:           # own clauses + any from sibling seeds
            fresh = [json.loads(line) for line in f][seen:]
        for D in fresh:
            outer.add_clause([svar[v] for v in D])
        seen += len(fresh)
        tot += sum(len(D) for D in news) // len(news)
        if it % 5 == 0 or it < 5:
            print(f'  it{it}: |sel|={len(sel)} hyperedge={len(D)} '
                  f'(avg {tot//it}) solve={tsolve:.1f}s '
                  f'total={round(time.time()-t0)}s', flush=True)


if __name__ == '__main__':
    main()

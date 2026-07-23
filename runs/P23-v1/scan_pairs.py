"""Double substitutions: for pairs (w_i,v_i),(w_j,v_j) of known single swaps,
test B = G509 - {v_i,v_j} + {w_i,w_j}. If UNSAT, exhaustively test every
single-vertex deletion B - u; any UNSAT => a 508-vertex 5-chromatic UDG.
Usage: POOL=pool_mink.pkl scan_pairs.py <nworkers> <worker_id>
"""
import itertools, pickle, random, sys
from coremin import solve_core

PAIRS = [(47264, 413), (620, 347), (1674, 300), (2731, 220),
         (47058, 415), (1666, 301), (2472, 217), (3452, 356)]
g509 = set(range(509))

def unsat(S, tag):
    st, keep = solve_core(S, seed=random.randrange(10**6), timeout=1800, tag=tag)
    return (st == 'UNSAT'), keep

if __name__ == '__main__':
    nw, wid = int(sys.argv[1]), int(sys.argv[2])
    tag = f'pr{wid}'
    combos = list(itertools.combinations(range(len(PAIRS)), 2))
    for ci, (i, j) in enumerate(combos):
        (wi, vi), (wj, vj) = PAIRS[i], PAIRS[j]
        if vi == vj or wi == wj:
            continue
        B = (g509 - {vi, vj}) | {wi, wj}
        if ci % nw == wid:
            ok, _ = unsat(B, tag)
            print(f'combo {ci} ({wi},{vi})+({wj},{vj}): {"UNSAT" if ok else "SAT"}',
                  flush=True)
            pickle.dump(ok, open(f'pair_{ci}.pkl', 'wb'))
    # barrier-free: reload pair results in phase 2 via files
    import glob, os, time
    while len(glob.glob('pair_*.pkl')) < len(combos):
        time.sleep(5)
    good = [ci for ci in range(len(combos))
            if pickle.load(open(f'pair_{ci}.pkl', 'rb'))]
    if wid == 0:
        print('valid double-substituted records:', good, flush=True)
    for ci in good:
        i, j = combos[ci]
        (wi, vi), (wj, vj) = PAIRS[i], PAIRS[j]
        B = (g509 - {vi, vj}) | {wi, wj}
        us = sorted(B)
        for k, u in enumerate(us):
            if (ci * 1000 + k) % nw != wid:
                continue
            ok, keep = unsat(B - {u}, tag)
            if ok:
                S = sorted(keep if keep else (B - {u}))
                print(f'!!! 508 FOUND: combo {ci} minus u={u} -> {len(S)}', flush=True)
                pickle.dump(S, open(f'FOUND508pair_c{ci}_u{u}.pkl', 'wb'))
        print(f'worker{wid}: done combo {ci}', flush=True)
    print(f'worker{wid}: ALL DONE', flush=True)

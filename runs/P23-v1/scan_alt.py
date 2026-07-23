"""For each alternative record A = G509 - v + w (found by scan508m), test every
single-vertex deletion A - u for non-4-colorability. Any UNSAT => 508-vertex graph.
Usage: POOL=pool_mink.pkl scan_alt.py <nworkers> <worker_id>
Pairs are hardcoded from the scan508m logs.
"""
import pickle, random, sys
from coremin import solve_core

PAIRS = [(47264, 413), (620, 347), (1674, 300), (2731, 220),
         (47058, 415), (1666, 301), (2472, 217), (3452, 356)]
g509 = set(range(509))

def unsat(S, tag):
    st, keep = solve_core(S, seed=random.randrange(10**6), timeout=1800, tag=tag)
    return (st == 'UNSAT'), keep

if __name__ == '__main__':
    nw, wid = int(sys.argv[1]), int(sys.argv[2])
    tag = f'alt{wid}'
    for pi, (w, v) in enumerate(PAIRS):
        A = (g509 - {v}) | {w}
        us = sorted(A)
        for k, u in enumerate(us):
            if (pi * 1000 + k) % nw != wid:
                continue
            ok, keep = unsat(A - {u}, tag)
            if ok:
                S = sorted(keep if keep else (A - {u}))
                print(f'!!! 508 FOUND: alt(w={w},v={v}) minus u={u} -> {len(S)}', flush=True)
                pickle.dump(S, open(f'FOUND508alt_w{w}_u{u}.pkl', 'wb'))
        print(f'worker{wid}: done alt {pi} (w={w},v={v})', flush=True)

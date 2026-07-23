"""For each candidate w: S = g509 + w, then greedy destructive deletion with core jumps.
If a run bottoms out < 509 with UNSAT (DRAT-cored), we have a new record. Save it.
Usage: addcore.py <nworkers> <worker_id>
"""
import pickle, random, sys, os
from coremin import solve_core, allpts, adj  # POOL=pool2.pkl

g509 = set(pickle.load(open('g509_pool2_idx.pkl', 'rb')))
NALL = len(allpts)

def minimize(S, rnd, tag, floor=509):
    S = set(S)
    improved = True
    while improved:
        improved = False
        order = sorted(S)
        rnd.shuffle(order)
        for v in order:
            if v not in S or len(S) <= 4:
                continue
            st, keep = solve_core(S - {v}, seed=rnd.randrange(10**6), timeout=900, tag=tag)
            if st == 'UNSAT':
                S = keep
                improved = True
    return S

if __name__ == '__main__':
    nw, wid = int(sys.argv[1]), int(sys.argv[2])
    rnd = random.Random(1000 + wid)
    cands = sorted(w for w in range(NALL) if w not in g509 and len(adj[w] & g509) >= 5)
    tag = f'ac_{wid}'
    for k, w in enumerate(cands):
        if k % nw != wid:
            continue
        S = minimize(g509 | {w}, rnd, tag)
        n = len(S)
        if n < 509:
            print(f'!!! w={w} -> {n} < 509 NEW RECORD', flush=True)
            pickle.dump(sorted(S), open(f'RECORD_{n}_w{w}.pkl', 'wb'))
        elif k % 5 == 0:
            print(f'w={w} -> {n}', flush=True)

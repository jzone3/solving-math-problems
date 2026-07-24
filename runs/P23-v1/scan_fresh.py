"""Swap scan over the fresh (apex/union) candidates in the combined pool.
Usage: POOL=pool_comb.pkl scan_fresh.py <nworkers> <worker_id> [mindeg]
"""
import pickle, random, sys
from coremin import solve_core, allpts, adj
from field import to_float

g509 = set(range(509))
fresh = pickle.load(open('fresh_idx.pkl', 'rb'))
fl = [(to_float(p[0]), to_float(p[1])) for p in allpts]

def unsat(S, tag):
    st, keep = solve_core(S, seed=random.randrange(10**6), timeout=1800, tag=tag)
    return st == 'UNSAT'

if __name__ == '__main__':
    nw, wid = int(sys.argv[1]), int(sys.argv[2])
    mindeg = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    cands = [w for w in fresh if len(adj[w] & g509) >= mindeg]
    cands.sort(key=lambda w: -len(adj[w] & g509))
    print(f'worker {wid}/{nw}: {len(cands)} fresh candidates (mindeg {mindeg})', flush=True)
    tag = f'fr{wid}'
    for k, w in enumerate(cands):
        if k % nw != wid:
            continue
        xw, yw = fl[w]
        near = [v for v in g509
                if (xw - fl[v][0]) ** 2 + (yw - fl[v][1]) ** 2 <= 2.05 ** 2]
        D = []
        for v in near:
            if unsat((g509 - {v}) | {w}, tag):
                D.append(v)
                print(f'w={w} swap-deletable v={v}', flush=True)
        for i in range(len(D)):
            for j in range(i + 1, len(D)):
                if unsat((g509 - {D[i], D[j]}) | {w}, tag):
                    S = sorted((g509 - {D[i], D[j]}) | {w})
                    print(f'!!! 508 FOUND: w={w} del {D[i]},{D[j]}', flush=True)
                    pickle.dump(S, open(f'FOUND508fresh_w{w}.pkl', 'wb'))
        print(f'progress {k}/{len(cands)} w={w} |D|={len(D)}', flush=True)
    print(f'worker{wid}: ALL DONE', flush=True)

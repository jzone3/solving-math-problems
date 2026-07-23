"""508-swap scan over the Minkowski pool (POOL=pool_mink.pkl).
Record vertices are indices 0..508. Usage: scan508m.py <nworkers> <worker_id> [mindeg]
"""
import pickle, random, sys
from coremin import solve_core, allpts, adj
from field import to_float

g509 = set(range(509))
NALL = len(allpts)
fl = [(to_float(p[0]), to_float(p[1])) for p in allpts]

def near(w, r=2.05):
    xw, yw = fl[w]
    return [v for v in g509
            if (xw - fl[v][0]) ** 2 + (yw - fl[v][1]) ** 2 <= r * r]

def unsat(S, tag):
    st, keep = solve_core(S, seed=random.randrange(10**6), timeout=1800, tag=tag)
    return st == 'UNSAT'

if __name__ == '__main__':
    nw, wid = int(sys.argv[1]), int(sys.argv[2])
    mindeg = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    cands = [w for w in range(509, NALL) if len(adj[w] & g509) >= mindeg]
    cands.sort(key=lambda w: -len(adj[w] & g509))
    print(f'worker {wid}/{nw}: {len(cands)} candidates (mindeg {mindeg})', flush=True)
    tag = f'm508_{wid}'
    for k, w in enumerate(cands):
        if k % nw != wid:
            continue
        D = []
        for v in near(w):
            if unsat((g509 - {v}) | {w}, tag):
                D.append(v)
                print(f'w={w} swap-deletable v={v}', flush=True)
        for i in range(len(D)):
            for j in range(i + 1, len(D)):
                if unsat((g509 - {D[i], D[j]}) | {w}, tag):
                    S = sorted((g509 - {D[i], D[j]}) | {w})
                    print(f'!!! 508 FOUND: w={w} del {D[i]},{D[j]}', flush=True)
                    pickle.dump(S, open(f'FOUND508m_w{w}.pkl', 'wb'))
        print(f'progress {k}/{len(cands)} w={w} |D|={len(D)}', flush=True)

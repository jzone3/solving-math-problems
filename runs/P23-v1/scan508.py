"""For each enriched-pool candidate w: test swaps G509 - v + w (v within radius 2.05 of w).
Collect deletables D_w; for |D_w|>=2 test pair deletions -> a 508-vertex UNSAT graph.
Usage: scan508.py <nworkers> <worker_id>
"""
import pickle, random, sys, time, math
from coremin import solve_core, allpts, adj  # POOL=pool2.pkl required
from field import to_float

g509 = set(pickle.load(open('g509_pool2_idx.pkl', 'rb')))
NALL = len(allpts)
fl = [(to_float(p[0]), to_float(p[1])) for p in allpts]

def near(w, r=2.05):
    xw, yw = fl[w]
    out = []
    for v in g509:
        dx, dy = xw - fl[v][0], yw - fl[v][1]
        if dx*dx + dy*dy <= r*r:
            out.append(v)
    return out

def unsat(S, tag):
    st, keep = solve_core(S, seed=random.randrange(10**6), timeout=1800, tag=tag)
    return st == 'UNSAT'

if __name__ == '__main__':
    nw, wid = int(sys.argv[1]), int(sys.argv[2])
    cands = [w for w in range(NALL) if w not in g509 and len(adj[w] & g509) >= 4]
    cands.sort()
    tag = f's508_{wid}'
    for k, w in enumerate(cands):
        if k % nw != wid:
            continue
        D = []
        for v in near(w):
            S = (g509 - {v}) | {w}
            if unsat(S, tag):
                D.append(v)
                print(f'w={w} swap-deletable v={v}', flush=True)
        if len(D) >= 2:
            for i in range(len(D)):
                for j in range(i+1, len(D)):
                    S = (g509 - {D[i], D[j]}) | {w}
                    if unsat(S, tag):
                        print(f'!!! 508 FOUND: w={w} del {D[i]},{D[j]}', flush=True)
                        pickle.dump(sorted(S), open(f'FOUND508_w{w}.pkl', 'wb'))
        if k % (nw*20) == wid:
            print(f'progress {k}/{len(cands)}', flush=True)

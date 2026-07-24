"""Around the triple-substituted record gmax.pkl: (a) full single-deletion
criticality scan; (b) swap scan 'gmax - v + w' for pool w with >=6 neighbours
in gmax, plus pair deletions among the deletables.
Usage: POOL=pool_mink.pkl scan_gmax.py <nworkers> <worker_id>
"""
import pickle, random, sys
from coremin import solve_core, adj, NALL
from field import to_float
from coremin import allpts

G = set(pickle.load(open('gmax.pkl', 'rb')))
fl = [(to_float(p[0]), to_float(p[1])) for p in allpts]

def unsat(S, tag):
    st, keep = solve_core(S, seed=random.randrange(10**6), timeout=1800, tag=tag)
    return (st == 'UNSAT'), keep

if __name__ == '__main__':
    nw, wid = int(sys.argv[1]), int(sys.argv[2])
    tag = f'gm{wid}'
    # (a) criticality
    for k, u in enumerate(sorted(G)):
        if k % nw != wid:
            continue
        ok, keep = unsat(G - {u}, tag)
        if ok:
            S = sorted(keep if keep else (G - {u}))
            print(f'!!! 508 FOUND: gmax minus u={u} -> {len(S)}', flush=True)
            pickle.dump(S, open(f'FOUND508gmax_u{u}.pkl', 'wb'))
    print(f'worker{wid}: criticality done', flush=True)
    # (b) swap scan
    cands = [w for w in range(NALL) if w not in G and len(adj[w] & G) >= 6]
    cands.sort(key=lambda w: -len(adj[w] & G))
    print(f'worker{wid}: {len(cands)} swap candidates', flush=True)
    for k, w in enumerate(cands):
        if k % nw != wid:
            continue
        xw, yw = fl[w]
        near = [v for v in G
                if (xw - fl[v][0]) ** 2 + (yw - fl[v][1]) ** 2 <= 2.05 ** 2]
        D = []
        for v in near:
            ok, _ = unsat((G - {v}) | {w}, tag)
            if ok:
                D.append(v)
                print(f'gmax swap-deletable w={w} v={v}', flush=True)
        for i in range(len(D)):
            for j in range(i + 1, len(D)):
                ok, keep = unsat((G - {D[i], D[j]}) | {w}, tag)
                if ok:
                    S = sorted(keep if keep else ((G - {D[i], D[j]}) | {w}))
                    print(f'!!! 508 FOUND: gmax w={w} del {D[i]},{D[j]}', flush=True)
                    pickle.dump(S, open(f'FOUND508gmax_w{w}.pkl', 'wb'))
        print(f'worker{wid}: swap {k}/{len(cands)} w={w} |D|={len(D)}', flush=True)
    print(f'worker{wid}: ALL DONE', flush=True)

"""Apply the paper's simplification to sample candidates from exp3/exp4/exp5:
iteratively remove edges contained in <=1 triangle, and vertices of degree < 8
(valid for K4-free graphs per Bikov-Nenov [5]); report the surviving core.
"""
import random, sys
from alterations import EXPS, N, edge_set
from arrow import triangles_of, has_k4

def simplify(adjset):
    adjset = [set(s) for s in adjset]
    changed = True
    while changed:
        changed = False
        tri_count = {}
        for (i, j, k) in triangles_of(N, adjset):
            for e in ((i, j), (i, k), (j, k)):
                tri_count[e] = tri_count.get(e, 0) + 1
        for i in range(N):
            for j in list(adjset[i]):
                if i < j and tri_count.get((i, j), 0) <= 1:
                    adjset[i].discard(j); adjset[j].discard(i)
                    changed = True
        for i in range(N):
            d = len(adjset[i])
            if 0 < d < 8:
                for j in list(adjset[i]):
                    adjset[j].discard(i)
                adjset[i].clear()
                changed = True
    return adjset

if __name__ == "__main__":
    for name in ("exp3", "exp4", "exp5"):
        fn = EXPS[name]
        for t in range(5):
            rng = random.Random(777000 + t)
            g = fn(rng)
            assert not has_k4(N, g)
            core = simplify(g)
            nv = sum(1 for i in range(N) if core[i])
            ne = len(edge_set(core))
            orig_e = len(edge_set(g))
            print(f"{name}-{t}: edges {orig_e} -> core: {nv} vertices, {ne} edges")

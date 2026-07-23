"""P16 childC — non-equitable constructions: overlays of two near-regular
bipartite graphs on the same vertex set.

Motivation: both bounds are tight exactly on bipartite regular graphs; a
counterexample must live near that manifold but escape the equitable-partition
families already searched. Overlaying two bipartite (near-)regular graphs with
DIFFERENT bipartitions produces graphs that are locally near-regular (small
degree spread, m_i close to d_i) yet typically have no small equitable
partition.

Families screened (float, exact verifier for any hit):
  A. union of a random d1-regular bipartite graph on parts (X,Y) and a random
     d2-regular bipartite graph on a rotated bipartition (overlapping parts),
     n up to 120, many random draws;
  B. same with one of the two layers perturbed (edge deleted / pendant);
  C. circulant-style overlays: vertex set Z_n, layer 1 connects i ~ i+odd
     offsets (bipartite when n even), layer 2 uses a different odd offset set.
"""
import itertools
import math
import random
import sys
import time

import numpy as np

sys.path.insert(0, "..")
import search_common  # noqa: E402


def gaps(A):
    d, m = search_common.degrees_and_m(A)
    mu = search_common.mu(A)
    r44 = search_common.rhs_graph(A, search_common.rhs44_edge)
    r46 = search_common.rhs_graph(A, search_common.rhs46_edge)
    return r44 - mu, r46 - mu


def random_biregular(nX, nY, dX, rng):
    """Random bipartite graph, X-side regular of degree dX (configuration model
    with rejection of multi-edges)."""
    assert nX * dX % nY == 0
    dY = nX * dX // nY
    for _ in range(200):
        stubsY = list(range(nY)) * dY
        rng.shuffle(stubsY)
        edges = set()
        ok = True
        it = iter(stubsY)
        for x in range(nX):
            for _ in range(dX):
                y = next(it)
                if (x, y) in edges:
                    ok = False
                    break
                edges.add((x, y))
            if not ok:
                break
        if ok:
            return edges
    return None


def family_A_B(rng, report):
    best = (math.inf, math.inf, None)
    for trial in range(4000):
        half = rng.choice([6, 8, 10, 12, 16, 20, 24, 30, 40, 50, 60])
        n = 2 * half
        d1 = rng.randint(2, min(8, half - 1))
        d2 = rng.randint(1, min(6, half - 1))
        # layer 1 on bipartition (0..half-1 | half..n-1)
        e1 = random_biregular(half, half, d1, rng)
        if e1 is None:
            continue
        # layer 2 on a rotated bipartition: parts shifted by half//2
        perm = [(i + half // 2) % n for i in range(n)]
        e2 = random_biregular(half, half, d2, rng)
        if e2 is None:
            continue
        A = np.zeros((n, n))
        for (x, y) in e1:
            A[x, half + y] = A[half + y, x] = 1.0
        for (x, y) in e2:
            u, v = perm[x], perm[half + y]
            if u != v:
                A[u, v] = A[v, u] = 1.0
        if A.sum() == 0:
            continue
        deg = A.sum(axis=1)
        if np.any(deg == 0):
            continue
        g44, g46 = gaps(A)
        # B-variant: delete one random edge
        iu, ju = np.nonzero(np.triu(A))
        t = rng.randrange(len(iu))
        A2 = A.copy()
        A2[iu[t], ju[t]] = A2[ju[t], iu[t]] = 0.0
        if np.all(A2.sum(axis=1) > 0):
            h44, h46 = gaps(A2)
            g44, g46 = min(g44, h44), min(g46, h46)
        if g44 < best[0] or g46 < best[1]:
            best = (min(g44, best[0]), min(g46, best[1]), n)
        if g44 < -1e-9 or g46 < -1e-9:
            print(f"CANDIDATE overlayAB n={n} d1={d1} d2={d2} "
                  f"gap44={g44:.3e} gap46={g46:.3e}", flush=True)
            np.save(f"overlay_cand_{trial}.npy", A)
    report("A/B random overlays", best)


def family_C(rng, report):
    best = (math.inf, math.inf, None)
    for n in range(8, 121, 2):
        offs_odd = [o for o in range(1, n // 2 + 1) if o % 2 == 1]
        offs_all = list(range(1, n // 2 + 1))
        for _ in range(60):
            k1 = rng.randint(1, min(3, len(offs_odd)))
            k2 = rng.randint(1, min(3, len(offs_all)))
            o1 = rng.sample(offs_odd, k1)          # bipartite layer
            o2 = rng.sample(offs_all, k2)          # arbitrary layer (may break bipartiteness)
            A = np.zeros((n, n))
            for i in range(n):
                for o in o1 + o2:
                    j = (i + o) % n
                    A[i, j] = A[j, i] = 1.0
            g44, g46 = gaps(A)
            if g44 < best[0] or g46 < best[1]:
                best = (min(g44, best[0]), min(g46, best[1]), (n, o1, o2))
            if g44 < -1e-9 or g46 < -1e-9:
                print(f"CANDIDATE circulant n={n} o1={o1} o2={o2} "
                      f"gap44={g44:.3e} gap46={g46:.3e}", flush=True)
    report("C circulant overlays", best)


if __name__ == "__main__":
    t0 = time.time()
    rng = random.Random(20260723)

    def report(name, best):
        print(f"[{name}] min gap44={best[0]:.6g} min gap46={best[1]:.6g} "
              f"at {best[2]}  ({time.time()-t0:.0f}s)", flush=True)

    family_C(rng, report)
    family_A_B(rng, report)

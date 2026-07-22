"""Probe 3c: literature-guided structured families, n = 13..21.

Rationale (V5): equality cases of Hajos' bound are K_{2k+1} (Hamilton
decomposition) and dense graphs with a dominating vertex. If a counterexample
exists at small n it plausibly lives near these tight cases: dense Eulerian
graphs obtained from K_n by deleting even-regular subgraphs (2-factors and
unions thereof), Eulerian complete multipartite graphs, and blowups of cycles
and triangles (triangle-dense, bounded-circumference flavour).
"""
import itertools
import random
import sys
from hajos import hajos_ok, is_eulerian, rlc_decompose

def check(name, n, edges, time_limit=900):
    bound = (n - 1) // 2
    if not is_eulerian(n, edges):
        return
    h = rlc_decompose(n, edges, tries=400)
    if h is not None and len(h) <= bound:
        return
    ok, cyc = hajos_ok(n, edges, time_limit=time_limit)
    print(f"HARD {name}: n={n} m={len(edges)} cpSAT={ok}", flush=True)
    if ok is False:
        print(f"*** COUNTEREXAMPLE {name} n={n} edges={edges}", flush=True)
        with open(f"counterexample_{name}.txt", "w") as f:
            f.write(repr((n, edges)))

def kn_minus_2factors(n, rng, samples=200, layers=(1, 2)):
    """K_n (n odd) minus a random union of L edge-disjoint 2-factors."""
    for L in layers:
        for s in range(samples):
            edges = set((u, v) for u in range(n) for v in range(u + 1, n))
            ok = True
            for _ in range(L):
                # random 2-factor: random Hamilton cycle on a random permutation
                p = list(range(n))
                rng.shuffle(p)
                fac = [(min(p[i], p[(i + 1) % n]), max(p[i], p[(i + 1) % n])) for i in range(n)]
                if any(e not in edges for e in fac):
                    ok = False
                    break
                edges -= set(fac)
            if ok:
                yield f"K{n}-minus-{L}x2factor-s{s}", n, tuple(sorted(edges))

def multipartite(n_parts_list):
    for parts in n_parts_list:
        n = sum(parts)
        vid = []
        for i, p in enumerate(parts):
            vid += [i] * p
        edges = tuple((u, v) for u in range(n) for v in range(u + 1, n) if vid[u] != vid[v])
        yield f"K_{'_'.join(map(str, parts))}", n, edges

def blowup_cycle(m, r):
    """C_m[empty_r]: cycle of m clusters of r independent vertices."""
    n = m * r
    edges = []
    for i in range(m):
        for a in range(r):
            for b in range(r):
                u, v = i * r + a, ((i + 1) % m) * r + b
                edges.append((min(u, v), max(u, v)))
    return f"C{m}[E{r}]", n, tuple(sorted(set(edges)))

def triangle_blowup(r, m):
    """m triangles sharing a common vertex-set structure: K_{r,r,r} handled by
    multipartite; here: chain of K5's glued on single vertices is not biconnected,
    so instead: 'theta of cliques' — two hub vertices joined by m internally
    disjoint paths of K4s. Simplified: hubs a,b; m groups of 2 vertices each,
    each group g={x,y}: edges ax,ay,bx,by,xy? gives odd hub degree if m odd."""
    return None

def main():
    rng = random.Random(42)
    # Eulerian complete multipartite: all degrees even <=> n - part_size even for all parts
    parts_list = []
    for n in range(13, 21):
        for k in range(2, 7):
            for parts in itertools.combinations_with_replacement(range(1, n), k):
                if sum(parts) != n:
                    continue
                if all((n - p) % 2 == 0 for p in parts):
                    parts_list.append(parts)
    parts_list = list(set(parts_list))
    print(f"{len(parts_list)} Eulerian multipartite partitions", flush=True)
    for name, n, edges in multipartite(parts_list):
        check(name, n, edges)
    print("multipartite done", flush=True)
    for m, r in [(3, 5), (5, 3), (3, 6), (4, 4), (5, 4), (6, 3), (7, 3), (4, 5), (3, 7)]:
        name, n, edges = blowup_cycle(m, r)
        check(name, n, edges)
    print("blowups done", flush=True)
    for n in (13, 15, 17):
        for name, nn, edges in kn_minus_2factors(n, rng, samples=150, layers=(1, 2, 3)):
            check(name, nn, edges)
        print(f"K{n} minus 2-factors done", flush=True)

if __name__ == "__main__":
    main()

"""Find nearly cubic uniquely hamiltonian graphs (2 vertices of degree 4, rest degree 3)
by simulated annealing over degree-preserving 2-opt edge swaps.
These exist for all even n >= 18 (Goedgebeur-Meersman-Zamfirescu 2020, Thm 3.2).
They are the V2 building blocks: two copies + a perfect matching on the degree-3
vertices yields a 4-regular graph.

Usage: python3 search_nearly_cubic.py n count [seed] -> appends graphs to nc_<n>.txt
"""
import random, sys, math
from hcutil import hc_count

def random_graph_with_degseq(degs, rng):
    """Configuration model, retry until simple."""
    n = len(degs)
    while True:
        stubs = [v for v in range(n) for _ in range(degs[v])]
        rng.shuffle(stubs)
        edges = set()
        ok = True
        for i in range(0, len(stubs), 2):
            u, v = stubs[i], stubs[i + 1]
            if u == v or (min(u, v), max(u, v)) in edges:
                ok = False
                break
            edges.add((min(u, v), max(u, v)))
        if ok:
            return edges

def connected(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    seen = [False] * n
    stack = [0]; seen[0] = True; c = 1
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if not seen[w]:
                seen[w] = True; c += 1; stack.append(w)
    return c == n

def objective(n, edges, cap=60):
    if not connected(n, edges):
        return 10000
    c = hc_count(n, list(edges), cutoff=cap)
    if c == 0:
        return 5000
    return c - 1  # 0 iff uniquely hamiltonian

def two_opt(edges, rng):
    """Swap (a,b),(c,d) -> (a,c),(b,d) or (a,d),(b,c), preserving degrees, keeping simple."""
    el = list(edges)
    for _ in range(200):
        (a, b), (c, d) = rng.sample(el, 2)
        if rng.random() < 0.5:
            p, q = (a, c), (b, d)
        else:
            p, q = (a, d), (b, c)
        p = (min(p), max(p)); q = (min(q), max(q))
        if p[0] == p[1] or q[0] == q[1] or p in edges or q in edges or p == q:
            continue
        ne = set(edges); ne.discard((min(a, b), max(a, b))); ne.discard((min(c, d), max(c, d)))
        ne.add(p); ne.add(q)
        if len(ne) == len(edges):
            return ne
    return None

def anneal(n, rng, iters=200000):
    degs = [4, 4] + [3] * (n - 2)
    edges = random_graph_with_degseq(degs, rng)
    cur = objective(n, edges)
    T0, T1 = 3.0, 0.05
    for it in range(iters):
        if cur == 0:
            return edges
        T = T0 * (T1 / T0) ** (it / iters)
        ne = two_opt(edges, rng)
        if ne is None:
            continue
        no = objective(n, ne)
        if no <= cur or rng.random() < math.exp((cur - no) / T):
            edges, cur = ne, no
    return None

if __name__ == "__main__":
    n = int(sys.argv[1]); want = int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    rng = random.Random(seed)
    found = 0; attempt = 0
    out = open(f"nc_{n}.txt", "a")
    while found < want:
        attempt += 1
        res = anneal(n, rng)
        if res is not None:
            assert hc_count(n, list(res)) == 1
            out.write(repr(sorted(res)) + "\n"); out.flush()
            found += 1
            print(f"found #{found} after {attempt} anneals", flush=True)

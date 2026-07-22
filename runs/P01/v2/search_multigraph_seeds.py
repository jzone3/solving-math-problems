"""V2 attack 2 ingredient: find small 4-regular uniquely hamiltonian MULTIGRAPHS
(Fleischner 1994 proved they exist). Annealed search over 4-regular multigraphs
(loopless, parallel edges allowed, multiplicity <= 2) using degree-preserving
2-opt swaps. Note: in a 1H multigraph the unique HC uses no parallel-pair edge
(else swapping copies gives a 2nd HC), so double edges are always "chords".

Usage: python3 search_multigraph_seeds.py n want seed -> appends to mg_<n>.txt
"""
import random, sys, math
from collections import Counter
from hcutil import hc_count

def rand_multigraph(n, rng):
    while True:
        stubs = [v for v in range(n) for _ in range(4)]
        rng.shuffle(stubs)
        edges = []
        mult = Counter()
        ok = True
        for i in range(0, len(stubs), 2):
            u, v = stubs[i], stubs[i + 1]
            if u == v:
                ok = False; break
            e = (min(u, v), max(u, v))
            mult[e] += 1
            if mult[e] > 2:
                ok = False; break
            edges.append(e)
        if ok:
            return edges

def connected(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    seen = [False] * n
    st = [0]; seen[0] = True; c = 1
    while st:
        u = st.pop()
        for w in adj[u]:
            if not seen[w]:
                seen[w] = True; c += 1; st.append(w)
    return c == n

def obj(n, edges, cap=100):
    if not connected(n, edges):
        return 10000
    c = hc_count(n, edges, cutoff=cap)
    return 5000 if c == 0 else c - 1

def swap(edges, rng):
    for _ in range(100):
        i, j = rng.sample(range(len(edges)), 2)
        (a, b), (c, d) = edges[i], edges[j]
        if rng.random() < 0.5:
            p, q = (a, c), (b, d)
        else:
            p, q = (a, d), (b, c)
        if p[0] == p[1] or q[0] == q[1]:
            continue
        ne = edges[:i] + edges[i+1:j] + edges[j+1:] if i < j else None
        ne = [e for k, e in enumerate(edges) if k != i and k != j]
        ne.append((min(p), max(p))); ne.append((min(q), max(q)))
        m = Counter(ne)
        if max(m.values()) <= 2:
            return ne
    return None

def anneal(n, rng, iters=60000):
    edges = rand_multigraph(n, rng)
    cur = obj(n, edges)
    T0, T1 = 3.0, 0.05
    for it in range(iters):
        if cur == 0:
            return edges
        ne = swap(edges, rng)
        if ne is None:
            continue
        no = obj(n, ne)
        T = T0 * (T1 / T0) ** (it / iters)
        if no <= cur or rng.random() < math.exp((cur - no) / T):
            edges, cur = ne, no
    return None

if __name__ == "__main__":
    n, want, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    rng = random.Random(seed)
    found = 0; att = 0
    with open(f"mg_{n}.txt", "a") as out:
        while found < want:
            att += 1
            res = anneal(n, rng)
            if res is not None:
                assert hc_count(n, res) == 1
                out.write(repr(sorted(res)) + "\n"); out.flush()
                found += 1
                print(f"mg n={n} found #{found} after {att} anneals", flush=True)

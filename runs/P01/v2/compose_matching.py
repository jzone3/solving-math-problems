"""V2 structured construction, attack 1: matching completions of nearly cubic
uniquely hamiltonian (1H) seeds to 4-regular graphs.

Two modes:
  self <nc_file>   : one seed graph G (n>=22 so we are past the exhausted n<=21
                     frontier); add a perfect matching on its degree-3 vertices
                     (avoiding existing edges) -> 4-regular, n vertices.
  pair <nc_file>   : two copies of seeds G1,G2; add a perfect matching between
                     their degree-3 vertex sets -> 4-regular, n1+n2 vertices.

Anneal over matchings; objective = (capped) Hamiltonian cycle count, target 1.
Logs best-ever results to compose_results.txt.
"""
import random, sys, math, itertools
from hcutil import hc_count

CAP = int(__import__("os").environ.get("CAP", "400"))

def load(fname):
    return [eval(line) for line in open(fname) if line.strip()]

def degs(n, edges):
    d = [0] * n
    for u, v in edges:
        d[u] += 1; d[v] += 1
    return d

def obj(n, edges):
    c = hc_count(n, edges, cutoff=CAP)
    return 5000 if c == 0 else c - 1

def anneal_matching(n, base_edges, left, right, rng, iters=4000, forbidden=frozenset()):
    """Perfect matching between lists left,right (equal length; for self-mode pass
    a single list split later). Moves: swap two right-endpoints."""
    k = len(left)
    perm = list(range(k))
    rng.shuffle(perm)
    def medges(p):
        return [(left[i], right[p[i]]) for i in range(k)]
    def valid(p):
        return all((min(u, v), max(u, v)) not in forbidden and u != v for u, v in medges(p))
    while not valid(perm):
        rng.shuffle(perm)
    cur = obj(n, base_edges + medges(perm))
    best = cur; best_p = perm[:]
    T0, T1 = 2.0, 0.05
    for it in range(iters):
        if cur == 0:
            return 0, perm
        i, j = rng.sample(range(k), 2)
        perm[i], perm[j] = perm[j], perm[i]
        if not valid(perm):
            perm[i], perm[j] = perm[j], perm[i]; continue
        no = obj(n, base_edges + medges(perm))
        T = T0 * (T1 / T0) ** (it / iters)
        if no <= cur or rng.random() < math.exp((cur - no) / T):
            cur = no
            if cur < best:
                best, best_p = cur, perm[:]
        else:
            perm[i], perm[j] = perm[j], perm[i]
    return best, best_p

def self_mode(fname, rng, restarts):
    graphs = load(fname)
    results = []
    for gi, edges in enumerate(graphs):
        n = max(max(e) for e in edges) + 1
        d = degs(n, edges)
        deg3 = [v for v in range(n) if d[v] == 3]
        assert len(deg3) % 2 == 0
        half = len(deg3) // 2
        forbidden = frozenset((min(u, v), max(u, v)) for u, v in edges)
        for r in range(restarts):
            rng.shuffle(deg3)
            left, right = deg3[:half], deg3[half:]
            best, perm = anneal_matching(n, list(edges), left, right, rng, forbidden=forbidden)
            m = [(left[i], right[perm[i]]) for i in range(half)]
            results.append((best, gi, r, m))
            log(f"self {fname} g{gi} r{r}: best={best+1} HCs (n={n})", best, list(edges) + m, n)
            if best == 0:
                return
    results.sort()
    print("top:", results[:3])

def pair_mode(fname, rng, restarts):
    graphs = load(fname)
    for gi, gj in itertools.combinations_with_replacement(range(len(graphs)), 2):
        e1 = graphs[gi]; e2 = graphs[gj]
        n1 = max(max(e) for e in e1) + 1
        n2 = max(max(e) for e in e2) + 1
        d1, d2 = degs(n1, e1), degs(n2, e2)
        left = [v for v in range(n1) if d1[v] == 3]
        right = [v + n1 for v in range(n2) if d2[v] == 3]
        base = list(e1) + [(u + n1, v + n1) for u, v in e2]
        n = n1 + n2
        for r in range(restarts):
            best, perm = anneal_matching(n, base, left, right, rng)
            m = [(left[i], right[perm[i]]) for i in range(len(left))]
            log(f"pair {fname} g{gi}+g{gj} r{r}: best={best+1} HCs (n={n})", best, base + m, n)
            if best == 0:
                return

def log(msg, best, edges, n):
    print(msg, flush=True)
    with open("compose_results.txt", "a") as f:
        f.write(msg + "\n")
        if best <= 3:
            f.write("EDGES " + repr(sorted(edges)) + "\n")
    if best == 0:
        with open("WITNESS.txt", "a") as f:
            f.write(f"n={n} edges={sorted(edges)}\n")
        print("!!! WITNESS FOUND !!!", flush=True)

if __name__ == "__main__":
    mode, fname = sys.argv[1], sys.argv[2]
    restarts = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    rng = random.Random(seed)
    (self_mode if mode == "self" else pair_mode)(fname, rng, restarts)

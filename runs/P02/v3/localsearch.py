"""LP-duality-guided local search (V3) for counterexamples at larger n,
targeting TWIN-FREE and/or 4-CHROMATIC maximal triangle-free graphs with
delta = n/3 whose multiplication system is infeasible (m* <= 0).

Search: simulated annealing over maximal triangle-free graphs.
Move: delete a random edge, re-maximalize with random addable edges.
Score (minimize): m*_LP (float, scipy HiGHS) + penalty * total degree deficiency
                  (sum over v of max(0, ceil(n/3) - deg(v))).
Candidates with m* < tol and no deficiency are exactly re-verified with the
Fraction simplex in p02lib before being reported.

Usage: python3 localsearch.py <n> <iters> <seed> [--require-chi4]
"""
import sys, os, random, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.optimize import linprog
from p02lib import (parse_graph6, to_graph6, is_triangle_free, is_maximal_tf,
                    degrees, exact_mstar)

def mstar_float(n, adj):
    A = np.zeros((n, n))
    for v in range(n):
        for u in range(n):
            if (adj[v] >> u) & 1:
                A[v, u] = 1.0
    c = np.zeros(n + 1); c[n] = -1.0
    Aub = np.hstack([-np.eye(n), np.ones((n, 1))])
    Aeq = np.hstack([A, np.zeros((n, 1))])
    r = linprog(c, A_ub=Aub, b_ub=np.zeros(n), A_eq=Aeq, b_eq=np.ones(n),
                bounds=[(None, None)] * (n + 1), method='highs')
    if not r.success:
        return -1.0  # Ax=1 unsolvable: strongly infeasible
    return -r.fun

def maximalize(n, adj, rng):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)
             if not (adj[u] >> v) & 1]
    rng.shuffle(pairs)
    changed = True
    while changed:
        changed = False
        for u, v in pairs:
            if not (adj[u] >> v) & 1 and not (adj[u] & adj[v]):
                adj[u] |= 1 << v; adj[v] |= 1 << u
                changed = True
    return adj

def random_mtf(n, rng):
    adj = [0] * n
    # seed with a random C5 blowup-ish sprinkle then maximalize
    for _ in range(n):
        u, v = rng.sample(range(n), 2)
        if not (adj[u] & adj[v]) and not (adj[u] >> v) & 1:
            adj[u] |= 1 << v; adj[v] |= 1 << u
    return maximalize(n, adj, rng)

def kcolorable(n, adj, k):
    col = [-1] * n
    order = sorted(range(n), key=lambda v: -bin(adj[v]).count('1'))
    def bt(i):
        if i == n:
            return True
        v = order[i]
        used = {col[u] for u in range(n) if (adj[v] >> u) & 1 and col[u] >= 0}
        for c in range(k):
            if c not in used:
                col[v] = c
                if bt(i + 1):
                    return True
        col[v] = -1
        return False
    return bt(0)

def score(n, adj, dmin, chi4_bonus):
    ms = mstar_float(n, adj)
    defic = sum(max(0, dmin - d) for d in degrees(n, adj))
    s = ms + 1.0 * defic
    if chi4_bonus:
        if kcolorable(n, adj, 3):
            s += 0.5
        twins = sum(1 for a in range(n) for b in range(a + 1, n)
                    if adj[a] == adj[b])
        s += 0.15 * twins
    return s, ms, defic

def main():
    n = int(sys.argv[1]); iters = int(sys.argv[2]); seed = int(sys.argv[3])
    require_chi4 = '--require-chi4' in sys.argv
    dmin = (n + 2) // 3
    rng = random.Random(seed)
    adj = random_mtf(n, rng)
    cur, _, _ = score(n, adj, dmin, require_chi4)
    best = cur
    seen = set()
    T0 = 0.3
    for it in range(iters):
        T = T0 * (1 - it / iters) + 1e-3
        edges = [(u, v) for u in range(n) for v in range(u + 1, n)
                 if (adj[u] >> v) & 1]
        u, v = rng.choice(edges)
        new = adj[:]
        new[u] &= ~(1 << v); new[v] &= ~(1 << u)
        # occasionally delete a second edge for bigger jumps
        if rng.random() < 0.3:
            e2 = rng.choice([(a, b) for a in range(n) for b in range(a + 1, n)
                             if (new[a] >> b) & 1])
            new[e2[0]] &= ~(1 << e2[1]); new[e2[1]] &= ~(1 << e2[0])
        new = maximalize(n, new, rng)
        s, ms, defic = score(n, new, dmin, require_chi4)
        if s <= cur or rng.random() < math.exp((cur - s) / T):
            adj, cur = new, s
        if defic == 0 and ms < 1e-9:
            g6 = to_graph6(n, adj)
            if g6 in seen:
                continue
            seen.add(g6)
            st, ems = exact_mstar(n, adj)
            if (st == 'infeasible' or ems <= 0) and is_maximal_tf(n, adj) \
                    and is_triangle_free(n, adj):
                tw = not any(adj[a] == adj[b] for a in range(n)
                             for b in range(a + 1, n))
                c4 = not kcolorable(n, adj, 3)
                print(f'CEX {g6} twin_free={tw} chi4={c4}', flush=True)
        if cur < best:
            best = cur
            print(f'it={it} best={best:.4f}', flush=True)
    print('DONE', flush=True)

if __name__ == '__main__':
    main()

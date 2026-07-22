"""P06 V2: annealed edge-flip search maximizing dev(Laplacian) - Randic.

KEY FACT (machine-checked in explore2.py): trace(L^2) = sum(d_i^2) + 2m, so
  dev(L)^2 = (sum d^2 + 2m)/n - (2m/n)^2
depends ONLY on the degree sequence. So the score
  f(G) = dev(L) - R(G),  R(G) = sum_{uv in E} 1/sqrt(d_u d_v)
is exactly computable in O(1)-ish incrementally per edge flip (no eigensolve).

Conjecture 129 (Graffiti / WoW): f(G) <= 0 for all graphs. We anneal to maximize f.
"""
import math
import random
import sys
import time


class State:
    def __init__(self, n, edges):
        self.n = n
        self.adj = [set() for _ in range(n)]
        for u, v in edges:
            self.adj[u].add(v)
            self.adj[v].add(u)
        self.recompute()

    def recompute(self):
        self.d = [len(a) for a in self.adj]
        self.m = sum(self.d) // 2
        self.sumd2 = sum(x * x for x in self.d)
        self.R = 0.0
        for u in range(self.n):
            for v in self.adj[u]:
                if v > u:
                    self.R += 1.0 / math.sqrt(self.d[u] * self.d[v])

    def score(self):
        n = self.n
        var = (self.sumd2 + 2 * self.m) / n - (2 * self.m / n) ** 2
        if var < 0:
            var = 0.0
        return math.sqrt(var) - self.R

    def flip_delta(self, u, v):
        """score delta if edge (u,v) flipped; returns (delta, apply_fn)."""
        adding = v not in self.adj[u]
        du, dv = self.d[u], self.d[v]
        if adding:
            ndu, ndv = du + 1, dv + 1
            dm = 1
        else:
            ndu, ndv = du - 1, dv - 1
            dm = -1
        # Randic change: edges incident to u (excluding v) get d_u -> ndu, same for v
        dR = 0.0
        for w in self.adj[u]:
            if w == v:
                continue
            dR += 1.0 / math.sqrt(ndu * self.d[w]) - 1.0 / math.sqrt(du * self.d[w])
        for w in self.adj[v]:
            if w == u:
                continue
            dR += 1.0 / math.sqrt(ndv * self.d[w]) - 1.0 / math.sqrt(dv * self.d[w])
        if adding:
            dR += 1.0 / math.sqrt(ndu * ndv)
        else:
            dR -= 1.0 / math.sqrt(du * dv)
        n = self.n
        nm = self.m + dm
        nsumd2 = self.sumd2 - du * du - dv * dv + ndu * ndu + ndv * ndv
        nvar = (nsumd2 + 2 * nm) / n - (2 * nm / n) ** 2
        if nvar < 0:
            nvar = 0.0
        new_score = math.sqrt(nvar) - (self.R + dR)
        delta = new_score - self.score()

        def apply():
            if adding:
                self.adj[u].add(v)
                self.adj[v].add(u)
            else:
                self.adj[u].discard(v)
                self.adj[v].discard(u)
            self.d[u], self.d[v] = ndu, ndv
            self.m, self.sumd2 = nm, nsumd2
            self.R += dR

        return delta, apply


def star_edges(n):
    return [(0, i) for i in range(1, n)]


def clique_iso_edges(n):
    """K_m + k iso with m chosen so k ~= m-2 (equality family)."""
    m = (n + 2) // 2
    return [(i, j) for i in range(m) for j in range(i + 1, m)]


def anneal(n, iters, T0=0.5, Tend=1e-4, seed=None, start_edges=None):
    rng = random.Random(seed)
    st = State(n, start_edges if start_edges is not None else star_edges(n))
    best = st.score()
    best_edges = [(u, v) for u in range(n) for v in st.adj[u] if v > u]
    cur = best
    for it in range(iters):
        T = T0 * (Tend / T0) ** (it / iters)
        u = rng.randrange(n)
        v = rng.randrange(n)
        if u == v:
            continue
        # avoid isolating: don't remove last edge of a vertex (degree-0 ok mathematically but hurts)
        delta, apply = st.flip_delta(u, v)
        if delta >= 0 or rng.random() < math.exp(delta / T):
            apply()
            cur += delta
            if cur > best + 1e-12:
                best = cur
                best_edges = [(a, b) for a in range(n) for b in st.adj[a] if b > a]
        if it % 200000 == 199999:
            st.recompute()
            cur = st.score()
    return best, best_edges


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [20, 30, 50, 75, 100, 150, 200, 300, 500]
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 300000
    restarts = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    for n in ns:
        t0 = time.time()
        overall = -1e9
        oe = None
        seeds = [star_edges(n), clique_iso_edges(n)]
        for r in range(restarts):
            for si, se in enumerate(seeds):
                b, be = anneal(n, iters, T0=0.05, Tend=1e-6, seed=9000 * n + 10 * r + si,
                               start_edges=se)
                if b > overall:
                    overall, oe = b, be
        # exact-ish check of best
        st = State(n, oe)
        print(f"n={n:4d} best f={overall:+.6f} (recheck {st.score():+.6f}) m={st.m} "
              f"maxdeg={max(st.d)} t={time.time()-t0:.1f}s", flush=True)
        if overall > 0:
            print("POSITIVE CANDIDATE! edges:", oe, flush=True)

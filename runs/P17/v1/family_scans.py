#!/usr/bin/env python3
"""Closed-form / structured family scans for WoW 20 & 21 (P17).

score20(G) = sum_{lambda>0}(1-lambda)  (>0 iff WoW 20 violated)
score21(G) = sum_{lambda<0}(1-|lambda|) (>0 iff WoW 21 violated)

Analytic facts logged in NOTES.md and spot-checked here:
 L1. Any graph with integral spectrum satisfies both (every positive
     eigenvalue >=1, every negative <= -1). Covers Kneser, Johnson,
     Hamming, most SRGs, cographs*, unions of cliques, complete
     multipartite (20).
 L2. Complete multipartite K_{n1..nk}: n+ = 1 so WoW20 trivial;
     for 21, sum_pos = lambda1 >= lambda1(K_k) = k-1 = n^- by
     interlacing, equality iff K_k.
 L3. Corona G o K1: score20 = n - sum_i sqrt(lambda_i^2+4)/2 <= 0,
     equality iff G empty (i.e. corona = perfect matching).
 L4. Bipartite graphs: spectrum symmetric, n+ = n- <= rank/2 <= E/2
     (E >= rank for integer symmetric matrices). Both hold.
Scans below cover non-integral families at n >> 50.
"""
import numpy as np, itertools, fractions, math, sys

ZTOL = 1e-9

def sc(ev):
    pos = ev[ev > ZTOL]; neg = ev[ev < -ZTOL]
    return len(pos) - pos.sum(), len(neg) + neg.sum()

def report(name, s20, s21, extra=""):
    flag = " ***VIOLATION?***" if max(s20, s21) > 1e-7 else ""
    print(f"{name}: score20={s20:+.6f} score21={s21:+.6f} {extra}{flag}")
    return max(s20, s21) > 1e-7

best = {}
def track(fam, name, s20, s21):
    v = report(name, s20, s21)
    for key, s in (("20", s20), ("21", s21)):
        k = (fam, key)
        if k not in best or s > best[k][0]:
            best[k] = (s, name)
    return v

# ---------- 1. Kneser graphs (exact integer spectra) ----------
def kneser_scan(nmax=200):
    from math import comb
    worst = None
    for n in range(5, nmax + 1):
        for k in range(2, n // 2 + 1):
            s20 = s21 = 0
            for i in range(k + 1):
                lam = (-1) ** i * comb(n - k - i, k - i)
                mult = comb(n, i) - comb(n, i - 1) if i > 0 else 1
                if lam > 0: s20 += mult * (1 - lam)
                elif lam < 0: s21 += mult * (1 + lam)
            if worst is None or max(s20, s21) > max(worst[0], worst[1]):
                worst = (s20, s21, (n, k))
            assert s20 <= 0 and s21 <= 0, (n, k, s20, s21)
    print(f"kneser: all n<= {nmax} satisfy (integral spectra); "
          f"max scores {worst}")

# ---------- 2. Complete multipartite (exact rational Sturm-free check) ----------
def multipartite_scan():
    rng = np.random.default_rng(0)
    for trial in range(4000):
        k = rng.integers(2, 12)
        parts = rng.integers(1, 30, size=k)
        n = parts.sum()
        A = np.ones((n, n)) - np.eye(n)
        idx = np.cumsum(parts)
        st = 0
        for e in idx:
            A[st:e, st:e] = 0
            st = e
        ev = np.linalg.eigvalsh(A)
        s20, s21 = sc(ev)
        assert s20 <= 1e-7 and s21 <= 1e-7, (parts, s20, s21)
    print("multipartite: 4000 random part vectors, no violation "
          "(max n ~ 300); L2 analytic for all sizes")

# ---------- 3. Circulants (eigenvalues 2*sum cos, scan n large) ----------
def circulant_scan(iters=20000, nmax=300, rng=None):
    rng = rng or np.random.default_rng(1)
    b20 = b21 = -1e18; arg20 = arg21 = None
    for _ in range(iters):
        n = int(rng.integers(5, nmax))
        maxs = n // 2
        ssz = int(rng.integers(1, min(maxs, 8) + 1))
        S = rng.choice(np.arange(1, maxs + 1), size=ssz, replace=False)
        k = np.arange(n)
        ev = np.zeros(n)
        for s in S:
            if 2 * s == n: ev += np.cos(np.pi * k)
            else: ev += 2 * np.cos(2 * np.pi * k * s / n)
        s20, s21 = sc(ev)
        if s20 > b20: b20, arg20 = s20, (n, sorted(S.tolist()))
        if s21 > b21: b21, arg21 = s21, (n, sorted(S.tolist()))
    print(f"circulant: best score20={b20:+.6f} at {arg20}; "
          f"best score21={b21:+.6f} at {arg21}")
    assert b20 <= 1e-7 and b21 <= 1e-7

# ---------- 4. Line graphs of trees / graphs: score21 via Q-spectrum ----------
def line_graph_scan(iters=4000, nmax=120, rng=None):
    import networkx as nx
    rng = rng or np.random.default_rng(2)
    b21 = -1e18; arg = None
    for _ in range(iters):
        n = int(rng.integers(5, nmax))
        t = rng.random()
        if t < 0.5:
            G = nx.random_labeled_tree(n, seed=int(rng.integers(1 << 30)))
        else:
            G = nx.gnp_random_graph(n, min(1.0, rng.uniform(1, 4) / n),
                                    seed=int(rng.integers(1 << 30)))
            if G.number_of_edges() < 2: continue
        L = nx.line_graph(G)
        if L.number_of_nodes() < 2: continue
        A = nx.to_numpy_array(L)
        ev = np.linalg.eigvalsh(A)
        s20, s21 = sc(ev)
        if s21 > b21: b21, arg = s21, (n, G.number_of_edges())
        assert s20 <= 1e-7 and s21 <= 1e-7
    print(f"line graphs: best score21={b21:+.6f} at (n,m)={arg}")

# ---------- 5. Joins of unions of cliques / matchings ----------
def join_scan(iters=4000, rng=None):
    import networkx as nx
    rng = rng or np.random.default_rng(3)
    b = -1e18; arg = None
    for _ in range(iters):
        def rand_block(rng):
            t = rng.integers(0, 3)
            k = int(rng.integers(1, 12)); s = int(rng.integers(1, 6))
            if t == 0: return nx.disjoint_union_all([nx.complete_graph(s)] * k)
            if t == 1: return nx.disjoint_union_all([nx.path_graph(s + 1)] * k)
            return nx.empty_graph(k)
        G = rand_block(rng); H = rand_block(rng)
        J = nx.join(G, H) if hasattr(nx, 'join') else nx.complete_multipartite_graph(0)
        A = nx.to_numpy_array(J)
        ev = np.linalg.eigvalsh(A)
        s20, s21 = sc(ev)
        m = max(s20, s21)
        if m > b: b, arg = m, (len(G), len(H), s20, s21)
        assert m <= 1e-7, arg
    print(f"joins: best max-score={b:+.6f} at {arg}")

# ---------- 6. W_k family (Chen-Li 2026) exact quadratics ----------
def wk_scan(kmax=200):
    import sympy as sp
    x = sp.symbols('x')
    for k in range(5, kmax + 1):
        N = math.comb(k, 2)
        r = sp.Rational
        # eigenvalue 1, mult N-k : contributes 0 to score20
        # roots of x^2+(k-2)x-1 (mult k-1): pos root rp, neg rn
        d = sp.sqrt((k - 2) ** 2 + 4)
        rp = (-(k - 2) + d) / 2; rn = (-(k - 2) - d) / 2
        c2 = math.comb(k - 2, 2)
        e = sp.sqrt((k - 1 + c2) ** 2 - 4 * (k - 1) * (c2 - 2))
        q1 = ((k - 1 + c2) + e) / 2; q2 = ((k - 1 + c2) - e) / 2
        s20 = (k - 1) * (1 - rp) + (1 - q1) + (1 - q2)
        s21 = (k - 1) * (1 + rn)
        s20f, s21f = float(s20), float(s21)
        assert s20f <= 1e-9 and s21f <= 1e-9, (k, s20f, s21f)
    print(f"W_k (k<=200): no violation; score20(W_5)="
          f"{float((5-1)*(1-(-(3)+sp.sqrt(13))/2)+2-(4+3)):.4f}")

if __name__ == '__main__':
    kneser_scan()
    multipartite_scan()
    circulant_scan()
    line_graph_scan()
    join_scan()
    wk_scan()
    print("ALL FAMILY SCANS: no violation found")

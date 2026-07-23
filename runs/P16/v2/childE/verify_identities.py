"""Machine verification (sympy + random graphs) of the exact algebra used in
PROOF44.md (childE lemmas).

L1 (sum-weight CW identity): for y_f = s_f + c on edges,
   (A_{L(G)} y)_e = M_e + (c-2) s_e - 2c   where
   M_e = d_i(d_i+m_i) + d_j(d_j+m_j), s_e = d_i+d_j, using
   sum_{k~i} d_k = d_i m_i.  Hence
   rho(Q) = 2 + lam <= 2 + max_e [M_e + (c-2)s_e - 2c]/(s_e + c)
          = max_e (M_e + c s_e)/(s_e + c)          (algebraic simplification)

L2 (affine-product CW identity): for y_f = (d_i+b)(d_j+b),
   (A y)_e = (d_i+b) d_j (m_j + b) + (d_j+b) d_i (m_i+b) - 2(d_i+b)(d_j+b),
   hence rho(Q) <= 2 + max_e [d_i(m_i+b)/(d_j+b) + d_j(m_j+b)/(d_i+b) - 2].

Both identities need NO Jensen/concavity: neighbor sums telescope exactly.
Checks: (a) sympy symbolic simplification of the algebra;
        (b) random multigraph-free graphs: compare (A_L y)_e computed from the
            line graph with the closed form, and CW bound vs rho(Q).
"""
import numpy as np
import sympy as sp

from common import g6_adj, graph_data, line_graph_adj


def symbolic():
    di, dj, mi, mj, c, b, T = sp.symbols("d_i d_j m_i m_j c b T", positive=True)
    s = di + dj
    M = di * (di + mi) + dj * (dj + mj)
    # L1 simplification: 2 + (M + (c-2)s - 2c)/(s+c) == (M + c*s)/(s+c) + ... ?
    lhs = 2 + (M + (c - 2) * s - 2 * c) / (s + c)
    rhs = (M + c * s) / (s + c)
    assert sp.simplify(lhs - rhs) == 0
    print("L1 simplification OK: 2 + (M+(c-2)s-2c)/(s+c) == (M+cs)/(s+c)")
    # feasibility condition: (M + c s) <= T (s + c)  <=>  (M - T s) <= c (T - s)
    cond = sp.expand((M + c * s) - T * (s + c) - ((M - T * s) - c * (T - s)))
    assert cond == 0
    print("L1 threshold algebra OK")
    # L2: CW term
    cw = di * (mi + b) / (dj + b) + dj * (mj + b) / (di + b)
    q = sp.expand(sp.together((cw - (T - 2)) * (di + b) * (dj + b)))
    q = sp.expand(sp.cancel(q))
    A2 = sp.Poly(q, b).all_coeffs()
    print("L2 quadratic in b coeffs (lead first):", [sp.factor(x) for x in A2])


def numeric(trials=300, seed=0):
    rng = np.random.default_rng(seed)
    from common import graphs
    import itertools
    pool = []
    for n in (6, 7, 8):
        pool += [g for g, _ in zip(graphs(n), range(400))]
    idxs = rng.choice(len(pool), size=trials)
    for t in idxs:
        A = g6_adj(pool[t])
        d, m, E = graph_data(A)
        AL = line_graph_adj(E)
        Q = np.diag(A.sum(1)) + A
        lam = np.linalg.eigvalsh(Q)[-1] - 2
        for c in (-1.0, 0.0, 2.5):
            smin = min(d[i] + d[j] for i, j in E)
            if smin + c <= 0:
                continue
            y = np.array([d[i] + d[j] + c for i, j in E])
            Ay = AL @ y
            closed = np.array([d[i] * (d[i] + m[i]) + d[j] * (d[j] + m[j])
                               + (c - 2) * (d[i] + d[j]) - 2 * c for i, j in E])
            assert np.allclose(Ay, closed), (pool[t], c)
            cw = 2 + (Ay / y).max()
            assert lam + 2 <= cw + 1e-9
        for b in (0.0, 1.0, 3.7):
            y = np.array([(d[i] + b) * (d[j] + b) for i, j in E])
            Ay = AL @ y
            closed = np.array([(d[i] + b) * (d[i] * (m[i] + b) - (d[j] + b))
                               + (d[j] + b) * (d[j] * (m[j] + b) - (d[i] + b))
                               for i, j in E])
            assert np.allclose(Ay, closed), (pool[t], b)
            cw = 2 + (Ay / y).max()
            assert lam + 2 <= cw + 1e-9
    print(f"numeric identity + bound checks OK on {trials} random graphs")


if __name__ == "__main__":
    symbolic()
    numeric()

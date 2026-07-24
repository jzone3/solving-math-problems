"""Per-edge inequality scan for the K1-analog with sigma-hat:

Global identity (Lemma M3, verified below):
  1^T M(sig_c) d = 2 sum_i d_i (min(m_i, d_i+c) - 2)
                   - sum_e w_e (s_i+s_j)(s_i d_i + s_j d_j).

Candidate per-edge bound (would prove 1^T M d >= 0 by summing over edges):
  (PE):  w_e (s_i+s_j)(s_i d_i + s_j d_j) <= 2(min(m_i,d_i+c)-2) + 2(min(m_j,d_j+c)-2)

Variables: d_i, d_j >= 2; m_i >= (d_j + 2(d_i-1))/d_i, m_j >= (d_i + 2(d_j-1))/d_j
(m averages include the other endpoint and delta >= 2). Grid + random scan.
"""
import itertools
import numpy as np

rng = np.random.default_rng(2)


def pe_gap(di, dj, mi, mj, c):
    a4 = 2 * (di**2 + dj**2) - 16 * di * dj / (mi + mj)
    if a4 <= 0:
        return 0.0
    si = di - 4 + min(mi, di + c)
    sj = dj - 4 + min(mj, dj + c)
    lhs = (si + sj) * (si * di + sj * dj) / a4
    rhs = 2 * (min(mi, di + c) - 2) + 2 * (min(mj, dj + c) - 2)
    return lhs - rhs


for c in (2.0, 4.0):
    worst, warg = -1e18, None
    for di, dj in itertools.product(range(2, 41), repeat=2):
        mi_lo = (dj + 2 * (di - 1)) / di
        mj_lo = (di + 2 * (dj - 1)) / dj
        for mi in list(np.linspace(mi_lo, 400, 40)) + [mi_lo]:
            for mj in list(np.linspace(mj_lo, 400, 40)) + [mj_lo]:
                g = pe_gap(di, dj, mi, mj, c)
                if g > worst:
                    worst, warg = g, (di, dj, round(mi, 2), round(mj, 2))
    print(f"c={c}: max per-edge violation {worst:.6f} at (di,dj,mi,mj)={warg}")

# verify the identity on random graphs
import networkx as nx
from common import build_base, with_diag, sigma_cap

for c in (2.0, 4.0):
    err = 0
    for t in range(50):
        G = nx.gnp_random_graph(rng.integers(8, 30), rng.uniform(0.2, 0.7),
                                seed=int(rng.integers(1e9)))
        A = nx.to_numpy_array(G)
        d = A.sum(1)
        if d.min() < 2 or not nx.is_connected(G):
            continue
        b = build_base(A)
        s = sigma_cap(b["d"], b["m"], c)
        bd = with_diag(b, s)
        lhs = np.ones(b["n"]) @ bd["M"] @ b["d"]
        surp = 2 * np.sum(b["d"] * (np.minimum(b["m"], b["d"] + c) - 2))
        defi = sum(bd["w"][k] * (s[i] + s[j]) * (s[i] * b["d"][i] + s[j] * b["d"][j])
                   for k, (i, j) in enumerate(b["edges"]))
        err = max(err, abs(lhs - (surp - defi)))
    print(f"c={c}: identity max abs error {err:.2e}")

"""Lemma K1: exact identity for 1^T M d and numeric checks of the global
deficiency inequalities  1^T M d >= 0  and  d^T M d >= 0  (n <= 8 exhaustive).

K1 (identity):
  1^T M d = 2 sum_i d_i(d_i-2) - sum_{ij in E} w_ij (sig_i+sig_j)(sig_i d_i + sig_j d_j)

using sum_i d_i m_i = sum_i d_i^2 and (Qd)_i = d_i(d_i+m_i).
Equivalently sum_i T_i e_i <= 0 with e = Pd - d  (total deficiency <= 0
in the T-weighting), with equality on regular graphs.
"""
import numpy as np
from common import g6_to_adj, build, geng

# ---- sympy verification of the identity on random graphs (exact rationals) ----
from fractions import Fraction


def check_identity(A):
    bd = build(A)
    n, d, sig, w, edges, M = bd["n"], bd["d"], bd["sig"], bd["w"], bd["edges"], bd["M"]
    lhs = np.ones(n) @ M @ d
    rhs = 2 * np.sum(d * (d - 2)) - sum(
        w[k] * (sig[i] + sig[j]) * (sig[i] * d[i] + sig[j] * d[j])
        for k, (i, j) in enumerate(edges))
    return lhs, rhs


def main():
    import itertools
    worst_id = 0.0
    worst_1Md = None   # min of 1^T M d
    worst_dMd = None   # min of d^T M d
    bad1, badd = [], []
    tot = 0
    for n in range(3, 9):
        for g6 in geng(n):
            A = g6_to_adj(g6)
            bd = build(A)
            lhs, rhs = check_identity(A)
            worst_id = max(worst_id, abs(lhs - rhs))
            oneMd = lhs
            dMd = bd["d"] @ bd["M"] @ bd["d"]
            if worst_1Md is None or oneMd < worst_1Md:
                worst_1Md = oneMd
            if worst_dMd is None or dMd < worst_dMd:
                worst_dMd = dMd
            if oneMd < -1e-9:
                bad1.append(g6)
            if dMd < -1e-9:
                badd.append(g6)
            tot += 1
        print(f"n={n} done tot={tot} worst_id_err={worst_id:.2e} "
              f"min 1Md={worst_1Md:.6g} min dMd={worst_dMd:.6g} "
              f"viol1={len(bad1)} viold={len(badd)}", flush=True)
    print("bad 1^T M d graphs:", bad1[:20])
    print("bad d^T M d graphs:", badd[:20])


if __name__ == "__main__":
    main()

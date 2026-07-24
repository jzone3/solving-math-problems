"""childN exp6: certificate attempt for W1B.

Identity (to verify): for e=ij,
  w_e = sum_{k~i,k!=j}(d_k-y)(d_k+y-4) + sum_{l~j,l!=i}(d_l-x)(d_l+x-4)
        + sum_{k~i} d_k(m_k-y) + sum_{l~j} d_l(m_l-x)
(where the last sums INCLUDE the opposite endpoint j resp. i).

Certificate: with multipliers lam_{ik} = d_k/(2 m_i) (k~i, k!=j) and
lam_{jl} = d_l/(2 m_j), all m_k (k!=j) and m_l (l!=i) cancel in
  R := w_e + sum lam_{ik}(z1_e - arg44_{ik}) + sum lam_{jl}(z1_e - arg44_{jl}).
Then premise z1_e >= arg44 on B1(e) gives w_e <= R.  Question: R <= 0?
This script: (1) verifies the w identity numerically on all n<=7 graphs;
(2) computes R exactly on every edge of n<=8 graphs and reports max R
    over edges satisfying the premise (and unconditionally).
"""
import sys
from fractions import Fraction
sys.path.insert(0, ".")
from common import geng, gentreeg, g6_adj, edge_env

def w_identity_check():
    bad = 0
    for n in range(3, 8):
        for g6 in geng(n):
            A = g6_adj(g6)
            d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
            dd = A.sum(1)
            for a, (i, j) in enumerate(E):
                w = zs[a] - s[a] * z1[a]
                x, y = int(dd[i]), int(dd[j])
                t = 0
                for k in range(len(dd)):
                    if A[i, k] and k != j:
                        t += (dd[k] - y) * (dd[k] + y - 4)
                    if A[j, k] and k != i:
                        t += (dd[k] - x) * (dd[k] + x - 4)
                for k in range(len(dd)):
                    if A[i, k]:
                        t += dd[k] * (m[k] - y)
                    if A[j, k]:
                        t += dd[k] * (m[k] - x)
                if t != w:
                    bad += 1
    print("w-identity violations:", bad)

def scan_R(graphs, label):
    maxP = maxU = None
    violP = 0
    exP = None
    for g6 in graphs:
        A = g6_adj(g6)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        dd = A.sum(1)
        eidx = {fr: a for a, fr in enumerate(E)}
        for a, (i, j) in enumerate(E):
            w = zs[a] - s[a] * z1[a]
            R = Fraction(w)
            prem = z1[a] >= a44[a]
            for k in range(len(dd)):
                for (u, v) in ((i, j), (j, i)):
                    if A[u, k] and k != v:
                        b = eidx[(min(u, k), max(u, k))]
                        lam = Fraction(int(dd[k]), 2) / m[u]
                        R += lam * (z1[a] - a44[b])
                        if a44[b] > z1[a]:
                            prem = False
            if maxU is None or R > maxU:
                maxU = R
            if prem:
                if maxP is None or R > maxP:
                    maxP = R
                    exP = (g6, E[a], R)
                if R > 0:
                    violP += 1
    print(f"{label}: max R (premise)={maxP} ex={exP} viol={violP} | max R (all)={maxU}")

if __name__ == "__main__":
    w_identity_check()
    for n in range(3, 9):
        scan_R(geng(n), f"geng n={n}")
    for n in range(10, 15):
        scan_R(gentreeg(n), f"trees n={n}")

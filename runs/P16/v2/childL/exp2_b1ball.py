"""exp2: 1-ball strengthening of the clause-(b) single-edge reduction.

(B1) z1_e > rho1(e)  =>  rho1(e)(s_e - 3) + 3 z1_e - zs_e > 0
(W1) z1_e = rho1(e)  =>  zs_e <= s_e z1_e
where rho1(e) = max_{g in B1(e)} arg44_g (edge e and its line-graph
neighbors only). Stronger than (B)/(W=) of exp1 since rho1 <= rho0.
"""
import sys, itertools
from common import geng, gentreeg, g6_adj, edge_env


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "geng"
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    if mode == "geng":
        gens = itertools.chain.from_iterable(geng(n) for n in range(3, nmax + 1))
    else:
        gens = itertools.chain.from_iterable(gentreeg(n) for n in range(3, nmax + 1))
    total = 0
    minB = None
    for g6 in gens:
        A = g6_adj(g6)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        for a in range(len(E)):
            if z1[a] > rho1[a]:
                val = rho1[a] * (s[a] - 3) + 3 * z1[a] - zs[a]
                if minB is None or val < minB:
                    minB = val
                if val <= 0:
                    print("VIOLATION B1", g6, a, val, flush=True)
            elif z1[a] == rho1[a]:
                if zs[a] > s[a] * z1[a]:
                    print("VIOLATION W1", g6, a, flush=True)
        total += 1
        if total % 20000 == 0:
            print("...", total, "minB1 =", minB, flush=True)
    print("DONE", total, "graphs; min B1-margin =", minB)


if __name__ == "__main__":
    main()

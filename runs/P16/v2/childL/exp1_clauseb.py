"""exp1: single-edge reduction of Conjecture J clause (b).

Claims tested (exact rational arithmetic):
  (ID)  zs_e - 2 z1_e = sum_{f ~L e} z1_f   (identity sanity)
  (B)   z1_e > rho0(e)  =>  rho0(e)(s_e - 3) + 3 z1_e - zs_e > 0
  (W=)  z1_e = rho0(e)  =>  zs_e <= s_e z1_e
  (K1)  z1_e <= rho1(e) OR z1_e > rho1(e)  -- record margin z1_e - rho1(e)
        distribution for heavy edges (diagnostics only).

(B)+(W=) imply clause (b) of Conjecture J using s_f >= 3 (connected, n>=3):
  g(rho) = rho*s_e - zs_e + s_f(z1_e - rho) is linear in rho and in s_f with
  nonneg s_f-coefficient on [rho0, z1_e]; worst case s_f = 3, then min over
  rho at rho = rho0(e) (slope s_e - 3 >= 0), strict there by (B); endpoint
  rho = z1_e is (W=)/(B).
"""
import sys
from common import geng, gentreeg, g6_adj, edge_env

def check(g6, stats):
    A = g6_adj(g6)
    d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
    ne = len(E)
    bad = []
    for a in range(ne):
        nb = [b for b in range(ne) if AL[a, b]]
        assert zs[a] - 2 * z1[a] == sum(z1[b] for b in nb), (g6, a, "ID")
        if z1[a] > rho0[a]:
            val = rho0[a] * (s[a] - 3) + 3 * z1[a] - zs[a]
            stats["minB"] = min(stats.get("minB", val), val)
            if val <= 0:
                bad.append(("B", a, val))
        elif z1[a] == rho0[a]:
            if zs[a] > s[a] * z1[a]:
                bad.append(("W=", a, zs[a] - s[a] * z1[a]))
    return bad, (d, m, E, s, z1, zs, a44, rho0)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "geng"
    import itertools
    stats = {}
    total = 0
    if mode == "geng":
        nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 8
        gens = itertools.chain.from_iterable(geng(n) for n in range(3, nmax + 1))
    elif mode == "trees":
        nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 14
        gens = itertools.chain.from_iterable(gentreeg(n) for n in range(3, nmax + 1))
    else:
        gens = [mode]  # single g6
    for g6 in gens:
        bad, env = check(g6, stats)
        total += 1
        for item in bad:
            print("VIOLATION", g6, item, flush=True)
        if total % 20000 == 0:
            print("...", total, "graphs, minB =", stats.get("minB"), flush=True)
    print("DONE", total, "graphs; min B-margin =", stats.get("minB"))


if __name__ == "__main__":
    main()

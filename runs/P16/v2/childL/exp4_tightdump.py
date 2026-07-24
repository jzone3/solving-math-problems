"""exp4: dump per-neighbor data for the tightest (B) configurations, and
test candidate per-neighbor certificates.

For heavy e (z1_e > rho0(e)) with small margin = E_e - sum_f E_f, print the
full neighbor table: for each f ~ e: u_f = s_f-2, E_f = z1_f - rho0(e),
arg44_f, X_f = z1_f - arg44_f, T_f, plus e's own data.
"""
import sys, itertools, heapq
from common import geng, gentreeg, g6_adj, edge_env


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "geng"
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    if mode == "geng":
        gens = itertools.chain.from_iterable(geng(n) for n in range(3, nmax + 1))
    else:
        gens = itertools.chain.from_iterable(gentreeg(n) for n in range(3, nmax + 1))
    recs = []
    seen = set()
    for g6 in gens:
        A = g6_adj(g6)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        ne = len(E)
        for a in range(ne):
            if z1[a] > rho0[a]:
                nb = [b for b in range(ne) if AL[a, b]]
                margin = (z1[a] - rho0[a]) - sum(z1[b] - rho0[a] for b in nb)
                key = (g6,)
                item = (float(margin), len(recs), g6, a, nb,
                        dict(d=list(map(int, d)), m=[str(x) for x in m], E=E,
                             s=s, z1=z1, zs=zs, a44=[str(x) for x in a44],
                             rho0=[str(x) for x in rho0]))
                if len(recs) < 8:
                    heapq.heappush(recs, (-item[0],) + item[1:])
                else:
                    heapq.heappushpop(recs, (-item[0],) + item[1:])
    for neg, _, g6, a, nb, env in sorted(recs, reverse=True):
        print("=" * 60)
        print("g6", g6, "edge", env["E"][a], "margin", -neg)
        print("  e: s=%d z1=%d zs=%d arg44=%s rho0=%s d=%s" % (
            env["s"][a], env["z1"][a], env["zs"][a], env["a44"][a],
            env["rho0"][a], env["d"]))
        print("  m =", env["m"])
        for b in nb:
            print("   f=%s s=%d z1=%d arg44=%s  E_f=%s" % (
                env["E"][b], env["s"][b], env["z1"][b], env["a44"][b],
                env["z1"][b] - eval(env["rho0"][a].replace("/", "/1.0/")) if False else ""))
            print("      u=%d z1_f=%d a44_f=%s" % (env["s"][b]-2, env["z1"][b], env["a44"][b]))


if __name__ == "__main__":
    main()

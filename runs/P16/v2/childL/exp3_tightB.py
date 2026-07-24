"""exp3: structure of tight cases of (B) and candidate per-neighbor lemmas.

For edges e with z1_e > rho0(e) record:
  marginB = rho0(s_e-3) + 3 z1_e - zs_e   (>0 is (B))
  LX  = (z1_e - rho0) - sum_{f~e} X_f          , X_f = z1_f - arg44_f
  LXp = X_e - sum_{f~e} max(X_f, 0)            (pure 2-ball candidate)
Print min margins and the tightest few configurations.
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
    tight = []  # (marginB, g6, a, info)
    minLX = None; badLX = 0
    minLXp = None; badLXp = 0
    total = 0; cnt = 0
    for g6 in gens:
        A = g6_adj(g6)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        ne = len(E)
        for a in range(ne):
            if z1[a] > rho0[a]:
                cnt += 1
                nb = [b for b in range(ne) if AL[a, b]]
                X = {b: z1[b] - a44[b] for b in nb + [a]}
                marginB = rho0[a] * (s[a] - 3) + 3 * z1[a] - zs[a]
                LX = (z1[a] - rho0[a]) - sum(X[b] for b in nb)
                LXp = X[a] - sum(max(X[b], 0) for b in nb)
                if minLX is None or LX < minLX: minLX = LX
                if LX <= 0: badLX += 1
                if minLXp is None or LXp < minLXp: minLXp = LXp
                if LXp <= 0: badLXp += 1
                item = (float(marginB), str(marginB), g6, a,
                        "s=%d z1=%s rho0=%s X_e=%s LX=%s LXp=%s" % (
                            s[a], z1[a], rho0[a], X[a], LX, LXp))
                if len(tight) < 15:
                    heapq.heappush(tight, tuple([-item[0]] + list(item[1:])))
                else:
                    heapq.heappushpop(tight, tuple([-item[0]] + list(item[1:])))
        total += 1
    print("graphs", total, "heavy edges", cnt)
    print("min LX =", minLX, " #LX<=0:", badLX)
    print("min LXp =", minLXp, " #LXp<=0:", badLXp)
    print("tightest B margins:")
    for t in sorted(tight, reverse=True):
        print("  marginB=%s" % t[1], t[2], "edge", t[3], t[4])


if __name__ == "__main__":
    main()

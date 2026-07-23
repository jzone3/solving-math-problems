"""childJ exp14: big-scale check of Conjecture J (within-graph pairwise,
2-ball rho0, rho free in [max(rho0(e,f), z1_f), z1_e]).

For each graph and each ordered pair (e,f), z1_e > z1_f, require on
I = [max(rho0_2ball(e,f), z1_f), z1_e]:
  q(rho) = (rho s_f - zs_f)(z1_e - rho) - (rho s_e - zs_e)(z1_f - rho) >= 0
  p(rho) = rho(s_e - s_f) - zs_e + s_f z1_e >= 0   (U_e >= -s_f)
Usage: scan n res mod | trees n | file path | rand seed count
"""
import subprocess
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44, line_graph_adj

TOL = 1e-7


def check(A, g6):
    d, m, E = graph_data(A)
    ne = len(E)
    a44 = np.array([arg44(d[i], d[j], m[i], m[j]) for i, j in E])
    AL = line_graph_adj(E)
    s = np.array([d[i] + d[j] for i, j in E])
    z1 = AL @ (AL @ np.ones(ne))
    zs = AL @ (AL @ s)
    N1 = AL + np.eye(ne)
    N2 = N1 @ N1 > 0
    rho0e = np.array([a44[N2[a]].max() for a in range(ne)])
    bad = []
    for e in range(ne):
        for f in range(ne):
            if z1[e] <= z1[f] + 1e-12:
                continue
            lo = max(rho0e[e], rho0e[f], z1[f])
            hi = z1[e]
            if lo > hi:
                continue
            aq = s[e] - s[f]
            bq = s[f] * z1[e] + zs[f] - s[e] * z1[f] - zs[e]
            cq = -zs[f] * z1[e] + zs[e] * z1[f]
            vals = [aq * lo * lo + bq * lo + cq, aq * hi * hi + bq * hi + cq]
            if abs(aq) > 1e-15:
                r = -bq / (2 * aq)
                if lo < r < hi and aq > 0:
                    vals.append(aq * r * r + bq * r + cq)
            if min(vals) < -TOL:
                bad.append(("q", e, f, min(vals)))
            pv = [lo * (s[e] - s[f]) - zs[e] + s[f] * z1[e],
                  hi * (s[e] - s[f]) - zs[e] + s[f] * z1[e]]
            if min(pv) < -TOL:
                bad.append(("p", e, f, min(pv)))
    return bad


def main():
    mode = sys.argv[1]
    if mode == "file":
        it = (l.strip() for l in open(sys.argv[2]))
        tag = sys.argv[2]
    elif mode == "trees":
        n = int(sys.argv[2])
        tag = f"trees{n}"
        p = subprocess.Popen(f"nauty-gentreeg -q {n} | nauty-copyg -g",
                             shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True)
        it = (l.strip() for l in p.stdout)
    elif mode == "rand":
        from exp11_random import rand_graph
        seed, count = int(sys.argv[2]), int(sys.argv[3])
        tag = f"rand{seed}"
        rng = np.random.default_rng(seed)
        tot = badg = 0
        for t in range(count):
            A = rand_graph(rng)
            tot += 1
            b = check(A, "rand")
            if b:
                badg += 1
                print("VIOL rand graph", t, b[:3])
        print(f"{tag}: {tot} graphs, viol={badg}")
        return
    else:
        n, res, md = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        tag = f"n{n}_{res}of{md}"
        suffix = f"{res}/{md}" if md > 1 else ""
        p = subprocess.Popen(f"nauty-geng -qc {n} {suffix}", shell=True,
                             stdout=subprocess.PIPE, text=True)
        it = (l.strip() for l in p.stdout)
    tot = badg = 0
    for g6 in it:
        if not g6:
            continue
        tot += 1
        b = check(g6_adj(g6), g6)
        if b:
            badg += 1
            print("VIOL", g6, b[:3])
    print(f"{tag}: {tot} graphs, viol={badg}")


main()

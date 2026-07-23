"""childJ exp16: FINAL Conjecture J verification, exactly as stated in
PROOF_H.md. For a connected graph G, per edge g: s_g, z1_g=(A_L^2 1)_g,
zs_g=(A_L^2 s)_g, B2(g) = edges within line-graph distance <= 2 of g,
rho0(g) = max arg44 over B2(g).

Conjecture J. For all ordered pairs (e,f) of edges (f=e allowed) and all real
rho >= max(rho0(e), rho0(f)):
 (a) if z1_f <= rho <= z1_e:
     (rho*s_f - zs_f)(z1_e - rho) - (rho*s_e - zs_e)(z1_f - rho) >= 0
 (b) if rho <= z1_e:
     rho*s_e - zs_e + s_f*(z1_e - rho) >= 0,
     with STRICT > whenever rho < z1_e (positivity clause).

Checks (a) via quadratic min on the interval, (b) via endpoints (linear).
Usage: scan n res mod | trees n | file path | rand seed count
"""
import subprocess
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44, line_graph_adj

TOL = 1e-7


def check(A):
    d, m, E = graph_data(A)
    ne = len(E)
    a44 = np.array([arg44(d[i], d[j], m[i], m[j]) for i, j in E])
    AL = line_graph_adj(E)
    s = np.array([d[i] + d[j] for i, j in E])
    z1 = AL @ (AL @ np.ones(ne))
    zs = AL @ (AL @ s)
    N2 = (AL + np.eye(ne)) @ (AL + np.eye(ne)) > 0
    rho0 = np.array([a44[N2[g]].max() for g in range(ne)])
    bad = []
    for e in range(ne):
        for f in range(ne):
            r0 = max(rho0[e], rho0[f])
            # clause (b): rho in [r0, z1_e]
            if r0 <= z1[e]:
                for rr in (r0, z1[e]):
                    v = rr * s[e] - zs[e] + s[f] * (z1[e] - rr)
                    if v < -TOL:
                        bad.append(("b", e, f, rr, v))
                # strictness at rho < z1_e: linear => check left endpoint
                if r0 < z1[e] - 1e-9:
                    v0 = r0 * s[e] - zs[e] + s[f] * (z1[e] - r0)
                    if v0 < TOL:  # not strictly positive
                        bad.append(("b-strict", e, f, r0, v0))
            # clause (a): rho in [max(r0, z1_f), z1_e]
            lo = max(r0, z1[f])
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
                bad.append(("a", e, f, min(vals)))
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
        rng = np.random.default_rng(seed)
        tot = badg = 0
        for t in range(count):
            b = check(rand_graph(rng))
            tot += 1
            if b:
                badg += 1
                print("VIOL rand", seed, t, b[:3])
        print(f"rand{seed}: {tot} graphs, viol={badg}")
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
        b = check(g6_adj(g6))
        if b:
            badg += 1
            if badg <= 30:
                print("VIOL", g6, b[:3])
    print(f"{tag}: {tot} graphs, viol={badg}")


if __name__ == "__main__":
    main()

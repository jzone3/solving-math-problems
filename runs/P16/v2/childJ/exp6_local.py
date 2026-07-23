"""childJ exp6: LOCAL versions of the structure lemmas.

For r in {1,2}: R_r(e) = max arg44 over edges within line-graph distance <= r
of e (r=1: e and its neighbors; r=2: also neighbors of neighbors).

 J1loc(r): (A_L^2 1)_e <= R_r(e)  =>  (A_L^2 s)_e <= R_r(e) s_e
 Dloc(r):  (s_e-2)^2 <= R_r(e)   =>  (A_L^2 1)_e <= R_r(e)
Usage: scan nmin nmax | trees nmin nmax | file <path>
"""
import subprocess
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44, line_graph_adj

TOL = 1e-9


def gen(mode, n):
    if mode == "trees":
        p = subprocess.Popen(f"nauty-gentreeg -q {n} | nauty-copyg -g",
                             shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True)
        return (l.strip() for l in p.stdout)
    return graphs(n)


def check(A):
    d, m, E = graph_data(A)
    ne = len(E)
    a44 = np.array([arg44(d[i], d[j], m[i], m[j]) for i, j in E])
    AL = line_graph_adj(E)
    s = np.array([d[i] + d[j] for i, j in E])
    z1 = AL @ (AL @ np.ones(ne))
    zs = AL @ (AL @ s)
    N1 = AL + np.eye(ne)
    R1 = np.array([a44[N1[a] > 0].max() for a in range(ne)])
    N2 = N1 @ N1
    R2 = np.array([a44[N2[a] > 0].max() for a in range(ne)])
    v = [False] * 4
    for r, Rl in ((0, R1), (1, R2)):
        for a in range(ne):
            if z1[a] <= Rl[a] + TOL and zs[a] > Rl[a] * s[a] + TOL:
                v[2 * r] = True          # J1loc fails
            if (s[a] - 2) ** 2 <= Rl[a] + TOL and z1[a] > Rl[a] + TOL:
                v[2 * r + 1] = True      # Dloc fails
    return v


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "file":
        src = [("file", [l.strip() for l in open(sys.argv[2]) if l.strip()])]
    else:
        nmin, nmax = int(sys.argv[2]), int(sys.argv[3])
        src = [(n, gen(mode, n)) for n in range(nmin, nmax + 1)]
    cnt = np.zeros(4, int)
    ex = [None] * 4
    tot = 0
    for tag, it in src:
        for g6 in it:
            if not g6:
                continue
            tot += 1
            v = check(g6_adj(g6))
            for k in range(4):
                if v[k]:
                    cnt[k] += 1
                    if ex[k] is None:
                        ex[k] = g6
    names = ["J1loc r=1", "Dloc r=1", "J1loc r=2", "Dloc r=2"]
    print(f"total={tot}")
    for k in range(4):
        print(f"  viol {names[k]}: {cnt[k]} ex={ex[k]}")

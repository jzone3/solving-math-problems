"""childJ exp4: sign census of (sigma_e, kappa_e) across graphs.

Hypotheses tested per graph class:
 A: sigma_e <= 0 => kappa_e <= 0   (would make all lower bounds L_f <= 0)
 B: U (min upper bound) attained at a max-s edge
 C: kappa_e <= 0 for all e (c=0 works)
 D: sigma_e > 0 => s_e > tau + 2 (heavy in first-order sense)
 E: s_e > tau + 2 => sigma_e > 0
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


def census(A):
    d, m, E = graph_data(A)
    R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
    tau = np.sqrt(max(R, 0))
    AL = line_graph_adj(E)
    s = np.array([d[i] + d[j] for i, j in E])
    zs = AL @ (AL @ s)
    z1 = AL @ (AL @ np.ones(len(E)))
    sigma = z1 - R
    kappa = zs - R * s
    vA = ((sigma <= TOL) & (kappa > TOL)).any()
    # B: U attained at max-s edge
    pos = sigma > TOL
    vB = False
    if pos.any():
        U = (-kappa[pos] / sigma[pos]).min()
        att = np.where(pos)[0][np.argmin(-kappa[pos] / sigma[pos])]
        vB = abs(s[att] - s.max()) > 0.5 and not any(
            abs(-kappa[a] / sigma[a] - U) < 1e-7 and abs(s[a] - s.max()) < .5
            for a in np.where(pos)[0])
    vC = (kappa > TOL).any()
    vD = (pos & (s <= tau + 2 + TOL)).any()
    vE = ((s > tau + 2 + TOL) & (sigma <= TOL)).any()
    return vA, vB, vC, vD, vE


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "file":
        gs = [l.strip() for l in open(sys.argv[2]) if l.strip()]
        src = [("file", gs)]
    else:
        nmin, nmax = int(sys.argv[2]), int(sys.argv[3])
        src = [(n, gen(mode, n)) for n in range(nmin, nmax + 1)]
    cnt = np.zeros(5, int)
    tot = 0
    ex = [None] * 5
    for tag, it in src:
        for g6 in it:
            if not g6:
                continue
            tot += 1
            v = census(g6_adj(g6))
            for k in range(5):
                if v[k]:
                    cnt[k] += 1
                    if ex[k] is None:
                        ex[k] = g6
    names = ["A: sig<=0&kap>0", "B: U not at max-s", "C: some kap>0",
             "D: sig>0&s<=tau+2", "E: s>tau+2&sig<=0"]
    print(f"total={tot}")
    for k in range(5):
        print(f"  viol {names[k]}: {cnt[k]}  ex={ex[k]}")

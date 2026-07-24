"""Closed-form sigma candidates for F2' — must pass n<=8 exhaustive AND the
windmill/wheel/hub families that kill sigma = d+m-4.

M(s) = 2 diag(s) + 4I - Q - diag(s) H diag(s); H fixed (w from arg46).
Constraint: on the equality manifold (regular bipartite) the feasible set
pins s = 2d-4, so candidates must reduce to 2d-4 on regular graphs.
"""
import numpy as np
from common import g6_to_adj, build, geng
from graphs import windmill, wheel, hub_plus_cycles, hub_plus_cliques


def mineig(bd, s):
    D = np.diag(s)
    Ms = 2 * D + 4 * np.eye(bd["n"]) - bd["Q"] - D @ bd["H"] @ D
    return np.linalg.eigvalsh(Ms)[0]


CANDS = {
    "sig=d+m-4 (orig)": lambda d, m: d + m - 4,
    "sig=2d-4": lambda d, m: 2 * d - 4,
    "sig=min(d+m,2d)-4": lambda d, m: np.minimum(d + m, 2 * d) - 4,
    "sig=2d-4+min(m-d,4)_+": lambda d, m: 2 * d - 4 + np.clip(m - d, 0, 4),
    "sig=2d-4+min(m-d,2)_+": lambda d, m: 2 * d - 4 + np.clip(m - d, 0, 2),
    "sig=d-4+min(m,d+4)": lambda d, m: d - 4 + np.minimum(m, d + 4),
    "sig=d-4+min(m,d+2)": lambda d, m: d - 4 + np.minimum(m, d + 2),
    "sig=d-4+min(m,2d)": lambda d, m: d - 4 + np.minimum(m, 2 * d),
    "sig=d+sqrt(dm)-4ish": lambda d, m: d + np.sqrt(d * m) - 4,
    "sig=2sqrt(d(d-2))": lambda d, m: 2 * np.sqrt(np.maximum(d * (d - 2), 0)),
}

fams = ([("F_%d" % k, windmill(k)) for k in [8, 14, 20, 40, 100]] +
        [("W_%d" % n, wheel(n)) for n in [30, 40, 60, 120]] +
        [("hub%dC4" % k, hub_plus_cycles(k, 4)) for k in [10, 25]] +
        [("hub%dK3" % k, hub_plus_cliques(k, 3)) for k in [15, 30]])

for name, f in CANDS.items():
    # families
    worstfam, wf = 0.0, None
    for fn, A in fams:
        bd = build(A)
        e = mineig(bd, np.maximum(f(bd["d"], bd["m"]), 0.0))
        if e < worstfam:
            worstfam, wf = e, fn
    # exhaustive n<=8
    nbad, worst, wg = 0, 1e9, None
    for n in range(3, 9):
        for g6 in geng(n):
            A = g6_to_adj(g6)
            bd = build(A)
            e = mineig(bd, np.maximum(f(bd["d"], bd["m"]), 0.0))
            if e < worst:
                worst, wg = e, g6
            if e < -1e-8:
                nbad += 1
    print(f"{name:28s} fam_worst={worstfam:10.4f}({wf}) "
          f"n<=8: bad={nbad:5d} worst={worst:.3e} ({wg})", flush=True)

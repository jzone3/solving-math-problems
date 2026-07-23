"""Exp 6: candidate closed-form rules b = b(G) for the affine certificate.
Count failures for each rule over all connected graphs n<=nmax.
Also dump working-b intervals for a sample to eyeball structure.
"""
import math
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44


def cw_affine(d, m, E, b):
    return max(d[i] * (m[i] + b) / (d[j] + b) + d[j] * (m[j] + b) / (d[i] + b)
               for i, j in E)


def rules(d, m, E):
    dd = np.asarray(d)
    delta, Delta = dd.min(), dd.max()
    davg = dd.mean()
    mmax = max(np.max(m), 1)
    return {
        "b=0": 0.0,
        "b=delta": delta,
        "b=Delta": Delta,
        "b=Delta-delta": Delta - delta,
        "b=Delta-2": max(Delta - 2, 0),
        "b=davg": davg,
        "b=Delta+delta": Delta + delta,
        "b=2Delta": 2 * Delta,
        "b=mmax": mmax,
        "b=Delta^2": Delta ** 2,
        "b=inf": 1e8,
    }


def run(nmax):
    keys = None
    failc = {}
    tot = 0
    for n in range(3, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, E = graph_data(A)
            R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
            target = 2 + math.sqrt(max(R, 0))
            rl = rules(d, m, E)
            if keys is None:
                keys = list(rl)
                failc = {k: 0 for k in keys}
            tot += 1
            for k, b in rl.items():
                if cw_affine(d, m, E, b) > target + 1e-9:
                    failc[k] += 1
    print(f"n<={nmax}: graphs={tot}")
    for k in keys:
        print(f"  {k:16s}: {failc[k]} failures")


def intervals(nmax=7, count=25):
    shown = 0
    bs = np.concatenate([np.linspace(0, 20, 2001), np.linspace(20, 300, 281)])
    for n in range(4, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, E = graph_data(A)
            R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
            target = 2 + math.sqrt(max(R, 0))
            ok = np.array([cw_affine(d, m, E, b) <= target + 1e-9 for b in bs])
            if ok.all() or not ok.any():
                continue
            # nontrivial interval
            lo = bs[ok][0] if ok.any() else None
            hi = bs[ok][-1]
            dd = np.asarray(d)
            print(f"{g6}: b in [{lo:.2f},{hi:.1f}] delta={dd.min():.0f} "
                  f"Delta={dd.max():.0f} davg={dd.mean():.2f}")
            shown += 1
            if shown >= count:
                return


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "iv":
        intervals()
    else:
        run(int(sys.argv[1]) if len(sys.argv) > 1 else 8)

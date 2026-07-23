"""Exp 7: for the 36 n=9 affine-family failures, does ANY concave phi work
(SLSQP feasibility as childB opt_phi), and does min(x+b, h) truncated-affine work?
"""
import math

import numpy as np

from common import g6_adj, graph_data, arg44
from exp4_shapes import solve_phi

FAILS = """H?`reQF H?ovE_N HCOf@pR HCOf?zB HCOedPb HCOedHb HCOebIb HCOe`ZB
HCQf@oN HCQe`r` HCQdbPF HCQdar` HCQb`pw HCQbRbo HCQfRjF HCQerjF HCQfbjF
HCRdrrF HCpf`zF HCpdrjF""".split()


def cw(d, m, E, phi):
    return max(d[i] * phi(m[i]) / phi(d[j]) + d[j] * phi(m[j]) / phi(d[i])
               for i, j in E)


def main():
    import subprocess
    # recover the full 36 list by rescanning n=9? use log's top-20 plus rescan flag
    for g6 in FAILS:
        A = g6_adj(g6)
        d, m, E = graph_data(A)
        R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
        target = 2 + math.sqrt(max(R, 0))
        # truncated affine grid
        okT = False
        for b in np.linspace(0, 10, 101):
            for h in np.linspace(1.5, 12, 106):
                if cw(d, m, E, lambda x, b=b, h=h: min(x + b, h)) <= target + 1e-9:
                    okT = True
                    break
            if okT:
                break
        pts, phi, F = solve_phi(d, m, E, trials=24, seed=1)
        dd = np.asarray(d)
        print(f"{g6}: concave-slack={target - F:+.5f} truncAffine={'OK' if okT else 'FAIL'}"
              f" delta={dd.min():.0f} Delta={dd.max():.0f}")
        if target - F < 1e-7:
            print("   pts:", [f"{p:.3g}" for p in pts])
            print("   phi:", [f"{v:.4f}" for v in phi])


if __name__ == "__main__":
    main()

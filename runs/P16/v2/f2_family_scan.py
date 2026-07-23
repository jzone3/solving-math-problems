#!/usr/bin/env python3
"""Scan the two-parameter family h = d + alpha*sigma + beta*(m-2) as a CW
certificate for F2, over all connected delta>=2 graphs n<=8 (fast) and report
(alpha,beta) with fewest failures; then test the best on n=9."""
import numpy as np, sys, subprocess
from f2_ground import g6_to_adj, build, graphs

ALPHAS = [0.0,0.05,0.1,0.15,0.2,0.25,0.3]
BETAS  = [0.0,0.1,0.2,0.3,0.5]

def scan(nmax=8):
    fails = {(a,b):0 for a in ALPHAS for b in BETAS}
    total = 0
    for n in range(4,nmax+1):
        for g6 in graphs(n):
            A = g6_to_adj(g6); total += 1
            d,m,sigma,B,T = build(A)
            for a in ALPHAS:
                for b in BETAS:
                    h = d + a*sigma + b*(m-2)
                    if not np.all(B@h <= T*h + 1e-9):
                        fails[(a,b)] += 1
    print(f"total={total}")
    for k,v in sorted(fails.items(), key=lambda kv: kv[1])[:15]:
        print(k, v)

if __name__ == "__main__":
    scan(int(sys.argv[1]) if len(sys.argv)>1 else 8)

#!/usr/bin/env python3
"""Probe the hard graphs for F2: dump ground state h* (Perron of diag(1/T)B),
its ratio to natural invariants, and check whether the exact ground state
certifies (it must, since F2 holds numerically: rho(diag(1/T)B)<=1).
Goal: learn structure of h* on the residue graphs where low-K smoothing fails.
"""
import numpy as np, sys
from f2_ground import g6_to_adj, build

HARD = ['FCXe_','FEhv?','FQjR_','G?r@d_','G?qa`o','G?qrd_','GCQRDO','GCR`u_',
        'H?bB@`W','H?bB`po','H?bB`rG','H?bB`qg','H?bB`qc']

for g6 in HARD:
    A = g6_to_adj(g6)
    d,m,sigma,B,T = build(A)
    P = B/ T[:,None]  # diag(1/T) B
    vals, vecs = np.linalg.eig(P)
    k = np.argmax(vals.real)
    rho = vals.real[k]
    h = np.abs(vecs[:,k].real); h /= h.min()
    print(f"{g6}: rho={rho:.12f}")
    print(f"  d     = {d.astype(int)}")
    print(f"  m     = {np.round(m,3)}")
    print(f"  sigma = {np.round(sigma,3)}")
    print(f"  h*    = {np.round(h,4)}")
    print(f"  h*/d  = {np.round(h/d,4)}")
    print(f"  h*/(d+m) = {np.round(h/(d+m),4)}")
    print(f"  h*/(d*m) = {np.round(h/(d*m),4)}")
    print(f"  h*/(sigma+2) = {np.round(h/(sigma+2),4)}")

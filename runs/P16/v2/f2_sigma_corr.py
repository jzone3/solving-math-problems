#!/usr/bin/env python3
"""Test SDP-inspired sigma corrections: sigma'_i = sigma_i + c*max(0, avg_{j~i}sigma_j - sigma_i)
(childF Theorem F3 holds for ANY diagonal D, so if M(sigma') >= 0 for all graphs
for some fixed c, D1 and Bound 46 delta>=2 follow). Scan c on all delta>=2 n<=8.
Caution: with modified sigma, degenerate edges (arg46=4) need sigma'=0 at both
ends for the w:=0 convention to stay valid; we check that too and count violations."""
import numpy as np, sys
from f2_ground import g6_to_adj, graphs

def M_of(A, c):
    n=len(A); d=A.sum(1); m=(A@d)/d
    sigma = d+m-4.0
    if c != 0.0:
        avg = (A@sigma)/d
        sigma = sigma + c*np.maximum(0.0, avg - sigma)
    edges=[(i,j) for i in range(n) for j in range(i+1,n) if A[i,j]]
    bad_deg = False
    H=np.zeros((n,n))
    for (i,j) in edges:
        arg=2*(d[i]**2+d[j]**2)-16*d[i]*d[j]/(m[i]+m[j])+4
        a=arg-4
        if a < 1e-12:
            if abs(sigma[i])>1e-12 or abs(sigma[j])>1e-12: bad_deg=True
            w=0.0
        else:
            w=1.0/a
        H[i,i]+=w; H[j,j]+=w; H[i,j]+=w; H[j,i]+=w
    D=np.diag(sigma); Q=np.diag(d)+A
    M = 2*D + 4*np.eye(n) - Q - D@H@D
    return M, bad_deg

CS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]

def main(nmax=8):
    fails={c:0 for c in CS}; degbad={c:0 for c in CS}; total=0
    for n in range(4,nmax+1):
        for g6 in graphs(n):
            A=g6_to_adj(g6); total+=1
            for c in CS:
                M,bd = M_of(A,c)
                if bd: degbad[c]+=1
                if np.linalg.eigvalsh(M)[0] < -1e-9:
                    fails[c]+=1
    print(f"total={total}")
    for c in CS: print(f"c={c}: M-not-PSD={fails[c]}, degenerate-sigma-violations={degbad[c]}")

if __name__=="__main__":
    main(int(sys.argv[1]) if len(sys.argv)>1 else 8)

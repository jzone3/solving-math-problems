#!/usr/bin/env python3
"""Does h=d certify M(sigma') >= 0 (CW: (Q+D'H D')d <= (2 sigma'+4-?)...) —
careful: with sigma' != d+m-4, T' must be 2 sigma'+4? NO: M(s)=2diag(s)+4I-Q-diag(s)H diag(s),
CW condition: (Q + S H S) h <= (2s+4) o h. Test h=d for corrected sigma'."""
import numpy as np, sys
from f2_ground import g6_to_adj, graphs

def cw_check(A, c, h=None):
    n=len(A); d=A.sum(1); m=(A@d)/d
    sigma=d+m-4.0
    if c!=0.0:
        avg=(A@sigma)/d
        sigma=sigma+c*np.maximum(0.0,avg-sigma)
    edges=[(i,j) for i in range(n) for j in range(i+1,n) if A[i,j]]
    H=np.zeros((n,n))
    for (i,j) in edges:
        arg=2*(d[i]**2+d[j]**2)-16*d[i]*d[j]/(m[i]+m[j])+4
        a=arg-4; w=0.0 if a<1e-12 else 1.0/a
        H[i,i]+=w; H[j,j]+=w; H[i,j]+=w; H[j,i]+=w
    D=np.diag(sigma); Q=np.diag(d)+A
    B=Q+D@H@D; T=2*sigma+4
    if h is None: h=d
    return np.all(B@h <= T*h + 1e-9)

CS=[0.0,0.1,0.2,0.3,0.5,0.7,1.0]
def main(nmax=8):
    fails={c:0 for c in CS}; total=0
    for n in range(4,nmax+1):
        for g6 in graphs(n):
            A=g6_to_adj(g6); total+=1
            for c in CS:
                if not cw_check(A,c): fails[c]+=1
    print(f"total={total}")
    for c in CS: print(f"c={c}: h=d CW fails on {fails[c]}")

if __name__=="__main__":
    main(int(sys.argv[1]) if len(sys.argv)>1 else 8)

#!/usr/bin/env python3
"""childF route (ii): the feasible set {s diagonal : M(s) >= 0} is SDP-representable
via Schur complement: [[2 diag(s)+4I-Q, diag(s) R W^{1/2}],[W^{1/2} R^T diag(s), I_E]] >= 0
is LINEAR in s. Maximize the min-eigenvalue margin over s on hard graphs to learn
whether an alternative closed-form sigma exists (better than d+m-4)."""
import numpy as np, cvxpy as cp, sys
from f2_ground import g6_to_adj

HARD = ['FCXe_','FEhv?','FQjR_','G?r@d_','G?qrd_','GCR`u_','H?bB@`W']

def data(A):
    n=len(A); d=A.sum(1); m=(A@d)/d
    edges=[(i,j) for i in range(n) for j in range(i+1,n) if A[i,j]]
    w=[]
    for (i,j) in edges:
        arg=2*(d[i]**2+d[j]**2)-16*d[i]*d[j]/(m[i]+m[j])+4
        a=arg-4; w.append(0.0 if a<1e-12 else 1.0/a)
    R=np.zeros((n,len(edges)))
    for e,(i,j) in enumerate(edges): R[i,e]=R[j,e]=1
    return d,m,edges,np.array(w),R

for g6 in HARD:
    A=g6_to_adj(g6); n=len(A)
    d,m,edges,w,R=data(A)
    Q=np.diag(d)+A; E=len(edges)
    s=cp.Variable(n); t=cp.Variable()
    Ws=np.sqrt(w)
    top=cp.bmat([[2*cp.diag(s)+4*np.eye(n)-Q, cp.diag(s)@R@np.diag(Ws)],
                 [np.diag(Ws)@R.T@cp.diag(s), np.eye(E)]])
    prob=cp.Problem(cp.Maximize(t),[top - t*np.eye(n+E) >> 0, s>=0, s<=20])
    prob.solve(solver=cp.SCS, verbose=False)
    sig=d+m-4
    print(f"{g6}: margin={t.value:.4f}")
    print(f"  d       = {d.astype(int)}")
    print(f"  d+m-4   = {np.round(sig,3)}")
    print(f"  s_opt   = {np.round(s.value,3)}")
    print(f"  s_opt-(d+m-4) = {np.round(s.value-sig,3)}")

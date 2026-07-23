#!/usr/bin/env python3
"""Round-5 local experiment: mine the ground state of M(G) (Conjecture F2)
on the hard graphs where h=d fails, and test refined closed-form candidates.

M = 2*diag(sigma) + 4I - Q - diag(sigma) H diag(sigma),
sigma = d + m - 4, H = R diag(1/(arg46-4)) R^T (w=0 on degenerate edges).
F2 <=> exists h>0 with (Q + DHD) h <= (2 sigma + 4) o h.

Candidates tested:
  h = d                    (baseline; fails on 627/8025 n<=8)
  h = d - alpha*(t-1)_+ *d for excess t (local correction)
  h = one CW smoothing step applied to d:  h1 = (1/T) B d  (K=1)
  h = max(d, (1/T) B d)   etc.
Also dumps ground-state vector vs invariants for regression.
"""
import subprocess, sys, math
import numpy as np

def graphs(n):
    p = subprocess.Popen(["nauty-geng", "-qcd2", str(n)], stdout=subprocess.PIPE)
    for line in p.stdout:
        yield line.strip().decode()

def g6_to_adj(s):
    data = [ord(c)-63 for c in s]
    n = data[0]; bits = []
    for x in data[1:]:
        bits += [(x>>k)&1 for k in range(5,-1,-1)]
    A = np.zeros((n,n)); k=0
    for j in range(1,n):
        for i in range(j):
            A[i,j]=A[j,i]=bits[k]; k+=1
    return A

def build(A):
    n = len(A); d = A.sum(1); m = (A@d)/d
    sigma = d + m - 4
    edges = [(i,j) for i in range(n) for j in range(i+1,n) if A[i,j]]
    w = []
    for (i,j) in edges:
        arg = 2*(d[i]**2+d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j]) + 4
        a = arg - 4
        w.append(0.0 if a < 1e-12 else 1.0/a)
    H = np.zeros((n,n))
    for (e,(i,j)) in enumerate(edges):
        H[i,i]+=w[e]; H[j,j]+=w[e]; H[i,j]+=w[e]; H[j,i]+=w[e]
    D = np.diag(sigma)
    Q = np.diag(d)+A
    B = Q + D@H@D
    T = 2*sigma + 4
    return d,m,sigma,B,T

def check(B,T,h):
    return np.all(B@h <= T*h + 1e-9)

def main(nmax=9):
    stats = {}
    for n in range(4, nmax+1):
        cnt=0; fails={"d":0,"k1":0,"k2":0,"maxdk1":0,"blend":0}
        hard=[]
        for g6 in graphs(n):
            A = g6_to_adj(g6); cnt+=1
            d,m,sigma,B,T = build(A)
            hd = check(B,T,d)
            h1 = (B@d)/T
            hk1 = check(B,T,h1)
            h2 = (B@h1)/T
            hk2 = check(B,T,h2)
            hm = np.maximum(d,h1)
            hmx = check(B,T,hm)
            hb = 0.5*(d+h1)
            hbl = check(B,T,hb)
            if not hd: fails["d"]+=1
            if not hk1: fails["k1"]+=1
            if not hk2: fails["k2"]+=1
            if not hmx: fails["maxdk1"]+=1
            if not hbl: fails["blend"]+=1
            if not (hd or hk1 or hk2):
                hard.append(g6)
        print(f"n={n}: {cnt} graphs, fails: {fails}, none-of-d/k1/k2: {len(hard)}")
        if hard[:5]: print("  hard examples:", hard[:5])
        sys.stdout.flush()

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv)>1 else 9)

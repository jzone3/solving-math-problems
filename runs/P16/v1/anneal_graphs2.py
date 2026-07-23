#!/usr/bin/env python3
"""P16: heavier direct-graph annealing; seeded from perturbed regular bipartite."""
import math, random, sys
import numpy as np
from anneal_graphs import margin, connected

def seed_graph(n, rng):
    A = np.zeros((n,n), dtype=np.int64)
    h = n//2
    for i in range(h):
        for j in range(h, n):
            A[i,j]=A[j,i]=1
    for _ in range(rng.randint(0, 3*n)):
        i,j = rng.sample(range(n),2)
        A[i,j]^=1; A[j,i]^=1
    return A

def run(which, n, seed, iters):
    rng = random.Random(seed)
    A = seed_graph(n, rng)
    cur = margin(which, A)
    tries=0
    while (cur is None or not connected(A)) and tries<200:
        i,j=rng.sample(range(n),2); A[i,j]|=1; A[j,i]|=1
        cur = margin(which,A); tries+=1
    if cur is None: return (-1e18,None)
    best=(cur,A.copy())
    T0,T1=0.3,0.002
    for t in range(iters):
        i,j=rng.sample(range(n),2)
        A[i,j]^=1; A[j,i]^=1
        v = margin(which,A) if connected(A) else None
        T=T0*(T1/T0)**(t/iters)
        if v is not None and (v>cur or rng.random()<math.exp((v-cur)/T)):
            cur=v
            if v>best[0]:
                best=(v,A.copy())
                if v > 1e-9:
                    print(f"[{which}] VIOLATION n={n} seed={seed} t={t} margin={v}", flush=True)
                    print(A.tolist(), flush=True)
        else:
            A[i,j]^=1; A[j,i]^=1
    return best

if __name__=="__main__":
    which=int(sys.argv[1]); lo=int(sys.argv[2]); hi=int(sys.argv[3]); s0=int(sys.argv[4])
    overall=(-1e18,None)
    for n in range(lo,hi+1,4):
        for s in range(2):
            v,_=run(which,n,s0*97+n*7+s, 120000)
            print(f"[{which}] n={n} seed={s} best={v:.6f}", flush=True)
            if v>overall[0]: overall=(v,n)
    print(f"[{which}] block lo={lo} OVERALL {overall}")

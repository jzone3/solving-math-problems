#!/usr/bin/env python3
"""Exhaustive screens over special families: trees (gentreeg) and bipartite (geng -b).
Also tracks the 'permissive' convention where non-real (inner<0) edges are ignored."""
import math, subprocess, sys
import numpy as np
from exhaustive_geng import g6_to_adj

def margins2(A):
    n=A.shape[0]; d=A.sum(axis=1); m=(A@d)/d
    L=np.diag(d)-A
    mu=np.max(np.linalg.eigvalsh(L.astype(float)))
    res={}
    for which in (44,46):
        r=-np.inf; anyneg=False
        for i in range(n):
            for j in range(i+1,n):
                if A[i,j]:
                    di,dj,mi,mj=float(d[i]),float(d[j]),m[i],m[j]
                    if which==44:
                        inner=2*((di-1)**2+(dj-1)**2+mi*mj-di*dj)
                    else:
                        inner=2*(di**2+dj**2)-16*di*dj/(mi+mj)+4
                    if inner<0: anyneg=True
                    else: r=max(r,2+math.sqrt(inner))
        res[which]=(mu-r, anyneg)
    return res

def run(cmd, label):
    proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,text=True,bufsize=1<<20)
    best={44:(-1e18,None,False),46:(-1e18,None,False)}
    cnt=0
    for line in proc.stdout:
        line=line.strip()
        if not line: continue
        cnt+=1
        A=g6_to_adj(line)
        r=margins2(A)
        for w in (44,46):
            mg,neg=r[w]
            if mg>best[w][0]: best[w]=(mg,line,neg)
            if mg>1e-9:
                print(f"VIOLATION{w} {label} g6={line} margin={mg} permissive_neg_edges={neg}",flush=True)
    print(f"{label} count={cnt} best44={best[44]} best46={best[46]}",flush=True)

if __name__=="__main__":
    mode=sys.argv[1]; n=int(sys.argv[2])
    if mode=="tree":
        import os
        run(["bash","-c",f"nauty-gentreeg -q {n} | nauty-copyg -gq"],f"trees n={n}")
    else:
        run(["nauty-geng","-c","-b","-q",str(n)],f"bipartite n={n}")

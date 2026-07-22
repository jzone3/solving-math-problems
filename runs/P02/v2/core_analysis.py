#!/usr/bin/env python3
"""Twin-free core + canonical form for each infeasible candidate (graph6 on stdin)."""
import subprocess, sys
from exact_check import g6_to_adj

def adj_to_g6(A):
    n=len(A); bits=[]
    for j in range(1,n):
        for i in range(j): bits.append(A[i][j])
    while len(bits)%6: bits.append(0)
    return chr(n+63)+''.join(chr(63+int(''.join(map(str,bits[i:i+6])),2)) for i in range(0,len(bits),6))

for line in sys.stdin:
    g=line.split()[-1].strip()
    if not g: continue
    n,A=g6_to_adj(g)
    seen={}
    for v in range(n):
        seen.setdefault(tuple(j for j in range(n) if A[v][j]),[]).append(v)
    reps=[vs[0] for vs in seen.values()]
    m=len(reps)
    B=[[A[reps[i]][reps[j]] for j in range(m)] for i in range(m)]
    canon=subprocess.run(['nauty-labelg'],input=adj_to_g6(B)+'\n',capture_output=True,text=True).stdout.strip()
    print(f'{g} n={n} twinfree={m==n} core_n={m} core={canon}',flush=True)

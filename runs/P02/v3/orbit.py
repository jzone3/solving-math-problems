"""Explore edge-delete + re-maximalize orbit around given CEXs, hunting twin-free chi4."""
import sys, random
sys.path.insert(0,'.')
from p02lib import *
from localsearch import kcolorable, maximalize, mstar_float
seen=set(); frontier=[s for s in sys.argv[1:]]
rng=random.Random(7)
best=[]
for depth in range(3):
    newf=[]
    for g6 in frontier:
        n,adj0=parse_graph6(g6)
        edges=[(u,v) for u in range(n) for v in range(u+1,n) if (adj0[u]>>v)&1]
        for (u,v) in edges:
            for t in range(30):
                adj=adj0[:]
                adj[u]&=~(1<<v); adj[v]&=~(1<<u)
                adj=maximalize(n,adj,rng)
                g=to_graph6(n,adj)
                if g in seen: continue
                seen.add(g)
                deg=degrees(n,adj)
                if min(deg)*3<n or not is_maximal_tf(n,adj): continue
                if mstar_float(n,adj)<1e-9:
                    st,ems=exact_mstar(n,adj)
                    if st=='infeasible' or ems<=0:
                        tw=not any(adj[a]==adj[b] for a in range(n) for b in range(a+1,n))
                        c4=not kcolorable(n,adj,3)
                        if c4 or tw: newf.append(g)
                        if c4 and tw:
                            print('JACKPOT',g,flush=True)
                        elif c4:
                            print('chi4',g,flush=True)
    frontier=newf[:40]
print('explored',len(seen))

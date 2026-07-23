import glob, os, pickle
from field import load_vtx, edges_of
from sat import color_cnf, solve
res=[]
for f in sorted(glob.glob('jp/*.vtx'), key=lambda x:int(''.join(c for c in x.split('/')[-1][1:] if c.isdigit())[:3] or 0)):
    pts=load_vtx(f); E=edges_of(pts)
    nvars,cls=color_cnf(len(pts),E,4)
    st,_=solve(nvars,cls,timeout=300)
    n=len(pts)
    res.append((n,f.split('/')[-1],len(E),st))
    print(n, f.split('/')[-1], 'E=',len(E), st, flush=True)
res.sort()
un=[r for r in res if r[3]=='UNSAT']
print('\nUNSAT (5-chromatic) graphs, smallest first:')
for r in un: print(r)

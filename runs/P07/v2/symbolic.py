"""V2: closed-form distance sums for structured families; exact rational optimization of
R = 2*m*mu^2 / n^3 with mu = S/n^2 (Roucairol-Cazenave convention, S = ordered-pair distance sum).
All formulas machine-verified against BFS on sampled parameters.
"""
import sympy as sp
from fractions import Fraction as F
from families import bfs_all

a,b,ell = sp.symbols('a b ell', positive=True, integer=True)

# ---------- lollipop L(a,ell): K_a with pendant path of ell vertices at v0 ----------
# S = 2*[ C(a,2)  +  sum_{k=1}^{ell} (k + (a-1)(k+1))  +  (ell^3-ell)/6 ]
k = sp.Symbol('k')
S_lol = 2*( a*(a-1)/2 + sp.summation(k + (a-1)*(k+1), (k,1,ell)) + (ell**3-ell)/6 )
S_lol = sp.expand(sp.simplify(S_lol))
n_lol = a+ell
m_lol = a*(a-1)/2 + ell

# ---------- dumbbell D(a,ell,b): K_a - path(ell internal) - K_b ----------
# attach clique A at u (in A), clique B at w (in B); path v1..v_ell between them, u-v1, v_ell-w
# distances: u-w = ell+1
# within A: C(a,2); within B: C(b,2)
# A-path: vertex v_k at dist k from u: other A vertices dist k+1 -> sum_k [k + (a-1)(k+1)]
# B-path: v_k at dist ell+1-k from w -> sum_k [(ell+1-k) + (b-1)(ell+2-k)]
# A-B: u to w = ell+1; u to other B: ell+2; other A to w: ell+2; other A to other B: ell+3
#   = (ell+1) + (b-1)(ell+2) + (a-1)(ell+2) + (a-1)(b-1)(ell+3)
# path-path: (ell^3-ell)/6
S_dum = 2*( a*(a-1)/2 + b*(b-1)/2
    + sp.summation(k + (a-1)*(k+1), (k,1,ell))
    + sp.summation((ell+1-k) + (b-1)*(ell+2-k), (k,1,ell))
    + (ell+1) + (b-1)*(ell+2) + (a-1)*(ell+2) + (a-1)*(b-1)*(ell+3)
    + (ell**3-ell)/6 )
S_dum = sp.expand(sp.simplify(S_dum))
n_dum = a+b+ell
m_dum = a*(a-1)/2 + b*(b-1)/2 + ell + 1

def lol_edges(A,L):
    e=[(i,j) for i in range(A) for j in range(i+1,A)]
    prev=0
    for kk in range(L): e.append((prev,A+kk)); prev=A+kk
    return e,A+L

def dum_edges(A,L,B):
    e=[(i,j) for i in range(A) for j in range(i+1,A)]
    e+=[(A+i,A+j) for i in range(B) for j in range(i+1,B)]
    prev=0
    for kk in range(L): e.append((prev,A+B+kk)); prev=A+B+kk
    e.append((prev,A))
    return e,A+B+L

def check():
    import random
    for _ in range(12):
        A=random.randint(3,12); L=random.randint(1,10)
        e,n=lol_edges(A,L)
        adj=[[] for _ in range(n)]
        for u,v in e: adj[u].append(v); adj[v].append(u)
        assert bfs_all(adj,n)==int(S_lol.subs({a:A,ell:L})), ("lol",A,L)
    for _ in range(12):
        A=random.randint(2,10); B=random.randint(2,10); L=random.randint(1,8)
        e,n=dum_edges(A,L,B)
        adj=[[] for _ in range(n)]
        for u,v in e: adj[u].append(v); adj[v].append(u)
        got=bfs_all(adj,n); want=int(S_dum.subs({a:A,b:B,ell:L}))
        assert got==want, ("dum",A,B,L,got,want)
    print("closed forms verified against BFS: PASS")

if __name__=="__main__":
    check()
    print("S_lol =",S_lol)
    print("S_dum =",S_dum)

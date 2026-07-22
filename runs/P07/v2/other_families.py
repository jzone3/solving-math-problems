"""V2 breadth: theta graphs, brooms (clique + multiple pendant paths), join families.
Confirms none beats the lollipop at equal n; ratios via exact integers + BFS."""
from fractions import Fraction as F
from families import bfs_all

def ratio(edges,n):
    adj=[[] for _ in range(n)]
    for u,v in edges: adj[u].append(v); adj[v].append(u)
    S=bfs_all(adj,n); m=len(edges)
    return F(2*m*S*S, n**7)

def theta(l1,l2,l3):
    # two hub vertices joined by three internally disjoint paths of l1,l2,l3 internal vertices
    n=2+l1+l2+l3; edges=[]; nxt=2
    for L in (l1,l2,l3):
        prev=0
        for k in range(L):
            edges.append((prev,nxt)); prev=nxt; nxt+=1
        edges.append((prev,1))
    return edges,n

def broom(a,paths):
    n=a+sum(paths)
    edges=[(i,j) for i in range(a) for j in range(i+1,a)]
    nxt=a
    for L in paths:
        prev=0
        for k in range(L):
            edges.append((prev,nxt)); prev=nxt; nxt+=1
    return edges,n

def join_clique_path(a,l):
    # K_a joined (complete bipartite) to a path P_l : distances all <=2 -> tiny mu
    n=a+l
    edges=[(i,j) for i in range(a) for j in range(i+1,a)]
    edges+=[(a+k,a+k+1) for k in range(l-1)]
    edges+=[(i,a+k) for i in range(a) for k in range(l)]
    return edges,n

def lollipop(a,l):
    return broom(a,[l])

if __name__=="__main__":
    n=120
    print("lollipop(50,70):", float(ratio(*lollipop(50,70))))
    # best theta at n=120 (symmetric and skewed)
    best=(F(0),None)
    for l1 in range(1,118):
        for l2 in range(l1,119-l1):
            l3=118-l1-l2
            if l3<l2: continue
            r=ratio(*theta(l1,l2,l3))
            if r>best[0]: best=(r,(l1,l2,l3))
    print("best theta n=120:", float(best[0]), best[1])
    # brooms: split the 70 path vertices into p equal pendant paths on K_50
    for p in (1,2,3,5,7):
        parts=[70//p]*p
        parts[0]+=70-sum(parts)
        print("broom K50 with %d paths %s:"%(p,parts), float(ratio(*broom(50,parts))))
    # broom optimization over clique size with 2 paths
    best=(F(0),None)
    for a in range(3,118):
        rest=120-a
        r=ratio(*broom(a,[rest//2, rest-rest//2]))
        if r>best[0]: best=(r,a)
    print("best 2-path broom n=120:", float(best[0]), "a=",best[1])
    # join family (small diameter, should be tiny)
    print("join K30 + P90:", float(ratio(*join_clique_path(30,90))))

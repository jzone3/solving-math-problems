import fractions, collections
F = fractions.Fraction

def bfs_all(adj, n):
    S = 0
    for s in range(n):
        dist = [-1]*n; dist[s]=0; q=collections.deque([s])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if dist[v]<0: dist[v]=dist[u]+1; q.append(v)
        if min(dist)<0: return None
        S += sum(dist)
    return S  # sum over ordered pairs

def score(edges, n):
    adj=[[] for _ in range(n)]
    for u,v in edges: adj[u].append(v); adj[v].append(u)
    S = bfs_all(adj,n)
    if S is None: return None
    m = len(edges)
    mu_code = F(S, n*n)          # Roucairol-Cazenave convention
    mu_std  = F(S, n*(n-1))      # standard
    lhs_code = 2*m*mu_code**2
    lhs_std  = 2*m*mu_std**2
    return m, S, lhs_code, lhs_std, F(n**3)

def lollipop(a, ell):
    # clique K_a, path of ell extra vertices attached to vertex 0
    n = a+ell
    edges=[(i,j) for i in range(a) for j in range(i+1,a)]
    prev=0
    for k in range(ell):
        edges.append((prev,a+k)); prev=a+k
    return edges,n

if __name__=="__main__":
    best=None
    for n in [50,100,150,200,300]:
        for a in range(3,n-1):
            ell=n-a
            e,nn=lollipop(a,ell)
            m,S,lc,ls,n3=score(e,nn)
            r=F(lc,n3)
            if best is None or r>best[0]: best=(r,n,a)
        print(n, "best ratio so far:", float(best[0]), "at n=%d a=%d"%(best[1],best[2]))

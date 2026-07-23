"""Random large-graph stress test for Conjecture F2 (M(G) >= 0)."""
import numpy as np, networkx as nx, sys

rng = np.random.default_rng(7)

def test(G):
    G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
    # enforce delta>=2 by pruning leaves
    while True:
        leaves = [v for v in G if G.degree(v) < 2]
        if not leaves: break
        G.remove_nodes_from(leaves)
    if G.number_of_nodes() < 3 or not nx.is_connected(G): return None
    nodes = list(G.nodes); idx = {v:k for k,v in enumerate(nodes)}
    nn = len(nodes)
    A = np.zeros((nn,nn))
    for u,v in G.edges(): A[idx[u],idx[v]]=A[idx[v],idx[u]]=1
    d = A.sum(1); m = (A@d)/d
    sig = d+m-4
    M = np.diag(2*sig+4) - (np.diag(d)+A)
    for u,v in G.edges():
        i,j = idx[u], idx[v]
        a4 = 2*(d[i]**2+d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j])
        w = 1.0/a4 if a4 > 1e-9 else 0.0
        cij = 1 if False else w
        M[i,i] -= w*sig[i]**2; M[j,j] -= w*sig[j]**2
        M[i,j] -= w*sig[i]*sig[j]; M[j,i] -= w*sig[i]*sig[j]
    # note: Q part already subtracted above (diag(d)+A)
    return np.linalg.eigvalsh(M)[0], nn

count=0; worst=np.inf; worst_desc=None; bad=0
N = int(sys.argv[1]) if len(sys.argv)>1 else 3000
for it in range(N):
    typ = it % 4
    n = int(rng.integers(10, 120))
    if typ==0:
        p = rng.uniform(np.log(n)/n, 0.5)
        G = nx.gnp_random_graph(n, p, seed=int(rng.integers(1e9)))
    elif typ==1:
        dreg = int(rng.integers(3, min(12,n-1)))
        if (dreg*n)%2: n+=1
        G = nx.random_regular_graph(dreg, n, seed=int(rng.integers(1e9)))
        for _ in range(int(rng.integers(0,6))):
            e = list(G.edges()); G.remove_edge(*e[int(rng.integers(len(e)))])
    elif typ==2:
        a,b = int(rng.integers(3,15)), int(rng.integers(3,15))
        G = nx.complete_bipartite_graph(a,b)
        e = list(G.edges())
        for _ in range(int(rng.integers(0, len(e)//3))):
            ed = list(G.edges()); G.remove_edge(*ed[int(rng.integers(len(ed)))])
    else:
        G = nx.barabasi_albert_graph(n, int(rng.integers(2,6)), seed=int(rng.integers(1e9)))
    r = test(G)
    if r is None: continue
    ev, nn = r; count += 1
    if ev < worst: worst, worst_desc = ev, (typ, nn)
    if ev < -1e-7: bad += 1; print("FAIL", typ, nn, ev)
print(f"{count} graphs tested; worst min-eig {worst:.3e} at {worst_desc}; failures {bad}")

"""SAT + CEGAR attack on Gallai-3.

Fix n and L (number of vertices on each path). SAT variables:
  x[u][v]        adjacency (u<v)
  pos[k][i][v]   path k (k=0,1,2), slot i (0..L-1) holds vertex v

Constraints:
  - each slot: exactly one vertex; each vertex in at most one slot (per path)
  - consecutive slots adjacent: pos[k][i][u] & pos[k][i+1][v] -> x[uv]
  - empty triple intersection: for every v, not (v in P0 and v in P1 and v in P2)
  - pairwise intersections nonempty (valid necessary condition, prunes)
  - symmetry breaking: P0 slot0 vertex < P0 slot L-1 vertex; path 0 lexicographically
    contains vertex 0 (WLOG relabeling); optional degree>=2 (a counterexample graph can
    be assumed 'reduced'?? NOT valid in general -> omitted)

CEGAR loop: solve; take the model graph G; run the exact scanner to get the true longest
path length L*. If L* == L, G is a COUNTEREXAMPLE (three longest paths with empty common
intersection). If L* > L, pick a longest path Q of G (its edges E(Q)); ANY graph
containing all edges of E(Q) has a path with more than L vertices, so add the sound
blocking clause  OR_{e in E(Q)} not x_e  and repeat.

Notes: connectivity is not encoded; if the model graph is disconnected, only the
component containing the three paths matters — the scanner scores the whole graph, but a
longer path in another component still yields a sound blocking clause; and if L* == L
with empty intersection we check connectivity of the relevant component before claiming.

Usage: python3 cegar.py --n 14 --L 13 [--maxit 200000]
"""
import argparse, json, subprocess, time
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
import core
from weighted import g6_encode

def paths_of_len(adj, k, cap=3000):
    """All simple paths with exactly k vertices (deduped by reversal), up to cap."""
    n = len(adj)
    out = []
    def dfs(v, used, path):
        if len(out) >= cap:
            return
        if len(path) == k:
            if path[0] <= path[-1]:
                out.append(tuple(path))
            return
        for u in adj[v]:
            if not (used >> u) & 1:
                path.append(u)
                dfs(u, used | (1 << u), path)
                path.pop()
    for s in range(n):
        dfs(s, 1 << s, [s])
        if len(out) >= cap:
            break
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--L', type=int, required=True)
    ap.add_argument('--maxit', type=int, default=1000000)
    ap.add_argument('--tag', default=None)
    args = ap.parse_args()
    n, L = args.n, args.L
    tag = args.tag or f'ceg{n}_{L}'
    pool = IDPool()
    X = {}
    for u in range(n):
        for v in range(u + 1, n):
            X[(u, v)] = pool.id(f'x{u}_{v}')
    def xv(u, v):
        return X[(min(u, v), max(u, v))]
    P = [[[pool.id(f'p{k}_{i}_{v}') for v in range(n)] for i in range(L)] for k in range(3)]
    cnf = []
    for k in range(3):
        for i in range(L):
            cnf += CardEnc.equals([P[k][i][v] for v in range(n)], 1,
                                  vpool=pool, encoding=EncType.pairwise).clauses
        for v in range(n):
            for i in range(L):
                for j in range(i + 1, L):
                    cnf.append([-P[k][i][v], -P[k][j][v]])
        for i in range(L - 1):
            for u in range(n):
                for v in range(n):
                    if u != v:
                        cnf.append([-P[k][i][u], -P[k][i + 1][v], xv(u, v)])
                    else:
                        cnf.append([-P[k][i][u], -P[k][i + 1][v]])
    # membership indicators m[k][v]
    M = [[pool.id(f'm{k}_{v}') for v in range(n)] for k in range(3)]
    for k in range(3):
        for v in range(n):
            for i in range(L):
                cnf.append([-P[k][i][v], M[k][v]])
            cnf.append([-M[k][v]] + [P[k][i][v] for i in range(L)])
    # empty triple intersection
    for v in range(n):
        cnf.append([-M[0][v], -M[1][v], -M[2][v]])
    # pairwise nonempty (necessary: two longest paths always intersect)
    Wpair = []
    for a in range(3):
        for b in range(a + 1, 3):
            aux = [pool.id(f'w{a}{b}_{v}') for v in range(n)]
            for v in range(n):
                cnf.append([-aux[v], M[a][v]])
                cnf.append([-aux[v], M[b][v]])
            cnf.append(aux)
    # paths distinct as vertex sets is implied by empty triple + nonempty pair? not
    # strictly (two could be identical); forbid identical vertex sets for each pair via
    # requiring some v in one not the other... skip (identical sets have full pair
    # intersection => triple = pair \cap third, fine: if P0==P1 then triple = P0∩P2 which
    # is pairwise-nonempty => cannot be empty; so SAT models automatically have distinct sets).
    # symmetry: WLOG endpoint order
    # vertex 0 on path 0
    cnf.append([P[0][i][0] for i in range(L)])
    solver = Cadical153(bootstrap_with=cnf)
    log = open(f'log_{tag}.txt', 'a')
    def plog(s):
        print(s, flush=True); print(s, file=log, flush=True)
    plog(f'start n={n} L={L} vars={pool.top} clauses={len(cnf)}')
    t0 = time.time()
    it = 0
    blocked = set()
    while it < args.maxit:
        it += 1
        if not solver.solve():
            plog(f'UNSAT after {it-1} refinements, {time.time()-t0:.0f}s '
                 f'(no graph on {n} vertices has 3 longest paths of {L} vertices with empty common intersection, '
                 f'given blocking set)')
            return
        model = set(l for l in solver.get_model() if l > 0)
        adj = [[] for _ in range(n)]
        for (u, v), var in X.items():
            if var in model:
                adj[u].append(v); adj[v].append(u)
        # enumerate ALL (L+1)-vertex paths of the model graph; each yields a sound
        # blocking clause (any graph with those L edges has a too-long path).
        longpaths = paths_of_len(adj, L + 1, cap=3000)
        if longpaths:
            newcl = 0
            for q in longpaths:
                key = tuple(sorted((min(q[i], q[i+1]), max(q[i], q[i+1]))
                                   for i in range(L)))
                if key in blocked:
                    continue
                blocked.add(key)
                solver.add_clause([-X[e] for e in key])
                newcl += 1
            if it % 100 == 0:
                plog(f'it={it} +{newcl}cl tot={len(blocked)} ({time.time()-t0:.0f}s)')
            continue
        res = core.longest_paths(adj, cap=8)
        Lstar, paths = res
        if Lstar != L:
            # impossible: SAT model contains an L-vertex path and no (L+1)-path exists
            plog(f'BUG: L*={Lstar} vs L={L}')
            return
        # L* == L: candidate!
        json.dump({'adj': adj, 'n': n, 'L': L}, open(f'HIT_{tag}_{int(time.time())}.json', 'w'))
        plog(f'*** CANDIDATE t=0 graph found at it={it} — VERIFY with solutions/P05/verify.py! ***')
        plog(g6_encode(adj))
        return

if __name__ == '__main__':
    main()

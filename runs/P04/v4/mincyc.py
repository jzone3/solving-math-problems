"""Exact cycle-decomposition tools for Hajos' conjecture (P04), variant V4.

Core oracle: decomposable_within(G, k) -- can edge set of simple Eulerian graph G
be partitioned into at most k edge-disjoint cycles?  CP-SAT model: k color classes,
each class is a single (possibly empty) circuit enforced via AddCircuit with
self-loop literals; every undirected edge gets exactly one (class, direction).

hajos_deficit(G) checks feasibility at K = floor((n-1)/2); infeasible => witness.
min_cycles(G) binary/linear searches the exact minimum.
"""
import itertools
from ortools.sat.python import cp_model


def is_eulerian_simple(n, edges):
    deg = [0] * n
    seen = set()
    for u, v in edges:
        assert u != v and 0 <= u < n and 0 <= v < n
        e = (min(u, v), max(u, v))
        assert e not in seen
        seen.add(e)
        deg[u] += 1
        deg[v] += 1
    if any(d % 2 for d in deg):
        return False
    # connectivity on non-isolated vertices
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    start = next((i for i in range(n) if deg[i]), None)
    if start is None:
        return True
    stack, vis = [start], {start}
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in vis:
                vis.add(y)
                stack.append(y)
    return all(deg[i] == 0 or i in vis for i in range(n))


def decomposable_within(n, edges, k, time_limit=600.0, workers=8):
    """Return True/False, or None on timeout."""
    m = len(edges)
    model = cp_model.CpModel()
    # x[e][c][d]: edge e assigned to class c with direction d (0: u->v, 1: v->u)
    x = [[[model.NewBoolVar(f"x{e}_{c}_{d}") for d in range(2)] for c in range(k)]
         for e in range(m)]
    for e in range(m):
        model.AddExactlyOne(x[e][c][d] for c in range(k) for d in range(2))
    inc = [[] for _ in range(n)]  # vertex -> list of (edge idx)
    for e, (u, v) in enumerate(edges):
        inc[u].append(e)
        inc[v].append(e)
    invert = []  # per class: vertex-in-class literals
    for c in range(k):
        arcs = []
        vlit = []
        for vtx in range(n):
            lit = model.NewBoolVar(f"in{c}_{vtx}")
            vlit.append(lit)
            arcs.append((vtx, vtx, lit.Not()))
        for e, (u, v) in enumerate(edges):
            arcs.append((u, v, x[e][c][0]))
            arcs.append((v, u, x[e][c][1]))
        model.AddCircuit(arcs)
        invert.append(vlit)
    # symmetry breaking: edge 0 in class 0; class-of-edge is nondecreasing "first use"
    # simple: for edge e, class c can be used only if some earlier edge uses class c-1
    use = [[model.NewBoolVar(f"u{e}_{c}") for c in range(k)] for e in range(m)]
    for e in range(m):
        for c in range(k):
            model.AddBoolOr([x[e][c][0], x[e][c][1]]).OnlyEnforceIf(use[e][c])
            model.AddImplication(x[e][c][0], use[e][c])
            model.AddImplication(x[e][c][1], use[e][c])
            model.Add(use[e][c] == 0).OnlyEnforceIf([x[e][c][0].Not(), x[e][c][1].Not()])
    for c in range(1, k):
        for e in range(m):
            # if edge e is first edge of class c, some edge e'<e must be in class c-1
            model.AddBoolOr([use[ep][c] for ep in range(e)] +
                            [use[ep][c - 1] for ep in range(e)] +
                            [use[e][c].Not()])
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    st = solver.Solve(model)
    if st == cp_model.OPTIMAL or st == cp_model.FEASIBLE:
        sol = []
        for c in range(k):
            cyc = [edges[e] for e in range(m)
                   if solver.Value(x[e][c][0]) or solver.Value(x[e][c][1])]
            if cyc:
                sol.append(cyc)
        return True, sol
    if st == cp_model.INFEASIBLE:
        return False, None
    return None, None


def greedy_upper(n, edges):
    """Greedy cycle removal upper bound (prefer long cycles via DFS)."""
    import random
    adj = {i: set() for i in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    cnt = 0
    deg = {i: len(adj[i]) for i in range(n)}
    while any(adj[v] for v in adj):
        start = max(adj, key=lambda v: len(adj[v]))
        # walk until revisit
        path = [start]
        pos = {start: 0}
        cur = start
        while True:
            nxt = max(adj[cur], key=lambda w: len(adj[w]))
            if nxt in pos:
                cyc = path[pos[nxt]:] + [nxt]
                for a, b in zip(cyc, cyc[1:]):
                    adj[a].discard(b)
                    adj[b].discard(a)
                cnt += 1
                break
            pos[nxt] = len(path)
            path.append(nxt)
            cur = nxt
    return cnt


def min_cycles(n, edges, time_limit=600.0, kmax=None):
    """Exact minimum number of cycles in a decomposition."""
    ub = greedy_upper(n, edges)
    lo = max((max(sum(1 for e in edges if v in e) for v in range(n)) + 1) // 2, 1)
    k = lo
    while k <= (kmax or ub):
        ok, _ = decomposable_within(n, edges, k, time_limit)
        if ok is None:
            return None
        if ok:
            return k
        k += 1
    return ub


def complete_graph(n):
    return n, [(i, j) for i in range(n) for j in range(i + 1, n)]

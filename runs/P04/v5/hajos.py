"""P04 V5: exact Hajos-conjecture checker + heuristics.

A graph is given as (n, edges) with edges a sorted tuple of (u,v), u<v.
hajos_ok(n, edges) decides whether the Eulerian graph decomposes into
<= floor((n-1)/2) edge-disjoint cycles, via CP-SAT with one AddCircuit
constraint per colour class.
"""
import random
from ortools.sat.python import cp_model


def is_eulerian(n, edges):
    deg = [0] * n
    adj = [[] for _ in range(n)]
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
        adj[u].append(v)
        adj[v].append(u)
    if any(d % 2 for d in deg):
        return False
    # connectivity over non-isolated vertices
    verts = [v for v in range(n) if deg[v] > 0]
    if not verts:
        return False
    seen = {verts[0]}
    stack = [verts[0]]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return all(v in seen for v in verts)


def rlc_decompose(n, edges, tries=200, rng=None):
    """Random-long-cycle greedy (HNS 'RLC'). Returns best (fewest cycles) found."""
    rng = rng or random.Random()
    best = None
    for _ in range(tries):
        rem = {e: True for e in edges}
        adj = [set() for _ in range(n)]
        for u, v in edges:
            adj[u].add(v)
            adj[v].add(u)
        cycles = []
        ok = True
        while any(adj[v] for v in range(n)):
            start = rng.choice([v for v in range(n) if adj[v]])
            # walk until we revisit a vertex; extract the longest closable cycle greedily
            path = [start]
            pos = {start: 0}
            cyc = None
            cur = start
            while True:
                nbrs = list(adj[cur])
                if not nbrs:
                    break
                rng.shuffle(nbrs)
                nxt = None
                closer = None
                for y in nbrs:
                    if y in pos:
                        closer = y if closer is None or pos[y] < pos[closer] else closer
                    else:
                        nxt = y
                if nxt is None:
                    # must close: take the earliest-position neighbour => longest cycle
                    cyc = path[pos[closer]:] + [closer]
                    break
                path.append(nxt)
                pos[nxt] = len(path) - 1
                cur = nxt
            if cyc is None:
                ok = False
                break
            for a, b in zip(cyc, cyc[1:]):
                adj[a].discard(b)
                adj[b].discard(a)
            cycles.append(cyc)
        if ok and (best is None or len(cycles) < len(best)):
            best = cycles
            if len(best) <= (n - 1) // 2:
                return best
    return best


def check_decomposition(n, edges, cycles):
    """Independent sanity check that `cycles` is an edge-disjoint cycle decomposition."""
    used = set()
    for cyc in cycles:
        assert cyc[0] == cyc[-1] and len(set(cyc[:-1])) == len(cyc) - 1 >= 3
        for a, b in zip(cyc, cyc[1:]):
            e = (min(a, b), max(a, b))
            assert e not in used
            used.add(e)
    assert used == set(edges), (len(used), len(edges))
    return True


def hajos_ok(n, edges, k=None, time_limit=600, workers=8):
    """True if decomposable into <= k (default floor((n-1)/2)) cycles.
    Returns (status_bool_or_None, cycles_or_None). None = timeout/unknown."""
    if k is None:
        k = (n - 1) // 2
    m = len(edges)
    model = cp_model.CpModel()
    x = {}  # (u,v,i) directed arc lit
    s = {}  # (v,i) self loop lit
    for i in range(k):
        arcs = []
        for v in range(n):
            s[v, i] = model.NewBoolVar(f"s{v}_{i}")
            arcs.append((v, v, s[v, i]))
        for (u, v) in edges:
            x[u, v, i] = model.NewBoolVar(f"x{u}_{v}_{i}")
            x[v, u, i] = model.NewBoolVar(f"x{v}_{u}_{i}")
            arcs.append((u, v, x[u, v, i]))
            arcs.append((v, u, x[v, u, i]))
        model.AddCircuit(arcs)
    for (u, v) in edges:
        model.Add(sum(x[u, v, i] + x[v, u, i] for i in range(k)) == 1)
    # symmetry break: class sizes non-increasing
    sizes = []
    for i in range(k):
        sz = model.NewIntVar(0, m, f"sz{i}")
        model.Add(sz == sum(x[u, v, i] + x[v, u, i] for (u, v) in edges))
        sizes.append(sz)
    for i in range(k - 1):
        model.Add(sizes[i] >= sizes[i + 1])
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    st = solver.Solve(model)
    if st == cp_model.INFEASIBLE:
        return False, None
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, None
    # extract cycles
    cycles = []
    for i in range(k):
        succ = {}
        for (u, v) in edges:
            if solver.Value(x[u, v, i]):
                succ[u] = v
            if solver.Value(x[v, u, i]):
                succ[v] = u
        if not succ:
            continue
        start = next(iter(succ))
        cyc = [start]
        cur = succ[start]
        while cur != start:
            cyc.append(cur)
            cur = succ[cur]
        cyc.append(start)
        cycles.append(cyc)
    check_decomposition(n, edges, cycles)
    return True, cycles


def min_decomp_size(n, edges, time_limit=600):
    """Exact minimum number of cycles, by decreasing k from heuristic UB."""
    ub = rlc_decompose(n, edges, tries=500)
    k = len(ub)
    while True:
        ok, _ = hajos_ok(n, edges, k=k - 1, time_limit=time_limit)
        if ok is False:
            return k
        if ok is None:
            return -k  # unknown, at most k
        k -= 1


if __name__ == "__main__":
    # sanity: K7 -> 3 Hamilton cycles; K13 -> 6
    for n in (7, 9, 13):
        edges = tuple((u, v) for u in range(n) for v in range(u + 1, n))
        ok, cyc = hajos_ok(n, edges, time_limit=120)
        assert ok and len(cyc) <= (n - 1) // 2, (n, ok)
        print(f"K{n}: OK with {len(cyc)} cycles (bound {(n-1)//2})")
    # K5 needs 2, cannot do 1
    edges = tuple((u, v) for u in range(5) for v in range(u + 1, 5))
    ok, _ = hajos_ok(5, edges, k=1)
    assert ok is False
    print("K5 with k=1 infeasible: correct")

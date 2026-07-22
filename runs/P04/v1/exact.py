"""Exact decision: can graph G be decomposed into at most k edge-disjoint cycles?

Encoding: OR-Tools CP-SAT with k AddCircuit "slots". Slot i is a directed circuit
over all n vertices with optional self-loops (self-loop at v = v not on cycle i).
Edge {u,v} is covered by slot i iff arc (u,v) or (v,u) is chosen in circuit i.
Each edge must be covered by exactly one slot. Empty slots (all self-loops) allowed,
so feasibility with k slots == min cycle decomposition size <= k.

Usage: decompose_leq_k(n, edges, k, time_limit) -> (status_str, cycles_or_None)
"""
from ortools.sat.python import cp_model


def decompose_leq_k(n, edges, k, time_limit=300.0, workers=8):
    model = cp_model.CpModel()
    edges = [tuple(sorted(e)) for e in edges]
    arcvar = {}  # (i,u,v) -> BoolVar, u!=v only for graph edges; plus self loops
    for i in range(k):
        arcs = []
        for v in range(n):
            lit = model.NewBoolVar(f"self_{i}_{v}")
            arcvar[(i, v, v)] = lit
            arcs.append((v, v, lit))
        for (u, v) in edges:
            a = model.NewBoolVar(f"a_{i}_{u}_{v}")
            b = model.NewBoolVar(f"a_{i}_{v}_{u}")
            arcvar[(i, u, v)] = a
            arcvar[(i, v, u)] = b
            arcs.append((u, v, a))
            arcs.append((v, u, b))
        model.AddCircuit(arcs)
    # each edge covered exactly once
    for (u, v) in edges:
        model.AddExactlyOne(
            [arcvar[(i, u, v)] for i in range(k)] + [arcvar[(i, v, u)] for i in range(k)]
        )
    # symmetry breaking: slot i nonempty only if slot i-1 nonempty;
    # lowest-index edge of slot i increases with i.
    used = []
    for i in range(k):
        u_i = model.NewBoolVar(f"used_{i}")
        cov = [arcvar[(i, a, b)] for (a, b) in edges] + [arcvar[(i, b, a)] for (a, b) in edges]
        model.AddMaxEquality(u_i, cov)
        used.append(u_i)
    for i in range(1, k):
        model.AddImplication(used[i], used[i - 1])
    # min-edge-index ordering
    m = len(edges)
    minidx = [model.NewIntVar(0, m, f"min_{i}") for i in range(k)]
    for i in range(k):
        for j, (u, v) in enumerate(edges):
            e_in = model.NewBoolVar(f"e_{i}_{j}")
            model.AddMaxEquality(e_in, [arcvar[(i, u, v)], arcvar[(i, v, u)]])
            model.Add(minidx[i] <= j).OnlyEnforceIf(e_in)
        model.Add(minidx[i] == m).OnlyEnforceIf(used[i].Not())
    for i in range(1, k):
        model.Add(minidx[i - 1] < minidx[i]).OnlyEnforceIf(used[i])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = workers
    st = solver.Solve(model)
    if st == cp_model.INFEASIBLE:
        return "INFEASIBLE", None
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return "UNKNOWN", None
    cycles = []
    for i in range(k):
        arcs = {}
        for (u, v) in edges:
            if solver.Value(arcvar[(i, u, v)]):
                arcs[u] = v
            if solver.Value(arcvar[(i, v, u)]):
                arcs[v] = u
        if not arcs:
            continue
        start = min(arcs)
        cyc = [start]
        cur = arcs[start]
        while cur != start:
            cyc.append(cur)
            cur = arcs[cur]
        cycles.append(cyc)
    return "FEASIBLE", cycles


def min_decomp(n, edges, kmax=None, time_limit=300.0):
    """Exact minimum decomposition size by descending k search from kmax."""
    if kmax is None:
        kmax = (n - 1) // 2
    lo, best = 1, None
    k = kmax
    while k >= 1:
        st, cyc = decompose_leq_k(n, edges, k, time_limit)
        if st == "FEASIBLE":
            best = cyc
            k = len(cyc) - 1
        elif st == "INFEASIBLE":
            return (k + 1 if best else None), best
        else:
            return None, best
    return 1, best


if __name__ == "__main__":
    # sanity: K7, n=7, k=(7-1)//2=3 tight
    n = 7
    edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    st3, c3 = decompose_leq_k(n, edges, 3, 60)
    st2, c2 = decompose_leq_k(n, edges, 2, 60)
    print("K7 <=3:", st3, c3)
    print("K7 <=2:", st2)
    assert st3 == "FEASIBLE" and st2 == "INFEASIBLE"
    print("SANITY PASS")

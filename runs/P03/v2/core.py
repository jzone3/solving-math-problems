"""Core machinery for P03 (Woodall's conjecture) V2 run.

Digraph representation: list of arcs (u, v) over vertices 0..n-1, plus a
parallel list of weights (for the weighted seeds).  For unweighted instances
all weights are 1.

Key routines:
  - dicut enumeration via lower-set (ancestor-closed set) enumeration on the
    condensation DAG,
  - tau(D, w): min weight dicut,
  - packing_exists(D, k): ILP test for k pairwise arc-disjoint dijoins
    (weighted: each arc a in <= w_a dijoins),
  - rho(D, tau): the Abdi-Cornuejols-Zlatin parity parameter.
"""

import itertools
from fractions import Fraction


def strong_components(n, arcs):
    """Tarjan SCC. Returns comp id per vertex."""
    adj = [[] for _ in range(n)]
    for (u, v) in arcs:
        adj[u].append(v)
    index = [None] * n
    low = [0] * n
    onstk = [False] * n
    stk = []
    comp = [None] * n
    counter = [0]
    ncomp = [0]

    for root in range(n):
        if index[root] is not None:
            continue
        # iterative Tarjan
        work = [(root, 0)]
        while work:
            v, pi = work[-1]
            if pi == 0:
                index[v] = low[v] = counter[0]
                counter[0] += 1
                stk.append(v)
                onstk[v] = True
            recurse = False
            for i in range(pi, len(adj[v])):
                w = adj[v][i]
                if index[w] is None:
                    work[-1] = (v, i + 1)
                    work.append((w, 0))
                    recurse = True
                    break
                elif onstk[w]:
                    low[v] = min(low[v], index[w])
            if recurse:
                continue
            if low[v] == index[v]:
                while True:
                    w = stk.pop()
                    onstk[w] = False
                    comp[w] = ncomp[0]
                    if w == v:
                        break
                ncomp[0] += 1
            work.pop()
            if work:
                pv = work[-1][0]
                low[pv] = min(low[pv], low[v])
    return comp, ncomp[0]


def lower_sets(n, arcs):
    """Enumerate all ancestor-closed vertex sets U (as bitmasks) of a DAG on n
    vertices: for every arc (x,y), y in U => x in U.  Excludes empty & full.
    Yields bitmask of U; dicut(U) = delta^+(U) and delta^-(U) is empty by
    construction."""
    # predecessor mask per vertex
    pred = [0] * n
    for (u, v) in arcs:
        if u != v:
            pred[v] |= 1 << u
    full = (1 << n) - 1
    # DFS over vertices in topological-ish order; classic downset enumeration
    results = []
    # order vertices so that predecessors come first (topological order)
    indeg = [0] * n
    adj = [[] for _ in range(n)]
    for (u, v) in arcs:
        if u != v:
            indeg[v] += 1
            adj[u].append(v)
    from collections import deque
    dq = deque(i for i in range(n) if indeg[i] == 0)
    topo = []
    indeg2 = indeg[:]
    while dq:
        v = dq.popleft()
        topo.append(v)
        for w in adj[v]:
            indeg2[w] -= 1
            if indeg2[w] == 0:
                dq.append(w)
    assert len(topo) == n, "graph must be a DAG (condense first)"

    def rec(i, mask):
        if i == len(topo):
            if mask != 0 and mask != full:
                results.append(mask)
            return
        v = topo[i]
        # exclude v
        rec(i + 1, mask)
        # include v only if all predecessors already in mask
        if pred[v] & ~mask == 0:
            rec(i + 1, mask | (1 << v))

    rec(0, 0)
    return results


def condense(n, arcs):
    """Return (nc, carcs, arc_map) where carcs are condensation arcs (with
    original arc indices kept via arc_map: index into arcs -> None if inside
    an SCC else index used consistently)."""
    comp, nc = strong_components(n, arcs)
    carcs = []
    orig_idx = []
    for i, (u, v) in enumerate(arcs):
        cu, cv = comp[u], comp[v]
        if cu != cv:
            carcs.append((cu, cv))
            orig_idx.append(i)
    return nc, carcs, orig_idx, comp


def all_dicuts(n, arcs):
    """Return list of dicuts, each a frozenset of ORIGINAL arc indices.
    Handles general digraphs by condensing.  Deduplicates."""
    nc, carcs, orig_idx, comp = condense(n, arcs)
    if nc == 1:
        return []
    cuts = set()
    for mask in lower_sets(nc, carcs):
        cut = frozenset(orig_idx[j] for j, (cu, cv) in enumerate(carcs)
                        if (mask >> cu) & 1 and not (mask >> cv) & 1)
        cuts.add(cut)
    return list(cuts)


def minimal_dicuts(cuts):
    """Filter to inclusion-minimal dicuts (sufficient for dijoin constraints)."""
    cuts = sorted(set(cuts), key=len)
    out = []
    for c in cuts:
        if not any(o <= c for o in out):
            out.append(c)
    return out


def tau(n, arcs, w=None):
    """Min weight of a (nonempty-weight?) dicut.  Standard def: min |dicut|;
    weighted: min w(dicut).  Returns (value, argmin cut)."""
    cuts = all_dicuts(n, arcs)
    if not cuts:
        return None, None  # strongly connected: no dicut
    if w is None:
        w = [1] * len(arcs)
    best, bestc = None, None
    for c in cuts:
        val = sum(w[i] for i in c)
        if best is None or val < best:
            best, bestc = val, c
    return best, bestc


def rho(n, arcs, t, w=None):
    """ACZ parameter rho(tau, D, w) = (1/tau) * sum_v m_v with
    m_v = (w(delta^+(v)) - w(delta^-(v))) mod tau in {0..tau-1}."""
    if w is None:
        w = [1] * len(arcs)
    imb = [0] * n
    for i, (u, v) in enumerate(arcs):
        imb[u] += w[i]
        imb[v] -= w[i]
    s = sum((x % t) for x in imb)
    assert s % t == 0
    return s // t


def packing_exists(n, arcs, k, w=None, cuts=None, time_limit=120, solver=None):
    """ILP: do there exist k dijoins J_1..J_k with each arc a in at most
    w_a of them?  Uses minimal dicuts as covering constraints.
    Returns True/False (None on solver failure)."""
    import pulp
    if w is None:
        w = [1] * len(arcs)
    if cuts is None:
        cuts = minimal_dicuts(all_dicuts(n, arcs))
    m = len(arcs)
    prob = pulp.LpProblem("pack", pulp.LpMinimize)
    x = {(i, j): pulp.LpVariable(f"x_{i}_{j}", cat="Binary")
         for i in range(m) for j in range(k) if w[i] > 0}
    prob += 0
    for i in range(m):
        if w[i] > 0 and k > w[i]:
            prob += pulp.lpSum(x[(i, j)] for j in range(k)) <= w[i]
    for c in cuts:
        for j in range(k):
            vs = [x[(i, j)] for i in c if w[i] > 0]
            if not vs:
                return False  # some dicut has only zero-weight arcs
            prob += pulp.lpSum(vs) >= 1
    # symmetry breaking: dijoin j must contain the j-th smallest-index arc of
    # some fixed minimum cut
    c0 = min(cuts, key=len)
    c0 = sorted(i for i in c0 if w[i] > 0)
    if len(c0) == k and all(w[i] == 1 for i in c0):
        for j, i in enumerate(c0):
            prob += x[(i, j)] == 1
    slv = solver or pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit)
    status = prob.solve(slv)
    if status == pulp.LpStatusOptimal:
        return True
    if status == pulp.LpStatusInfeasible:
        return False
    return None


def nu(n, arcs, w=None, tmax=None, **kw):
    """Max packing size, computed by testing k = tau, tau-1, ..."""
    t, _ = tau(n, arcs, w)
    if t is None or t == 0:
        return t, t
    cuts = minimal_dicuts(all_dicuts(n, arcs))
    k = t
    while k >= 1:
        r = packing_exists(n, arcs, k, w, cuts=cuts, **kw)
        if r:
            return t, k
        if r is None:
            return t, None
        k -= 1
    return t, 0


def is_planar(n, arcs):
    try:
        import networkx as nx
        g = nx.MultiGraph()
        g.add_nodes_from(range(n))
        g.add_edges_from([(u, v) for (u, v) in arcs])
        ok, _ = nx.check_planarity(g)
        return ok
    except Exception:
        return None


def canon_key(n, arcs):
    """Cheap isomorphism-ish key: sorted degree/neighborhood refinement hash."""
    from collections import Counter
    outd = Counter()
    ind = Counter()
    for (u, v) in arcs:
        outd[u] += 1
        ind[v] += 1
    col = {v: (outd[v], ind[v]) for v in range(n)}
    for _ in range(3):
        newcol = {}
        for v in range(n):
            outs = sorted(col[y] for (x, y) in arcs if x == v)
            ins = sorted(col[x] for (x, y) in arcs if y == v)
            newcol[v] = hash((col[v], tuple(outs), tuple(ins)))
        col = newcol
    return (n, len(arcs), tuple(sorted(col.values())))

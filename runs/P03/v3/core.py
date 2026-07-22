"""Core routines for P03 V3 (tau=3 targeted search for Woodall counterexample).

Digraph representation: (n, arcs) where arcs is a tuple of (u,v) pairs, 0<=u,v<n, u!=v.
Parallel arcs allowed (multiset). Loops disallowed.

Definitions:
- dicut: delta^+(U) for nonempty proper U with delta^-(U) = empty (and delta^+(U) may be
  any size; if the digraph is weakly connected and not strongly connected, dicuts exist).
- tau = min |dicut| over all dicuts.
- dijoin: arc set intersecting every dicut.
- Woodall counterexample: tau = 3 but no 3 pairwise disjoint dijoins
  (equivalently no partition of A into 3 classes each hitting every dicut,
  since supersets of dijoins are dijoins).
"""
from itertools import combinations


def enumerate_dicuts(n, arcs):
    """Return list of dicuts, each a frozenset of arc indices.

    U ranges over nonempty proper subsets (bitmask) with no arc entering U.
    """
    dicuts = []
    for U in range(1, (1 << n) - 1):
        out_arcs = []
        ok = True
        for i, (u, v) in enumerate(arcs):
            uin = (U >> u) & 1
            vin = (U >> v) & 1
            if vin and not uin:  # arc enters U
                ok = False
                break
            if uin and not vin:
                out_arcs.append(i)
        if ok and out_arcs:
            dicuts.append(frozenset(out_arcs))
    return dicuts


def minimal_dicuts(dicuts):
    """Inclusion-wise minimal dicuts suffice for covering constraints."""
    ds = sorted(set(dicuts), key=len)
    out = []
    for d in ds:
        if not any(m <= d for m in out):
            out.append(d)
    return out


def tau(dicuts):
    return min(len(d) for d in dicuts) if dicuts else None


def rho3(n, arcs):
    """ACZ rho(3, D, 1) = (1/3) sum_v ((outdeg-indeg) mod 3)."""
    imb = [0] * n
    for (u, v) in arcs:
        imb[u] += 1
        imb[v] -= 1
    s = sum(x % 3 for x in imb)
    assert s % 3 == 0
    return s // 3


def is_weakly_connected(n, arcs):
    adj = [[] for _ in range(n)]
    for (u, v) in arcs:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    stack = [0]
    seen[0] = True
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if not seen[y]:
                seen[y] = True
                stack.append(y)
    return all(seen)


def reach(n, arcs, srcs):
    adj = [[] for _ in range(n)]
    for (u, v) in arcs:
        adj[u].append(v)
    seen = [False] * n
    stack = list(srcs)
    for s in srcs:
        seen[s] = True
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if not seen[y]:
                seen[y] = True
                stack.append(y)
    return seen


def is_source_sink_connected(n, arcs):
    """Every source (indeg 0... actually: vertex with no entering arcs) reaches every sink.

    Schrijver / Feofiloff-Younger: Woodall holds for source-sink connected digraphs.
    NOTE: the theorem's notion: every source reaches every sink, where source = vertex
    with indegree 0, sink = vertex with outdegree 0. Digraphs may have no sources/sinks
    (then vacuously source-sink connected only if strongly...?). We use the standard
    def: for all sources s and sinks t, s reaches t. If there are no source/sink pairs,
    returns True (treat as safe/skip).
    """
    indeg = [0] * n
    outdeg = [0] * n
    for (u, v) in arcs:
        outdeg[u] += 1
        indeg[v] += 1
    sources = [v for v in range(n) if indeg[v] == 0]
    sinks = [v for v in range(n) if outdeg[v] == 0]
    for s in sources:
        r = reach(n, arcs, [s])
        if any(not r[t] for t in sinks):
            return False
    return True


def underlying_planar(n, arcs):
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from((u, v) for (u, v) in arcs)
    ok, _ = nx.check_planarity(G)
    return ok


def pack3_sat(arcs, dicuts, return_model=False):
    """SAT: partition arcs into 3 classes, each class hits every dicut.

    Returns True (packable) / False (COUNTEREXAMPLE if tau>=3).
    """
    from pysat.solvers import Minicard as Solver
    m = len(arcs)
    # var id for arc i color c: 3*i + c + 1
    cnf = []
    for i in range(m):
        vs = [3 * i + c + 1 for c in range(3)]
        cnf.append(vs)  # at least one color
        cnf.append([-vs[0], -vs[1]])
        cnf.append([-vs[0], -vs[2]])
        cnf.append([-vs[1], -vs[2]])
    for d in dicuts:
        for c in range(3):
            cnf.append([3 * i + c + 1 for i in d])
    with Solver(bootstrap_with=cnf) as s:
        sat = s.solve()
        if sat and return_model:
            model = s.get_model()
            colors = [None] * m
            for i in range(m):
                for c in range(3):
                    if model[3 * i + c] > 0:
                        colors[i] = c
            return True, colors
    return (sat, None) if return_model else sat


def analyze(n, arcs, require_filters=True):
    """Full pipeline. Returns dict with fields; 'counterexample' True if found."""
    res = {"n": n, "m": len(arcs)}
    if not is_weakly_connected(n, arcs):
        res["skip"] = "not weakly connected"
        return res
    dicuts = enumerate_dicuts(n, arcs)
    t = tau(dicuts)
    res["tau"] = t
    if t != 3:
        res["skip"] = "tau != 3"
        return res
    res["rho3"] = rho3(n, arcs)
    if require_filters and res["rho3"] <= 3:
        res["skip"] = "rho<=3 (ACZ safe)"
        return res
    if require_filters and is_source_sink_connected(n, arcs):
        res["skip"] = "source-sink connected (Schrijver safe)"
        return res
    if require_filters and underlying_planar(n, arcs):
        res["skip"] = "planar (LY safe)"
        return res
    md = minimal_dicuts(dicuts)
    res["n_dicuts"] = len(dicuts)
    res["n_min_dicuts"] = len(md)
    sat = pack3_sat(arcs, md)
    res["packable"] = sat
    res["counterexample"] = not sat
    return res


def brute_pack3(arcs, dicuts):
    """Independent slow check: try all 3^m colorings (only for tiny m)."""
    m = len(arcs)
    for code in range(3 ** m):
        cols = []
        x = code
        for _ in range(m):
            cols.append(x % 3)
            x //= 3
        if all(len({cols[i] for i in d}) == 3 for d in dicuts):
            return True
    return False

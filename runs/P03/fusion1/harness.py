"""
P03 Woodall's conjecture -- V5 harness.

Core routines:
- enumerate closed sets / dicuts of a digraph (bitmask, n <= ~20)
- tau(D) = min dicut size
- minimal dicuts
- has_k_disjoint_dijoins(D, k): SAT check (exact partition into k dijoins)
- structural filters: rho(k,D), planarity, source-sink connectivity, chordality

Digraph representation: (n, arcs) where arcs is a list of (u, v) pairs,
vertices 0..n-1. Parallel arcs allowed.
"""

import itertools
import networkx as nx
from pysat.solvers import Minicard, Glucose4
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def closed_sets(n, arcs):
    """Yield masks U (nonempty, proper) with no arc entering U: delta^-(U) = empty.
    delta^+(U) is then a dicut."""
    # in_mask[v] = bitmask of in-neighbours of v
    in_mask = [0] * n
    for (u, v) in arcs:
        in_mask[v] |= (1 << u)
    full = (1 << n) - 1
    for U in range(1, full):
        ok = True
        m = U
        while m:
            v = (m & -m).bit_length() - 1
            if in_mask[v] & ~U:
                ok = False
                break
            m &= m - 1
        if ok:
            yield U


def dicut_arcs(U, arcs):
    """Arc indices leaving mask U."""
    return frozenset(i for i, (u, v) in enumerate(arcs)
                     if (U >> u) & 1 and not (U >> v) & 1)


def all_dicuts(n, arcs):
    return [dicut_arcs(U, arcs) for U in closed_sets(n, arcs)]


def tau(n, arcs):
    """Min dicut size; None if strongly connected (no dicut)."""
    best = None
    for U in closed_sets(n, arcs):
        c = sum(1 for (u, v) in arcs if (U >> u) & 1 and not (U >> v) & 1)
        if best is None or c < best:
            best = c
            if best == 0:
                break
    return best


def minimal_dicuts(n, arcs):
    cuts = set(all_dicuts(n, arcs))
    cuts = sorted(cuts, key=len)
    minimal = []
    for c in cuts:
        if not any(m < c for m in minimal):
            minimal.append(c)
    return minimal


def has_k_disjoint_dijoins(n, arcs, k, return_model=False):
    """SAT: can arcs be partitioned into k dijoins? (equivalent to k disjoint
    dijoins existing, since supersets of dijoins are dijoins)."""
    mcuts = minimal_dicuts(n, arcs)
    if any(len(c) < k for c in mcuts):
        return (False, None) if return_model else False
    m = len(arcs)
    pool = IDPool()
    var = lambda a, c: pool.id((a, c))
    solver = Glucose4()
    for a in range(m):
        solver.add_clause([var(a, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                solver.add_clause([-var(a, c1), -var(a, c2)])
    for cut in mcuts:
        for c in range(k):
            solver.add_clause([var(a, c) for a in cut])
    sat = solver.solve()
    if not return_model:
        solver.delete()
        return sat
    model = None
    if sat:
        mset = set(l for l in solver.get_model() if l > 0)
        model = [None] * m
        for a in range(m):
            for c in range(k):
                if var(a, c) in mset:
                    model[a] = c
                    break
    solver.delete()
    return sat, model


def rho(n, arcs, k):
    """ACZ rho parameter: (1/k) * sum_v ((outdeg-indeg) mod k)."""
    exc = [0] * n
    for (u, v) in arcs:
        exc[u] += 1
        exc[v] -= 1
    return sum(e % k for e in exc) // k


def underlying_graph(n, arcs):
    G = nx.MultiGraph()
    G.add_nodes_from(range(n))
    for (u, v) in arcs:
        G.add_edge(u, v)
    return G


def is_planar(n, arcs):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from((u, v) for (u, v) in arcs)
    return nx.check_planarity(G)[0]


def is_chordal_underlying(n, arcs):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from((u, v) for (u, v) in arcs if u != v)
    return nx.is_chordal(G)


def is_source_sink_connected(n, arcs):
    """Schrijver's safe class: every source vertex reaches every sink vertex
    by a directed path (applied to the DAG of strong components; here we
    assume D is a DAG). Sources/sinks = vertices with indeg 0 / outdeg 0."""
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(arcs)
    sources = [v for v in range(n) if G.in_degree(v) == 0]
    sinks = [v for v in range(n) if G.out_degree(v) == 0]
    reach = {s: nx.descendants(G, s) | {s} for s in sources}
    return all(t in reach[s] for s in sources for t in sinks)


def is_dag(n, arcs):
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(arcs)
    return nx.is_directed_acyclic_graph(G)


def weakly_3_arc_connected(n, arcs):
    """Every nonempty proper subset has total degree >= 3 in underlying multigraph."""
    for U in range(1, (1 << n) - 1):
        d = sum(1 for (u, v) in arcs if ((U >> u) & 1) != ((U >> v) & 1))
        if d < 3:
            return False
    return True


def check_candidate(n, arcs, k=3, verbose=False):
    """Full filter + SAT check. Returns dict of properties; 'counterexample'
    True iff tau == k and no k disjoint dijoins."""
    t = tau(n, arcs)
    res = {'tau': t}
    if t != k:
        res['counterexample'] = False
        return res
    sat = has_k_disjoint_dijoins(n, arcs, k)
    res['packs'] = sat
    res['counterexample'] = not sat
    if verbose or not sat:
        res['rho'] = rho(n, arcs, k)
        res['planar'] = is_planar(n, arcs)
        res['ss_connected'] = is_source_sink_connected(n, arcs)
        res['chordal'] = is_chordal_underlying(n, arcs)
    return res

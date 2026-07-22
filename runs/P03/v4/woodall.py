"""Core tools for P03 (Woodall's conjecture) V4: LP/ILP integrality-gap search.

Digraph representation: (n, arcs) where arcs is a tuple of (u, v) pairs,
0 <= u, v < n, u != v. Parallel arcs allowed (multiset).

Key quantities:
  tau(D)          = size of a minimum nonempty dicut (via ideal enumeration of
                    the condensation DAG).
  pack_ilp(D, k)  = True iff there exist k pairwise disjoint dijoins
                    (ILP feasibility, dicut rows generated lazily).
  pack_lp(D, k)   = LP relaxation value of the same model (for gap diagnostics).

A dicut is delta+(U) for a proper nonempty U with delta-(U) = 0 (U is an
"ideal": no arc enters U). A dijoin is an arc set J meeting every dicut,
equivalently D with the arcs of J made bidirectional is strongly connected.
"""

import itertools
import random
from functools import lru_cache

import pulp


# ---------------------------------------------------------------------------
# basic digraph utilities (no external graph lib; keep it self-contained)
# ---------------------------------------------------------------------------

def tarjan_scc(n, adj):
    """Iterative Tarjan. Returns comp[] labels, 0..k-1, in reverse topo order."""
    index = [None] * n
    low = [0] * n
    onstack = [False] * n
    stack = []
    comp = [None] * n
    ncomp = 0
    counter = 0
    for root in range(n):
        if index[root] is not None:
            continue
        work = [(root, 0)]
        while work:
            v, pi = work[-1]
            if pi == 0:
                index[v] = low[v] = counter
                counter += 1
                stack.append(v)
                onstack[v] = True
            recurse = False
            for i in range(pi, len(adj[v])):
                w = adj[v][i]
                if index[w] is None:
                    work[-1] = (v, i + 1)
                    work.append((w, 0))
                    recurse = True
                    break
                elif onstack[w]:
                    low[v] = min(low[v], index[w])
            if recurse:
                continue
            if pi < len(adj[v]):
                pass
            # done with v
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[v])
            if low[v] == index[v]:
                while True:
                    w = stack.pop()
                    onstack[w] = False
                    comp[w] = ncomp
                    if w == v:
                        break
                ncomp += 1
    return comp, ncomp


def adjacency(n, arcs, extra_bidir=()):
    adj = [[] for _ in range(n)]
    for (u, v) in arcs:
        adj[u].append(v)
    for (u, v) in extra_bidir:
        adj[v].append(u)
    return adj


def is_strongly_connected(n, arcs, extra_bidir=()):
    adj = adjacency(n, arcs, extra_bidir)
    _, k = tarjan_scc(n, adj)
    return k == 1


def condensation(n, arcs):
    adj = adjacency(n, arcs)
    comp, k = tarjan_scc(n, adj)
    dag_arcs = set()
    for (u, v) in arcs:
        if comp[u] != comp[v]:
            dag_arcs.add((comp[u], comp[v]))
    return comp, k, dag_arcs


def enumerate_ideals(k, dag_arcs):
    """All ideals (no incoming arc from outside) of DAG on k nodes.
    An ideal here: set S with no arc from V\\S into S -- i.e. closed under
    predecessors' absence: if (a,b) arc and b in S then a in S? No:
    delta-(U)=0 means no arc enters U, so for arc (a,b), b in U => a in U.
    So U is closed under taking predecessors: an 'up-set' of the reverse
    order = down-closed under predecessors. Enumerate by DFS over nodes.
    """
    preds = [[] for _ in range(k)]
    for (a, b) in dag_arcs:
        preds[b].append(a)
    ideals = []
    # brute force over subsets when k small; else incremental
    if k <= 20:
        for mask in range(1, (1 << k) - 1):
            ok = True
            for b in range(k):
                if (mask >> b) & 1:
                    for a in preds[b]:
                        if not (mask >> a) & 1:
                            ok = False
                            break
                    if not ok:
                        break
            if ok:
                ideals.append(mask)
    else:
        raise ValueError("too many components")
    return ideals


def all_dicuts(n, arcs):
    """Return list of dicuts, each a frozenset of arc indices. Empty if
    strongly connected."""
    comp, k, dag_arcs = condensation(n, arcs)
    if k == 1:
        return []
    dicuts = []
    for mask in enumerate_ideals(k, dag_arcs):
        cut = frozenset(i for i, (u, v) in enumerate(arcs)
                        if (mask >> comp[u]) & 1 and not (mask >> comp[v]) & 1)
        # sanity: no arc enters U
        dicuts.append(cut)
    return dicuts


def min_dicut(n, arcs):
    """tau = min |dicut| over nonempty dicuts; None if strongly connected.
    Note: dicuts from ideals are exactly all dicuts; a dicut could be empty
    only if the graph is disconnected between parts -- an empty dicut means
    tau = 0 (degenerate; Woodall needs nonempty dicuts so we require weak
    connectivity in generators, but handle it)."""
    cuts = all_dicuts(n, arcs)
    if not cuts:
        return None
    return min(len(c) for c in cuts)


def is_dijoin(n, arcs, arc_subset):
    """J is a dijoin iff adding reversal of J's arcs makes D strongly conn."""
    extra = [arcs[i] for i in arc_subset]
    return is_strongly_connected(n, arcs, extra_bidir=extra)


def find_dicut_avoiding(n, arcs, arc_subset):
    """Return a dicut (frozenset of arc indices) disjoint from arc_subset,
    or None if arc_subset is a dijoin. Uses condensation of D + rev(J):
    any ideal of that condensation yields a dicut of D with no J arc."""
    extra = [arcs[i] for i in arc_subset]
    adj = adjacency(n, arcs, extra_bidir=extra)
    comp, k = tarjan_scc(n, adj)
    if k == 1:
        return None
    # find a source component set: take an ideal = all comps that cannot be
    # reached... simplest: pick minimal ideal = a source in the comp DAG of
    # the augmented graph; U = its vertices. delta-_D(U) may include only
    # arcs whose reversal we added? No: augmented condensation ideal U has no
    # augmented arc entering U, in particular no D arc enters U and no rev(J)
    # arc enters U (i.e., no J arc leaves U). So delta+_D(U) is a dicut of D
    # disjoint from J. Pick the ideal minimizing cut size among sources.
    dag_preds = [set() for _ in range(k)]
    for (u, v) in arcs:
        if comp[u] != comp[v]:
            dag_preds[comp[v]].add(comp[u])
    for (u, v) in extra:
        # reverse arc v->u
        if comp[v] != comp[u]:
            dag_preds[comp[u]].add(comp[v])
    # sources of augmented condensation
    best = None
    for c in range(k):
        if not dag_preds[c]:
            U = set(v for v in range(n) if comp[v] == c)
            cut = frozenset(i for i, (u, v) in enumerate(arcs)
                            if u in U and v not in U)
            if best is None or len(cut) < len(best):
                best = cut
    assert best is not None
    return best


# ---------------------------------------------------------------------------
# packing via ILP with lazy dicut generation
# ---------------------------------------------------------------------------

def pack(n, arcs, k, relax=False, time_limit=60, init_cuts=None):
    """Try to find k pairwise disjoint dijoins.
    Returns (feasible: bool, info dict). If relax=True solves the LP
    relaxation instead and returns (lp_feasible, info with 'fractional').
    Lazy row generation: start with the minimal dicuts from source/sink
    components, resolve, separate per class with find_dicut_avoiding.
    """
    m = len(arcs)
    cuts = set(init_cuts or [])
    if not cuts:
        # seed with all dicuts if cheap, else the source/sink ones
        allc = all_dicuts(n, arcs)
        if allc and len(allc) <= 2000:
            cuts = set(allc)
        else:
            cuts = set(allc[:50])
    if not cuts:
        return False, {"reason": "no dicuts (strongly connected)"}

    rounds = 0
    while True:
        rounds += 1
        prob = pulp.LpProblem("pack", pulp.LpMinimize)
        cat = "Continuous" if relax else "Binary"
        x = {(i, j): pulp.LpVariable(f"x_{i}_{j}", 0, 1, cat)
             for i in range(m) for j in range(k)}
        for i in range(m):
            prob += pulp.lpSum(x[(i, j)] for j in range(k)) <= 1
        for cset in cuts:
            for j in range(k):
                prob += pulp.lpSum(x[(i, j)] for i in cset) >= 1
        prob += 0  # feasibility
        status = prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit))
        if pulp.LpStatus[status] != "Optimal":
            return False, {"status": pulp.LpStatus[status], "rounds": rounds,
                           "ncuts": len(cuts)}
        if relax:
            vals = {key: x[key].value() for key in x}
            frac = sum(1 for v in vals.values() if 1e-6 < v < 1 - 1e-6)
            return True, {"fractional_vars": frac, "rounds": rounds,
                          "ncuts": len(cuts), "vals": vals}
        # integral: separate
        violated = False
        for j in range(k):
            J = [i for i in range(m) if (x[(i, j)].value() or 0) > 0.5]
            new_cut = find_dicut_avoiding(n, arcs, J)
            if new_cut is not None:
                if new_cut in cuts:
                    # shouldn't happen: cut in model but class misses it?
                    raise RuntimeError("separation returned known cut")
                cuts.add(new_cut)
                violated = True
        if not violated:
            classes = [[i for i in range(m) if (x[(i, j)].value() or 0) > 0.5]
                       for j in range(k)]
            return True, {"classes": classes, "rounds": rounds,
                          "ncuts": len(cuts)}


def max_packing(n, arcs, tau=None, time_limit=60):
    """Return (tau, nu) with nu = max number of disjoint dijoins (capped at
    tau, since nu <= tau always)."""
    if tau is None:
        tau = min_dicut(n, arcs)
    if tau is None or tau == 0:
        return tau, None
    k = tau
    while k >= 1:
        ok, info = pack(n, arcs, k, time_limit=time_limit)
        if ok:
            return tau, k
        k -= 1
    return tau, 0


# ---------------------------------------------------------------------------
# canonical form (cheap isomorph rejection)
# ---------------------------------------------------------------------------

def canon_key(n, arcs, tries=30, rng=None):
    """Cheap canonical-ish key: refine by (indeg,outdeg) then hash sorted arc
    multiset under best-of random relabelings within classes. Not exact
    isomorphism, but good enough to dedupe most repeats."""
    indeg = [0] * n
    outdeg = [0] * n
    for (u, v) in arcs:
        outdeg[u] += 1
        indeg[v] += 1
    base = tuple(sorted((indeg[v], outdeg[v]) for v in range(n)))
    ms = sorted(((indeg[u], outdeg[u]), (indeg[v], outdeg[v]))
                for (u, v) in arcs)
    # exact labeled arc multiset appended: dedup only true repeats.  The
    # coarse degree-based key alone over-blocked the search near structured
    # seeds (many non-isomorphic graphs share degree data).
    return (n, len(arcs), base, tuple(ms), tuple(sorted(arcs)))

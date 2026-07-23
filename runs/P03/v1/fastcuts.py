#!/usr/bin/env python3
"""Fast dicut enumeration for larger n: sets U with delta^-(U)=0 are exactly
the ancestor-closed unions of strong components, i.e. the down-sets (order
ideals, w.r.t. reversed reachability) of the condensation poset. Enumerate
ideals recursively instead of scanning 2^n subsets."""
import sys
sys.setrecursionlimit(100000)


def strong_components(n, arcs):
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]
    for (u, v) in arcs:
        adj[u].append(v); radj[v].append(u)
    order = []; seen = [False] * n
    for s in range(n):
        if seen[s]:
            continue
        stack = [(s, 0)]
        seen[s] = True
        while stack:
            v, i = stack[-1]
            if i < len(adj[v]):
                stack[-1] = (v, i + 1)
                w = adj[v][i]
                if not seen[w]:
                    seen[w] = True
                    stack.append((w, 0))
            else:
                order.append(v); stack.pop()
    comp = [-1] * n; c = 0
    for v in reversed(order):
        if comp[v] != -1:
            continue
        stack = [v]; comp[v] = c
        while stack:
            x = stack.pop()
            for w in radj[x]:
                if comp[w] == -1:
                    comp[w] = c
                    stack.append(w)
        c += 1
    return comp, c


def min_dicuts(n, arcs):
    """Return (list of inclusion-minimal dicuts as frozensets of arc indices,
    tau) or (None, None) if no dicut / weakly disconnected."""
    # weak connectivity
    und = [[] for _ in range(n)]
    for (u, v) in arcs:
        und[u].append(v); und[v].append(u)
    seen = {0}; st = [0]
    while st:
        x = st.pop()
        for y in und[x]:
            if y not in seen:
                seen.add(y); st.append(y)
    if len(seen) != n:
        return None, None

    comp, nc = strong_components(n, arcs)
    if nc == 1:
        return None, None
    # condensation DAG: preds[c] = set of components with an arc into c
    preds = [set() for _ in range(nc)]
    succs = [set() for _ in range(nc)]
    arcs_between = {}
    for i, (u, v) in enumerate(arcs):
        cu, cv = comp[u], comp[v]
        if cu != cv:
            preds[cv].add(cu); succs[cu].add(cv)
            arcs_between.setdefault((cu, cv), []).append(i)
    # ancestors closure per component
    anc = [None] * nc
    def get_anc(c):
        if anc[c] is None:
            a = set()
            for p in preds[c]:
                a.add(p); a |= get_anc(p)
            anc[c] = a
        return anc[c]
    for c in range(nc):
        get_anc(c)
    # enumerate ancestor-closed sets U (nonempty, proper) via ideal DFS
    cuts = set()
    full = (1 << nc) - 1
    def ideal_of(c):
        m = 1 << c
        for a in anc[c]:
            m |= 1 << a
        return m
    ideals = {0}
    for c in range(nc):  # BFS over adding one component (+its ancestors)
        newi = set()
        for I in ideals:
            J = I | ideal_of(c)
            newi.add(J)
        ideals |= newi
    for I in ideals:
        if I == 0 or I == full:
            continue
        cut = []
        ok = True
        for (cu, cv), idxs in arcs_between.items():
            if (I >> cu) & 1 and not (I >> cv) & 1:
                cut.extend(idxs)
        if cut:
            cuts.add(frozenset(cut))
    if not cuts:
        return None, None
    cuts = sorted(cuts, key=len)
    minimal = []
    for c in cuts:
        if not any(m <= c for m in minimal):
            minimal.append(c)
    return minimal, len(minimal[0])

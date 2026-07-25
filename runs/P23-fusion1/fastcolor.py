"""Cheap exact 4-colorability check via structural reduction, then SAT.

The bottleneck of the whole exact-LNS approach is the non-4-colorability check:
1-3 s at 509 vertices but > 8 min at the 1924-vertex W16 witness (E28). Two
classical reductions apply before any solver is called, and both preserve
4-colorability exactly:

* **degree peeling** - a vertex of degree <= 3 can always be coloured last, so
  G is 4-colorable iff G minus that vertex is;
* **block decomposition** - colourings of two blocks sharing a cut vertex can be
  merged after permuting colours, so G is 4-colorable iff every biconnected
  block is.

Both are exact, so an UNSAT verdict here is as good as one from the flat
encoding; only the cost changes.  A triangle is colour-fixed inside each block
(unit-distance graphs in the plane contain no K4, so a triangle is the largest
clique available for symmetry breaking).
"""
import subprocess
import sys

from sat import color_cnf, write_cnf, KISSAT


def peel(V, adjmap, k=4):
    """Repeatedly drop vertices of degree < k (they never obstruct)."""
    live = set(V)
    while True:
        drop = {v for v in live if len(adjmap[v] & live) < k}
        if not drop:
            return live
        live -= drop


def blocks(live, adjmap):
    """Biconnected components (iterative Hopcroft-Tarjan)."""
    out, seen = [], set()
    num, low, stack = {}, {}, []
    counter = 0
    for root in live:
        if root in seen:
            continue
        work = [(root, None, iter(sorted(adjmap[root] & live)))]
        seen.add(root)
        num[root] = low[root] = counter
        counter += 1
        while work:
            v, parent, it = work[-1]
            advanced = False
            for u in it:
                if u == parent:
                    continue
                if u in num:
                    if num[u] < num[v]:
                        stack.append((v, u))
                        low[v] = min(low[v], num[u])
                else:
                    stack.append((v, u))
                    seen.add(u)
                    num[u] = low[u] = counter
                    counter += 1
                    work.append((u, v, iter(sorted(adjmap[u] & live))))
                    advanced = True
                    break
            if advanced:
                continue
            work.pop()
            if work:
                p = work[-1][0]
                low[p] = min(low[p], low[v])
                if low[v] >= num[p]:
                    comp = []
                    while stack:
                        e = stack.pop()
                        comp.append(e)
                        if e == (p, v):
                            break
                    if comp:
                        out.append(comp)
    return out


def sat_4color(vs, edges, tag):
    """None if not 4-colorable, else a colouring dict."""
    S = sorted(vs)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in edges]
    nvars, cls = color_cnf(len(S), E2, 4)
    # symmetry breaking: fix a triangle's colours (no K4 exists in a plane UDG)
    tri = None
    inc = {}
    for u, v in E2:
        inc.setdefault(u, set()).add(v)
        inc.setdefault(v, set()).add(u)
    for u, v in E2:
        common = inc.get(u, set()) & inc.get(v, set())
        if common:
            tri = (u, v, min(common))
            break
    if tri:
        for i, x in enumerate(tri):
            cls.append([4 * x + i + 1])
    cnf = f'/tmp/fc_{tag}.cnf'
    write_cnf(cnf, nvars, cls)
    r = subprocess.run([KISSAT, cnf], capture_output=True, text=True)
    if 's UNSATISFIABLE' in r.stdout:
        return None
    pos = {int(x) for line in r.stdout.splitlines() if line.startswith('v ')
           for x in line[2:].split() if int(x) > 0}
    return {v: c for i, v in enumerate(S) for c in range(4)
            if 4 * i + c + 1 in pos}


def is_4colorable(V, adjmap, tag='fc'):
    live = peel(V, adjmap)
    if not live:
        return True
    for comp in blocks(live, adjmap):
        vs = {x for e in comp for x in e}
        if len(vs) < 5:
            continue
        if sat_4color(vs, comp, tag) is None:
            return False
    return True


if __name__ == '__main__':
    import os
    import pickle
    import time
    import coremin
    S = sorted(pickle.load(open(sys.argv[1], 'rb')))
    Sset = set(S)
    adjmap = {v: coremin.adj[v] & Sset for v in S}
    t0 = time.time()
    live = peel(S, adjmap)
    bs = sorted((len({x for e in c for x in e}) for c in blocks(live, adjmap)),
                reverse=True)
    print(f'{len(S)} vertices -> peeled {len(live)}, blocks {bs[:5]}'
          f' ({round(time.time()-t0, 1)}s)', flush=True)
    print('4-colorable:', is_4colorable(S, adjmap, os.getpid()),
          round(time.time() - t0, 1), 's')

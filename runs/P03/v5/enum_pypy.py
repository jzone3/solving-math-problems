"""
Pure-python (PyPy-friendly) exhaustive orientation enumerator for cubic
graphs (justification chain in orient_exhaust.py). Reads JSON lines
{"g6":..., "edges": [[u,v],...]} (pre-filtered: non-planar, 3-edge-connected)
and writes candidate orientations (allowed degree profile, acyclic, NOT
source-sink connected) as JSON lines to stdout for SAT checking in CPython.

Usage: pypy3 enum_pypy.py n start end < keptN.jsonl > candN.jsonl
"""

import sys
import json
import time
import random

PROFILES = {
    12: {(2, 2, 4, 4)},
    14: {(2, 2, 5, 5), (3, 3, 4, 4), (2, 3, 6, 3), (3, 2, 3, 6)},
    16: {(2, 2, 6, 6), (3, 3, 5, 5), (4, 4, 4, 4), (2, 3, 7, 4), (3, 2, 4, 7),
         (2, 4, 8, 2), (4, 2, 2, 8), (3, 4, 6, 3), (4, 3, 3, 6)},
}


def ss_connected(n, arcs):
    adj = [0] * n
    ind = [0] * n
    outd = [0] * n
    for (u, v) in arcs:
        adj[u] |= (1 << v)
        outd[u] += 1
        ind[v] += 1
    reach = list(adj)
    for _ in range(n):
        changed = False
        for v in range(n):
            r = reach[v]
            m = reach[v]
            while m:
                w = (m & -m).bit_length() - 1
                r |= reach[w]
                m &= m - 1
            if r != reach[v]:
                reach[v] = r
                changed = True
        if not changed:
            break
    sinks = 0
    for v in range(n):
        if outd[v] == 0:
            sinks |= (1 << v)
    for v in range(n):
        if ind[v] == 0 and (reach[v] & sinks) != sinks:
            return False
    return True


def dicut_structure_ok(n, arcs):
    """Schrijver reduced form: every dicut of size 3 must be delta+(source)
    (closed set U = {source}) or delta-(sink) (U = V minus {sink}).
    Enumerates all closed sets U (down-sets of the reachability poset) with
    an incremental dicut-size counter; returns False if some size-3 dicut
    is not a source/sink star."""
    outd = [0] * n
    ind = [0] * n
    inmask = [0] * n
    adj = [[] for _ in range(n)]
    for (u, v) in arcs:
        outd[u] += 1
        ind[v] += 1
        inmask[v] |= (1 << u)
        adj[u].append(v)
    # topological order (graph is a DAG by construction)
    indeg = ind[:]
    order = [v for v in range(n) if indeg[v] == 0]
    qi = 0
    while qi < len(order):
        u = order[qi]
        qi += 1
        for w in adj[u]:
            indeg[w] -= 1
            if indeg[w] == 0:
                order.append(w)
    full = (1 << n) - 1

    def rec(i, mask, cnt, size):
        if i == n:
            if cnt == 3 and 0 < size < n:
                if size == 1:
                    v = mask.bit_length() - 1
                    return ind[v] == 0
                if size == n - 1:
                    v = (full ^ mask).bit_length() - 1
                    return outd[v] == 0
                return False
            return True
        v = order[i]
        if not rec(i + 1, mask, cnt, size):
            return False
        if (inmask[v] & mask) == inmask[v]:
            return rec(i + 1, mask | (1 << v), cnt + outd[v] - ind[v],
                       size + 1)
        return True

    return rec(0, 0, 0, 0)


def _strong(n, adjm):
    """Strong connectivity via bitmask forward/backward reach from vertex 0."""
    reach = 1
    while True:
        new = reach
        m = reach
        while m:
            v = (m & -m).bit_length() - 1
            new |= adjm[v]
            m &= m - 1
        if new == reach:
            break
        reach = new
    full = (1 << n) - 1
    if reach != full:
        return False
    radm = [0] * n
    for u in range(n):
        m = adjm[u]
        while m:
            v = (m & -m).bit_length() - 1
            radm[v] |= (1 << u)
            m &= m - 1
    reach = 1
    while True:
        new = reach
        m = reach
        while m:
            v = (m & -m).bit_length() - 1
            new |= radm[v]
            m &= m - 1
        if new == reach:
            break
        reach = new
    return reach == full


def try_pack(n, arcs, rng, tries=40):
    """Randomized search for a partition into 3 dijoins. Colors source
    out-stars and sink in-stars rainbow (necessary), rest random; validates
    each color class as a dijoin (adding its reverse arcs must make the
    digraph strongly connected). Returns True if a packing was found."""
    m = len(arcs)
    ind = [0] * n
    outd = [0] * n
    for (u, v) in arcs:
        ind[v] += 1
        outd[u] += 1
    src_stars = []
    snk_stars = []
    for v in range(n):
        if ind[v] == 0:
            src_stars.append([i for i, a in enumerate(arcs) if a[0] == v])
        if outd[v] == 0:
            snk_stars.append([i for i, a in enumerate(arcs) if a[1] == v])
    base = [0] * n
    for (u, v) in arcs:
        base[u] |= (1 << v)
    for _ in range(tries):
        color = [rng.randrange(3) for _ in range(m)]
        for star in src_stars + snk_stars:
            perm = [0, 1, 2]
            rng.shuffle(perm)
            for j, i in enumerate(star):
                color[i] = perm[j]
        ok = True
        for c in range(3):
            adjm = base[:]
            for i in range(m):
                if color[i] == c:
                    u, v = arcs[i]
                    adjm[v] |= (1 << u)
            if not _strong(n, adjm):
                ok = False
                break
        if ok:
            return True
    return False


def minimal_dicuts_pp(n, arcs):
    """All inclusion-minimal dicuts (as frozensets of arc indices), via
    down-set enumeration of the reachability poset."""
    ind = [0] * n
    inmask = [0] * n
    outidx = [[] for _ in range(n)]
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(arcs):
        ind[v] += 1
        inmask[v] |= (1 << u)
        outidx[u].append(i)
        adj[u].append(v)
    indeg = ind[:]
    order = [v for v in range(n) if indeg[v] == 0]
    qi = 0
    while qi < len(order):
        u = order[qi]
        qi += 1
        for w in adj[u]:
            indeg[w] -= 1
            if indeg[w] == 0:
                order.append(w)
    cuts = []

    def rec(i, mask, size):
        if i == n:
            if 0 < size < n:
                cut = []
                for u in range(n):
                    if mask & (1 << u):
                        for j in outidx[u]:
                            if not (mask & (1 << arcs[j][1])):
                                cut.append(j)
                cuts.append(frozenset(cut))
            return
        v = order[i]
        rec(i + 1, mask, size)
        if (inmask[v] & mask) == inmask[v]:
            rec(i + 1, mask | (1 << v), size + 1)

    rec(0, 0, 0)
    cuts = sorted(set(cuts), key=len)
    minimal = []
    for c in cuts:
        if not any(m2 < c for m2 in minimal):
            minimal.append(c)
    return minimal


def exact_pack(n, arcs):
    """Exact test: can arcs be 3-colored so every minimal dicut gets all 3
    colors (equivalently, D partitions into 3 dijoins)? Pure-python
    backtracking with per-cut color/remaining propagation."""
    m = len(arcs)
    cuts = [sorted(c) for c in minimal_dicuts_pp(n, arcs)]
    ncuts = len(cuts)
    arc_cuts = [[] for _ in range(m)]
    for ci, c in enumerate(cuts):
        for j in c:
            arc_cuts[j].append(ci)
    # order arcs: those in small cuts first
    arc_order = sorted(range(m),
                       key=lambda j: min([len(cuts[c]) for c in arc_cuts[j]]
                                         or [99]))
    used = [0] * ncuts        # bitmask of colors present in cut
    left = [len(c) for c in cuts]
    color = [-1] * m

    def rec(k):
        if k == m:
            return True
        j = arc_order[k]
        opts = (0, 1, 2) if k > 0 else (0,)   # symmetry: fix first arc
        for col in opts:
            ok = True
            changed = []
            for ci in arc_cuts[j]:
                u2 = used[ci] | (1 << col)
                left[ci] -= 1
                changed.append((ci, used[ci]))
                used[ci] = u2
                need = 3 - bin(u2).count("1")
                if need > left[ci]:
                    ok = False
                    break
            if ok:
                color[j] = col
                if rec(k + 1):
                    return True
                color[j] = -1
            for (ci, old) in changed:
                used[ci] = old
                left[ci] += 1
        return False

    return rec(0)


def search_graph(n, g6, edges, profiles, out, stats):
    rng = random.Random(12345)
    m = len(edges)
    max_s = max(p[0] for p in profiles)
    max_t = max(p[1] for p in profiles)
    max_a = max(p[2] for p in profiles)
    max_b = max(p[3] for p in profiles)
    outd = [0] * n
    ind = [0] * n
    done = [0] * n
    reach = [0] * n
    arcs = []
    cnt = [0, 0, 0, 0]        # s, t, a, b
    caps = [max_s, max_t, max_a, max_b]

    def leaf():
        stats['dags'] += 1
        if tuple(cnt) not in profiles:
            return
        stats['profile_dags'] += 1
        if ss_connected(n, arcs):
            stats['ss_skip'] += 1
            return
        if not dicut_structure_ok(n, arcs):
            stats['dicut_skip'] += 1
            return
        if try_pack(n, arcs, rng, tries=5):
            stats['packed_heur'] += 1
            return
        if exact_pack(n, arcs):
            stats['packed_exact'] += 1
            return
        # candidate NON-PACKING instance: emit for independent CPython/SAT
        # verification (this would be a counterexample!)
        stats['cand'] += 1
        out.write(json.dumps({"g6": g6, "arcs": arcs}) + "\n")
        out.flush()

    def rec(i):
        if i == m:
            leaf()
            return
        u, v = edges[i]
        for (x, y) in ((u, v), (v, u)):
            if outd[x] >= 3 or ind[y] >= 3:
                continue
            if reach[y] & (1 << x):
                continue
            outd[x] += 1
            ind[y] += 1
            done[x] += 1
            done[y] += 1
            finals = []
            ok = True
            for w in (x, y):
                if done[w] == 3:
                    if ind[w] == 0:
                        r = 0
                    elif outd[w] == 0:
                        r = 1
                    elif ind[w] == 1:
                        r = 2
                    else:
                        r = 3
                    cnt[r] += 1
                    finals.append(r)
                    if cnt[r] > caps[r]:
                        ok = False
            if ok:
                saved = reach[:]
                add = reach[y] | (1 << y)
                for w in range(n):
                    if w == x or (reach[w] & (1 << x)):
                        reach[w] |= add
                arcs.append((x, y))
                rec(i + 1)
                arcs.pop()
                for w in range(n):
                    reach[w] = saved[w]
            for r in finals:
                cnt[r] -= 1
            outd[x] -= 1
            ind[y] -= 1
            done[x] -= 1
            done[y] -= 1

    rec(0)


if __name__ == "__main__":
    n = int(sys.argv[1])
    lines = [l for l in sys.stdin if l.strip()]
    if len(sys.argv) > 3:
        lines = lines[int(sys.argv[2]):int(sys.argv[3])]
    profiles = PROFILES[n]
    stats = {'graphs': 0, 'dags': 0, 'profile_dags': 0, 'ss_skip': 0,
             'dicut_skip': 0, 'packed_heur': 0, 'packed_exact': 0, 'cand': 0}
    t0 = time.time()
    out = sys.stdout
    for gi, line in enumerate(lines):
        rec_in = json.loads(line)
        edges = [tuple(e) for e in rec_in["edges"]]
        stats['graphs'] += 1
        search_graph(n, rec_in["g6"], edges, profiles, out, stats)
        sys.stderr.write("[%d/%d] %s t=%.0fs\n"
                         % (gi + 1, len(lines), stats, time.time() - t0))
        sys.stderr.flush()
    sys.stderr.write("DONE %s wall=%.0fs\n" % (stats, time.time() - t0))

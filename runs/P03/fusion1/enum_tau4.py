"""Exhaustive reduced tau=4 orientation search for the n=10 cell."""

import json
import sys
import time
from collections import Counter

from enum_pypy import (minimal_dicuts_pp, ss_connected, _violated_cut,
                       star_cuts)

PROFILES = {(2, 2, 3, 3)}
K = 4


def rho(n, arcs):
    excess = [0] * n
    for u, v in arcs:
        excess[u] += 1
        excess[v] -= 1
    return sum(x % K for x in excess) // K


def exact_pack_cegar4(n, arcs, seed_cuts):
    m = len(arcs)
    cuts = [list(c) for c in seed_cuts]
    while True:
        arc_cuts = [[] for _ in range(m)]
        for ci, cut in enumerate(cuts):
            for j in cut:
                arc_cuts[j].append(ci)
        constrained = [j for j in range(m) if arc_cuts[j]]
        constrained.sort(key=lambda j: min(len(cuts[c]) for c in arc_cuts[j]))
        used = [0] * len(cuts)
        left = [len(c) for c in cuts]
        color = [0] * m

        def rec(k):
            if k == len(constrained):
                return True
            j = constrained[k]
            opts = range(K) if k else (0,)
            for col in opts:
                changed = []
                ok = True
                for ci in arc_cuts[j]:
                    old = used[ci]
                    used[ci] |= 1 << col
                    left[ci] -= 1
                    changed.append((ci, old))
                    if K - bin(used[ci]).count("1") > left[ci]:
                        ok = False
                        break
                if ok:
                    color[j] = col
                    if rec(k + 1):
                        return True
                for ci, old in changed:
                    used[ci] = old
                    left[ci] += 1
            return False

        if not rec(0):
            return False
        violated = None
        for col in range(K):
            violated = _violated_cut(n, arcs, color, col)
            if violated is not None:
                break
        if violated is None:
            return True
        cuts.append(violated)


def reduced_dicut_ok(n, arcs):
    indeg = [0] * n
    outdeg = [0] * n
    for u, v in arcs:
        outdeg[u] += 1
        indeg[v] += 1
    for cut in minimal_dicuts_pp(n, arcs):
        if len(cut) != K:
            continue
        tails = {arcs[i][0] for i in cut}
        heads = {arcs[i][1] for i in cut}
        if len(tails) == 1:
            v = next(iter(tails))
            if indeg[v] == 0 and outdeg[v] == K:
                continue
        if len(heads) == 1:
            v = next(iter(heads))
            if outdeg[v] == 0 and indeg[v] == K:
                continue
        return False
    return True


def profile(n, arcs, degrees):
    indeg = [0] * n
    outdeg = [0] * n
    for u, v in arcs:
        outdeg[u] += 1
        indeg[v] += 1
    s = t = a = b = 0
    for v in range(n):
        if indeg[v] == 0 and degrees[v] == 4:
            s += 1
        elif outdeg[v] == 0 and degrees[v] == 4:
            t += 1
        elif (indeg[v], outdeg[v]) == (1, 2) and degrees[v] == 3:
            a += 1
        elif (indeg[v], outdeg[v]) == (2, 1) and degrees[v] == 3:
            b += 1
        else:
            return None
    return s, t, a, b


def orientations(n, edges, degrees, stats):
    outd = [0] * n
    ind = [0] * n
    done = [0] * n
    reach = [0] * n
    arcs = []

    def rec(i):
        if i == len(edges):
            stats["orientations"] += 1
            p = profile(n, arcs, degrees)
            if p in PROFILES:
                stats["profile"] += 1
                if rho(n, arcs) < 3 or rho(n, [(v, u) for u, v in arcs]) < 3:
                    return
                if ss_connected(n, arcs):
                    stats["ss_skip"] += 1
                    return
                cuts = minimal_dicuts_pp(n, arcs)
                if not cuts or min(len(c) for c in cuts) != K:
                    stats["tau_skip"] += 1
                    return
                stats["tau4"] += 1
                if not reduced_dicut_ok(n, arcs):
                    stats["dicut_skip"] += 1
                    return
                stats["structural"] += 1
                if exact_pack_cegar4(n, arcs, star_cuts(n, arcs)):
                    stats["packed"] += 1
                else:
                    stats["cand"] += 1
                    print(json.dumps({"arcs": arcs}), flush=True)
            return
        u, v = edges[i]
        for x, y in ((u, v), (v, u)):
            if outd[x] >= degrees[x] or ind[y] >= degrees[y]:
                continue
            if reach[y] & (1 << x):
                continue
            outd[x] += 1
            ind[y] += 1
            done[x] += 1
            done[y] += 1
            saved = reach[:]
            add = reach[y] | (1 << y)
            for w in range(n):
                if w == x or (reach[w] & (1 << x)):
                    reach[w] |= add
            arcs.append((x, y))
            rec(i + 1)
            arcs.pop()
            reach[:] = saved
            done[x] -= 1
            done[y] -= 1
            outd[x] -= 1
            ind[y] -= 1

    rec(0)


if __name__ == "__main__":
    lines = [x.strip() for x in sys.stdin if x.strip()]
    if len(sys.argv) > 3:
        lines = lines[int(sys.argv[2]):int(sys.argv[3])]
    stats = Counter()
    start = time.time()
    for gi, line in enumerate(lines):
        rec = json.loads(line)
        edges = [tuple(e) for e in rec["edges"]]
        degrees = rec["degrees"]
        stats["graphs"] += 1
        orientations(len(degrees), edges, degrees, stats)
        print(f"[{gi+1}/{len(lines)}] {dict(stats)} t={time.time()-start:.0f}s",
              file=sys.stderr, flush=True)
    print(f"DONE {dict(stats)} wall={time.time()-start:.0f}s",
          file=sys.stderr, flush=True)

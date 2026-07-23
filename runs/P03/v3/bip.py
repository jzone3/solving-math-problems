"""Search the ACZ-complete target class: sink-regular (3,4)-bipartite digraphs.

ACZ (arXiv:2202.00392, Stage 0 'Decompose, Lift, and Reduce', valid unweighted for
tau>=3) reduce tau=3 Woodall to this class: if any tau=3 counterexample exists, then a
counterexample exists among sink-regular (3,4)-bipartite digraphs. Definitions:
  - bipartite digraph: every vertex is a source or a sink, all arcs source->sink;
  - every sink has in-degree exactly 3; every source has out-degree 3 or 4;
  - every dicut has size >= 3 (=> tau = 3);
  - rho(3,D,1) = |S4|/3 where S4 = degree-4 sources; ACZ safe for rho<=3, so a
    counterexample needs |S4| >= 12 (=> >= 12 sources, >= 16 sinks, >= 48 arcs, n >= 28);
  - planar underlying graph is LY-safe => require non-planar.

Dicuts: U = X u Y with nonempty X subseteq S, Y subseteq {t : N^-(t) subseteq X};
minimal dicuts take Y = Ymax(X); dicut arcs = {(s,t): s in X, t not in Ymax(X)}.

Representation: nbrs = list over sources of sorted tuple of sink ids (0..T-1).
"""
import json
import random
import sys
import time

from pysat.solvers import Minicard


def all_min_dicuts(nbrs, nT):
    """Return (tau, list of minimal dicuts as frozensets of arc indices).

    Arc index: (source i, j-th neighbor) -> arc_id[i][j].
    """
    nS = len(nbrs)
    arc_id = []
    k = 0
    for nb in nbrs:
        arc_id.append(list(range(k, k + len(nb))))
        k += len(nb)
    # in-neighbor sets of sinks as source bitmasks
    innb = [0] * nT
    for i, nb in enumerate(nbrs):
        for t in nb:
            innb[t] |= 1 << i
    dicuts = set()
    tau = None
    # sink in-arc dicuts: U = V \ {t} (arise from any closed X u Ymax by re-exposing t;
    # dicut(X, Ymax) alone misses these when the closed set has no leaving arcs)
    inarcs = [[] for _ in range(nT)]
    for i, nb in enumerate(nbrs):
        for j, t in enumerate(nb):
            inarcs[t].append(arc_id[i][j])
    for t in range(nT):
        if inarcs[t]:
            cut = frozenset(inarcs[t])
            dicuts.add(cut)
            if tau is None or len(cut) < tau:
                tau = len(cut)
    for X in range(1, 1 << nS):
        ymax = 0
        for t in range(nT):
            if innb[t] and (innb[t] & ~X) == 0:
                ymax |= 1 << t
        cut = []
        for i in range(nS):
            if (X >> i) & 1:
                for j, t in enumerate(nbrs[i]):
                    if not (ymax >> t) & 1:
                        cut.append(arc_id[i][j])
        if not cut:
            continue  # U would be V or have no leaving arcs -> not a dicut
        dicuts.add(frozenset(cut))
        if tau is None or len(cut) < tau:
            tau = len(cut)
    ds = sorted(dicuts, key=len)
    md = []
    for d in ds:
        if not any(x <= d for x in md):
            md.append(d)
    return tau, md


def pack3(nbrs, md):
    m = sum(len(nb) for nb in nbrs)
    cnf = []
    for i in range(m):
        vs = [3 * i + 1, 3 * i + 2, 3 * i + 3]
        cnf.append(vs)
        cnf.append([-vs[0], -vs[1]])
        cnf.append([-vs[0], -vs[2]])
        cnf.append([-vs[1], -vs[2]])
    for d in md:
        for c in range(3):
            cnf.append([3 * i + c + 1 for i in d])
    with Minicard(bootstrap_with=cnf) as s:
        return s.solve()


def nonplanar(nbrs, nT):
    import networkx as nx
    G = nx.Graph()
    nS = len(nbrs)
    G.add_nodes_from(range(nS + nT))
    for i, nb in enumerate(nbrs):
        for t in nb:
            G.add_edge(i, nS + t)
    return not nx.check_planarity(G)[0]


def gen_random(rng, n4, n3):
    """Random config-model bipartite digraph: n4 deg-4 + n3 deg-3 sources, sinks deg 3."""
    narcs = 4 * n4 + 3 * n3
    assert narcs % 3 == 0
    nT = narcs // 3
    while True:
        stubs = []
        for t in range(nT):
            stubs += [t] * 3
        rng.shuffle(stubs)
        nbrs = []
        k = 0
        ok = True
        for i in range(n4 + n3):
            deg = 4 if i < n4 else 3
            nb = stubs[k:k + deg]
            k += deg
            if len(set(nb)) != deg:  # no parallel arcs (simple)
                ok = False
                break
            nbrs.append(tuple(sorted(nb)))
        if ok:
            return nbrs, nT


def swap_mutate(nbrs, nT, rng, tries=30):
    """Degree-preserving double swap of two arcs."""
    nbrs = [list(nb) for nb in nbrs]
    for _ in range(tries):
        i1, i2 = rng.randrange(len(nbrs)), rng.randrange(len(nbrs))
        if i1 == i2:
            continue
        j1, j2 = rng.randrange(len(nbrs[i1])), rng.randrange(len(nbrs[i2]))
        t1, t2 = nbrs[i1][j1], nbrs[i2][j2]
        if t1 == t2 or t2 in nbrs[i1] or t1 in nbrs[i2]:
            continue
        nbrs[i1][j1], nbrs[i2][j2] = t2, t1
        return [tuple(sorted(nb)) for nb in nbrs]
    return None


def score(tau, md):
    if tau is None or tau < 3:
        return -1000 + (0 if tau is None else tau * 100), False
    tight = sum(1 for d in md if len(d) == 3)
    return 10 * tight + len(md), True


def run(seed, minutes, n4, n3, restart_steps=1200):
    rng = random.Random(seed)
    t0 = time.time()
    last = t0
    stats = {"iters": 0, "valid": 0, "sat": 0, "unsat": 0, "restarts": 0}
    best_ever = -10**9
    while time.time() - t0 < minutes * 60:
        stats["restarts"] += 1
        nbrs, nT = gen_random(rng, n4, n3)
        tau, md = all_min_dicuts(nbrs, nT)
        cur, valid = score(tau, md)
        stale = 0
        while stale < restart_steps and time.time() - t0 < minutes * 60:
            stats["iters"] += 1
            cand = swap_mutate(nbrs, nT, rng)
            if cand is None:
                stale += 1
                continue
            tau2, md2 = all_min_dicuts(cand, nT)
            s2, valid2 = score(tau2, md2)
            if s2 >= cur:
                improved = s2 > cur
                nbrs, cur = cand, s2
                if valid2:
                    stats["valid"] += 1
                    if nonplanar(cand, nT):
                        stats["sat"] += 1
                        if not pack3(cand, md2):
                            stats["unsat"] += 1
                            fn = f"witness_bip_{int(time.time())}.json"
                            with open(fn, "w") as f:
                                json.dump({"n4": n4, "n3": n3, "nT": nT,
                                           "nbrs": [list(nb) for nb in cand]}, f)
                            print(f"!!! UNSAT BIPARTITE CANDIDATE: {fn}", flush=True)
                            return
                stale = 0 if improved else stale + 1
                best_ever = max(best_ever, s2)
            else:
                stale += 1
            if time.time() - last > 120:
                last = time.time()
                print(f"[{int(time.time()-t0)}s] best={best_ever} cur={cur} {stats}",
                      flush=True)
    print(f"FINAL best={best_ever} {stats}", flush=True)


if __name__ == "__main__":
    seed = int(sys.argv[1])
    minutes = float(sys.argv[2])
    n4 = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    n3 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    run(seed, minutes, n4, n3)

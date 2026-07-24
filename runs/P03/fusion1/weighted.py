"""Weighted (Edmonds-Giles) analog, used to VALIDATE the gap detector.

Schrijver 1980 disproved the weighted version with a 0/1-weighted DAG on 9
vertices (tau_w = 2, nu_w = 1). If our machinery independently rediscovers a
weighted counterexample, the gap-detection pipeline (dicut enumeration +
lazy-separation packing ILP) demonstrably works end-to-end, which derisks the
unweighted (Woodall) search: any unweighted gap would be caught the same way.

nu(D,w) = max number of dijoins where each arc a is used <= w(a) times.
tau(D,w) = min over nonempty dicuts C of w(C). Note: dicuts with w(C)=0 are
allowed and make packing impossible (nu=0) but the conjectured relation is
still nu = tau (= 0), so they are not counterexamples; we require tau_w >= 1.
"""

import random
import sys
import time

import pulp

from woodall import all_dicuts, tarjan_scc


def tau_w(n, arcs, w):
    cuts = all_dicuts(n, arcs)
    if not cuts:
        return None, None
    best = None
    for c in cuts:
        wt = sum(w[i] for i in c)
        if best is None or wt < best[0]:
            best = (wt, c)
    return best[0], cuts


def find_dicut_avoiding_w(n, arcs, J):
    """dicut with no arc of J (J = multiset of arc indices used by a class).
    Same as unweighted separation."""
    adj = [[] for _ in range(n)]
    for (u, v) in arcs:
        adj[u].append(v)
    for i in J:
        u, v = arcs[i]
        adj[v].append(u)
    comp, k = tarjan_scc(n, adj)
    if k == 1:
        return None
    dag_preds = [set() for _ in range(k)]
    for (u, v) in arcs:
        if comp[u] != comp[v]:
            dag_preds[comp[v]].add(comp[u])
    for i in J:
        u, v = arcs[i]
        if comp[v] != comp[u]:
            dag_preds[comp[u]].add(comp[v])
    for c in range(k):
        if not dag_preds[c]:
            U = set(v for v in range(n) if comp[v] == c)
            return frozenset(i for i, (u, v) in enumerate(arcs)
                             if u in U and v not in U)
    raise RuntimeError("no source component")


def pack_w(n, arcs, w, k, time_limit=60):
    m = len(arcs)
    cuts = set(all_dicuts(n, arcs))
    while True:
        prob = pulp.LpProblem("packw", pulp.LpMinimize)
        x = {(i, j): pulp.LpVariable(f"x_{i}_{j}", 0, 1, "Binary")
             for i in range(m) for j in range(k)}
        for i in range(m):
            prob += pulp.lpSum(x[(i, j)] for j in range(k)) <= w[i]
        for cset in cuts:
            for j in range(k):
                prob += pulp.lpSum(x[(i, j)] for i in cset) >= 1
        prob += 0
        status = prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit))
        if pulp.LpStatus[status] != "Optimal":
            return False, None
        violated = False
        for j in range(k):
            J = [i for i in range(m) if (x[(i, j)].value() or 0) > 0.5]
            nc = find_dicut_avoiding_w(n, arcs, J)
            if nc is not None:
                assert nc not in cuts
                cuts.add(nc)
                violated = True
        if not violated:
            return True, [[i for i in range(m)
                           if (x[(i, j)].value() or 0) > 0.5]
                          for j in range(k)]


def random_dag(rng, n, m):
    perm = list(range(n))
    rng.shuffle(perm)
    arcs = []
    for _ in range(m):
        i = rng.randrange(n - 1)
        j = rng.randrange(i + 1, n)
        arcs.append((perm[i], perm[j]))
    return arcs


def weakly_connected(n, arcs):
    adj = [[] for _ in range(n)]
    for (u, v) in arcs:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    st = [0]
    seen[0] = True
    c = 1
    while st:
        v = st.pop()
        for x in adj[v]:
            if not seen[x]:
                seen[x] = True
                c += 1
                st.append(x)
    return c == n


def search(seconds=600, seed=0):
    rng = random.Random(seed)
    t0 = time.time()
    tries = 0
    while time.time() - t0 < seconds:
        tries += 1
        n = rng.randint(6, 9)
        m = rng.randint(10, 18)
        arcs = random_dag(rng, n, m)
        if not weakly_connected(n, arcs):
            continue
        w = [rng.randint(0, 1) for _ in range(m)]
        t, cuts = tau_w(n, arcs, w)
        if t is None or t != 2:
            continue
        ok, classes = pack_w(n, arcs, w, t)
        if not ok:
            print("WEIGHTED GAP FOUND after", tries, "tries:")
            print("n =", n)
            print("arcs =", arcs)
            print("w =", w)
            print("tau_w =", t)
            # confirm nu < tau: check k = t-1 feasible for sanity
            ok1, _ = pack_w(n, arcs, w, t - 1)
            print("pack", t - 1, "feasible:", ok1)
            return n, arcs, w, t
    print("no weighted gap found in", tries, "tries")
    return None


if __name__ == "__main__":
    seconds = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    search(seconds, seed)

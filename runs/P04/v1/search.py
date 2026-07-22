"""V1 annealed gap search for P04 (Hajos cycle decomposition conjecture).

Search over simple connected Eulerian graphs with delta >= 6 (minimum-counterexample
constraint, Fuchs-Gellert-Heinrich). Score = heuristic minimum cycle decomposition
size (upper bound via randomized Euler-circuit splitting + improvement passes).
Counterexample requires exact min decomposition > k = floor((n-1)/2); candidates
whose heuristic count stays > k after heavy restarts are sent to the exact CP-SAT
oracle (exact.py).

Usage: python3 search.py N SECONDS [SEED]
Appends results to results_nN_seedS.jsonl and prints checkpoints.
"""
import json
import random
import sys
import time

import networkx as nx

from exact import decompose_leq_k


def euler_split(G, rng):
    """Random Eulerian circuit -> split into cycles via stack; returns cycle count."""
    # random eulerian circuit: Hierholzer with shuffled adjacency
    adj = {v: list(G.neighbors(v)) for v in G.nodes()}
    for v in adj:
        rng.shuffle(adj[v])
    used = set()
    start = rng.choice(list(G.nodes()))
    stack = [start]
    circuit = []
    ptr = {v: 0 for v in adj}
    while stack:
        v = stack[-1]
        found = False
        while ptr[v] < len(adj[v]):
            u = adj[v][ptr[v]]
            ptr[v] += 1
            e = (min(u, v), max(u, v), 0)
            key = frozenset((u, v))
            # multigraph not allowed (simple), key suffices
            if key not in used:
                used.add(key)
                stack.append(u)
                found = True
                break
        if not found:
            circuit.append(stack.pop())
    # split circuit into cycles: scan, cut at first vertex repeat
    count = 0
    pos = {}
    cur = []
    for v in circuit:
        if v in pos:
            count += 1
            # remove the closed cycle from cur
            i = pos[v]
            for w in cur[i + 1:]:
                del pos[w]
            cur = cur[: i + 1]
        else:
            pos[v] = len(cur)
            cur.append(v)
    return count


def _long_cycle(adj, deg, rng, tries=4):
    """Randomized long simple cycle in graph given by adj sets (Posa-style rotations)."""
    verts = [v for v in adj if deg[v] > 0]
    if not verts:
        return None
    best = None
    for _ in range(tries):
        start = rng.choice(verts)
        path = [start]
        onpath = {start}
        for _ in range(4 * len(verts)):
            v = path[-1]
            nbrs = [u for u in adj[v] if u not in onpath]
            if nbrs:
                u = rng.choice(nbrs)
                path.append(u)
                onpath.add(u)
                continue
            # rotation: pick neighbor u on path, reverse tail after u
            cand = [u for u in adj[v] if u in onpath and u != path[-2 if len(path) > 1 else -1]]
            if len(path) >= 3 and start in adj[v] and rng.random() < 0.5:
                break
            if not cand:
                break
            u = rng.choice(cand)
            i = path.index(u)
            path[i + 1:] = reversed(path[i + 1:])
        # close to longest suffix cycle: find earliest path vertex adjacent to path[-1]
        v = path[-1]
        cyc = None
        for i, u in enumerate(path):
            if u in adj[v] and len(path) - i >= 3:
                cyc = path[i:]
                break
        if cyc and (best is None or len(cyc) > len(best)):
            best = cyc
    return best


def greedy_peel(G, rng):
    """Repeatedly peel a long cycle; returns number of cycles used."""
    adj = {v: set(G.neighbors(v)) for v in G.nodes()}
    deg = {v: len(adj[v]) for v in adj}
    m = G.number_of_edges()
    count = 0
    while m > 0:
        cyc = _long_cycle(adj, deg, rng)
        if cyc is None:
            return 10 ** 9
        for i in range(len(cyc)):
            u, v = cyc[i], cyc[(i + 1) % len(cyc)]
            adj[u].discard(v)
            adj[v].discard(u)
            deg[u] -= 1
            deg[v] -= 1
            m -= 1
        count += 1
    return count


def heuristic_min_decomp(G, restarts, rng):
    best = 10 ** 9
    for i in range(restarts):
        best = min(best, euler_split(G, rng), greedy_peel(G, rng))
    return best


def heuristic_score(G, restarts, rng):
    """(min, min + 0.02*avg) over restarts of both heuristics; avg is the anneal tie-break:
    graphs whose random decompositions are consistently large are 'harder'."""
    vals = []
    for i in range(restarts):
        vals.append(euler_split(G, rng))
        vals.append(greedy_peel(G, rng))
    mn = min(vals)
    return mn, mn + 0.02 * (sum(vals) / len(vals))


def random_even_graph(n, p, rng, delta=6):
    while True:
        G = nx.gnp_random_graph(n, p, seed=rng.randrange(1 << 30))
        odd = [v for v in G.nodes() if G.degree(v) % 2 == 1]
        rng.shuffle(odd)
        for i in range(0, len(odd) - 1, 2):
            u, v = odd[i], odd[i + 1]
            if G.has_edge(u, v):
                G.remove_edge(u, v)
            else:
                G.add_edge(u, v)
        if min(dict(G.degree()).values(), default=0) >= delta and nx.is_connected(G):
            return G


def parity_move(G, n, rng, delta=6):
    """Toggle edges of a random triangle or C4 in K_n (parity preserving)."""
    k = rng.choice([3, 3, 4])
    vs = rng.sample(range(n), k)
    cyc = [(vs[i], vs[(i + 1) % k]) for i in range(k)]
    for u, v in cyc:
        if G.has_edge(u, v):
            G.remove_edge(u, v)
        else:
            G.add_edge(u, v)
    if min(dict(G.degree()).values()) >= delta and nx.is_connected(G):
        return cyc
    for u, v in cyc:  # revert
        if G.has_edge(u, v):
            G.remove_edge(u, v)
        else:
            G.add_edge(u, v)
    return None


def anneal(n, seconds, seed, quick_restarts=12, deep_restarts=400):
    rng = random.Random(seed)
    k = (n - 1) // 2
    out = open(f"results_n{n}_seed{seed}.jsonl", "a")
    G = random_even_graph(n, 0.7, rng)
    cur_min, cur = heuristic_score(G, quick_restarts, rng)
    best_seen = cur_min
    t0 = time.time()
    it = 0
    T0, T1 = 1.0, 0.05
    exact_checked = set()
    while time.time() - t0 < seconds:
        it += 1
        frac = (time.time() - t0) / seconds
        T = T0 * (T1 / T0) ** frac
        mv = parity_move(G, n, rng)
        if mv is None:
            continue
        new_min, new = heuristic_score(G, quick_restarts, rng)
        if new >= cur or rng.random() < pow(2.71828, (new - cur) / T):
            cur_min, cur = new_min, new
        else:
            for u, v in mv:  # revert
                if G.has_edge(u, v):
                    G.remove_edge(u, v)
                else:
                    G.add_edge(u, v)
            continue
        if cur_min > best_seen:
            best_seen = cur_min
            print(f"[n={n} it={it} t={time.time()-t0:.0f}s] heuristic best={cur_min} (k={k})",
                  flush=True)
        if cur_min > k:
            deep = heuristic_min_decomp(G, deep_restarts, rng)
            edges = tuple(sorted(tuple(sorted(e)) for e in G.edges()))
            rec = {"n": n, "m": G.number_of_edges(), "k": k, "heur_quick": cur_min,
                   "heur_deep": deep, "edges": [list(e) for e in edges]}
            if deep > k and edges not in exact_checked:
                exact_checked.add(edges)
                print(f"[n={n}] CANDIDATE deep heuristic={deep} > k={k}; exact check...",
                      flush=True)
                st, cyc = decompose_leq_k(n, [tuple(e) for e in edges], k,
                                          time_limit=600)
                rec["exact"] = st
                if st == "INFEASIBLE":
                    rec["COUNTEREXAMPLE"] = True
                    print("!!! COUNTEREXAMPLE:", json.dumps(rec), flush=True)
                else:
                    print(f"[n={n}] exact: {st} (feasible with <= {k}; not a CE)",
                          flush=True)
                out.write(json.dumps(rec) + "\n")
                out.flush()
            cur_min = deep
    print(f"DONE n={n} seed={seed}: iters={it}, best heuristic={best_seen}, k={k}",
          flush=True)
    out.close()


if __name__ == "__main__":
    n = int(sys.argv[1])
    seconds = float(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    anneal(n, seconds, seed)

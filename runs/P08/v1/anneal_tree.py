"""V1 simulated annealing over trees, score = dev(D) - mu(T).

For trees n+ = n- = matching number mu(T) (standard: rank(A)=2*mu for forests),
so conjectures 39 and 40 coincide on trees and mu is O(n) to compute.
dev(D) computed exactly from BFS (O(n^2) total on a tree).

Usage: python3 anneal_tree.py <n> <iters> [seed]
"""
import sys
import math
import random
from collections import deque


def tree_dev(parenting_adj, n):
    """Population std of all n^2 distance-matrix entries; also returns diameter."""
    total = 0
    total_sq = 0
    diam = 0
    dist = [0] * n
    for s in range(n):
        for i in range(n):
            dist[i] = -1
        dist[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            du = dist[u]
            total += du
            total_sq += du * du
            if du > diam:
                diam = du
            for v in parenting_adj[u]:
                if dist[v] < 0:
                    dist[v] = du + 1
                    q.append(v)
    m = n * n
    mean = total / m
    var = total_sq / m - mean * mean
    return math.sqrt(max(var, 0.0)), diam


def matching_number(adj, n):
    """Greedy leaf-based maximum matching on a tree (exact)."""
    deg = [len(adj[u]) for u in range(n)]
    matched = [False] * n
    removed = [False] * n
    q = deque(u for u in range(n) if deg[u] == 1)
    mu = 0
    while q:
        leaf = q.popleft()
        if removed[leaf]:
            continue
        removed[leaf] = True
        p = next((v for v in adj[leaf] if not removed[v]), None)
        if p is None:
            continue
        if not matched[leaf] and not matched[p]:
            matched[leaf] = matched[p] = True
            mu += 1
        # remove p as well if it got matched? standard: remove leaf; decrement p
        deg[p] -= 1
        if deg[p] == 1 and not removed[p]:
            q.append(p)
    return mu


def score(adj, n):
    dev, diam = tree_dev(adj, n)
    mu = matching_number(adj, n)
    return dev - mu, dev, mu, diam


def random_tree(n, rng):
    adj = [[] for _ in range(n)]
    for v in range(1, n):
        u = rng.randrange(v)
        adj[u].append(v)
        adj[v].append(u)
    return adj


def leaf_move(adj, n, rng):
    """Detach a random leaf and reattach to a random other vertex. Returns undo info."""
    leaves = [u for u in range(n) if len(adj[u]) == 1]
    leaf = rng.choice(leaves)
    old_p = adj[leaf][0]
    new_p = rng.randrange(n)
    while new_p == leaf or new_p == old_p:
        new_p = rng.randrange(n)
    adj[old_p].remove(leaf)
    adj[leaf][0] = new_p
    adj[new_p].append(leaf)
    return leaf, old_p, new_p


def undo(adj, mv):
    leaf, old_p, new_p = mv
    adj[new_p].remove(leaf)
    adj[leaf][0] = old_p
    adj[old_p].append(leaf)


def main():
    n = int(sys.argv[1])
    iters = int(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rng = random.Random(seed)
    adj = random_tree(n, rng)
    cur, dev, mu, diam = score(adj, n)
    best = cur
    best_info = (dev, mu, diam)
    T0, T1 = 1.0, 0.01
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / max(iters - 1, 1))
        mv = leaf_move(adj, n, rng)
        s, dev, mu, diam = score(adj, n)
        if s > cur or rng.random() < math.exp((s - cur) / T):
            cur = s
            if s > best:
                best = s
                best_info = (dev, mu, diam)
                if s > 1e-5:
                    print("VIOLATION", n, s, dev, mu, diam, flush=True)
                    print(adj, flush=True)
        else:
            undo(adj, mv)
        if it % max(iters // 20, 1) == 0:
            print(f"n={n} it={it} T={T:.3f} cur={cur:.4f} best={best:.4f} "
                  f"(dev={best_info[0]:.4f} mu={best_info[1]} diam={best_info[2]})", flush=True)
    print(f"FINAL n={n} best={best:.6f} dev={best_info[0]:.6f} mu={best_info[1]} diam={best_info[2]}", flush=True)


if __name__ == "__main__":
    main()

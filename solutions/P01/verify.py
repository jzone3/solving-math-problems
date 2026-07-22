#!/usr/bin/env python3
"""Independent verifier for P01 (Sheehan's conjecture) witnesses.

A witness is a uniquely hamiltonian 4-regular simple graph, given either as:
  * a file of edges "u v" per line (vertices 0..n-1), passed as argv[1]; or
  * the `COUNTEREXAMPLE` chord format emitted by runs/P01/v4/search1h
    (chords only; pass --chords n file, the cycle 0-1-...-(n-1)-0 is added).

Checks, with no external dependencies:
  1. graph is simple (no loops / parallel edges),
  2. every vertex has degree exactly 4,
  3. the graph has EXACTLY ONE hamiltonian cycle (exhaustive DFS count,
     independent of the search program's counter).
Prints PASS iff all checks hold, otherwise FAIL with a reason.
"""
import sys
sys.setrecursionlimit(100000)


def read_edges(path):
    edges = []
    for line in open(path):
        line = line.split("#")[0].strip()
        if not line or line.startswith("COUNTEREXAMPLE"):
            continue
        u, v = map(int, line.split())
        edges.append((u, v))
    return edges


def count_hamiltonian_cycles(n, adj, cap=3):
    """Exact number of hamiltonian cycles (stops early at cap)."""
    full = (1 << n) - 1
    count = 0

    def dfs(v, visited):
        nonlocal count
        if count >= cap:
            return
        if visited == full:
            if 0 in adj[v]:
                count += 1
            return
        for w in adj[v]:
            if not (visited >> w) & 1:
                dfs(w, visited | (1 << w))

    dfs(0, 1)  # directed cycles through vertex 0; each HC counted twice
    if count >= cap:
        return cap
    assert count % 2 == 0, "directed HC count must be even"
    return count // 2


def main():
    args = sys.argv[1:]
    if args and args[0] == "--chords":
        n = int(args[1])
        edges = [(i, (i + 1) % n) for i in range(n)] + read_edges(args[2])
    else:
        edges = read_edges(args[0])
        n = max(max(e) for e in edges) + 1

    seen = set()
    for u, v in edges:
        if u == v:
            print(f"FAIL: loop at {u}")
            return 1
        key = (min(u, v), max(u, v))
        if key in seen:
            print(f"FAIL: parallel edge {key}")
            return 1
        seen.add(key)

    adj = [[] for _ in range(n)]
    for u, v in seen:
        adj[u].append(v)
        adj[v].append(u)

    bad = [v for v in range(n) if len(adj[v]) != 4]
    if bad:
        print(f"FAIL: vertices with degree != 4: {bad[:10]}")
        return 1

    c = count_hamiltonian_cycles(n, adj, cap=3)
    if c == 1:
        print(f"PASS: n={n}, simple, 4-regular, exactly one hamiltonian cycle")
        return 0
    print(f"FAIL: hamiltonian cycle count = {c}{'+' if c >= 3 else ''} (need exactly 1)")
    return 1


if __name__ == "__main__":
    sys.exit(main())

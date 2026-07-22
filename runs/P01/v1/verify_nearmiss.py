#!/usr/bin/env python3
"""Independent (differently written, iterative) HC counter for near-miss graphs.
Usage: python3 verify_nearmiss.py graphfile [expected_count]
Graph file: first line n, then one edge "a b" per line.
Prints the exact number of Hamiltonian cycles and PASS/FAIL vs expected.
"""
import sys

def count_hc(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    for v in range(n):
        assert len(adj[v]) == 4, f"vertex {v} has degree {len(adj[v])} != 4"
    # iterative DFS over simple paths starting/ending at 0; counts each cycle twice
    count = 0
    visited = [False]*n
    visited[0] = True
    # stack holds (vertex, iterator over neighbors)
    stack = [(0, iter(sorted(adj[0])))]
    depth = 1
    while stack:
        v, it = stack[-1]
        advanced = False
        for w in it:
            if visited[w]:
                continue
            if depth == n - 1:
                if 0 in adj[w]:
                    count += 1
                continue
            visited[w] = True
            stack.append((w, iter(sorted(adj[w]))))
            depth += 1
            advanced = True
            break
        if not advanced:
            stack.pop()
            if stack:
                visited[v] = False
                depth -= 1
    assert count % 2 == 0
    return count // 2

def main():
    lines = [l for l in open(sys.argv[1]).read().split("\n") if l.strip()]
    n = int(lines[0])
    edges = [tuple(map(int, l.split())) for l in lines[1:]]
    c = count_hc(n, edges)
    print(f"n={n} hamiltonian cycles = {c}")
    if len(sys.argv) > 2:
        exp = int(sys.argv[2])
        print("PASS" if c == exp else "FAIL")
        sys.exit(0 if c == exp else 1)

if __name__ == "__main__":
    main()

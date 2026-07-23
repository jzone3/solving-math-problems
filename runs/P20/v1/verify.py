#!/usr/bin/env python3
"""Independent exact verifier for P20 (Grünbaum girth-6 case) artifacts.

Modes:
  verify.py certs <file.jsonl> [...]
      For every line {"n","adj","coloring"}: check (all integer arithmetic, no floats)
        (1) adj describes a simple undirected 4-regular graph on n vertices,
        (2) the graph is connected and has girth >= 6 (BFS from every vertex),
        (3) coloring is a proper 3-coloring (colors in {0,1,2}).
      A graph with "coloring": null is reported as a WITNESS CANDIDATE and
      checked for (1)+(2) only; its non-3-colorability must be certified
      separately by a DRAT UNSAT proof (see witness mode).
      Prints PASS iff every record checks out and no candidate is present.

  verify.py witness <adjlist.txt>
      Reads a 1-based adjacency list ("v : u1 u2 u3 u4" per line); checks
      4-regularity, connectivity and girth >= 6; then writes 3col.cnf, a DIMACS
      encoding of 3-colorability, for UNSAT certification with a DRAT-producing
      SAT solver (e.g. `kissat 3col.cnf proof.drat` then
      `drat-trim 3col.cnf proof.drat`). Prints WITNESS-STRUCTURE-OK on success.

No external dependencies; exact integer computations only.
"""
import json, sys
from collections import deque

def check_graph(adj, n):
    """Return error string or None. Checks simple, 4-regular, connected, girth>=6."""
    if len(adj) != n:
        return "adjacency list count != n"
    nbrs = []
    for v in range(1, n + 1):
        row = adj[v - 1]
        if len(row) != 4 or len(set(row)) != 4:
            return f"vertex {v} degree != 4"
        for u in row:
            if not (1 <= u <= n) or u == v:
                return f"vertex {v} has bad neighbour {u}"
        nbrs.append(sorted(row))
    for v in range(1, n + 1):
        for u in nbrs[v - 1]:
            if v not in nbrs[u - 1]:
                return f"asymmetric edge {v}-{u}"
    # connectivity
    seen = [False] * (n + 1)
    seen[1] = True
    q = deque([1])
    cnt = 1
    while q:
        v = q.popleft()
        for u in nbrs[v - 1]:
            if not seen[u]:
                seen[u] = True
                cnt += 1
                q.append(u)
    if cnt != n:
        return "graph not connected"
    # girth >= 6: BFS from each vertex; any cycle of length <=5 is detected by
    # finding, from root r, an edge between two vertices u,v with
    # dist[u]+dist[v]+1 <= 5 where the edge closes a cycle through r.
    # Standard method: BFS layers; a non-tree edge between depth d1,d2 vertices
    # implies a cycle of length <= d1+d2+1 through the root.
    for r in range(1, n + 1):
        dist = [-1] * (n + 1)
        parent = [0] * (n + 1)
        dist[r] = 0
        q = deque([r])
        while q:
            v = q.popleft()
            if dist[v] >= 3:
                continue
            for u in nbrs[v - 1]:
                if dist[u] == -1:
                    dist[u] = dist[v] + 1
                    parent[u] = v
                    q.append(u)
                elif u != parent[v] and parent[u] != v:
                    cyc = dist[u] + dist[v] + 1
                    if cyc <= 5:
                        return f"cycle of length <= {cyc} through {r}"
    return None

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    mode = sys.argv[1]
    if mode == "certs":
        total = witnesses = 0
        for path in sys.argv[2:]:
            with open(path) as fh:
                for lineno, line in enumerate(fh, 1):
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    n, adj, col = rec["n"], rec["adj"], rec["coloring"]
                    err = check_graph(adj, n)
                    if err:
                        print(f"FAIL {path}:{lineno}: {err}")
                        return 1
                    if col is None:
                        witnesses += 1
                        print(f"WITNESS CANDIDATE at {path}:{lineno} (needs DRAT cert)")
                        continue
                    if len(col) != n or any(c not in (0, 1, 2) for c in col):
                        print(f"FAIL {path}:{lineno}: bad coloring vector")
                        return 1
                    for v in range(1, n + 1):
                        for u in adj[v - 1]:
                            if col[v - 1] == col[u - 1]:
                                print(f"FAIL {path}:{lineno}: edge {v}-{u} monochromatic")
                                return 1
                    total += 1
        if witnesses:
            print(f"{witnesses} witness candidate(s) present; not a PASS for 3-colorability")
            return 2
        print(f"PASS  ({total} graphs: each verified 4-regular, connected, girth>=6, properly 3-colored)")
        return 0
    if mode == "witness":
        adj = {}
        with open(sys.argv[2]) as fh:
            for line in fh:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                v, rest = line.split(":", 1)
                adj[int(v)] = [int(x) for x in rest.split()]
        n = max(adj)
        rows = [adj[v] for v in range(1, n + 1)]
        err = check_graph(rows, n)
        if err:
            print(f"FAIL: {err}")
            return 1
        with open("3col.cnf", "w") as out:
            var = lambda i, c: 3 * (i - 1) + c + 1
            clauses = []
            for v in range(1, n + 1):
                clauses.append([var(v, 0), var(v, 1), var(v, 2)])
            for v in range(1, n + 1):
                for u in rows[v - 1]:
                    if u > v:
                        for c in range(3):
                            clauses.append([-var(v, c), -var(u, c)])
            out.write(f"p cnf {3*n} {len(clauses)}\n")
            for cl in clauses:
                out.write(" ".join(map(str, cl)) + " 0\n")
        print("WITNESS-STRUCTURE-OK: graph is 4-regular, connected, girth>=6.")
        print("Wrote 3col.cnf; UNSAT + DRAT check certifies chromatic number >= 4.")
        return 0
    print(__doc__)
    return 1

if __name__ == "__main__":
    sys.exit(main())

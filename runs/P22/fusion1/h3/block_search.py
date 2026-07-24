#!/usr/bin/env python3
"""Probe K4-free balanced-block subgraphs of H_3.

Each of the 28 order-9 maximal cliques is replaced by a balanced K_{4,5}.
Every original edge belongs to exactly one such clique, so a block assignment
is represented by one 4/5 bipartition per unital point.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
import subprocess
import time
from pathlib import Path

from build_h3 import build


def prepare():
    G = build()
    cliques = [
        tuple(i for i, pts in enumerate(G["son"]) if p in pts)
        for p in G["unital"]
    ]
    assert len(cliques) == 28
    assert all(len(c) == 9 for c in cliques)
    edge_clique = {}
    for ci, clique in enumerate(cliques):
        for e in itertools.combinations(sorted(clique), 2):
            assert e not in edge_clique
            edge_clique[e] = ci
    assert len(edge_clique) == len(G["edges"]) == 1008
    nondeg = set()
    crossing = G["cross_pt"]

    def cp(i, j):
        return crossing[(i, j) if i < j else (j, i)]

    for i, j, k in itertools.combinations(range(63), 3):
        if j in G["adj"][i] and k in G["adj"][i] and k in G["adj"][j]:
            if len({cp(i, j), cp(i, k), cp(j, k)}) == 3:
                nondeg.add((i, j, k))
    assert len(nondeg) == 3024
    return G, cliques, edge_clique, nondeg


def balanced_partition(rng):
    chosen = set(rng.sample(range(9), 4))
    return tuple(i in chosen for i in range(9))


def subgraph(G, cliques, edge_clique, parts, check_k4=True):
    surviving = []
    for edge in G["edges"]:
        ci = edge_clique[edge]
        clique = cliques[ci]
        u, v = clique.index(edge[0]), clique.index(edge[1])
        if parts[ci][u] != parts[ci][v]:
            surviving.append(edge)
    surviving = sorted(surviving)
    adj = [set() for _ in range(63)]
    for u, v in surviving:
        adj[u].add(v)
        adj[v].add(u)
    triangles = []
    for i, j in surviving:
        for k in adj[i] & adj[j]:
            if k > j:
                triangles.append((i, j, k))
    if check_k4:
        k4 = sum(
            1
            for a, b, c, d in itertools.combinations(range(63), 4)
            if b in adj[a]
            and c in adj[a]
            and d in adj[a]
            and c in adj[b]
            and d in adj[b]
            and d in adj[c]
        )
        assert k4 == 0, k4
    return surviving, triangles


def write_cnf(path, edges, triangles):
    evar = {e: i + 1 for i, e in enumerate(edges)}
    clauses = []
    for i, j, k in triangles:
        a = evar[(i, j) if i < j else (j, i)]
        b = evar[(i, k) if i < k else (k, i)]
        c = evar[(j, k) if j < k else (k, j)]
        clauses.extend(((a, b, c), (-a, -b, -c)))
    with path.open("w") as f:
        f.write(f"p cnf {len(edges)} {len(clauses)}\n")
        for clause in clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")


def score(G, cliques, edge_clique, parts, check_k4=False):
    edges, triangles = subgraph(G, cliques, edge_clique, parts, check_k4)
    return len(edges), len(triangles), edges, triangles


def greedy_parts(G, cliques, edge_clique, rng, steps=25):
    parts = [balanced_partition(rng) for _ in cliques]
    best_e, best_t, _, _ = score(G, cliques, edge_clique, parts)
    for _ in range(steps):
        candidates = []
        for ci in range(len(cliques)):
            one = [i for i, x in enumerate(parts[ci]) if x]
            zero = [i for i, x in enumerate(parts[ci]) if not x]
            a, b = rng.choice(one), rng.choice(zero)
            candidate = list(parts)
            bits = list(candidate[ci])
            bits[a], bits[b] = bits[b], bits[a]
            candidate[ci] = tuple(bits)
            e, t, _, _ = score(G, cliques, edge_clique, candidate)
            candidates.append((t, e, candidate))
        t, e, candidate = max(candidates, key=lambda x: (x[0], x[1]))
        if (t, e) <= (best_t, best_e):
            break
        parts = candidate
        best_e, best_t = e, t
    return parts


def run_kissat(cnf, timeout):
    start = time.monotonic()
    try:
        proc = subprocess.run(
            ["kissat", "--quiet", f"--time={timeout}", str(cnf)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout + 10,
        )
        elapsed = time.monotonic() - start
        if proc.returncode == 10:
            status = "SAT"
        elif proc.returncode == 20:
            status = "UNSAT"
        elif proc.returncode == 0 and elapsed >= timeout - 1:
            status = "TIMEOUT"
        else:
            status = f"RC{proc.returncode}"
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        status = "TIMEOUT"
    return status, round(elapsed, 3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--random", type=int, default=200)
    parser.add_argument("--greedy", type=int, default=50)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--seed", type=int, default=32263)
    parser.add_argument("--out", type=Path, default=Path("block_results.json"))
    parser.add_argument("--cnf-dir", type=Path, default=Path("blocks"))
    args = parser.parse_args()
    args.cnf_dir.mkdir(parents=True, exist_ok=True)
    G, cliques, edge_clique, nondeg = prepare()
    rng = random.Random(args.seed)
    results = []
    total = args.random + args.greedy

    for kind, count in (("random", args.random), ("greedy", args.greedy)):
        for index in range(count):
            if kind == "random":
                parts = [balanced_partition(rng) for _ in cliques]
            else:
                parts = greedy_parts(G, cliques, edge_clique, rng)
            n_edges, n_triangles, edges, triangles = score(
                G, cliques, edge_clique, parts, check_k4=True
            )
            assert set(triangles) <= nondeg
            cnf = args.cnf_dir / f"block_{len(results):03d}_{kind}.cnf"
            write_cnf(cnf, edges, triangles)
            status, seconds = run_kissat(cnf, args.timeout)
            result = {
                "index": len(results),
                "strategy": kind,
                "edges": n_edges,
                "triangles": n_triangles,
                "status": status,
                "seconds": seconds,
                "cnf": str(cnf),
                "partitions": [list(map(int, p)) for p in parts],
                "cliques": [list(c) for c in cliques],
            }
            results.append(result)
            args.out.write_text(json.dumps(results, indent=2))
            print(
                f"{len(results)}/{total} {kind} edges={len(edges)} "
                f"triangles={len(triangles)} {status} {seconds:.3f}s",
                flush=True,
            )
            if status == "UNSAT":
                print("UNSAT FOUND; stopping immediately", flush=True)
                return

    def summary(key):
        values = sorted(r[key] for r in results)
        return min(values), values[len(values) // 2], max(values)

    counts = {s: sum(r["status"] == s for r in results) for s in ("SAT", "UNSAT", "TIMEOUT")}
    print("summary:")
    print(f"edges min/median/max={summary('edges')}")
    print(f"triangles min/median/max={summary('triangles')}")
    print(f"status counts={counts}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()

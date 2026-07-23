#!/usr/bin/env python3
"""Incremental-SAT CEGAR search for a uniquely Hamiltonian 4-regular simple graph.

Same encoding as cegar.py (fixed HC 0..n-1, chord vars, exactly-2 chords/vertex,
prefix-lex dihedral symmetry breaking, blocking clauses for every discovered second HC
+ all dihedral images), but on an incremental SAT solver (CaDiCaL via PySAT) so learned
clauses persist across CEGAR iterations -- far cheaper than re-presolving CP-SAT.

Usage: python3 cegar_sat.py n [time_limit_s] [max_block_per_iter]
"""
import os, sys, time, functools
print = functools.partial(print, flush=True)
from pysat.solvers import Cadical195
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

sys.setrecursionlimit(100000)


def chords(n):
    return [(i, j) for i in range(n) for j in range(i + 2, n)
            if not (i == 0 and j == n - 1)]


def canon(i, j):
    return (i, j) if i < j else (j, i)


def dihedral_maps(n):
    return [[(s * v + r) % n for v in range(n)] for r in range(n) for s in (1, -1)]


def count_hcs(n, adj, cutoff, collect):
    found = 0
    nbrs = [sorted(adj[v]) for v in range(n)]
    visited = [False] * n
    visited[0] = True
    path = [0]

    def dfs(v):
        nonlocal found
        if found >= cutoff:
            return
        if len(path) == n:
            if 0 in adj[v] and path[1] < path[-1]:
                found += 1
                collect.append(path[:])
            return
        for w in nbrs[v]:
            if not visited[w]:
                visited[w] = True
                path.append(w)
                dfs(w)
                path.pop()
                visited[w] = False
                if found >= cutoff:
                    return

    dfs(0)
    return found


def main():
    n = int(sys.argv[1])
    tlimit = float(sys.argv[2]) if len(sys.argv) > 2 else 3600.0
    max_block = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    LEXK = 30
    cs = chords(n)
    dmaps = dihedral_maps(n)
    pool = IDPool()
    x = {c: pool.id(("x", c)) for c in cs}
    clauses = []
    for v in range(n):
        lits = [x[c] for c in cs if v in c]
        enc = CardEnc.equals(lits=lits, bound=2, encoding=EncType.seqcounter,
                             vpool=pool)
        clauses.extend(enc.clauses)
    # prefix-lex dihedral symmetry breaking: x <=lex sigma(x) on first LEXK chords
    for m in dmaps[1:]:
        prev = None  # e_0 == True handled by omitting it
        for t, (i, j) in enumerate(cs[:LEXK]):
            a = x[(i, j)]
            b = x[canon(m[i], m[j])]
            if a == b:
                continue
            if prev is None:
                clauses.append([-a, b])
                e = pool.id(("e", id(m), t))
                clauses.append([-e, -a, b])   # e -> a==b (with next clause)
                clauses.append([-e, a, -b])
                clauses.append([-a, -b, e])   # a==b -> e (prev true)
                clauses.append([a, b, e])
                prev = e
            else:
                clauses.append([-prev, -a, b])
                e = pool.id(("e", id(m), t))
                clauses.append([-e, prev])
                clauses.append([-e, -a, b])
                clauses.append([-e, a, -b])
                clauses.append([-prev, -a, -b, e])
                clauses.append([-prev, a, b, e])
                prev = e

    solver = Cadical195(bootstrap_with=clauses)
    print(f"n={n}: {len(cs)} chord vars, {len(clauses)} base clauses")
    t0 = time.time()
    it = 0
    nblock = 0
    best = None
    while True:
        if time.time() - t0 > tlimit:
            print(f"TIMEOUT n={n} after {it} iters, {nblock} blocking clauses, best #HC seen={best}")
            return 2
        if not solver.solve():
            print(f"UNSAT n={n} after {it} iters, {nblock} blocking clauses, "
                  f"{time.time()-t0:.1f}s -- VERIFIED NEGATIVE (no 4-regular graph on "
                  f"{n} vertices has cycle 0..{n-1} as its unique HC; WLOG none uniquely hamiltonian)")
            return 0
        it += 1
        model = set(l for l in solver.get_model() if l > 0)
        adj = [set() for _ in range(n)]
        for v in range(n):
            adj[v].add((v + 1) % n); adj[v].add((v - 1) % n)
        chosen = [c for c in cs if x[c] in model]
        for (i, j) in chosen:
            adj[i].add(j); adj[j].add(i)
        cycles = []
        cnt = count_hcs(n, adj, max_block + 1, cycles)
        others = []
        for cyc in cycles:
            edges = set(canon(cyc[k], cyc[(k + 1) % n]) for k in range(n))
            ch = [e for e in edges if e in x]
            if ch:
                others.append(ch)
        if best is None or cnt < best:
            best = cnt
            print(f"[{time.time()-t0:8.1f}s] it={it} model #HC>= {cnt} (new best)")
        if not others:
            print(f"WITNESS FOUND n={n}!!! chords: {chosen}")
            with open(f"witness_n{n}.txt", "w") as f:
                f.write(f"{n}\n")
                for v in range(n):
                    f.write(f"{v} {(v+1)%n}\n")
                for (i, j) in chosen:
                    f.write(f"{i} {j}\n")
            return 1
        maps_for_block = dmaps if not os.environ.get("NOIMG") else dmaps[:1]
        for ch in others:
            seen = set()
            for m in maps_for_block:
                img = frozenset(canon(m[i], m[j]) for (i, j) in ch)
                if img in seen:
                    continue
                seen.add(img)
                solver.add_clause([-x[e] for e in img])
                nblock += 1
        if it % 200 == 0:
            print(f"[{time.time()-t0:8.1f}s] it={it} nblock={nblock} best={best}")


if __name__ == "__main__":
    sys.exit(main())

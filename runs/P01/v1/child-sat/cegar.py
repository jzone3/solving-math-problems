#!/usr/bin/env python3
"""CEGAR CP-SAT search for a uniquely Hamiltonian 4-regular simple graph.

Encoding: WLOG the unique Hamiltonian cycle is 0-1-...-(n-1)-0 (relabel any witness).
Boolean var x[(i,j)] for every chord (cyclic distance >= 2): chord present.
Constraints: every vertex has exactly 2 chord endpoints (degree 4 total).
Symmetry breaking: chord incidence vector lex-minimal under the dihedral group D_n
(rotations + reflections of the fixed cycle), which is the full symmetry of the encoding.

CEGAR loop: solve -> enumerate Hamiltonian cycles of the model (cutoff) ->
if any HC other than the fixed cycle exists, add for each found "second" HC C the
blocking clause  OR_{e chord of C} (not x_e)  -> resolve.  If the model has exactly
one HC, we have a counterexample to Sheehan's conjecture.  If the solver returns
INFEASIBLE, the CEGAR has converged: NO 4-regular graph on n vertices with unique
HC exists (verified negative for order n).

Usage: python3 cegar.py n [time_limit_s] [max_block_per_iter]
"""
import sys, time
from ortools.sat.python import cp_model


def chords(n):
    cs = []
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue  # cycle edge
            cs.append((i, j))
    return cs


def canon(i, j):
    return (i, j) if i < j else (j, i)


def dihedral_maps(n):
    maps = []
    for r in range(n):
        for s in (1, -1):
            maps.append([ (s * v + r) % n for v in range(n) ])
    return maps


def count_hcs(n, adj, cutoff, collect):
    """Count HCs up to cutoff (undirected, each counted once by fixing start=0 and
    direction via neighbor order). Append found cycles (as vertex lists) to collect."""
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
            if 0 in adj[v] and path[1] < path[-1]:  # direction canonicalization
                found += 1
                collect.append(path[:])
            return
        for w in nbrs[v]:
            if not visited[w]:
                # prune: any unvisited vertex (other than potential extension) with
                # fewer than 2 available connections cannot be completed -- cheap check skipped
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
    max_block = int(sys.argv[3]) if len(sys.argv) > 3 else 500
    cs = chords(n)
    dmaps = dihedral_maps(n)
    model = cp_model.CpModel()
    x = {c: model.NewBoolVar(f"x{c}") for c in cs}
    for v in range(n):
        model.Add(sum(x[c] for c in cs if v in c) == 2)
    # dihedral lex symmetry breaking (prefix-truncated, sound relaxation):
    # chord incidence vector lex-<= each of its images under D_n
    LEXK = 30
    base = [x[c] for c in cs]
    true_lit = model.NewBoolVar("true")
    model.Add(true_lit == 1)
    for m in dihedral_maps(n)[1:]:
        img = [x[canon(m[i], m[j])] for (i, j) in cs]
        prev_all_eq = true_lit
        for a, b in list(zip(base, img))[:LEXK]:
            # if prev_all_eq then a <= b
            model.Add(a <= b).OnlyEnforceIf(prev_all_eq)
            cur = model.NewBoolVar("")
            # cur = prev_all_eq AND (a == b)
            aeqb = model.NewBoolVar("")
            model.Add(a == b).OnlyEnforceIf(aeqb)
            model.Add(a != b).OnlyEnforceIf(aeqb.Not())
            model.AddBoolAnd([prev_all_eq, aeqb]).OnlyEnforceIf(cur)
            model.AddBoolOr([prev_all_eq.Not(), aeqb.Not()]).OnlyEnforceIf(cur.Not())
            prev_all_eq = cur

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 8
    t0 = time.time()
    it = 0
    nblock = 0
    best = None
    while True:
        remaining = tlimit - (time.time() - t0)
        if remaining <= 0:
            print(f"TIMEOUT n={n} after {it} iters, {nblock} blocking clauses, best #HC seen={best}")
            return 2
        solver.parameters.max_time_in_seconds = remaining
        st = solver.Solve(model)
        if st == cp_model.INFEASIBLE:
            print(f"UNSAT n={n} after {it} iters, {nblock} blocking clauses, "
                  f"{time.time()-t0:.1f}s -- VERIFIED NEGATIVE (no 4-regular graph on "
                  f"{n} vertices has cycle 0..{n-1} as its unique HC; WLOG none uniquely hamiltonian)")
            return 0
        if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            print(f"SOLVER TIMEOUT/UNKNOWN n={n} it={it} nblock={nblock} best={best}")
            return 2
        it += 1
        adj = [set() for _ in range(n)]
        for v in range(n):
            adj[v].add((v + 1) % n); adj[v].add((v - 1) % n)
        chosen = [c for c in cs if solver.Value(x[c])]
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
        if cnt - len(others) != 1:
            # fixed cycle should always be among them
            print(f"WARNING it={it}: fixed cycle not found among HCs?! cnt={cnt} others={len(others)}")
        if best is None or cnt < best:
            best = cnt
            print(f"[{time.time()-t0:7.1f}s] it={it} model #HC>= {cnt} (new best), chords={chosen[:8]}...")
        if not others:
            print(f"WITNESS FOUND n={n}!!! chords: {chosen}")
            with open(f"witness_n{n}.txt", "w") as f:
                f.write(f"{n}\n")
                for v in range(n):
                    f.write(f"{v} {(v+1)%n}\n")
                for (i, j) in chosen:
                    f.write(f"{i} {j}\n")
            return 1
        for ch in others:
            # block this second-HC chord pattern and all its dihedral images
            seen = set()
            for m in dmaps:
                img = frozenset(canon(m[i], m[j]) for (i, j) in ch)
                if img in seen:
                    continue
                seen.add(img)
                model.AddBoolOr([x[e].Not() for e in img])
                nblock += 1
        if it % 50 == 0:
            print(f"[{time.time()-t0:7.1f}s] it={it} nblock={nblock} best={best}")


if __name__ == "__main__":
    sys.exit(main())

"""V3 SAT/CEGAR attack on Sheehan's conjecture (P01).

Encoding insight / symmetry breaking: if G is a 4-regular uniquely
Hamiltonian graph on n vertices, relabel so its unique HC is the base cycle
C_n = (0,1,...,n-1). Then E(G) = C_n + X where X is a set of chords forming a
2-regular graph (each vertex gets exactly 2 chord endpoints). So the search
space is exactly: 2-factors X of K_n minus C_n, such that C_n + X has no HC
other than C_n.

CEGAR loop:
  - SAT vars: one per chord {i,j} (cyclic distance >= 2).
  - Constraints: exactly 2 chords at each vertex (sequential-counter encoding).
  - Get model -> candidate graph -> search for a second HC (fast backtracker).
  - If found: block it (clause: at least one of its chords absent), plus all
    2n dihedral images of that clause (rotations/reflections preserve C_n).
  - If no second HC: exact-count HCs; if exactly 1 -> COUNTEREXAMPLE FOUND.

Exhausting the loop (UNSAT) proves no counterexample at that n.
"""

import argparse
import json
import sys
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical153

from hc import find_second_hc, count_hcs


def chords_of(n):
    out = []
    for i in range(n):
        for j in range(i + 1, n):
            d = (j - i) % n
            if 2 <= d <= n - 2:
                out.append((i, j))
    return out


def dihedral_images(n, edge):
    i, j = edge
    for r in range(n):
        for refl in (False, True):
            a, b = (i + r) % n, (j + r) % n
            if refl:
                a, b = (-a) % n, (-b) % n
            yield (min(a, b), max(a, b))


def run(n, max_seconds, hc_per_model=4, log_every=500, notes=None, nearmiss=True):
    chords = chords_of(n)
    pool = IDPool()
    var = {e: pool.id(("x", e)) for e in chords}
    solver = Cadical153()

    # exactly 2 chords per vertex
    for v in range(n):
        lits = [var[e] for e in chords if v in e]
        cnf = CardEnc.equals(lits=lits, bound=2, vpool=pool, encoding=EncType.seqcounter)
        for cl in cnf.clauses:
            solver.add_clause(cl)

    t0 = time.time()
    models = 0
    clauses_added = 0
    best = (64, None)  # (hc_count cap, chordset) near-miss tracking
    status = "running"
    witness = None

    while True:
        if time.time() - t0 > max_seconds:
            status = "timeout"
            break
        if not solver.solve():
            status = "exhausted-unsat"
            break
        model = set(l for l in solver.get_model() if l > 0)
        X = [e for e in chords if var[e] in model]
        adj = [[] for _ in range(n)]
        for i in range(n):
            adj[i].append((i + 1) % n)
            adj[i].append((i - 1) % n)
        for (i, j) in X:
            adj[i].append(j)
            adj[j].append(i)
        models += 1

        second = find_second_hc(n, adj, limit=hc_per_model)
        if not second:
            cnt, capped = count_hcs(n, adj, cap=3)
            if cnt == 1 and not capped:
                status = "FOUND"
                witness = X
                break
            # shouldn't happen (cnt>=2 implies a second HC exists); guard anyway
            second = find_second_hc(n, adj, limit=hc_per_model * 4)
            assert second, "inconsistent HC search"

        # near-miss tracking: count HCs with early cutoff at current best.
        # Only bother when the second-HC search did NOT saturate its limit
        # (i.e. the graph plausibly has few HCs) to avoid full-tree DFS cost.
        cnt, capped = (None, True)
        if nearmiss and len(second) < hc_per_model:
            cnt, capped = count_hcs(n, adj, cap=best[0])
        if not capped and cnt < best[0]:
            best = (cnt, list(X))
            msg = f"n={n} NEAR-MISS hc_count={cnt} chords={X} (model {models})"
            print(msg, flush=True)
            if notes:
                with open(notes, "a") as f:
                    f.write(msg + "\n")

        newcl = set()
        chordset = set(X)
        for cyc in second:
            cedges = set()
            for k in range(n):
                a, b = cyc[k], cyc[(k + 1) % n]
                e = (min(a, b), max(a, b))
                if e in chordset:
                    cedges.add(e)
            assert cedges
            # dihedral images of the blocking clause
            for r in range(n):
                for refl in (False, True):
                    img = []
                    ok = True
                    for (i, j) in cedges:
                        a, b = (i + r) % n, (j + r) % n
                        if refl:
                            a, b = (-a) % n, (-b) % n
                        img.append((min(a, b), max(a, b)))
                    img = tuple(sorted(img))
                    newcl.add(img)
        for cl in newcl:
            solver.add_clause([-var[e] for e in cl])
            clauses_added += 1

        if models % log_every == 0 or time.time() - t0 > getattr(run, "_next_log", 0):
            run._next_log = time.time() - t0 + 120
            msg = (f"n={n} models={models} clauses={clauses_added} "
                   f"t={time.time()-t0:.0f}s best_hc_count={best[0] if best[1] else 'NA'}")
            print(msg, flush=True)
            if notes:
                with open(notes, "a") as f:
                    f.write(msg + "\n")

    elapsed = time.time() - t0
    result = {
        "n": n, "status": status, "models": models,
        "clauses": clauses_added, "seconds": round(elapsed, 1),
        "best_hc_count": best[0] if best[1] else None,
        "best_chords": best[1],
        "witness": witness,
    }
    print(json.dumps(result), flush=True)
    if notes:
        with open(notes, "a") as f:
            f.write(json.dumps(result) + "\n")
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--seconds", type=float, default=3600)
    ap.add_argument("--notes", type=str, default=None)
    ap.add_argument("--no-nearmiss", action="store_true")
    a = ap.parse_args()
    r = run(a.n, a.seconds, notes=a.notes, nearmiss=not a.no_nearmiss)
    sys.exit(0 if r["status"] in ("exhausted-unsat", "FOUND") else 2)

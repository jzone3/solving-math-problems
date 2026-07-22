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


def chords_of(n, min_dist=2):
    out = []
    for i in range(n):
        for j in range(i + 1, n):
            d = min((j - i) % n, (i - j) % n)
            if d >= min_dist:
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


def run(n, max_seconds, hc_per_model=4, log_every=500, notes=None, nearmiss=True,
        min_dist=2):
    chords = chords_of(n, min_dist)
    pool = IDPool()
    var = {e: pool.id(("x", e)) for e in chords}

    # exactly 2 chords per vertex
    base_clauses = []
    for v in range(n):
        lits = [var[e] for e in chords if v in e]
        cnf = CardEnc.equals(lits=lits, bound=2, vpool=pool, encoding=EncType.seqcounter)
        base_clauses.extend(cnf.clauses)
    blocking = []  # all learned blocking clauses, for solver rebuilds

    # Rotation/reflection symmetry breaking: some dihedral image maps a
    # minimum-distance chord to (0, d) with d = global min chord distance.
    # Constraint: OR_d z_d, with z_d -> x_{(0,d)} and z_d -> (no chord of
    # distance < d exists). Sound: every candidate has a dihedral image
    # satisfying it; completeness preserved because blocking clauses are
    # added for all dihedral images anyway.
    def dist(e):
        return min((e[1] - e[0]) % n, (e[0] - e[1]) % n)

    for d in range(min_dist, n // 2 + 1):
        e0 = (0, d)
        if e0 not in var:
            continue
        z = pool.id(("z", d))
        base_clauses.append([-z, var[e0]])
        for e in chords:
            if dist(e) < d:
                base_clauses.append([-z, -var[e]])
    base_clauses.append([pool.id(("z", d)) for d in range(min_dist, n // 2 + 1)
                         if (0, d) in var])

    def fresh_solver():
        s = Cadical153(bootstrap_with=base_clauses)
        for cl in blocking:
            s.add_clause(cl)
        return s

    solver = fresh_solver()
    restarts = 0

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
        # budgeted solve; on stall, rebuild solver fresh (re-preprocessing the
        # accumulated clause DB is often far faster than grinding on)
        solver.conf_budget(2_000_000)
        res = solver.solve_limited()
        if res is None:
            restarts += 1
            solver.delete()
            solver = fresh_solver()
            msg = f"n={n} solver stall -> rebuild #{restarts} (models={models}, blocking={len(blocking)})"
            print(msg, flush=True)
            if notes:
                with open(notes, "a") as f:
                    f.write(msg + "\n")
            res = solver.solve()
        if not res:
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
            lits = [-var[e] for e in cl]
            blocking.append(lits)
            solver.add_clause(lits)
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
        "n": n, "min_dist": min_dist, "status": status, "models": models,
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
    ap.add_argument("--min-dist", type=int, default=2,
                    help="minimum cyclic distance of allowed chords (subfamily restriction)")
    a = ap.parse_args()
    r = run(a.n, a.seconds, notes=a.notes, nearmiss=not a.no_nearmiss,
            min_dist=a.min_dist)
    sys.exit(0 if r["status"] in ("exhausted-unsat", "FOUND") else 2)

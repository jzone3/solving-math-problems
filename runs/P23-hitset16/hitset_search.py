"""Sound minimum-hitting-set CEGAR loop over one complete UDG universe.

The only clauses added to the outer problem are genuine hyperedges D:
the driver holds a proper colouring of U \\ D and re-checks coverage and every
edge before adding ``sum(x[v] for v in D) >= 1``.
"""
import argparse
import json
import os
import pickle
import random
import time

from ortools.sat.python import cp_model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="wt_r3.pkl")
    ap.add_argument("--bank", default="hyperedges_r3.pkl")
    ap.add_argument("--out", default="hitset_r3.jsonl")
    ap.add_argument("--max-iters", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--outer-seconds", type=int, default=300)
    ap.add_argument("--no-degree", action="store_true",
                    help="diagnostic fallback; omit critical-degree constraints")
    ap.add_argument("--sample-period", type=int, default=50)
    args = ap.parse_args()

    os.environ["POOL"] = args.pool
    os.environ["WHOLE"] = "1"
    os.environ["FROZEN"] = ""
    import hyperpar as H

    pts, edges = pickle.load(open(args.pool, "rb"))
    universe = set(range(len(pts)))
    bank = [sorted(set(d)) for d in pickle.load(open(args.bank, "rb"))]
    bank = list({tuple(d) for d in bank})
    support = sorted(set().union(*(set(d) for d in bank))) if bank else []
    support_set = set(support)
    def build_adj():
        out = {v: set() for v in support}
        for u, v in edges:
            if u in support_set and v in support_set:
                out[u].add(v)
                out[v].add(u)
        return out

    adj = build_adj()
    rng = random.Random(128371)
    started = time.time()
    history = []

    def solve_outer():
        model = cp_model.CpModel()
        x = {v: model.NewBoolVar(f"x_{v}") for v in support}
        for d in bank:
            model.Add(sum(x[v] for v in d) >= 1)
        # A minimum critical witness may be assumed to have minimum induced
        # degree at least four: a vertex of degree <=3 is colourable last.
        if not args.no_degree:
            for v in support:
                ns = [u for u in adj[v] if u in x]
                if len(ns) < 4:
                    model.Add(x[v] == 0)
                else:
                    model.Add(sum(x[u] for u in ns) >= 4 * x[v])
        model.Minimize(sum(x.values()))
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = args.workers
        solver.parameters.max_time_in_seconds = args.outer_seconds
        solver.parameters.random_seed = 712367
        status = solver.Solve(model)
        selected = [v for v in support if solver.Value(x[v])]
        return solver, status, selected

    def assert_sound(D, col):
        assert set(col) == universe, (
            f"colouring coverage {len(col)} != universe {len(universe)}")
        outside = universe - set(D)
        assert all(v in col for v in outside)
        for u, v in edges:
            if u not in D and v not in D:
                assert col[u] != col[v], f"residual conflict {(u, v)}"

    def independent_bank_check():
        if not bank:
            return
        for i, d in enumerate(rng.sample(bank, min(8, len(bank)))):
            st = H.kissat_color(sorted(universe - set(d)), f"ind_{i}")
            assert st, f"independent bank check failed for edge {i}"

    with open(args.out, "a", buffering=1) as log:
        for iteration in range(1, args.max_iters + 1):
            solver, status, selected = solve_outer()
            status_name = solver.StatusName(status)
            bound = solver.BestObjectiveBound()
            rec = {
                "iteration": iteration,
                "seconds": round(time.time() - started, 3),
                "bank": len(bank),
                "support": len(support),
                "outer_status": status_name,
                "outer_bound": bound,
                "selection": len(selected),
            }
            if status == cp_model.OPTIMAL:
                rec["proven_infeasible_bounds"] = [
                    b for b in (508, 450, 400, 300, 200, 100)
                    if len(selected) > b
                ]
            if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                print(json.dumps(rec), flush=True)
                log.write(json.dumps(rec) + "\n")
                break
            # A proper colouring of the selected graph is extended over the
            # whole complement.  The resulting D is therefore disjoint from
            # the selection and is a valid cut against this model.
            col = H.kissat_color(selected, f"sel_{iteration}")
            if col is None:
                rec["witness"] = len(selected)
                print(json.dumps(rec), flush=True)
                log.write(json.dumps(rec) + "\n")
                pickle.dump(selected, open(
                    f"hitset_r3_witness_{len(selected)}.pkl", "wb"))
                break
            if not col:
                rec["colouring"] = "UNKNOWN"
                print(json.dumps(rec), flush=True)
                log.write(json.dumps(rec) + "\n")
                break
            result = H.tabu_hyperedge(
                col, [v for v in universe if v not in set(selected)],
                rng, return_col=True)
            if not result:
                rec["hyperedge"] = "TABU_FAILED"
                print(json.dumps(rec), flush=True)
                log.write(json.dumps(rec) + "\n")
                continue
            d, full_col = result
            assert not (set(d) & set(selected))
            assert_sound(d, full_col)
            bank.append(sorted(d))
            bank = list({tuple(d) for d in bank})
            support = sorted(set().union(*(set(d) for d in bank)))
            support_set = set(support)
            adj = build_adj()
            # Persist every sound clause before the next outer solve.
            pickle.dump([list(d) for d in bank],
                        open(args.bank, "wb"))
            rec["hyperedge"] = len(d)
            rec["bank_min"] = min(map(len, bank))
            rec["bank_median"] = sorted(map(len, bank))[len(bank) // 2]
            rec["bank_max"] = max(map(len, bank))
            print(json.dumps(rec), flush=True)
            log.write(json.dumps(rec) + "\n")
            if iteration % args.sample_period == 0:
                independent_bank_check()


if __name__ == "__main__":
    main()

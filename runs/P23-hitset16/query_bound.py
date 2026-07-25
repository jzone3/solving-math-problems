"""Feasibility query for a size-bounded outer selection on one universe."""
import argparse
import json
import os
import pickle

from ortools.sat.python import cp_model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="wt_witness2167.pkl")
    ap.add_argument("--bank", default="maxcolor_bank_witness2167_fast.pkl")
    ap.add_argument("--bound", type=int, required=True)
    ap.add_argument("--seconds", type=int, default=60)
    ap.add_argument("--workers", type=int, default=8)
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
    adj = {v: set() for v in support}
    for u, v in edges:
        if u in support_set and v in support_set:
            adj[u].add(v)
            adj[v].add(u)

    model = cp_model.CpModel()
    x = {v: model.NewBoolVar(f"x_{v}") for v in support}
    for d in bank:
        model.Add(sum(x[v] for v in d) >= 1)
    model.Add(sum(x.values()) <= args.bound)
    for v in support:
        ns = [u for u in adj[v] if u in x]
        if len(ns) < 4:
            model.Add(x[v] == 0)
        else:
            model.Add(sum(x[u] for u in ns) >= 4 * x[v])
    model.Minimize(sum(x.values()))

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = args.workers
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.random_seed = 712367
    status = solver.Solve(model)
    status_name = solver.StatusName(status)
    out = {
        "bank": len(bank),
        "support": len(support),
        "bound": args.bound,
        "status": status_name,
        "objective": solver.ObjectiveValue() if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None,
        "best_bound": solver.BestObjectiveBound(),
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        selected = [v for v in support if solver.Value(x[v])]
        out["selection"] = len(selected)
        col = H.kissat_color(selected, f"bound_{args.bound}")
        out["colourable"] = bool(col)
        if not col:
            out["witness"] = len(selected)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

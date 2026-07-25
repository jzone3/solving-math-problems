"""Maximum-colourable-subset hyperedge generation on a scoped universe."""
import argparse
import json
import os
import pickle
import random
import statistics
import time
from multiprocessing import Pool

from ortools.sat.python import cp_model


def solve_one(job):
    pts, edges, seed, seconds, tabu = job
    n = len(pts)
    model = cp_model.CpModel()
    y = [model.NewBoolVar(f"y{v}") for v in range(n)]
    c = [[model.NewBoolVar(f"c{v}_{k}") for k in range(4)]
         for v in range(n)]
    for v in range(n):
        model.Add(sum(c[v]) == y[v])
    for u, v in edges:
        for k in range(4):
            model.Add(c[u][k] + c[v][k] <= 1)
    # WLOG fix one colour on one vertex when that vertex is retained.
    model.Add(c[0][0] == y[0])
    warm = None
    if tabu:
        import hyperpar as h
        rng = random.Random(seed)
        ca = h.kissat_color(h.SIDE_VERTICES[0], f"mc_a{seed}")
        cb = h.kissat_color(h.SIDE_VERTICES[1], f"mc_b{seed}")
        base = dict(ca)
        perm = list(range(4))
        rng.shuffle(perm)
        base.update({v: perm[cb[v]] for v in cb})
        # Reuse the sound tabu path only as a feasible warm start.
        warm = h.tabu_hyperedge(base, range(n), rng, tabu=tabu,
                                return_col=True)
        if warm:
            warm_d, warm_col = warm
            if 0 in warm_col:
                shift = warm_col[0]
                warm_col = {v: (color - shift) % 4
                            for v, color in warm_col.items()}
            warm_d = set(warm_d)
            for v in range(n):
                model.AddHint(y[v], int(v not in warm_d))
                for k in range(4):
                    model.AddHint(c[v][k],
                                  int(v not in warm_d and warm_col[v] == k))
    rng = random.Random(seed)
    weights = [10000 + rng.randrange(1000) for _ in range(n)]
    model.Maximize(sum(weights[v] * y[v] for v in range(n)))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = seed
    solver.parameters.cp_model_presolve = True
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"seed": seed, "status": solver.StatusName(status)}
    keep = [v for v in range(n) if solver.Value(y[v])]
    colors = {v: next(k for k in range(4) if solver.Value(c[v][k]))
              for v in keep}
    # Exact post-check of the returned coloured subset.
    keep_set = set(keep)
    assert len(colors) == len(keep)
    assert all(colors[u] != colors[v]
               for u, v in edges if u in keep_set and v in keep_set)
    return {
        "seed": seed,
        "status": solver.StatusName(status),
        "keep": keep,
        "colors": colors,
        "objective": solver.ObjectiveValue(),
        "bound": solver.BestObjectiveBound(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="wt_r3_core5751.pkl")
    ap.add_argument("--out", default="maxcolor_bank.pkl")
    ap.add_argument("--log", default="logs/maxcolor_bank.jsonl")
    ap.add_argument("--runs", type=int, default=16)
    ap.add_argument("--seconds", type=int, default=120)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--tabu", type=int, default=1000000)
    ap.add_argument("--seed-offset", type=int, default=0)
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--min-d", type=int, default=0)
    ap.add_argument("--max-frac", type=float, default=0.05)
    args = ap.parse_args()
    pts, edges = pickle.load(open(args.pool, "rb"))
    jobs = [(pts, edges, args.seed_offset + i + 1, args.seconds, args.tabu)
            for i in range(args.runs)]
    results = []
    with Pool(args.workers) as p:
        for result in p.imap_unordered(solve_one, jobs):
            if "keep" in result:
                d = len(pts) - len(result["keep"])
                result["d_size"] = d
                result["accepted"] = d >= args.min_d and d <= args.max_frac * len(pts)
                if result["accepted"]:
                    results.append(result)
            with open(args.log, "a") as f:
                f.write(json.dumps({k: v for k, v in result.items()
                                    if k not in ("keep", "colors")}) + "\n")
            print(json.dumps({k: v for k, v in result.items()
                              if k not in ("keep", "colors")}), flush=True)
    bank = pickle.load(open(args.out, "rb")) if args.append and os.path.exists(args.out) else []
    seen = {tuple(d) for d in bank}
    for result in results:
        d = tuple(sorted(set(range(len(pts))) - set(result["keep"])))
        if d not in seen:
            seen.add(d)
            bank.append(list(d))
    pickle.dump(bank, open(args.out, "wb"))
    sizes = sorted(map(len, bank))
    if sizes:
        print(f"accepted={len(bank)} min={min(sizes)} "
              f"median={statistics.median(sizes)} max={max(sizes)}")
    else:
        print("accepted=0")


if __name__ == "__main__":
    main()

"""Wave 2d: decomposition-count-guided annealing.

Fundamentally different signal from feasibility: for tight instances, count the
number of decompositions into <= K cycles (capped enumeration via CP-SAT solution
callback).  Score = count; anneal toggles/moves to MINIMIZE the count.  A graph
whose count hits 0 is a counterexample.  Near-misses (tiny counts) are logged as
frontier data -- they show how 'close' the conjecture is to failing.
"""
import random, sys, time, argparse
from ortools.sat.python import cp_model
import mincyc as M
from search import toggle_even_set, valid, canon, degrees


class Counter(cp_model.CpSolverSolutionCallback):
    def __init__(self, cap):
        super().__init__()
        self.count = 0
        self.cap = cap

    def on_solution_callback(self):
        self.count += 1
        if self.count >= self.cap:
            self.StopSearch()


def count_decomps(n, edges, k, cap=2000, time_limit=240.0):
    """Capped count of (class-assignment, orientation) solutions for <= k cycles.
    Not the exact decomposition count (orientations/symmetries inflate it), but a
    consistent relative score; 0 <=> counterexample."""
    m = len(edges)
    model = cp_model.CpModel()
    x = [[[model.NewBoolVar(f"x{e}_{c}_{d}") for d in range(2)] for c in range(k)]
         for e in range(m)]
    for e in range(m):
        model.AddExactlyOne(x[e][c][d] for c in range(k) for d in range(2))
    for c in range(k):
        arcs = []
        for vtx in range(n):
            lit = model.NewBoolVar(f"in{c}_{vtx}")
            arcs.append((vtx, vtx, lit.Not()))
        for e, (u, v) in enumerate(edges):
            arcs.append((u, v, x[e][c][0]))
            arcs.append((v, u, x[e][c][1]))
        model.AddCircuit(arcs)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.enumerate_all_solutions = True
    solver.parameters.num_search_workers = 1
    cb = Counter(cap)
    solver.Solve(model, cb)
    return cb.count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=14)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--iters", type=int, default=3000)
    ap.add_argument("--cap", type=int, default=2000)
    args = ap.parse_args()
    n = args.n
    K = (n - 1) // 2
    rng = random.Random(args.seed)
    lf = open(f"count_anneal_n{n}_s{args.seed}.txt", "a")

    def log(m_):
        print(m_, flush=True)
        lf.write(m_ + "\n")
        lf.flush()

    if n % 2 == 0:
        # seed: split of K_{n-1} (structurally constrained tight instance)
        base = n - 1
        a = 4
        E = []
        for i in range(base):
            for j in range(i + 1, base):
                if i == 0 and j <= a:
                    E.append((base, j))
                else:
                    E.append((i, j))
    else:
        # seed: clique tree of K5 blocks (structurally tight, Erdos-Gallai extremal)
        assert (n - 1) % 4 == 0, "odd n must be 4l+1 for a K5 clique path"
        E = []
        start = 0
        while start + 4 < n or start == 0:
            vs = list(range(start, start + 5))
            E += [(vs[i], vs[j]) for i in range(5) for j in range(i + 1, 5)]
            start += 4
            if start + 4 >= n + 1:
                break
    cur = sorted(canon(E))
    cur_score = count_decomps(n, cur, K, args.cap)
    best_score = cur_score
    log(f"=== count-anneal n={n} K={K} cap={args.cap} start score={cur_score} "
        f"m={len(cur)} ===")
    temp = 1.0
    for it in range(args.iters):
        cand = toggle_even_set(n, cur, rng, max_len=8)
        if cand is None or not valid(n, cand):
            continue
        sc = count_decomps(n, cand, K, args.cap)
        if sc == 0:
            # verify it's a real infeasibility (not enumeration artifact)
            ok, _ = M.decomposable_within(n, cand, K, 600)
            if ok is False:
                log(f"*** WITNESS *** n={n} edges={sorted(canon(cand))}")
                import json
                with open("witness_count.json", "w") as f:
                    json.dump({"n": n, "edges": sorted(canon(cand))}, f)
                return
            log(f"it={it} count=0 but feasible (cap/time artifact) m={len(cand)}")
            continue
        # accept if better, or with annealing probability
        if sc <= cur_score or rng.random() < temp * 0.25:
            cur, cur_score = sorted(canon(cand)), sc
        if sc < best_score:
            best_score = sc
            log(f"it={it} BEST count={sc} m={len(cand)} deg={sorted(set(degrees(n, cand)))} "
                f"edges={sorted(canon(cand))}")
        if it % 100 == 0:
            log(f"it={it} cur={cur_score} best={best_score} m={len(cur)} temp={temp:.2f}")
        temp = max(0.05, temp * 0.999)
    log(f"=== done best={best_score} ===")


if __name__ == "__main__":
    main()

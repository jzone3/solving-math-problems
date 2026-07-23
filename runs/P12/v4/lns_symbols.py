#!/usr/bin/env python3
"""Symbol-neighborhood LNS for T2(n) — orthogonal to row-LNS.

Free a set F of k symbols across ALL rows: in each row, the non-freed symbols
keep their relative order, while freed symbols may be re-inserted anywhere.
All pos vars re-solved with those ordering chains; full soft objective.

Usage: lns_symbols.py n start_file [seconds] [k] [iter_tl] [seed]
"""
import random
import sys
import time

from ortools.sat.python import cp_model

from t2_common import cost, write_witness


def violating_symbols(arr):
    n = len(arr)
    c1, c2 = {}, {}
    for r in arr:
        for i in range(n - 1):
            c1[(r[i], r[i + 1])] = c1.get((r[i], r[i + 1]), 0) + 1
        for i in range(n - 2):
            c2[(r[i], r[i + 2])] = c2.get((r[i], r[i + 2]), 0) + 1
    bad = set()
    for (a, b), v in c1.items():
        if v > 1:
            bad.update((a, b))
    for (a, b), v in c2.items():
        if v > 1:
            bad.update((a, b))
    return bad


def solve_neighborhood(arr, free, iter_tl, target, seed):
    n = len(arr)
    m = cp_model.CpModel()
    pos = [[m.NewIntVar(0, n - 1, f"p{r}_{a}") for a in range(n)] for r in range(n)]
    for r in range(n):
        m.AddAllDifferent(pos[r])
        chain = [a for a in arr[r] if a not in free]
        for x, y in zip(chain, chain[1:]):
            m.Add(pos[r][x] < pos[r][y])
    adj1, adj2 = {}, {}
    for r in range(n):
        for a in range(n):
            for b in range(n):
                if a == b:
                    continue
                v1 = m.NewBoolVar(f"a1_{r}_{a}_{b}")
                m.Add(pos[r][b] - pos[r][a] == 1).OnlyEnforceIf(v1)
                m.Add(pos[r][b] - pos[r][a] != 1).OnlyEnforceIf(v1.Not())
                adj1[r, a, b] = v1
                v2 = m.NewBoolVar(f"a2_{r}_{a}_{b}")
                m.Add(pos[r][b] - pos[r][a] == 2).OnlyEnforceIf(v2)
                m.Add(pos[r][b] - pos[r][a] != 2).OnlyEnforceIf(v2.Not())
                adj2[r, a, b] = v2
    pens = []
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            e1 = m.NewIntVar(0, n, f"e1_{a}_{b}")
            m.Add(sum(adj1[r, a, b] for r in range(n)) - 1 <= e1)
            pens.append(e1)
            e2 = m.NewIntVar(0, n, f"e2_{a}_{b}")
            m.Add(sum(adj2[r, a, b] for r in range(n)) - 1 <= e2)
            pens.append(e2)
    obj = sum(pens)
    m.Add(obj <= target)
    m.Minimize(obj)
    for r in range(n):
        for c in range(n):
            m.AddHint(pos[r][arr[r][c]], c)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = iter_tl
    s.parameters.num_workers = 4
    s.parameters.random_seed = seed
    res = s.Solve(m)
    if res not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    new = [[0] * n for _ in range(n)]
    for r in range(n):
        for a in range(n):
            new[r][s.Value(pos[r][a])] = a
    return new


def main():
    n = int(sys.argv[1])
    start = sys.argv[2]
    seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 3600
    k = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    iter_tl = float(sys.argv[5]) if len(sys.argv) > 5 else 60
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    rng = random.Random(seed)
    with open(start) as f:
        arr = [[int(x) for x in line.split()] for line in f if line.strip()]
    cur = cost(arr)
    best = cur
    print(f"start cost {cur}", flush=True)
    t_end = time.time() + seconds
    it = 0
    while time.time() < t_end and best > 0:
        it += 1
        bad = list(violating_symbols(arr))
        rng.shuffle(bad)
        free = set(bad[:max(1, k - 1)])
        while len(free) < k:
            free.add(rng.randrange(n))
        new = solve_neighborhood(arr, free, iter_tl, target=cur, seed=it)
        if new is not None:
            nc = cost(new)
            if nc < cur or (nc == cur and rng.random() < 0.7):
                arr = new
                cur = nc
                if nc < best:
                    best = nc
                    write_witness(arr, f"lnssym_T2_{n}_seed{seed}_best.txt")
                    print(f"[it {it}] new best {best}", flush=True)
                    if best == 0:
                        print("SOLVED")
                        return
        if it % 10 == 0:
            print(f"[it {it}] cur {cur} best {best}", flush=True)
    write_witness(arr, f"lnssym_T2_{n}_seed{seed}_final.txt")
    print(f"FINAL best={best}", flush=True)


if __name__ == "__main__":
    main()

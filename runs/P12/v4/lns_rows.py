#!/usr/bin/env python3
"""Row-neighborhood LNS for T2(n).

Keep an incumbent array; each iteration free k random rows (biased toward rows
involved in violations), fix the rest, and CP-SAT-minimize total excess over the
freed rows' adjacencies (full objective recomputed over all rows, fixed rows'
contributions constant). Accept strictly-better; occasional random-walk accept
of equal cost to escape plateaus.

Usage: lns_rows.py n start_file [seconds] [k] [iter_tl] [seed]
"""
import random
import sys
import time

from ortools.sat.python import cp_model

from t2_common import cost, write_witness


def pair_counts(arr):
    n = len(arr)
    c1, c2 = {}, {}
    for r in arr:
        for i in range(n - 1):
            c1[(r[i], r[i + 1])] = c1.get((r[i], r[i + 1]), 0) + 1
        for i in range(n - 2):
            c2[(r[i], r[i + 2])] = c2.get((r[i], r[i + 2]), 0) + 1
    return c1, c2


def violating_rows(arr):
    n = len(arr)
    c1, c2 = pair_counts(arr)
    bad = set()
    for ri, r in enumerate(arr):
        for i in range(n - 1):
            if c1[(r[i], r[i + 1])] > 1:
                bad.add(ri)
        for i in range(n - 2):
            if c2[(r[i], r[i + 2])] > 1:
                bad.add(ri)
    return bad


def solve_neighborhood(arr, free, iter_tl, target):
    """Re-solve freed rows; returns new array or None."""
    n = len(arr)
    m = cp_model.CpModel()
    pos = {}
    for r in free:
        pos[r] = [m.NewIntVar(0, n - 1, f"p{r}_{a}") for a in range(n)]
        m.AddAllDifferent(pos[r])
    # fixed contributions
    fc1, fc2 = {}, {}
    for ri, row in enumerate(arr):
        if ri in free:
            continue
        for i in range(n - 1):
            fc1[(row[i], row[i + 1])] = fc1.get((row[i], row[i + 1]), 0) + 1
        for i in range(n - 2):
            fc2[(row[i], row[i + 2])] = fc2.get((row[i], row[i + 2]), 0) + 1
    adj1, adj2 = {}, {}
    for r in free:
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
            s1 = fc1.get((a, b), 0) + sum(adj1[r, a, b] for r in free)
            e1 = m.NewIntVar(0, n, f"e1_{a}_{b}")
            m.Add(s1 - 1 <= e1)
            pens.append(e1)
            s2 = fc2.get((a, b), 0) + sum(adj2[r, a, b] for r in free)
            e2 = m.NewIntVar(0, n, f"e2_{a}_{b}")
            m.Add(s2 - 1 <= e2)
            pens.append(e2)
    obj = sum(pens)
    m.Add(obj <= target)
    m.Minimize(obj)
    for r in free:
        for c in range(n):
            m.AddHint(pos[r][arr[r][c]], c)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = iter_tl
    s.parameters.num_workers = 4
    res = s.Solve(m)
    if res not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    new = [row[:] for row in arr]
    for r in free:
        for a in range(n):
            new[r][s.Value(pos[r][a])] = a
    return new


def main():
    n = int(sys.argv[1])
    start = sys.argv[2]
    seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 3600
    k = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    iter_tl = float(sys.argv[5]) if len(sys.argv) > 5 else 30
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
        bad = list(violating_rows(arr))
        rng.shuffle(bad)
        free = set(bad[:max(1, k - 1)])
        while len(free) < k:
            free.add(rng.randrange(n))
        # allow equal-cost moves (plateau walk) and rare uphill (+1) diversification
        uphill = rng.random() < 0.15
        new = solve_neighborhood(arr, free, iter_tl, target=cur + (1 if uphill else 0))
        if new is None:
            continue
        nc = cost(new)
        if nc < cur or (nc == cur and rng.random() < 0.7) or (uphill and nc == cur + 1 and rng.random() < 0.5):
            arr = new
            cur = nc
            if nc < best:
                best = nc
                write_witness(arr, f"lns_T2_{n}_seed{seed}_best.txt")
                print(f"[it {it}] new best {best}", flush=True)
                if best == 0:
                    print("SOLVED")
                    return
        if it % 20 == 0:
            print(f"[it {it}] cur {cur} best {best}", flush=True)
    write_witness(arr, f"lns_T2_{n}_seed{seed}_final.txt")
    print(f"FINAL best={best}", flush=True)


if __name__ == "__main__":
    main()

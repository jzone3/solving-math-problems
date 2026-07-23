#!/usr/bin/env python3
"""Complete Kramer–Mesner decision for BTD(14,28;8,3,14;7,6) admitting the
automorphism sigma = (0 1 2 3 4 5 6)(7 8 9 10 11 12 13) (two 7-cycles).

Under sigma, blocks split into orbits of size 7 (generic) or size 1 (fixed
blocks). A fixed block is a sigma-invariant multiset of size 7 with mult<=2:
multiplicities constant on each point orbit, 7a+7b=7 => exactly one point
orbit with multiplicity 1 (two types: O1x1, O2x1).

We enumerate ALL size-7 base-block multisets m in {0,1,2}^14 (up to sigma
shift), compute each orbit's contribution signature, and solve the exact
integer feasibility problem with CP-SAT over ALL possible orbit-type counts
simultaneously (t7 size-7 orbit columns with total multiplicity t, n1/n2
fixed blocks, 7*t + n1 + n2 = 28):

  per point-orbit O in {O1,O2}:  sum_b cnt_b*c1_b(O) + fixed contributions = p1 = 8
                                  sum_b cnt_b*c2_b(O) + 0                  = p2 = 3
  per pair-orbit P (13 of them): sum_b cnt_b*A_b(P) + fixed contributions = L = 6

A solution reconstructs a full 14x28 witness (verified externally by
solutions/P14/verify.py). INFEASIBLE = no BTD(14,28;8,3,14;7,6) admits this
automorphism (a complete structured-nonexistence statement for this sigma).
"""
import itertools
import sys
from ortools.sat.python import cp_model

V, B, P1, P2, R, K, L = 14, 28, 8, 3, 14, 7, 6
sigma = [(i + 1) % 7 for i in range(7)] + [7 + (i + 1) % 7 for i in range(7)]

# pair-orbit representatives: within-half diffs 1..3 (each half), cross diffs 0..6
PAIR_REPS = ([("w1", d, (0, d)) for d in (1, 2, 3)]
             + [("w2", d, (7, 7 + d)) for d in (1, 2, 3)]
             + [("x", d, (0, 7 + d)) for d in range(7)])


def shift(m, k):
    return tuple(m[(i - k) % 7] for i in range(7)) + tuple(m[7 + (i - k) % 7] for i in range(7))


def signature(m):
    c1 = [sum(1 for i in range(7) if m[i] == 1), sum(1 for i in range(14) if i >= 7 and m[i] == 1)]
    c2 = [sum(1 for i in range(7) if m[i] == 2), sum(1 for i in range(14) if i >= 7 and m[i] == 2)]
    A = []
    for _, _, (u, v) in PAIR_REPS:
        s = 0
        uu, vv = u, v
        for _ in range(7):
            s += m[uu] * m[vv]
            uu, vv = sigma[uu], sigma[vv]
        A.append(s)
    return tuple(c1 + c2 + A)


def enumerate_blocks():
    """all m in {0,1,2}^14, sum 7, up to sigma-shift; return list of (rep, sig)."""
    seen = set()
    reps = []
    # choose positions of 2s (t2 of them) and 1s (7-2*t2)
    for t2 in range(0, 4):
        n1 = 7 - 2 * t2
        for pos2 in itertools.combinations(range(14), t2):
            rest = [i for i in range(14) if i not in pos2]
            for pos1 in itertools.combinations(rest, n1):
                m = [0] * 14
                for i in pos2:
                    m[i] = 2
                for i in pos1:
                    m[i] = 1
                m = tuple(m)
                canon = min(shift(m, k) for k in range(7))
                if canon in seen:
                    continue
                seen.add(canon)
                reps.append(canon)
    return reps


def main():
    max_s = float(sys.argv[1]) if len(sys.argv) > 1 else 3600
    reps = enumerate_blocks()
    sigs = [signature(m) for m in reps]
    print(f"{len(reps)} block-orbit representatives")

    md = cp_model.CpModel()
    cnt = [md.NewIntVar(0, 4, f"c{i}") for i in range(len(reps))]
    n1 = md.NewIntVar(0, 28, "n1")
    n2 = md.NewIntVar(0, 28, "n2")
    t = md.NewIntVar(0, 4, "t")
    md.Add(sum(cnt) == t)
    md.Add(7 * t + n1 + n2 == B)
    # p1 per orbit: fixed type1 contributes 1 to c1(O1) each; type2 to c1(O2)
    md.Add(sum(c * s[0] for c, s in zip(cnt, sigs)) + n1 == P1)
    md.Add(sum(c * s[1] for c, s in zip(cnt, sigs)) + n2 == P1)
    md.Add(sum(c * s[2] for c, s in zip(cnt, sigs)) == P2)
    md.Add(sum(c * s[3] for c, s in zip(cnt, sigs)) == P2)
    # pair orbits: fixed type1 covers each within-O1 pair once (orbits 0..2);
    # type2 covers within-O2 pairs (orbits 3..5); cross pairs (6..12) uncovered.
    for pi in range(13):
        fixed = 0
        if pi <= 2:
            fixed = n1
        elif pi <= 5:
            fixed = n2
        md.Add(sum(c * s[4 + pi] for c, s in zip(cnt, sigs)) + fixed == L)

    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = max_s
    sv.parameters.num_workers = 8
    sv.parameters.log_search_progress = True
    st = sv.Solve(md)
    print("status:", sv.StatusName(st), "wall:", round(sv.WallTime(), 1), "s")
    if st in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        chosen = []
        for i, c in enumerate(cnt):
            v = sv.Value(c)
            for _ in range(v):
                chosen.append(reps[i])
        N1, N2 = sv.Value(n1), sv.Value(n2)
        print("n1,n2 =", N1, N2)
        cols = []
        for m in chosen:
            for k in range(7):
                cols.append(shift(m, k))
        cols += [tuple([1] * 7 + [0] * 7)] * N1 + [tuple([0] * 7 + [1] * 7)] * N2
        rows = [" ".join(str(cols[j][i]) for j in range(B)) for i in range(V)]
        with open("witness-14-28-8-3-14-7-6.txt", "w") as f:
            f.write("\n".join(rows) + "\n")
        print("witness written")


if __name__ == "__main__":
    main()

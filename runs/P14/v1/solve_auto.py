#!/usr/bin/env python3
"""Prescribed-automorphism (Kramer–Mesner-style) CP-SAT search for
BTD(14,28;8,3,14;7,6).

We prescribe an automorphism sigma of the point set (a permutation of the V
rows) and a compatible action on blocks: blocks are partitioned into orbits
whose sizes divide ord(sigma); within an orbit, column j_{k+1} is column j_k
with rows permuted by sigma; a representative column of an orbit of size s
must additionally be invariant under sigma^s. This collapses the search to
one representative column per orbit — a huge reduction — at the cost of only
finding designs admitting sigma. UNSAT here does NOT prove nonexistence, it
only rules out sigma-invariant designs.

Usage: solve_auto.py CONFIG_NAME [max_seconds] [workers] [out_file]
Configs defined in CONFIGS below.
"""
import sys
from ortools.sat.python import cp_model

V, B, P1, P2, R, K, L = 14, 28, 8, 3, 14, 7, 6


def cyc(*cycles, n=V):
    p = list(range(n))
    for c in cycles:
        for t in range(len(c)):
            p[c[t]] = c[(t + 1) % len(c)]
    return p


Z7_two7 = cyc(list(range(7)), list(range(7, 14)))          # two 7-cycles
Z7_fix7 = cyc(list(range(7)))                               # 7-cycle + 7 fixed
Z2_seven = cyc(*[[2 * i, 2 * i + 1] for i in range(7)])     # 7 transpositions
Z2_six = cyc(*[[2 * i, 2 * i + 1] for i in range(6)])       # 6 transp + 2 fixed
Z13 = cyc(list(range(13)))                                  # 13-cycle + 1 fixed
Z14 = cyc(list(range(14)))                                  # 14-cycle
Z4 = cyc(*[[4*i, 4*i+1, 4*i+2, 4*i+3] for i in range(3)], [12, 13])  # order 4: three 4-cycles + one 2-cycle

# CONFIGS: name -> (sigma, order, list of block orbit sizes summing to 28)
CONFIGS = {
    "z7-two7-4x7":  (Z7_two7, 7, [7, 7, 7, 7]),
    "z7-two7-7f-3x7": (Z7_two7, 7, [1] * 7 + [7, 7, 7]),
    "z7-two7-14f-2x7": (Z7_two7, 7, [1] * 14 + [7, 7]),
    "z7-fix7-4x7":  (Z7_fix7, 7, [7, 7, 7, 7]),
    "z7-fix7-7f-3x7": (Z7_fix7, 7, [1] * 7 + [7, 7, 7]),
    "z7-fix7-14f-2x7": (Z7_fix7, 7, [1] * 14 + [7, 7]),
    "z7-fix7-21f-1x7": (Z7_fix7, 7, [1] * 21 + [7]),
    "z7-fix7-28f": (Z7_fix7, 7, [1] * 28),
    "z14-2x14":     (Z14, 14, [14, 14]),
    "z14-2x7-1x14": (Z14, 14, [7, 7, 14]),
    "z14-4x7":      (Z14, 14, [7, 7, 7, 7]),
    "z14-14f-1x14": (Z14, 14, [2] * 7 + [14]),
    "z13-2x13-2f":  (Z13, 13, [1, 1, 13, 13]),
    "z2-seven-14x2": (Z2_seven, 2, [2] * 14),
    "z2-seven-4f-12x2": (Z2_seven, 2, [1] * 4 + [2] * 12),
    "z2-seven-8f-10x2": (Z2_seven, 2, [1] * 8 + [2] * 10),
    "z2-six-14x2":  (Z2_six, 2, [2] * 14),
    "z4-7x4":       (Z4, 4, [4] * 7),
    "z4-2x2-6x4":   (Z4, 4, [2, 2, 4, 4, 4, 4, 4, 4]),
}



Z3_four = cyc(*[[3*i,3*i+1,3*i+2] for i in range(4)])       # four 3-cycles + 2 fixed
Z5_two = cyc(list(range(5)), list(range(5,10)))             # two 5-cycles + 4 fixed
Z6 = cyc(list(range(6)), list(range(6,12)), [12,13])        # 6+6+2 cycles, order 6

CONFIGS.update({
    "z3-9x3-1f": (Z3_four, 3, [3]*9+[1]),
    "z3-8x3-4f": (Z3_four, 3, [3]*8+[1]*4),
    "z3-7x3-7f": (Z3_four, 3, [3]*7+[1]*7),
    "z5-5x5-3f": (Z5_two, 5, [5]*5+[1]*3),
    "z5-4x5-8f": (Z5_two, 5, [5]*4+[1]*8),
    "z5-3x5-13f": (Z5_two, 5, [5]*3+[1]*13),
    "z2-seven-2f-13x2": (Z2_seven, 2, [1]*2+[2]*13),
    "z2-seven-6f-11x2": (Z2_seven, 2, [1]*6+[2]*11),
    "z2-seven-10f-9x2": (Z2_seven, 2, [1]*10+[2]*9),
    "z2-seven-12f-8x2": (Z2_seven, 2, [1]*12+[2]*8),
    "z3-6x3-10f": (Z3_four, 3, [3]*6+[1]*10),
    "z6-4x6-2x2": (Z6, 6, [6]*4+[2,2]),
    "z6-4x6-1x3-1f": (Z6, 6, [6]*4+[3,1]),
    "z6-3x6-1x6-2x2": (Z6, 6, [6,6,6,6,2,2]),
    "z6-2x6-2x6-4f": (Z6, 6, [6]*4+[1]*4),
})

def perm_pow(p, k):
    q = list(range(len(p)))
    for _ in range(k):
        q = [p[x] for x in q]
    return q


def main():
    name = sys.argv[1]
    sigma, order, orbit_sizes = CONFIGS[name]
    assert sum(orbit_sizes) == B
    max_s = float(sys.argv[2]) if len(sys.argv) > 2 else 600
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    out = sys.argv[4] if len(sys.argv) > 4 else None

    md = cp_model.CpModel()
    m = [[md.NewIntVar(0, 2, f"m{i}_{j}") for j in range(B)] for i in range(V)]

    # automorphism structure: assign columns to orbits sequentially
    col = 0
    for s in orbit_sizes:
        assert order % s == 0 or s % 1 == 0
        rep = col
        sig_s = perm_pow(sigma, s)
        # orbit columns: col..col+s-1 ; m[i][col+k+1] = m[sigma^{-1}... ] use forward:
        for k in range(s - 1):
            for i in range(V):
                md.Add(m[sigma[i]][col + k + 1] == m[i][col + k])
        # representative invariant under sigma^s
        for i in range(V):
            if sig_s[i] != i:
                md.Add(m[sig_s[i]][rep] == m[i][rep])
        col += s

    for i in range(V):
        md.Add(sum(m[i]) == R)
        ones, twos = [], []
        for j in range(B):
            b1 = md.NewBoolVar("")
            md.Add(m[i][j] == 1).OnlyEnforceIf(b1)
            md.Add(m[i][j] != 1).OnlyEnforceIf(b1.Not())
            b2 = md.NewBoolVar("")
            md.Add(m[i][j] == 2).OnlyEnforceIf(b2)
            md.Add(m[i][j] != 2).OnlyEnforceIf(b2.Not())
            ones.append(b1)
            twos.append(b2)
        md.Add(sum(ones) == P1)
        md.Add(sum(twos) == P2)
    for j in range(B):
        md.Add(sum(m[i][j] for i in range(V)) == K)
    for i in range(V):
        for k in range(i + 1, V):
            prods = []
            for j in range(B):
                p = md.NewIntVar(0, 4, "")
                md.AddMultiplicationEquality(p, [m[i][j], m[k][j]])
                prods.append(p)
            md.Add(sum(prods) == L)

    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = max_s
    sv.parameters.num_workers = workers
    st = sv.Solve(md)
    print(name, "status:", sv.StatusName(st), "wall:", round(sv.WallTime(), 1), "s")
    if st in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        rows = [" ".join(str(sv.Value(m[i][j])) for j in range(B)) for i in range(V)]
        print("\n".join(rows))
        if out:
            with open(out, "w") as f:
                f.write("\n".join(rows) + "\n")


if __name__ == "__main__":
    main()

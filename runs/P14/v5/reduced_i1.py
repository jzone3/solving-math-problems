"""I1 = BTD(14,18;7,1,9;7,4), reduced formulation for the b2=14 sector
(every block has at most one doubled element).

Derivation (machine-independent): r2=1 so each element v is doubled in exactly
one block; if no block has 2+ doubles, the map block->double element is a
bijection on 14 of the 18 blocks; remaining 4 blocks are pure 7-subsets.
Writing block_i = {x_i, x_i} u S_i (|S_i| = 5, x_i not in S_i) and pure blocks
P_j, let T be the 14x14 0/1 matrix with T[i][w] = 1 iff w in S_i (zero diag,
row sums 5) and Q the 4x14 pure-block incidence (row sums 7). Then
N = [2I + T^T | Q^T] and N N^T = 7I + 4J is equivalent to
    T^T T + 2(T + T^T) + Q^T Q = 3I + 4J    ... (*)
whose diagonal gives indeg_T(v) + colsum_Q(v) = 7 (v is single in 7 blocks).
CP-SAT decides (*). UNSAT here + UNSAT of the multidouble branch of the full
model = nonexistence proof for I1. SAT = explicit design.
"""
from ortools.sat.python import cp_model

def build():
    V = 14
    m = cp_model.CpModel()
    T = [[m.NewBoolVar(f"T{i}_{w}") for w in range(V)] for i in range(V)]
    Q = [[m.NewBoolVar(f"Q{j}_{w}") for w in range(V)] for j in range(4)]
    for i in range(V):
        m.Add(T[i][i] == 0)
        m.Add(sum(T[i]) == 5)
    for j in range(4):
        m.Add(sum(Q[j]) == 7)
    for v in range(V):
        m.Add(sum(T[i][v] for i in range(V)) + sum(Q[j][v] for j in range(4)) == 7)
    # pair equations: for u < w:
    # sum_i T[i][u] T[i][w] + sum_j Q[j][u] Q[j][w] + 2 T[u][w] + 2 T[w][u] = 4
    def AND(a, b, tag):
        p = m.NewBoolVar(tag)
        m.AddBoolAnd([a, b]).OnlyEnforceIf(p)
        m.AddBoolOr([a.Not(), b.Not(), p])
        return p
    for u in range(V):
        for w in range(u+1, V):
            terms = []
            for i in range(V):
                terms.append(AND(T[i][u], T[i][w], f"t{i}_{u}_{w}"))
            for j in range(4):
                terms.append(AND(Q[j][u], Q[j][w], f"q{j}_{u}_{w}"))
            m.Add(sum(terms) + 2*T[u][w] + 2*T[w][u] == 4)
    # symmetry: elements can be relabeled (simultaneous row+col perm of T and
    # col perm of Q); pure blocks permutable. Break pure-block order lexicographically.
    for j in range(3):
        # lex: Q[j] >= Q[j+1]
        eq = [m.NewBoolVar(f"qe{j}_{k}") for k in range(V)]
        for k in range(V):
            m.Add(Q[j][k] == Q[j+1][k]).OnlyEnforceIf(eq[k])
            m.Add(Q[j][k] >= Q[j+1][k]).OnlyEnforceIf(eq[:k])
    # element-relabel partial break: indegree sequence of T non-increasing
    ind = [m.NewIntVar(0, 13, f"ind{v}") for v in range(V)]
    for v in range(V):
        m.Add(ind[v] == sum(T[i][v] for i in range(V)))
    # (only a heuristic ordering aid; sound since some relabeling sorts indegrees)
    for v in range(13):
        m.Add(ind[v] >= ind[v+1])
    return m, T, Q

if __name__ == "__main__":
    m, T, Q = build()
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = 14400
    sol.parameters.num_search_workers = 3
    st = sol.Solve(m)
    print("reduced I1 (b2=14 sector):", sol.StatusName(st), f"wall={sol.WallTime():.1f}s")
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        V = 14
        print("T rows (S_i):")
        for i in range(V):
            print("".join(str(sol.Value(T[i][w])) for w in range(V)))
        print("Q rows:")
        for j in range(4):
            print("".join(str(sol.Value(Q[j][w])) for w in range(V)))

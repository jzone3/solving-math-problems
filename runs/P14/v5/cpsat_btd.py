"""CP-SAT model for BTD(V,B; r1,r2,R; K,L) — complete decision.

Encoding: x[v][b] in {0,1,2} via indicator booleans s[v][b] (=1 iff mult 1) and
d[v][b] (=1 iff mult 2), s+d <= 1.
Row: sum_b s = r1, sum_b d = r2. Column: sum_v (s+2d) = K.
Pair: sum_b (s_v s_w + 2 s_v d_w + 2 d_v s_w + 4 d_v d_w) = L, products as ANDs.
Symmetry breaking (sound for UNSAT): lexicographic non-increasing rows and
columns of the multiplicity matrix.

Usage: python3 cpsat_btd.py V B r1 r2 R K L [timelimit_s] [extra]
 extra = 'force_multidouble' -> require some block with >= 2 doubles
"""
import sys
from ortools.sat.python import cp_model

def build(V, B, r1, r2, R, K, L, force_multidouble=False):
    m = cp_model.CpModel()
    s = [[m.NewBoolVar(f"s{v}_{b}") for b in range(B)] for v in range(V)]
    d = [[m.NewBoolVar(f"d{v}_{b}") for b in range(B)] for v in range(V)]
    x = [[m.NewIntVar(0, 2, f"x{v}_{b}") for b in range(B)] for v in range(V)]
    for v in range(V):
        for b in range(B):
            m.AddAtMostOne([s[v][b], d[v][b]])
            m.Add(x[v][b] == s[v][b] + 2*d[v][b])
    for v in range(V):
        m.Add(sum(s[v]) == r1)
        m.Add(sum(d[v]) == r2)
    for b in range(B):
        m.Add(sum(x[v][b] for v in range(V)) == K)
    # pair constraints
    for v in range(V):
        for w in range(v+1, V):
            terms = []
            for b in range(B):
                # products
                for (av, aw, coef) in ((s, s, 1), (s, d, 2), (d, s, 2), (d, d, 4)):
                    p = m.NewBoolVar(f"p{v}_{w}_{b}_{coef}_{id(av)}")
                    m.AddBoolAnd([av[v][b], aw[w][b]]).OnlyEnforceIf(p)
                    m.AddImplication(p, av[v][b])
                    m.AddImplication(p, aw[w][b])
                    m.AddBoolOr([av[v][b].Not(), aw[w][b].Not(), p])
                    terms.append(coef*p)
            m.Add(sum(terms) == L)
    # symmetry breaking: columns lex non-increasing, rows lex non-increasing
    def add_lex_ge(m, X, Y, tag):
        # lexicographic X >= Y
        n = len(X)
        eq = [m.NewBoolVar(f"eq_{tag}_{i}") for i in range(n)]
        for i in range(n):
            pre = eq[:i]
            m.Add(X[i] == Y[i]).OnlyEnforceIf(eq[i])
            m.Add(X[i] >= Y[i]).OnlyEnforceIf(pre)
        # nothing else needed: if all eq true, equal (allowed)
    cols = [[x[v][b] for v in range(V)] for b in range(B)]
    for b in range(B-1):
        add_lex_ge(m, cols[b], cols[b+1], f"c{b}")
    rows = [[x[v][b] for b in range(B)] for v in range(V)]
    for v in range(V-1):
        add_lex_ge(m, rows[v], rows[v+1], f"r{v}")
    if force_multidouble:
        # some block has >= 2 doubles (disjunction: sound alongside lex constraints)
        ts = []
        for b in range(B):
            t = m.NewBoolVar(f"md{b}")
            m.Add(sum(d[v][b] for v in range(V)) >= 2).OnlyEnforceIf(t)
            ts.append(t)
        m.AddBoolOr(ts)
    return m, x

def solve(V, B, r1, r2, R, K, L, tl=600, force_multidouble=False, workers=8):
    m, x = build(V, B, r1, r2, R, K, L, force_multidouble)
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = tl
    sol.parameters.num_search_workers = workers
    st = sol.Solve(m)
    name = sol.StatusName(st)
    mat = None
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        mat = [[sol.Value(x[v][b]) for b in range(B)] for v in range(V)]
    return name, mat, sol.WallTime()

if __name__ == "__main__":
    a = sys.argv[1:]
    V, B, r1, r2, R, K, L = map(int, a[:7])
    tl = float(a[7]) if len(a) > 7 else 600
    fm = len(a) > 8 and a[8] == "force_multidouble"
    name, mat, wt = solve(V, B, r1, r2, R, K, L, tl, fm)
    print(f"status={name} wall={wt:.1f}s")
    if mat:
        for row in mat: print("".join(map(str, row)))

"""SAT encoding (DIMACS) of the reduced I1 formulation, for cube-and-conquer.

Reduced I1 (b2=14 sector, from NOTES.md):
  T: 14x14 binary, zero diagonal, row sums 5
  Q: 4x14 binary, row sums 7
  T^T T + 2(T + T^T) + Q^T Q = 3I + 4J
  off-diagonal (i<j):  sum_k T[k][i]T[k][j] + 2(T[i][j]+T[j][i])
                       + sum_r Q[r][i]Q[r][j] = 4
  diagonal:            indeg_T(i) + colsum_Q(i) = 7

Symmetry: columns (elements) can be permuted; Q rows permuted; WLOG
Q row 0 = {0..6}.  Cubes: Q row 1 canonical by |row1 ∩ {0..6}| = t:
row1 = {0..t-1} ∪ {7..13-t}.  Usage: python3 i1_sat.py <t> > cube_t.cnf
"""
import sys
from pysat.formula import IDPool
from pysat.card import CardEnc, EncType

pool = IDPool()
Tv = [[pool.id(f"T{i}_{j}") if i != j else None for j in range(14)] for i in range(14)]
Qv = [[pool.id(f"Q{r}_{j}") for j in range(14)] for r in range(4)]
clauses = []

def AND(a, b):
    v = pool.id(f"and_{a}_{b}")
    clauses.extend([[-v, a], [-v, b], [v, -a, -b]])
    return v

def alias(a):
    v = pool.id(f"al_{a}_{len(clauses)}")
    clauses.extend([[-v, a], [v, -a]])
    return v

def exactly(lits, k):
    cnf = CardEnc.equals(lits=lits, bound=k, vpool=pool, encoding=EncType.seqcounter)
    clauses.extend(cnf.clauses)

# row sums
for i in range(14):
    exactly([Tv[i][j] for j in range(14) if j != i], 5)
for r in range(4):
    exactly(Qv[r], 7)
# diagonal: indeg + colsumQ = 7
for j in range(14):
    lits = [Tv[i][j] for i in range(14) if i != j] + [Qv[r][j] for r in range(4)]
    exactly(lits, 7)
# off-diagonal pair equations
for i in range(14):
    for j in range(i + 1, 14):
        lits = []
        for k in range(14):
            if k != i and k != j:
                lits.append(AND(Tv[k][i], Tv[k][j]))
        # weight-2 terms via aliases
        for v in (Tv[i][j], Tv[j][i]):
            lits.append(v)
            lits.append(alias(v))
        for r in range(4):
            lits.append(AND(Qv[r][i], Qv[r][j]))
        exactly(lits, 4)

# symmetry: Q row 0 = {0..6}
for j in range(14):
    clauses.append([Qv[0][j]] if j < 7 else [-Qv[0][j]])

t = int(sys.argv[1]) if len(sys.argv) > 1 else -1
if t >= 0:
    row1 = set(range(t)) | set(range(7, 14 - t))
    for j in range(14):
        clauses.append([Qv[1][j]] if j in row1 else [-Qv[1][j]])

print(f"p cnf {pool.top} {len(clauses)}")
for c in clauses:
    print(" ".join(map(str, c)) + " 0")

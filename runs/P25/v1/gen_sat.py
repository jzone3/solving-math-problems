#!/usr/bin/env python3
"""Generate CNF for: exists ternary covering code of length 6, radius 1, size <= K.
Vars 1..729 = indicator of word w (index w+1). Cardinality sum <= K via pysat totalizer.
Symmetry breaking: WLOG 000000 (word 0) is a codeword (per-coordinate symbol permutations
act transitively on words and preserve covering codes)."""
import sys
from pysat.formula import CNF
from pysat.card import CardEnc, EncType

K = int(sys.argv[1])
out = sys.argv[2]

N = 729
def ball(w):
    d = []
    t = w
    for _ in range(6):
        d.append(t % 3); t //= 3
    res = [w]
    p3 = 1
    for i in range(6):
        for v in (1, 2):
            res.append(w + (((d[i] + v) % 3) - d[i]) * p3)
        p3 *= 3
    return res

cnf = CNF()
for w in range(N):
    cnf.append([b + 1 for b in ball(w)])
cnf.append([1])  # WLOG word 000000 in code
card = CardEnc.atmost(lits=list(range(1, N + 1)), bound=K, top_id=N, encoding=EncType.totalizer)
cnf.extend(card.clauses)
cnf.to_file(out)
print("vars", card.nv, "clauses", len(cnf.clauses))

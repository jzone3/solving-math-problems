#!/usr/bin/env python3
"""Generate CNF deciding: exists <g>-invariant covering code of size <= TARGET,
for a sweep class given as 'lam' and 'assign'. Orbit vars + PB constraint (weights =
orbit sizes) via pysat pblib. Usage: orbit_sat.py TARGET "lam" "assign" OUT.cnf"""
import ast
import sys
from pysat.formula import CNF
from pysat.card import CardEnc, EncType

TARGET = int(sys.argv[1])
lam = ast.literal_eval(sys.argv[2])
assign = ast.literal_eval(sys.argv[3])
if isinstance(assign, str):
    assign = (assign,)
out = sys.argv[4]

N = 729
def digits(w):
    return [(w // 3**i) % 3 for i in range(6)]
def undig(d):
    return sum(v * 3**i for i, v in enumerate(d))
BALL = []
for w in range(N):
    d = digits(w)
    b = [w]
    for i in range(6):
        for v in (1, 2):
            e = d[:]; e[i] = (e[i] + v) % 3
            b.append(undig(e))
    BALL.append(b)
S3 = {"id": (0, 1, 2), "tau": (1, 0, 2), "sigma": (1, 2, 0)}
perm = [0] * 6
smap = [S3["id"]] * 6
pos = 0
for (L, s) in zip(lam, assign):
    idxs = list(range(pos, pos + L))
    for k, i in enumerate(idxs):
        perm[i] = idxs[(k + 1) % L]
    smap[idxs[-1]] = S3[s]
    pos += L

def apply_g(w):
    d = digits(w)
    e = [0] * 6
    for i in range(6):
        e[perm[i]] = smap[i][d[i]]
    return undig(e)

seen = [False] * N
orbits = []
orb_id = [0] * N
for w in range(N):
    if seen[w]:
        continue
    o = []
    x = w
    while not seen[x]:
        seen[x] = True
        o.append(x)
        orb_id[x] = len(orbits)
        x = apply_g(x)
    orbits.append(o)
M = len(orbits)
cnf = CNF()
for w in range(N):
    cnf.append(sorted(set(orb_id[b] + 1 for b in BALL[w])))
# weighted cardinality: orbit of size s contributes s copies of its literal
lits = []
for j, o in enumerate(orbits):
    lits.extend([j + 1] * len(o))
card = CardEnc.atmost(lits=lits, bound=TARGET, top_id=M, encoding=EncType.totalizer)
cnf.extend(card.clauses)
cnf.to_file(out)
print("orbits", M, "vars", card.nv, "clauses", len(cnf.clauses))

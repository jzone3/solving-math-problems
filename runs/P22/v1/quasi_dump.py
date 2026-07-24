"""Dump the n=9 quasi-Folkman synthesis instance (masks + 4-set faces + lex-leader
symmetry breaking, same construction as quasi_exact.py) to DIMACS for kissat."""
import sys, random
from itertools import combinations

n = int(sys.argv[1]); maskfile = sys.argv[2]; outfile = sys.argv[3]
VERTS = list(range(n))
TRIPLES = list(combinations(VERTS, 3))
NT = len(TRIPLES)
T_ID0 = {t: i + 1 for i, t in enumerate(TRIPLES)}
rng = random.Random(7)
PERMS = [tuple(range(n))] + [tuple(rng.sample(VERTS, n)) for _ in range(299)]

clauses = []
nv = NT
def newvar():
    global nv
    nv += 1
    return nv

for p in PERMS[1:120]:
    prev = None
    for t in TRIPLES:
        ft = tuple(sorted((p[t[0]], p[t[1]], p[t[2]])))
        if ft == t:
            continue
        a, b = T_ID0[t], T_ID0[ft]
        if prev is None:
            clauses.append([-a, b])
        else:
            clauses.append([-prev, -a, b])
        nxt = newvar()
        if prev is None:
            clauses += [[-nxt, -a, b], [-nxt, a, -b], [nxt, -a, -b], [nxt, a, b]]
        else:
            clauses += [[-nxt, prev], [-nxt, -a, b], [-nxt, a, -b],
                        [nxt, -prev, -a, -b], [nxt, -prev, a, b]]
        prev = nxt

for q in combinations(VERTS, 4):
    clauses.append([-T_ID0[f] for f in combinations(q, 3)])

with open(outfile, "w") as f:
    f.write(f"p cnf PLACEHOLDER\n")
    nc = 0
    for c in clauses:
        f.write(" ".join(map(str, c)) + " 0\n")
        nc += 1
    for line in open(maskfile):
        h, l = line.strip().split(":")
        m = (int(h, 16) << 64) | int(l, 16)
        f.write(" ".join(str(i + 1) for i in range(NT) if (m >> i) & 1) + " 0\n")
        nc += 1
# fix header
import subprocess
subprocess.run(["sed", "-i", f"1s/.*/p cnf {nv} {nc}/", outfile], check=True)
print("vars", nv, "clauses", nc)

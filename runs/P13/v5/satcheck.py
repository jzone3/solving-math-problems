"""Independent second verification of small (v,k,1)-PMD existence via SAT
(CaDiCaL), with a deliberately different encoding from fullsearch.py's exact
cover: direct cell variables x[b][p][val] plus pair-occurrence auxiliaries.

Usage: python3 satcheck.py v k [fix|nofix]
"""
import sys, time
from pysat.solvers import Cadical153
from pysat.formula import IDPool

V, K = int(sys.argv[1]), int(sys.argv[2])
FIX = (sys.argv[3] if len(sys.argv) > 3 else "fix") == "fix"
B = V * (V - 1) // K
pool = IDPool()
X = lambda b, p, v: pool.id(("x", b, p, v))
A = lambda b, p, t, x, y: pool.id(("a", b, p, t, x, y))

cls = []
# each cell exactly one value
for b in range(B):
    for p in range(K):
        cls.append([X(b, p, v) for v in range(V)])
        for v1 in range(V):
            for v2 in range(v1 + 1, V):
                cls.append([-X(b, p, v1), -X(b, p, v2)])
    # block values distinct
    for v in range(V):
        for p1 in range(K):
            for p2 in range(p1 + 1, K):
                cls.append([-X(b, p1, v), -X(b, p2, v)])
# pair occurrence aux: a <-> x[b,p,x] & x[b,p+t,y]
occ = {}
for t in range(1, K):
    for x in range(V):
        for y in range(V):
            if x != y:
                occ[(t, x, y)] = []
for b in range(B):
    for p in range(K):
        for t in range(1, K):
            q = (p + t) % K
            for x in range(V):
                for y in range(V):
                    if x == y:
                        continue
                    a = A(b, p, t, x, y)
                    cls.append([-a, X(b, p, x)])
                    cls.append([-a, X(b, q, y)])
                    cls.append([a, -X(b, p, x), -X(b, q, y)])
                    occ[(t, x, y)].append(a)
# each (t,x,y) exactly once
for key, lst in occ.items():
    cls.append(lst)
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            cls.append([-lst[i], -lst[j]])
# symmetry: fix block 0 = (0,1,...,K-1)
if FIX:
    for p in range(K):
        cls.append([X(0, p, p)])

print(f"(v,k)=({V},{K}) blocks={B} vars={pool.top} clauses={len(cls)}", flush=True)
t0 = time.time()
s = Cadical153(bootstrap_with=cls)
res = s.solve()
print(f"SAT={res} time={time.time()-t0:.0f}s", flush=True)
if res:
    model = set(l for l in s.get_model() if l > 0)
    blocks = []
    for b in range(B):
        blk = []
        for p in range(K):
            for v in range(V):
                if X(b, p, v) in model:
                    blk.append(v)
                    break
        blocks.append(tuple(blk))
    print(blocks)
    from pmdlib import check_pmd
    print(check_pmd(blocks, V, K, 1))
else:
    print(f"UNSAT: no ({V},{K},1)-PMD (independent SAT verification)", flush=True)

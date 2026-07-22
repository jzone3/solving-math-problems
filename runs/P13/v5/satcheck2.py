"""Third (9,6) check: SAT over candidate-block variables (exact cover CNF,
sequential at-most-one), decided by CaDiCaL's CDCL — different search
paradigm from the DFS in fullsearch.py/xcover.c and different encoding from
satcheck.py. Usage: python3 satcheck2.py v k [fix|nofix]
"""
import sys, time, itertools
from pysat.solvers import Cadical153
from pysat.formula import IDPool

V, K = int(sys.argv[1]), int(sys.argv[2])
FIX = (sys.argv[3] if len(sys.argv) > 3 else "fix") == "fix"
items = {}
for t in range(1, K):
    for x in range(V):
        for y in range(V):
            if x != y:
                items[(t, x, y)] = len(items)
N = len(items)


def cover_list(block):
    out = []
    for t in range(1, K):
        for i in range(K):
            out.append(items[(t, block[i], block[(i + t) % K])])
    return out


cands = []
for sub in itertools.combinations(range(V), K):
    for perm in itertools.permutations(sub[1:]):
        cands.append((sub[0],) + perm)

pool = IDPool()
Xv = lambda ci: pool.id(("c", ci))
by_item = [[] for _ in range(N)]
for ci, b in enumerate(cands):
    for it in cover_list(b):
        by_item[it].append(ci)

cls = []
for it in range(N):
    lst = [Xv(ci) for ci in by_item[it]]
    cls.append(lst)  # at least one
    # sequential AMO
    s_prev = None
    for idx, lit in enumerate(lst):
        s = pool.id(("s", it, idx))
        cls.append([-lit, s])
        if s_prev is not None:
            cls.append([-s_prev, s])
            cls.append([-lit, -s_prev])
        s_prev = s
if FIX:
    fixed_ci = cands.index(tuple(range(K)))
    cls.append([Xv(fixed_ci)])

print(f"(v,k)=({V},{K}) cands={len(cands)} vars={pool.top} clauses={len(cls)}", flush=True)
t0 = time.time()
s = Cadical153(bootstrap_with=cls)
res = s.solve()
print(f"SAT={res} time={time.time()-t0:.0f}s", flush=True)
if res:
    model = set(l for l in s.get_model() if l > 0)
    blocks = [cands[ci] for ci in range(len(cands)) if Xv(ci) in model]
    print(blocks)
    from pmdlib import check_pmd
    print(check_pmd(blocks, V, K, 1))
else:
    print(f"UNSAT: no ({V},{K},1)-PMD", flush=True)

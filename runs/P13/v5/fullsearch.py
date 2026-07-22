"""Generalized full exhaustive (v,k,1)-PMD search by exact cover (no
prescribed symmetry). Usage: python3 fullsearch.py v k [fix|nofix]

items = (t,x,y), t=1..k-1, ordered pairs; candidates = cyclic k-tuples
(rotation reps: minimal element first); WLOG (relabeling) the design contains
block (0,1,...,k-1) when 'fix' (default).
"""
import sys, time, itertools
from collections import defaultdict

V, K = int(sys.argv[1]), int(sys.argv[2])
FIX = (sys.argv[3] if len(sys.argv) > 3 else "fix") == "fix"
assert V * (V - 1) % K == 0
pts = list(range(V))
items = {}
for t in range(1, K):
    for x in pts:
        for y in pts:
            if x != y:
                items[(t, x, y)] = len(items)
N = len(items)


def mask_of(block):
    m = 0
    for t in range(1, K):
        for i in range(K):
            m |= 1 << items[(t, block[i], block[(i + t) % K])]
    return m


cands = []
for sub in itertools.combinations(pts, K):
    first, rest = sub[0], sub[1:]
    for perm in itertools.permutations(rest):
        block = (first,) + perm
        cands.append((block, mask_of(block)))
print(f"(v,k)=({V},{K}) items={N} candidates={len(cands)} fix={FIX}", flush=True)

by_item = defaultdict(list)
for ci, (b, m) in enumerate(cands):
    for n in range(N):
        if (m >> n) & 1:
            by_item[n].append(ci)

target = (1 << N) - 1
fixed_block = tuple(range(K))
fixed = mask_of(fixed_block) if FIX else 0
nodes, t0, sols = 0, time.time(), []


def dfs(cov, chosen):
    global nodes
    nodes += 1
    if nodes % 2000000 == 0:
        print(f"nodes={nodes/1e6:.0f}M depth={len(chosen)} t={time.time()-t0:.0f}s", flush=True)
    if cov == target:
        sols.append(list(chosen))
        return True
    rem = target & ~cov
    best = None
    x = rem
    while x:
        bb = x & -x
        i = bb.bit_length() - 1
        lst = [ci for ci in by_item[i] if not (cands[ci][1] & cov)]
        if best is None or len(lst) < len(best):
            best = lst
            if not lst:
                return False
        x ^= bb
    for ci in best:
        chosen.append(ci)
        if dfs(cov | cands[ci][1], chosen):
            return True
        chosen.pop()
    return False


dfs(fixed, [])
print(f"DONE nodes={nodes} time={time.time()-t0:.0f}s solutions={len(sols)}", flush=True)
if sols:
    from pmdlib import check_pmd
    blocks = ([fixed_block] if FIX else []) + [cands[ci][0] for ci in sols[0]]
    print(blocks)
    print(check_pmd(blocks, V, K, 1))
else:
    print(f"NO ({V},{K},1)-PMD exists (exhaustive)", flush=True)

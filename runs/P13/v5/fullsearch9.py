"""Full (no prescribed symmetry) exhaustive search for a (9,6,1)-PMD as exact
cover: items = (t,x,y) for t=1..5 and ordered pairs of distinct points (360
items); candidates = cyclic 6-tuples of distinct points (rotation class reps,
10080 of them), each covering 30 items. A (9,6)-PMD = exact cover by 12
candidates. WLOG (point relabeling) the design contains block (0,1,2,3,4,5).

DFS pivots on the uncovered item with fewest live candidates. Prints node
counts; exhaustive if it terminates.
"""
import sys, time, itertools
from collections import defaultdict

V, K = 9, 6
pts = list(range(V))
items = {}
for t in range(1, K):
    for x in pts:
        for y in pts:
            if x != y:
                items[(t, x, y)] = len(items)
N = len(items)  # 360


def mask_of(block):
    m = 0
    for t in range(1, K):
        for i in range(K):
            m |= 1 << items[(t, block[i], block[(i + t) % K])]
    return m


cands = []
for sub in itertools.combinations(pts, K):
    first = sub[0]
    rest = sub[1:]
    for perm in itertools.permutations(rest):
        block = (first,) + perm
        cands.append((block, mask_of(block)))
print(f"candidates: {len(cands)}", flush=True)

by_item = defaultdict(list)
for ci, (b, m) in enumerate(cands):
    for n in range(N):
        if (m >> n) & 1:
            by_item[n].append(ci)

target = (1 << N) - 1
fixed = mask_of((0, 1, 2, 3, 4, 5))
nodes = 0
t0 = time.time()
best_depth = 0
sols = []


def dfs(cov, chosen):
    global nodes, best_depth
    nodes += 1
    if nodes % 2000000 == 0:
        print(f"nodes={nodes/1e6:.0f}M depth={len(chosen)} best={best_depth} "
              f"t={time.time()-t0:.0f}s", flush=True)
    if len(chosen) > best_depth:
        best_depth = len(chosen)
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


found = dfs(fixed, [])
print(f"DONE nodes={nodes} time={time.time()-t0:.0f}s solutions={len(sols)}", flush=True)
if sols:
    print(sols[0])
    from pmdlib import check_pmd
    blocks = [(0, 1, 2, 3, 4, 5)] + [cands[ci][0] for ci in sols[0]]
    print(check_pmd(blocks, 9, 6, 1))
else:
    print("NO (9,6,1)-PMD exists (exhaustive, given WLOG block fix)", flush=True)

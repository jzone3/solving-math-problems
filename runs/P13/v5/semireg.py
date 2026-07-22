"""Extended difference-method search: group H = Z_m acting semiregularly on
c point-orbits (classes) of size m, plus at most one fixed point 'inf'.
v = c*m (+1). Only FULL orbits of base blocks are considered here, so we
require b = v(v-1)/k divisible by m. (Short-orbit variants are noted in
NOTES.md as not covered by this script.)

Items (exact cover universe), for each t in 1..k-1:
  (t, i, j, d): ordered class pair (i,j), d in Z_m (d != 0 when i == j)
  (t, i, 'toinf') and (t, 'frominf', i): pairs (x, inf) / (inf, y), x,y in class i
A full orbit of a base block covers item (t,i,j,d) once for each position pair
(p, p+t) with classes (i,j) and element difference d; validity (lambda=1 inside
the orbit) forces all labels distinct within the block.

Exhaustive within ansatz: DFS exact cover on bitmasks, pivoting on the item
with fewest live candidates; final block resolved by dictionary lookup.
"""
import sys, time, itertools
from collections import defaultdict


class SemiregEngine:
    def __init__(self, m, c, use_inf, k):
        self.m, self.c, self.use_inf, self.k = m, c, use_inf, k
        self.points = [(i, h) for i in range(c) for h in range(m)] + (['inf'] if use_inf else [])
        items = []
        for t in range(1, k):
            for i in range(c):
                for j in range(c):
                    for d in range(m):
                        if i == j and d == 0:
                            continue
                        items.append((t, i, j, d))
            if use_inf:
                for i in range(c):
                    items.append((t, i, 'toinf'))
                    items.append((t, 'frominf', i))
        self.items = items
        self.idx = {it: n for n, it in enumerate(items)}
        self.n_items = len(items)

    def block_mask(self, block):
        k, m = self.k, self.m
        mask = 0
        for t in range(1, k):
            for p in range(k):
                x, y = block[p], block[(p + t) % k]
                if x == 'inf' and y == 'inf':
                    return None
                if x == 'inf':
                    it = (t, 'frominf', y[0])
                elif y == 'inf':
                    it = (t, x[0], 'toinf')
                else:
                    d = (y[1] - x[1]) % m
                    if x[0] == y[0] and d == 0:
                        return None
                    it = (t, x[0], y[0], d)
                bit = 1 << self.idx[it]
                if mask & bit:
                    return None
                mask |= bit
        return mask

    def gen_candidates(self, max_report=True):
        """All base blocks up to rotation and translation, dedup by mask."""
        k = self.k
        seen = {}
        pts = self.points
        cnt = 0
        for tup in itertools.permutations(pts, k):
            # normalization: skip tuples that are not rotation-minimal after
            # translating first finite entry's element to 0
            # (cheap partial normalization: require first entry to be a finite
            #  point with element 0, or 'inf' first)
            first = tup[0]
            if first == 'inf':
                pass
            elif first[1] != 0:
                continue
            m_ = self.block_mask(tup)
            cnt += 1
            if m_ is not None and m_ not in seen:
                seen[m_] = tup
        return [(b, mk) for mk, b in seen.items()]

    def solve(self, cands):
        target = (1 << self.n_items) - 1
        by_item = defaultdict(list)
        Adict = defaultdict(list)
        for ci, (b, mk) in enumerate(cands):
            Adict[mk].append(ci)
            for n in range(self.n_items):
                if (mk >> n) & 1:
                    by_item[n].append(ci)
        sols = []

        def dfs(cov, chosen, live):
            if cov == target:
                sols.append(list(chosen))
                return True
            rem = target & ~cov
            # try dict lookup if remaining could be one block
            if rem in Adict:
                sols.append(list(chosen) + [Adict[rem][0]])
                return True
            # pivot: uncovered item with fewest live candidates
            best_i, best = None, None
            x = rem
            while x:
                bbit = x & -x
                i = bbit.bit_length() - 1
                lst = [ci for ci in by_item[i] if not (cands[ci][1] & cov)]
                if best is None or len(lst) < len(best):
                    best, best_i = lst, i
                    if not lst:
                        return False
                x ^= bbit
            for ci in best:
                chosen.append(ci)
                if dfs(cov | cands[ci][1], chosen, None):
                    return True
                chosen.pop()
            return False

        dfs(0, [], None)
        return sols

    def expand(self, block):
        m = self.m
        return [tuple('inf' if x == 'inf' else (x[0], (x[1] + g) % m) for x in block)
                for g in range(m)]


def run(name, m, c, use_inf, k):
    from pmdlib import check_pmd
    v = m * c + (1 if use_inf else 0)
    b = v * (v - 1) // k
    assert v * (v - 1) % k == 0 and b % m == 0, "full-orbit ansatz needs m | b"
    eng = SemiregEngine(m, c, use_inf, k)
    t0 = time.time()
    cands = eng.gen_candidates()
    print(f"[{name}] v={v} k={k} H=Z{m} classes={c} inf={use_inf} "
          f"candidates={len(cands)} gen {time.time()-t0:.0f}s", flush=True)
    t1 = time.time()
    sols = eng.solve(cands)
    print(f"[{name}] solve {time.time()-t1:.0f}s solutions={len(sols)}", flush=True)
    if sols:
        blocks = []
        for ci in sols[0]:
            blocks += eng.expand(cands[ci][0])
        ok, msg = check_pmd(blocks, v, k, 1)
        print(f"[{name}] base blocks: {[cands[ci][0] for ci in sols[0]]}")
        print(f"[{name}] verify: {msg}", flush=True)
    else:
        print(f"[{name}] EXHAUSTIVE NEGATIVE within ansatz", flush=True)
    return sols


CASES = {
    "9_6_Z4c2inf":  (4, 2, True, 6),
    "9_6_Z3c3":     (3, 3, False, 6),
    "15_6_Z7c2inf": (7, 2, True, 6),
    "15_6_Z5c3":    (5, 3, False, 6),
    "16_6_Z8c2":    (8, 2, False, 6),
    "16_6_Z5c3inf": (5, 3, True, 6),
    # controls (known-existing):
    "7_6_Z7c1":     (7, 1, False, 6),
    "13_6_Z13c1":   (13, 1, False, 6),
}

if __name__ == "__main__":
    name = sys.argv[1]
    m, c, ui, k = CASES[name]
    run(name, m, c, ui, k)

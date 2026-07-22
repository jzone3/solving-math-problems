"""Exhaustive difference-method search engine for (v,k,1)-PMDs, variant V5.

Ansatz: point set = G (abelian group, order m) optionally + one infinity point
(v = m or m+1). The design is a union of G-orbits of base blocks under
translation. Orbits may be short: a base block B has stabilizer <s> of order d
iff there is a rotation r of the cyclic block with ord(r mod k) = ord(s in G) = d
and B[i + r] = B[i] + s for all i.

Existence of the PMD is equivalent to an exact cover: for each t in 1..k-1 the
multiset of t-apart differences contributed by the chosen base blocks (counted
once per base block, with short orbits counted once per "strand") covers each
nonzero g in G exactly once; and if an infinity point is used, exactly one full
orbit contains it.

We solve the exact cover by DFS, always branching on the uncovered item with
the fewest remaining candidates. This is exhaustive within the ansatz.
"""
import itertools, sys
from functools import reduce


def cyclic_group(m):
    els = list(range(m))
    add = lambda a, b: (a + b) % m
    neg = lambda a: (-a) % m
    return els, add, neg


def product_group(ms):
    els = [tuple(p) for p in itertools.product(*[range(m) for m in ms])]
    add = lambda a, b: tuple((x + y) % m for x, y, m in zip(a, b, ms))
    neg = lambda a: tuple((-x) % m for x, a_, m in [(x, None, m) for x, m in zip(a, ms)])
    neg = lambda a: tuple((-x) % m for x, m in zip(a, ms))
    return els, add, neg


class Engine:
    def __init__(self, els, add, neg, k, use_inf):
        self.els, self.add, self.neg, self.k, self.use_inf = els, add, neg, k, use_inf
        self.zero = els[0] if not isinstance(els[0], tuple) else tuple([0] * len(els[0]))
        assert self.zero in els
        self.nonzero = [g for g in els if g != self.zero]
        self.idx = {g: i for i, g in enumerate(self.nonzero)}
        self.n_items = (k - 1) * len(self.nonzero) + (1 if use_inf else 0)
        self.INF_ITEM = self.n_items - 1 if use_inf else None

    def sub(self, a, b):
        return self.add(a, self.neg(b))

    def block_mask(self, block):
        """Bitmask of covered items for one base block (full or short-strand rep).
        block entries: group elements or 'inf'. Returns None if internally invalid
        (a difference repeated for some t). For short-orbit blocks the mask below
        already double counts; use strand_mask instead."""
        k = self.k
        mask = 0
        for t in range(1, k):
            for i in range(k):
                x, y = block[i], block[(i + t) % k]
                if x == 'inf' or y == 'inf':
                    continue
                d = self.sub(y, x)
                if d == self.zero:
                    return None
                bit = 1 << ((t - 1) * len(self.nonzero) + self.idx[d])
                if mask & bit:
                    return None
                mask |= bit
        if self.use_inf and 'inf' in block:
            mask |= 1 << self.INF_ITEM
        return mask

    def full_orbit_candidates(self, with_inf):
        """All base blocks (up to per-block translation and rotation) with trivial
        stabilizer requirement not enforced (a block that happens to be short-
        stabilized would generate repeats when fully developed; such blocks have
        repeated differences? no -- short blocks have repeated diffs per t, so
        block_mask returns None for them. Good: full-orbit candidates are exactly
        those with all-distinct per-t differences)."""
        k = self.k
        out = []
        seen = set()
        if with_inf:
            # block = (0, x1..x_{k-2}, inf), first entry normalized to 0 by translation,
            # inf rotated to last position
            for perm in itertools.permutations(self.nonzero, k - 2):
                block = (self.zero,) + perm + ('inf',)
                m = self.block_mask(block)
                if m is not None and m not in seen:
                    seen.add(m)
                    out.append((block, m, 'full'))
        else:
            for perm in itertools.permutations(self.nonzero, k - 1):
                block = (self.zero,) + perm
                m = self.block_mask(block)
                if m is not None and m not in seen:
                    seen.add(m)
                    out.append((block, m, 'full'))
        return out

    def short_orbit_candidates(self):
        """Blocks with stabilizer <s> of order d>1: B[i+r] = B[i]+s, ord(r in Z_k)
        = ord(s) = d. Developed over coset reps (orbit size m/d). Mask counts each
        distinct (t,d) once -- for a short block each per-t difference appears d
        times in the block but only m/d translates, net coverage 1 per listed diff.
        So require: per t, the k differences consist of k/d distinct values each
        repeated d times, and mask = those k/d values. Returns candidate list."""
        k = self.k
        out = []
        seen = set()
        m_ord = len(self.els)
        # orders of rotations r in Z_k
        def ordmod(a, n):
            x, c = a % n, 1
            while x != 0:
                x = (x + a) % n
                c += 1
                if c > n:
                    return None
            return c
        for s in self.nonzero:
            # order of s
            d = 1
            acc = s
            while acc != self.zero:
                acc = self.add(acc, s)
                d += 1
            if d == 1 or k % d != 0:
                continue
            for r in range(1, k):
                # need ord(r mod k) == d
                if ordmod(r, k) != d:
                    continue
                # block determined by entries on strand representatives:
                # positions form <r> cosets in Z_k; there are k/d strands.
                # choose values for one rep per strand; rest forced.
                strands = []
                used_pos = set()
                for p in range(k):
                    if p in used_pos:
                        continue
                    strand = []
                    q, val_mult = p, 0
                    while q not in used_pos:
                        used_pos.add(q)
                        strand.append((q, val_mult))
                        q = (q + r) % k
                        val_mult += 1
                    strands.append(strand)
                nst = len(strands)
                # first strand starts at position 0 with value normalized to 0 (translate)
                for choice in itertools.product(self.els, repeat=nst - 1):
                    vals = (self.zero,) + choice
                    block = [None] * k
                    ok = True
                    for st, v0 in zip(strands, vals):
                        for (pos, mult) in st:
                            x = v0
                            for _ in range(mult):
                                x = self.add(x, s)
                            block[pos] = x
                    if len(set(block)) != k:
                        continue
                    # compute per-t coverage: each t gives k diffs = (k/d) distinct x d
                    mask = 0
                    ok = True
                    for t in range(1, k):
                        from collections import Counter
                        c = Counter(self.sub(block[(i + t) % k], block[i]) for i in range(k))
                        if self.zero in c:
                            ok = False
                            break
                        for dv, cnt in c.items():
                            if cnt != d:
                                ok = False
                                break
                            mask |= 1 << ((t - 1) * len(self.nonzero) + self.idx[dv])
                        if not ok:
                            break
                    if not ok:
                        continue
                    if mask not in seen:
                        seen.add(mask)
                        out.append((tuple(block), mask, ('short', s, r, d)))
        return out

    def solve(self, candidates, target_mask=None, find_all=False, progress=False):
        """Exact cover DFS. Returns list of solutions (each = list of candidates)."""
        if target_mask is None:
            target_mask = (1 << self.n_items) - 1
        # item -> candidate indices
        n = self.n_items
        by_item = [[] for _ in range(n)]
        for ci, (b, m, kind) in enumerate(candidates):
            if m & ~target_mask:
                continue
            for it in range(n):
                if (m >> it) & 1:
                    by_item[it].append(ci)
        sols = []
        cand = candidates
        def dfs(cov, chosen):
            if cov == target_mask:
                sols.append(list(chosen))
                return not find_all
            # pick uncovered item with fewest live candidates
            best_it, best_list = None, None
            rem = target_mask & ~cov
            it = (rem & -rem).bit_length() - 1
            # scan all uncovered items for min branching
            best_len = None
            x = rem
            while x:
                b_ = x & -x
                i = b_.bit_length() - 1
                lst = [c for c in by_item[i] if not (cand[c][1] & cov)]
                if best_len is None or len(lst) < best_len:
                    best_len, best_it, best_list = len(lst), i, lst
                    if best_len == 0:
                        return False
                x ^= b_
            for c in best_list:
                chosen.append(c)
                if dfs(cov | cand[c][1], chosen):
                    return True
                chosen.pop()
            return False
        dfs(0, [])
        return sols

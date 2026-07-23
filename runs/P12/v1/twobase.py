#!/usr/bin/env python3
"""Two-base (index-2 subgroup) construction of circular (n-1) x n Tuscan-2
arrays for prime n, generalizing the multiplicative construction.

Rows: {u*b1 : u in QR} ∪ {u*b2 : u in QNR}, where QR/QNR are the quadratic
residues / non-residues mod n and b1, b2 are circular arrangements of Z_n
with b[0] = 0.

Correctness conditions (pair (x, ρx), x,y nonzero, at distance d ∈ {1,2}):
a distance-d position c of base j with both entries nonzero and ratio
ρ = b[c+d]/b[c] covers x ranging over the coset H_j * b[c]
(H_1 = QR, H_2 = QNR).  Exact coverage iff for every ρ != 1 the tokens
(coset types) contributed by b1 and b2 for ratio ρ are exactly {QR, QNR}.
Pairs involving 0 (predecessor/successor of the zero position at distance
d): need q(b1[±d]) == q(b2[±d]) where q = 1 iff quadratic residue and
indices relative to the zero position (b[0]=0).

Each resulting array is fed to the exact cut-conversion search (as in
mult_circ.py) — a success is an n x n Tuscan-2 square (open problem for
n = 11, 13).

Usage: python3 twobase.py n [--count-only]
"""
import sys
from collections import defaultdict
from mult_circ import try_cuts


def qr_set(n):
    return {pow(x, 2, n) for x in range(1, n)}


def enum_bases(n):
    """All circular arrangements b (b[0]=0) such that within the base no
    (ratio, coset) token repeats at distance 1 or distance 2.  Returns list
    of (b, sig1, sig2, zpar) where sig_d maps ratio -> frozenset/multiset of
    coset types (as sorted tuple), zpar = (q(b[-1]), q(b[1]), q(b[-2]), q(b[2]))."""
    QR = qr_set(n)
    inv = [0] * n
    for x in range(1, n):
        inv[x] = pow(x, n - 2, n)
    q = [0] * n
    for x in range(1, n):
        q[x] = 1 if x in QR else 0
    res = []
    b = [0] * n

    def tokens(seq, d):
        toks = []
        for c in range(n):
            x, y = seq[c], seq[(c + d) % n]
            if x and y:
                toks.append((y * inv[x] % n, q[x]))
        return toks

    def rec(pos, used):
        if pos == n:
            t1 = tokens(b, 1)
            t2 = tokens(b, 2)
            if len(set(t1)) != len(t1) or len(set(t2)) != len(t2):
                return
            sig1 = defaultdict(list)
            sig2 = defaultdict(list)
            for r, cs in t1:
                sig1[r].append(cs)
            for r, cs in t2:
                sig2[r].append(cs)
            zpar = (q[b[n - 1]], q[b[1]], q[b[n - 2]], q[b[2]])
            res.append((b[:],
                        frozenset((r, tuple(sorted(v))) for r, v in sig1.items()),
                        frozenset((r, tuple(sorted(v))) for r, v in sig2.items()),
                        zpar))
            return
        for v in range(1, n):
            if used >> v & 1:
                continue
            # incremental prune: distance-1 token with previous
            if pos >= 2:
                prev = b[pos - 1]
                # ratio token (v/prev, q[prev]) must not duplicate existing d1 token
                # (cheap check: scan current partial tokens)
                r_ = v * inv[prev] % n
                if r_ == 1:
                    continue
                dup = False
                for c in range(1, pos - 1):
                    x, y = b[c], b[c + 1]
                    if x and y and y * inv[x] % n == r_ and q[x] == q[prev]:
                        dup = True
                        break
                if dup:
                    continue
            if pos >= 3:
                pp = b[pos - 2]
                if pp:
                    r2_ = v * inv[pp] % n
                    if r2_ == 1:
                        continue
                    dup = False
                    for c in range(1, pos - 2):
                        x, y = b[c], b[c + 2]
                        if x and y and y * inv[x] % n == r2_ and q[x] == q[pp]:
                            dup = True
                            break
                    if dup:
                        continue
            b[pos] = v
            rec(pos + 1, used | 1 << v)

    rec(1, 1)
    return res


def check_array(n, rows):
    """independent check: circular (n-1) x n Tuscan-2 array — every ordered
    pair exactly once at circular distance 1 and exactly once at distance 2."""
    for d in (1, 2):
        seen = set()
        for r in rows:
            for c in range(n):
                p = (r[c], r[(c + d) % n])
                if p in seen:
                    return False
                seen.add(p)
        if len(seen) != n * (n - 1):
            return False
    return True


def main():
    n = int(sys.argv[1])
    count_only = "--count-only" in sys.argv
    QR = qr_set(n)
    bases = enum_bases(n)
    print(f"n={n}: {len(bases)} single-base candidates", file=sys.stderr)

    # index bases by (sig1, sig2, zpar) for complement lookup
    idx = defaultdict(list)
    for b, s1, s2, zp in bases:
        idx[(s1, s2, zp)].append(b)

    def comp(sig):
        """b1 token (rho, q) covers coset TYPE q; b2 token (rho, q) covers
        coset type 1-q.  Per rho both types must appear once, so b2's raw-q
        signature must contain, for each needed type t, the value 1-t."""
        d = {r: list(v) for r, v in sig}
        out = []
        for rho in range(2, n):
            have_types = d.get(rho, [])
            need_raw = []
            for t in (0, 1):
                cnt = 1 - have_types.count(t)
                if cnt < 0:
                    return None
                need_raw.extend([1 - t] * cnt)
            if need_raw:
                out.append((rho, tuple(sorted(need_raw))))
        return frozenset(out)

    tried = 0
    pairs = 0
    for (s1, s2, zp), blist in idx.items():
        c1 = comp(s1)
        c2 = comp(s2)
        if c1 is None or c2 is None:
            continue
        for b2 in idx.get((c1, c2, zp), []):
            for b1 in blist:
                pairs += 1
                if count_only:
                    continue
                rows = [[u * x % n for x in b1] for u in sorted(QR)] + \
                       [[u * x % n for x in b2] for u in sorted(set(range(1, n)) - QR)]
                if not check_array(n, rows):
                    print("BUG: invalid array from construction", b1, b2,
                          file=sys.stderr)
                    continue
                sq = try_cuts(n, rows)
                tried += 1
                if sq:
                    print(f"SQUARE from b1={b1} b2={b2}", file=sys.stderr)
                    for row in sq:
                        print(" ".join(map(str, row)))
                    return 0
                if tried % 1000 == 0:
                    print(f"tried {tried} arrays", file=sys.stderr)
    print(f"pairs (arrays) = {pairs}, conversions tried = {tried}, none succeeded",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Algebraic attack part 2: rows from permutation polynomials of F_p (p=11,13).

Pool = rows [f(0),...,f(p-1)] for f in a parametrized family of permutation
polynomials: f(x) = a*(x+c)^k + b (gcd(k,p-1)=1), plus permutation binomials
a*(x^u + d*x^v) + b when they permute F_p, plus g-ary 'geometric' rows using a
primitive root ordering of columns: j -> a*g^j + b extended with 0 handled by
column p-1 (i.e. rows [a*g^0+b, ..., a*g^(p-2)+b, b]).

Search: pick p rows from the pool forming a T2(p) via DFS over the pool with
distance-1 exact-cover pruning. Reports best depth reached (near-miss data).
"""
import sys
import time
from itertools import product

sys.path.insert(0, ".")
from t2lib import compatible_partial, check_t2


def build_pool(p):
    rows = set()
    ks = [k for k in range(1, p - 1) if __import__("math").gcd(k, p - 1) == 1]
    for a in range(1, p):
        for b in range(p):
            for c in range(p):
                for k in ks:
                    r = tuple((a * pow((x + c) % p, k, p) + b) % p for x in range(p))
                    rows.add(r)
    # permutation binomials x^u + d x^v
    for u in range(1, p - 1):
        for v in range(1, u):
            for d in range(1, p):
                vals = [(pow(x, u, p) + d * pow(x, v, p)) % p for x in range(p)]
                if len(set(vals)) == p:
                    for a in range(1, p):
                        for b in range(p):
                            rows.add(tuple((a * t + b) % p for t in vals))
    # geometric orderings: columns as powers of primitive root
    g = primitive_root(p)
    for e in range(1, p - 1):
        if __import__("math").gcd(e, p - 1) != 1:
            continue
        base = [pow(g, e * j, p) for j in range(p - 1)]
        for a in range(1, p):
            for b in range(p):
                seq = [(a * t + b) % p for t in base]
                rows.add(tuple(seq + [b]))       # 0 -> at end
                rows.add(tuple([b] + seq))       # 0 -> at front
    return sorted(rows)


def primitive_root(p):
    for g in range(2, p):
        s = set()
        x = 1
        for _ in range(p - 1):
            x = x * g % p
            s.add(x)
        if len(s) == p - 1:
            return g
    raise ValueError


def search(p, pool, time_budget=600):
    n = p
    t0 = time.time()
    best = [0, None]
    occ1 = [[False] * n for _ in range(n)]
    occ2 = [[False] * n for _ in range(n)]
    chosen = []

    def ok(r):
        for i in range(n - 1):
            if occ1[r[i]][r[i + 1]]:
                return False
        for i in range(n - 2):
            if occ2[r[i]][r[i + 2]]:
                return False
        return True

    def place(r, val):
        for i in range(n - 1):
            occ1[r[i]][r[i + 1]] = val
        for i in range(n - 2):
            occ2[r[i]][r[i + 2]] = val

    def rec(start):
        if time.time() - t0 > time_budget:
            raise TimeoutError
        if len(chosen) > best[0]:
            best[0] = len(chosen)
            best[1] = [list(r) for r in chosen]
        if len(chosen) == n:
            return True
        for idx in range(start, len(pool)):
            r = pool[idx]
            if not ok(r):
                continue
            place(r, True)
            chosen.append(r)
            if rec(idx + 1):
                return True
            chosen.pop()
            place(r, False)
        return False

    try:
        found = rec(0)
    except TimeoutError:
        found = False
    return found, best


if __name__ == "__main__":
    for p in (11, 13):
        pool = build_pool(p)
        print(f"p={p}: pool size {len(pool)}")
        found, best = search(p, pool, time_budget=float(sys.argv[1]) if len(sys.argv) > 1 else 600)
        print(f"p={p}: full T2 from pool: {found}; best depth {best[0]}/{p}")
        if best[1]:
            for r in best[1]:
                print("  ", r)
        if found:
            assert check_t2(best[1], p)
            print("VALID T2!", p)

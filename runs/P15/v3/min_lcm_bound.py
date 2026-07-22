#!/usr/bin/env python3
"""Necessary-condition calibration for min modulus m: any covering system with
distinct moduli >= m and lcm N needs sum_{d | N, d >= m} 1/d >= 1.
Search prime-exponent vectors (non-increasing over growing primes, WLOG-ish for
maximizing divisor reciprocal mass at fixed N) for the minimal N satisfying it,
and report the divisor counts => minimum witness scale."""
import heapq, sys
from sympy import primerange

PRIMES = list(primerange(2, 200))


def recip_and_count(exps, m):
    ds = [1]
    for p, e in zip(PRIMES, exps):
        ds = [d * p**k for d in ds for k in range(e + 1)]
    r = sum(1.0 / d for d in ds if d >= m)
    return r, sum(1 for d in ds if d >= m), len(ds)


def search(m, max_states=200000):
    # best-first search over exponent vectors ordered by N
    start = ()
    seen = {start}
    heap = [(1, start)]
    while heap and max_states:
        max_states -= 1
        N, exps = heapq.heappop(heap)
        r, cnt, tot = recip_and_count(exps, m)
        if r >= 1.0:
            return N, exps, r, cnt
        # successors: bump exponent i (keep non-increasing) or add next prime
        e = list(exps)
        for i in range(len(e)):
            if i == 0 or e[i] < e[i - 1]:
                ne = tuple(e[:i] + [e[i] + 1] + e[i + 1:])
                if ne not in seen:
                    seen.add(ne)
                    heapq.heappush(heap, (N * PRIMES[i], ne))
        ne = tuple(e + [1])
        if len(ne) <= len(PRIMES) and ne not in seen:
            seen.add(ne)
            heapq.heappush(heap, (N * PRIMES[len(e)], ne))
    return None


if __name__ == "__main__":
    for m in [int(x) for x in sys.argv[1:]] or [5, 6, 7, 10, 14, 18, 25, 30, 36, 40, 42, 43, 50]:
        res = search(m)
        if res:
            N, exps, r, cnt = res
            fact = "*".join(f"{p}^{e}" for p, e in zip(PRIMES, exps))
            print(f"m={m}: minimal recip-feasible N={N} = {fact}  recip={r:.4f} "
                  f"divisors>={m}: {cnt}", flush=True)
        else:
            print(f"m={m}: not found in state budget", flush=True)

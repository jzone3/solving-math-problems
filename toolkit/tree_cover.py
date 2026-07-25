#!/usr/bin/env python3
"""Bounded top-down recursive tree builder for distinct-modulus covers.

The builder starts with the open cell (0 mod 1).  A binary refinement of
(a mod M) has children

    a                 (mod 2M)
    a + M             (mod 2M).

One child is closed by its level class when 2M is an admissible unused
modulus; the other child remains open.  Below the minimum modulus, the
closed-looking child is recursively refined instead.  An odd fresh prime
tail closes the remaining binary path: its classes are CRT combinations of
the path ancestors with all residues modulo the tail prime.

This is deliberately a top-down search, rather than a residual-measure
greedy algorithm.  Every state transition is exact and every modulus is
checked globally for distinctness.  DFS limits are intentional: failure to
close is reported as a bounded-search result, not treated as a cover.
"""

import argparse
import json
import sys
from math import gcd


DEFAULT_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43)

def _primes_below(limit):
    sieve = bytearray(b"\1") * (limit + 1)
    sieve[:2] = b"\0\0"
    for p in range(2, int(limit ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = b"\0" * len(sieve[p * p::p])
    return tuple(p for p in range(19, limit + 1) if sieve[p])


DEFAULT_TAILS = _primes_below(2000)


class SearchLimit(Exception):
    pass


class DeadEnd(Exception):
    pass


def crt_coprime(a, m, b, p):
    if gcd(m, p) != 1:
        raise ValueError("CRT moduli are not coprime")
    return (a + m * ((b - a) * pow(m, -1, p) % p)) % (m * p)


class TreeBuilder:
    def __init__(self, minmod, primes=DEFAULT_PRIMES, tails=DEFAULT_TAILS,
                 max_depth=80, max_nodes=200000, max_classes=200000):
        self.minmod = minmod
        self.primes = tuple(primes)
        self.tails = tuple(tails)
        self.max_depth = max_depth
        self.max_nodes = max_nodes
        self.max_classes = max_classes
        self.used = set()
        self.blocked = set()
        self.out = []
        self.nodes = 0
        self.backtracks = 0
        self.max_open_depth = 0
        self.closure_nodes = 0

    def inherited(self, a, M):
        """Exact check whether (a mod M) lies inside a chosen class."""
        return any(M % n == 0 and (a - r) % n == 0
                   for r, n in self.out)

    def fully_covered(self, a, M, cap=20000):
        """Exact bounded union check for a currently open AP.

        Only chosen classes whose moduli divide M can contribute to this
        cell.  The recursive refinement is exact; if its finite branch count
        exceeds cap, conservatively return False rather than approximating.
        """
        compatible = [(r, n) for r, n in self.out
                      if M % n == 0 and (a - r) % gcd(n, M) == 0]
        if not compatible:
            return False
        stack = [(a % M, M)]
        seen = 0
        while stack:
            r, m = stack.pop()
            seen += 1
            self.closure_nodes += 1
            if seen > cap:
                return False
            if any(m % n == 0 and (r - q) % n == 0
                   for q, n in compatible):
                continue
            prime = None
            for q, n in compatible:
                t = n
                d = 2
                while d * d <= t:
                    if t % d:
                        d += 1
                        continue
                    vn = vm = 0
                    while t % d == 0:
                        t //= d
                        vn += 1
                    u = m
                    while u % d == 0:
                        u //= d
                        vm += 1
                    if vn > vm:
                        prime = d
                        break
                    d += 1
                if prime is None and t > 1:
                    u = m
                    vm = 0
                    while u % t == 0:
                        u //= t
                        vm += 1
                    if vm == 0:
                        prime = t
                if prime is not None:
                    break
            if prime is None:
                return False
            child_mod = m * prime
            for j in range(prime):
                stack.append((r + j * m, child_mod))
        return True

    def take(self, a, n):
        if n < self.minmod or n <= 1 or n in self.used or n in self.blocked:
            raise DeadEnd("inadmissible or duplicate modulus")
        if len(self.out) >= self.max_classes:
            raise SearchLimit("class limit")
        self.used.add(n)
        self.out.append((a % n, n))

    def rollback(self, mark):
        for _, n in self.out[mark:]:
            self.used.remove(n)
        del self.out[mark:]

    def _check_limits(self, depth):
        self.nodes += 1
        self.max_open_depth = max(self.max_open_depth, depth)
        if self.nodes > self.max_nodes:
            raise SearchLimit("node limit")
        if depth > self.max_depth:
            raise SearchLimit("depth limit")

    def _chain(self, a, M, depth, split, tail):
        """Try one finite p-ary chain with a fresh odd-prime tail."""
        if split == tail or gcd(M, tail) != 1:
            raise DeadEnd("tail shares a factor with cell modulus")

        # Tail exponents run from K down to K+1-tail.  The smallest tail
        # modulus must itself meet the minimum-modulus requirement.
        K = max(tail - 1, 1)
        while tail * M * split ** (K + 1 - tail) < self.minmod:
            K += 1

        tail_mods = [tail * M * split ** (K + 1 - j)
                     for j in range(1, tail + 1)]
        # Level classes are optional: recursively closing a sibling instead
        # can avoid a collision with another branch.  Only the tail classes
        # are reserved up front.
        planned = tail_mods
        if len(set(planned)) != len(planned):
            raise DeadEnd("chain modulus collision")
        if any(n in self.used or n in self.blocked for n in planned):
            raise DeadEnd("chain collides with chosen modulus")

        mark = len(self.out)
        reserved = set(planned)
        old_blocked = self.blocked
        self.blocked = set(old_blocked)
        self.blocked.update(reserved)
        try:
            def walk(k, path_a, path_M, ancestors):
                self._check_limits(depth + k)
                if k > K:
                    # The j-th tail class uses ancestor K+1-j,
                    # including the root ancestor at index zero.
                    for j in range(1, tail + 1):
                        anc_a, anc_M = ancestors[K + 1 - j]
                        n = tail * anc_M
                        reserved.remove(n)
                        self.blocked.remove(n)
                        self.take(crt_coprime(anc_a, anc_M, j, tail), n)
                        reserved.add(n)
                        self.blocked.add(n)
                    return
                child_mod = path_M * split
                for open_j in range(split):
                    sibling_js = [j for j in range(split) if j != open_j]
                    next_a = (path_a + open_j * path_M) % child_mod
                    submark = len(self.out)
                    try:
                        for sibling_j in sibling_js:
                            sibling_a = (path_a + sibling_j * path_M) % child_mod
                            if split == 2 and child_mod >= self.minmod:
                                # Binary splits have one non-open child, so
                                # it can use the level modulus directly.
                                try:
                                    self.take(sibling_a, child_mod)
                                    continue
                                except DeadEnd:
                                    pass
                            self._close(sibling_a, child_mod, depth + k)
                        walk(k + 1, next_a, child_mod,
                             ancestors + [(next_a, child_mod)])
                        return
                    except SearchLimit:
                        self.rollback(submark)
                        raise
                    except DeadEnd:
                        self.rollback(submark)
                raise DeadEnd("binary child choices exhausted")

            walk(1, a % M, M, [(a % M, M)])
        except (DeadEnd, SearchLimit):
            self.rollback(mark)
            raise
        finally:
            self.blocked = old_blocked

    def _close(self, a, M, depth):
        self._check_limits(depth)
        if self.inherited(a, M) or self.fully_covered(a, M):
            return
        if M >= self.minmod and M not in self.used:
            self.take(a, M)
            return

        # Try p-ary splits whose first usable modulus is closest to the
        # minimum.  Binary is preferred when it can consume one direct level
        # class; larger p values diversify branches but recurse on p-1
        # siblings because equal moduli are forbidden.
        splits = [p for p in self.primes if p > 1 and gcd(p, M) == 1]
        splits.sort(key=lambda p: (abs(p * M - self.minmod), p))
        tails = [p for p in self.tails
                 if gcd(p, M) == 1 and p not in self.used]
        tails.sort()
        for split in splits:
            for tail in tails:
                mark = len(self.out)
                try:
                    self._chain(a, M, depth, split, tail)
                    return
                except SearchLimit:
                    self.rollback(mark)
                    raise
                except DeadEnd:
                    self.rollback(mark)
                    self.backtracks += 1
        raise DeadEnd("no tail closes cell")

    def run(self):
        self._close(0, 1, 0)
        return sorted(self.out, key=lambda x: x[1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("minmod", type=int)
    ap.add_argument("--max-depth", type=int, default=80)
    ap.add_argument("--max-nodes", type=int, default=200000)
    ap.add_argument("--max-classes", type=int, default=200000)
    ap.add_argument("--tail-limit", type=int, default=40)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    b = TreeBuilder(args.minmod, tails=DEFAULT_TAILS[:args.tail_limit],
                    max_depth=args.max_depth,
                    max_nodes=args.max_nodes,
                    max_classes=args.max_classes)
    print("TREE minmod=%d depth=%d nodes=%d" %
          (args.minmod, args.max_depth, args.max_nodes), flush=True)
    try:
        congs = b.run()
    except SearchLimit as exc:
        print("LIMIT: %s nodes=%d backtracks=%d classes=%d depth=%d" %
              (exc, b.nodes, b.backtracks, len(b.out),
               b.max_open_depth), flush=True)
        return 2
    except DeadEnd as exc:
        print("DEAD: %s nodes=%d backtracks=%d classes=%d depth=%d" %
              (exc, b.nodes, b.backtracks, len(b.out),
               b.max_open_depth), flush=True)
        return 1

    fn = args.out or ("/tmp/tree_cover_m%d.json" % args.minmod)
    with open(fn, "w") as f:
        json.dump({"minmod": args.minmod,
                   "congruences": [[int(a), int(n)] for a, n in congs]},
                  f)
    print("SUCCESS: classes=%d nodes=%d backtracks=%d -> %s" %
          (len(congs), b.nodes, b.backtracks, fn), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

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

    def inherited(self, a, M):
        """Exact check whether (a mod M) lies inside a chosen class."""
        return any(M % n == 0 and (a - r) % n == 0
                   for r, n in self.out)

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

    def _chain(self, a, M, depth, tail):
        """Try one finite binary chain with a fresh odd tail prime."""
        if gcd(M, tail) != 1:
            raise DeadEnd("tail shares a factor with cell modulus")

        # Tail exponents run from K down to K+1-tail.  The smallest tail
        # modulus must itself meet the minimum-modulus requirement.
        K = max(tail - 1, 1)
        while tail * M * 2 ** (K + 1 - tail) < self.minmod:
            K += 1

        tail_mods = [tail * M * 2 ** (K + 1 - j)
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
                child_mod = path_M * 2
                for open_j in (0, 1):
                    sibling_j = 1 - open_j
                    sibling_a = (path_a + sibling_j * path_M) % child_mod
                    next_a = (path_a + open_j * path_M) % child_mod
                    submark = len(self.out)
                    try:
                        if child_mod >= self.minmod:
                            # Prefer the economical direct level class, but
                            # backtrack to a recursive closure if it collides
                            # or prevents the rest of the tree from closing.
                            try:
                                self.take(sibling_a, child_mod)
                            except DeadEnd:
                                self._close(sibling_a, child_mod, depth + k)
                        else:
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
        if self.inherited(a, M):
            return
        if M >= self.minmod and M not in self.used:
            self.take(a, M)
            return

        # A fresh tail is selected per attempted cell.  Tail order is a
        # deterministic heuristic; DFS backtracks on all exact failures.
        tails = [p for p in self.tails if gcd(p, M) == 1 and p not in self.used]
        for tail in tails:
            mark = len(self.out)
            try:
                self._chain(a, M, depth, tail)
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

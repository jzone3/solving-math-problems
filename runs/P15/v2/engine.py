#!/usr/bin/env python3
"""P15 V2 engine: CRT-layered set-cover construction of covering systems with
distinct moduli >= T, moduli restricted to divisors of a smooth N = prod p^cap_p.

Model: a *cell* is a residue class r mod m (m | N). Cover Z = cover the root
cell (0 mod 1). To cover a cell we either close it with the (single-use)
modulus value m (allowed iff m >= T and unused), or split it along a prime p
with exponent slack into p subcells mod m*p and cover each.

The choice of split prime at each node is the whole game; this engine takes a
strategy function and supports randomized restarts. Explicit witness emitted;
verify with solutions/P15/verify.py.
"""
import sys
import random
from heapq import heappush, heappop


class Pool:
    def __init__(self, caps):  # caps: dict prime -> max exponent
        self.caps = dict(caps)
        self.primes = sorted(caps)


def build(T, pool, strategy, max_congs=2_000_000, seed=0, order="bfs"):
    """Attempt to build a covering. Returns (congs, stats) or (None, stats).

    Cells processed from a priority queue (largest measure first by default).
    cell = (m, r, fact) with fact dict prime->exp.
    """
    rng = random.Random(seed)
    used = set()
    congs = []
    tie = 0
    heap = []

    def push(m, r, fact):
        nonlocal tie
        tie += 1
        heappush(heap, (m, tie, r, fact))

    push(1, 0, {})
    peak = 0
    while heap:
        peak = max(peak, len(heap))
        m, _, r, fact = heappop(heap)
        if m >= T and m not in used:
            used.add(m)
            congs.append((r, m))
            if len(congs) > max_congs:
                return None, {"reason": "max_congs", "congs": len(congs), "peak": peak}
            continue
        # must split: candidate primes with slack
        cands = [p for p in pool.primes if fact.get(p, 0) < pool.caps[p]]
        if not cands:
            return None, {"reason": "stuck", "cell_mod": m, "congs": len(congs), "peak": peak}
        p = strategy(m, fact, cands, used, T, rng)
        nf = dict(fact)
        nf[p] = nf.get(p, 0) + 1
        mp = m * p
        ks = list(range(p))
        # close one child immediately if its value is fresh (reservation),
        # so sibling cells see contention at decision time
        if mp >= T and mp not in used:
            used.add(mp)
            congs.append((r, mp))  # child k=0
            if len(congs) > max_congs:
                return None, {"reason": "max_congs", "congs": len(congs), "peak": peak}
            ks = ks[1:]
        for k in ks:
            push(mp, r + k * m, nf)
        if len(heap) > 4 * max_congs:
            return None, {"reason": "heap_blowup", "congs": len(congs),
                          "open": len(heap), "peak": peak}
    return congs, {"reason": "done", "congs": len(congs), "peak": peak}


# ---------------- strategies ----------------

def strat_smallest(m, fact, cands, used, T, rng):
    """Smallest prime with slack whose child value is fresh & >= T; else the
    prime that reaches T fastest; else smallest."""
    for p in cands:
        if m * p >= T and m * p not in used:
            return p
    for p in cands:
        if m * p >= T:
            return p
    return cands[-1] if m * cands[-1] < T else cands[0]


def strat_frontier(m, fact, cands, used, T, rng):
    """Score each candidate p by immediate value freshness AND how many fresh
    grandchild values exist per open child (one-step lookahead)."""
    best, bestscore = None, None
    for p in cands:
        mp = m * p
        fresh = 1.0 if (mp >= T and mp not in used) else 0.0
        open_children = p - fresh
        # lookahead: fresh grandchild values m*p*q
        gq = 0
        for q in cands:
            extra = 1 if q == p else 0
            if fact.get(q, 0) + extra < (fact.get(q, 0) + extra) + 1:  # slack proxy
                if mp * q >= T and mp * q not in used:
                    gq += 1
        score = (fresh + min(gq, open_children)) / open_children if open_children else 2.0
        if bestscore is None or score > bestscore or (score == bestscore and p < best):
            best, bestscore = p, score
    return best


def strat_cheapest_ratio(m, fact, cands, used, T, rng):
    """Prefer fresh closable child with smallest p (least branching); among
    non-closable, prefer prime minimizing p (keeps siblings cheap)."""
    fresh = [p for p in cands if m * p >= T and m * p not in used]
    if fresh:
        return fresh[0]
    below = [p for p in cands if m * p < T]
    if below:
        # still under threshold: jump with the largest prime to cross T quickly
        return below[-1]
    return cands[0]


def strat_random(m, fact, cands, used, T, rng):
    fresh = [p for p in cands if m * p >= T and m * p not in used]
    if fresh and rng.random() < 0.9:
        return rng.choice(fresh[: 3])
    return rng.choice(cands)


STRATS = {
    "smallest": strat_smallest,
    "ratio": strat_cheapest_ratio,
    "random": strat_random,
    "frontier": strat_frontier,
}


def default_pool(T, nprimes, cap_small=30, cap=1):
    """Primes 2,3 with deep caps; further primes shallow."""
    ps = []
    n = 2
    while len(ps) < nprimes:
        if all(n % q for q in ps):
            ps.append(n)
        n += 1
    caps = {}
    for p in ps:
        caps[p] = cap_small if p <= 3 else (3 if p <= 7 else cap)
    return Pool(caps)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("--nprimes", type=int, default=25)
    ap.add_argument("--strategy", default="smallest")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-congs", type=int, default=2_000_000)
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()
    pool = default_pool(args.T, args.nprimes)
    congs, stats = build(args.T, pool, STRATS[args.strategy],
                         max_congs=args.max_congs, seed=args.seed)
    print(f"T={args.T} strat={args.strategy} nprimes={args.nprimes} -> {stats}")
    if congs and args.out:
        with open(args.out, "w") as f:
            f.write(f"# T={args.T} strategy={args.strategy} nprimes={args.nprimes}\n")
            for r, m in congs:
                f.write(f"{r % m} {m}\n")
        print(f"wrote {len(congs)} congruences to {args.out}")


if __name__ == "__main__":
    main()

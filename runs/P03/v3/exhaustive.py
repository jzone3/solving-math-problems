"""Exhaustive verification of Woodall's conjecture on all simple digraphs on n<=N vertices.

Pipeline: nauty-geng -c N | nauty-directg  -> digraph6 lines -> for each digraph:
  tau = min dicut size; if tau >= 2, decide whether arcs partition into tau classes each
  hitting every minimal dicut (= tau disjoint dijoins). Any failure = counterexample.

Note ACZ rho-based results already force n >= 6 for a tau=3 counterexample, so n=6
exhaustion (simple digraphs, 2-cycles allowed, no parallel arcs) is the first
interesting frontier. Run: nauty-geng -c 6 | nauty-directg | python3 exhaustive.py
"""
import random
import sys

from pysat.solvers import Minicard


def parse_digraph6(line):
    """Parse digraph6 format '&' + N(n) + bitvector of adjacency matrix rows."""
    assert line[0] == '&'
    data = [ord(c) - 63 for c in line[1:]]
    n = data[0]
    assert 0 <= n <= 62
    bits = []
    for x in data[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    arcs = []
    idx = 0
    for u in range(n):
        for v in range(n):
            if bits[idx]:
                arcs.append((u, v))
            idx += 1
    return n, arcs


def min_dicuts_and_tau(n, arcs):
    m = len(arcs)
    tails = [1 << u for (u, _) in arcs]
    heads = [1 << v for (_, v) in arcs]
    dicuts = []
    tau = None
    full = (1 << n) - 1
    for U in range(1, full):
        cut = []
        ok = True
        for i in range(m):
            hin = heads[i] & U
            tin = tails[i] & U
            if hin and not tin:
                ok = False
                break
            if tin and not hin:
                cut.append(i)
        if ok and cut:
            dicuts.append(frozenset(cut))
            if tau is None or len(cut) < tau:
                tau = len(cut)
    # minimal only
    ds = sorted(set(dicuts), key=len)
    md = []
    for d in ds:
        if not any(x <= d for x in md):
            md.append(d)
    return tau, md


def greedy_pack(m, md, k, rng, tries=15):
    for _ in range(tries):
        cols = [rng.randrange(k) for _ in range(m)]
        bad = [d for d in md if len({cols[i] for i in d}) < k]
        steps = 0
        while bad and steps < 200:
            d = bad[0]
            present = {cols[i] for i in d}
            missing = [c for c in range(k) if c not in present]
            i = rng.choice(sorted(d))
            cols[i] = rng.choice(missing)
            bad = [dd for dd in md if len({cols[j] for j in dd}) < k]
            steps += 1
        if not bad:
            return True
    return False


def sat_pack(m, md, k):
    cnf = []
    for i in range(m):
        vs = [k * i + c + 1 for c in range(k)]
        cnf.append(vs)
        for a in range(k):
            for b in range(a + 1, k):
                cnf.append([-vs[a], -vs[b]])
    for d in md:
        for c in range(k):
            cnf.append([k * i + c + 1 for i in d])
    with Minicard(bootstrap_with=cnf) as s:
        return s.solve()


def main():
    rng = random.Random(0)
    total = 0
    by_tau = {}
    cex = 0
    sat_calls = 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        n, arcs = parse_digraph6(line)
        total += 1
        tau, md = min_dicuts_and_tau(n, arcs)
        if tau is None:  # strongly connected: no dicuts, conjecture vacuous
            by_tau["strong"] = by_tau.get("strong", 0) + 1
            continue
        by_tau[tau] = by_tau.get(tau, 0) + 1
        if tau < 2:
            continue  # tau=1: whole arc set is one dijoin, trivially holds
        m = len(arcs)
        if greedy_pack(m, md, tau, rng):
            continue
        sat_calls += 1
        if not sat_pack(m, md, tau):
            cex += 1
            print(f"COUNTEREXAMPLE: digraph6={line} n={n} arcs={arcs} tau={tau}",
                  flush=True)
        if total % 100000 == 0:
            print(f"...{total} done, by_tau={by_tau}, sat_calls={sat_calls}",
                  file=sys.stderr, flush=True)
    print(f"TOTAL={total} by_tau={by_tau} sat_fallback_calls={sat_calls} "
          f"counterexamples={cex}", flush=True)


if __name__ == "__main__":
    main()

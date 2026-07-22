"""Optimized exhaustive Woodall verification over digraph6 stdin (see exhaustive.py).

Speedups: closed-set test via in-neighbor masks (n ops/subset), arc-index recovery only
for closed sets, single fast greedy then SAT fallback.
Usage: nauty-geng -c 6 | nauty-directg | python3 exhaustive2.py
"""
import sys

from pysat.solvers import Minicard


def parse_digraph6(line):
    data = [ord(c) - 63 for c in line[1:]]
    n = data[0]
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


def greedy_pack(m, md, k):
    """Deterministic greedy: color arcs to satisfy dicuts in size order."""
    cols = [-1] * m
    for d in sorted(md, key=len):
        present = set()
        free = []
        for i in d:
            if cols[i] >= 0:
                present.add(cols[i])
            else:
                free.append(i)
        missing = [c for c in range(k) if c not in present]
        if len(missing) > len(free):
            return False
        for c, i in zip(missing, free):
            cols[i] = c
    return True


def main():
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
        if total % 200000 == 0:
            print(f"...{total} done, by_tau={by_tau}, sat={sat_calls}",
                  file=sys.stderr, flush=True)
        m = len(arcs)
        inmask = [0] * n
        outmask = [0] * n
        for (u, v) in arcs:
            inmask[v] |= 1 << u
            outmask[u] |= 1 << v
        full = (1 << n) - 1
        verts = range(n)
        # find tau and all dicut vertex-sets
        tau = None
        cutsets = []
        for U in range(1, full):
            inn = 0
            out = 0
            bad = False
            for v in verts:
                if (U >> v) & 1:
                    if inmask[v] & ~U:
                        bad = True
                        break
                    out |= outmask[v]
            if bad:
                continue
            if not out & ~U:
                continue
            cnt = 0
            for v in verts:
                if (U >> v) & 1:
                    x = outmask[v] & ~U
                    while x:
                        x &= x - 1
                        cnt += 1
            cutsets.append(U)
            if tau is None or cnt < tau:
                tau = cnt
        if tau is None:
            by_tau["strong"] = by_tau.get("strong", 0) + 1
            continue
        by_tau[tau] = by_tau.get(tau, 0) + 1
        if tau < 2:
            continue
        # arc-index dicuts, minimal only
        aidx = {}
        for i, (u, v) in enumerate(arcs):
            aidx.setdefault((u, v), []).append(i)
        dicuts = set()
        for U in cutsets:
            cut = []
            for i, (u, v) in enumerate(arcs):
                if (U >> u) & 1 and not (U >> v) & 1:
                    cut.append(i)
            dicuts.add(frozenset(cut))
        ds = sorted(dicuts, key=len)
        md = []
        for d in ds:
            if not any(x <= d for x in md):
                md.append(d)
        if greedy_pack(m, md, tau):
            continue
        sat_calls += 1
        if not sat_pack(m, md, tau):
            cex += 1
            print(f"COUNTEREXAMPLE: digraph6={line} n={n} arcs={arcs} tau={tau}",
                  flush=True)
    print(f"TOTAL={total} by_tau={by_tau} sat_fallback_calls={sat_calls} "
          f"counterexamples={cex}", flush=True)


if __name__ == "__main__":
    main()

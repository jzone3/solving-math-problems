"""Exhaustive check of the block construction inside the smallest open class.

p=12 sources (out-deg 4), q=16 sinks (in-deg 3). Sources are grouped into 4
blocks of 3; block i fully covers 3 private sinks (9 arcs), so U = block i +
its sinks yields a NONTRIVIAL tight 3-cut (the block's 3 leftover arcs).
The 12 leftover arcs (one per source) feed 4 extra sinks (3 each, distinct
sources). We exhaust all set-partitions of the 12 sources into 4 unordered
triples for the extra sinks: 12!/(3!^4 4!) = 15400 instances, each containing
4 disjoint nontrivial tight 3-cuts by construction.
"""
import sys
from itertools import combinations
from bipsearch import min_dicuts_bip, packs3

P = 12


def partitions_into_triples(elems):
    if not elems:
        yield []
        return
    first = elems[0]
    rest = elems[1:]
    for pair in combinations(rest, 2):
        tri = (first,) + pair
        remaining = [x for x in rest if x not in pair]
        for tail in partitions_into_triples(remaining):
            yield [list(tri)] + tail


def main():
    base = []
    for b in range(4):
        blk = [3 * b, 3 * b + 1, 3 * b + 2]
        for _ in range(3):
            base.append(sorted(blk))
    n = tau3 = 0
    for part in partitions_into_triples(list(range(P))):
        sinks = base + [sorted(t) for t in part]
        n += 1
        cuts, tau = min_dicuts_bip(P, sinks)
        if cuts is None or tau != 3:
            continue
        tau3 += 1
        if not packs3(sinks, cuts):
            print("UNSAT COUNTEREXAMPLE", sinks, flush=True)
            with open("counterexample.txt", "a") as f:
                f.write("BLOCKCONS %r\n" % (sinks,))
        if n % 1000 == 0:
            print(f"[blockcons] n={n} tau3={tau3}", flush=True)
    print(f"[blockcons] DONE n={n} tau3={tau3}", flush=True)


if __name__ == "__main__":
    main()

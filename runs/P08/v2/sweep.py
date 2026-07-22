"""Parameter sweep over the V2 structured families for Graffiti 39/40.

For every instance we record the score dev(D) - min(n+, n-) (a counterexample to
39-or-40 needs score > 0; a counterexample to 39 alone needs dev - n+ > 0) and we
assert the proof chain dev <= diam/2 <= ceil(diam/2) <= min(n+, n-).

Usage: python3 sweep.py [max_n]
"""

import sys
import math
from families import (evaluate, broom, double_broom, caterpillar,
                      caterpillar_legpattern, spider, multipartite_plus_path,
                      kite, path_edges)

MAX_N = int(sys.argv[1]) if len(sys.argv) > 1 else 400

best = []          # (score, desc, stats)
violations = []    # proof-chain violations (should stay empty)
count = 0


def consider(desc, edges, n):
    global count
    if n > MAX_N or n < 2:
        return
    st = evaluate(edges, n)
    if st is None:
        return
    count += 1
    sc = max(st["score39"], st["score40"])
    best.append((sc, desc, st))
    # proof chain check
    half = st["diam"] / 2.0
    if not (st["dev"] <= half + 1e-9 and
            math.ceil(st["diam"] / 2) <= min(st["npos"], st["nneg"])):
        violations.append((desc, st))


def main():
    # paths (baseline)
    for n in range(2, MAX_N + 1, max(1, MAX_N // 100)):
        consider(f"path({n})", path_edges(n), n)

    # brooms
    for handle in range(2, MAX_N, 8):
        for bristles in (1, 2, 3, 5, 10, 20, 50, 100):
            e, n = broom(handle, bristles)
            consider(f"broom(h={handle},b={bristles})", e, n)

    # double brooms
    for handle in range(2, MAX_N, 12):
        for b1 in (1, 3, 10, 30):
            for b2 in (1, 3, 10, 30):
                e, n = double_broom(handle, b1, b2)
                consider(f"dbroom(h={handle},{b1},{b2})", e, n)

    # caterpillars: periodic single legs
    for spine in range(4, MAX_N, 8):
        for legs in (1, 2, 3):
            for period in (1, 2, 3, 4, 6):
                e, n = caterpillar(spine, legs, period)
                consider(f"cat(s={spine},l={legs},p={period})", e, n)

    # caterpillars with leg patterns (spectral degeneracy hunting)
    for spine in range(6, MAX_N, 12):
        for pat in ([1, 0], [2, 0], [1, 0, 0], [3, 0, 0, 0], [1, 1, 0, 0]):
            e, n = caterpillar_legpattern(spine, pat)
            consider(f"catpat(s={spine},pat={pat})", e, n)

    # spiders / subdivided stars
    for nlegs in (3, 4, 5, 8, 12, 20, 40):
        for leglen in range(1, MAX_N, 4):
            e, n = spider(nlegs, leglen)
            consider(f"spider(k={nlegs},L={leglen})", e, n)

    # complete multipartite + pendant path (small n+ = k-1, stretched diameter)
    for k in (2, 3, 4, 5):
        for part in (2, 3, 5, 10, 20):
            for tail in range(0, MAX_N, 10):
                e, n = multipartite_plus_path([part] * k, tail)
                consider(f"Kmulti({k}x{part})+tail{tail}", e, n)

    # kites / lollipops
    for clique in (3, 5, 10, 20, 40):
        for tail in range(0, MAX_N, 10):
            e, n = kite(clique, tail)
            consider(f"kite(K{clique},tail{tail})", e, n)

    best.sort(key=lambda t: -t[0])
    print(f"instances evaluated: {count}  (max n = {MAX_N})")
    print(f"proof-chain violations: {len(violations)}")
    for d, st in violations[:10]:
        print("VIOLATION", d, st)
    print("\ntop 15 by score = dev - min(n+,n-):")
    for sc, d, st in best[:15]:
        print(f"  {sc:+9.4f}  {d:40s} n={st['n']:4d} dev={st['dev']:8.3f} "
              f"n+={st['npos']:4d} n-={st['nneg']:4d} diam={st['diam']:4d}")
    # ratio view: how close does dev/min(n+,n-) get to 1?
    ratio = sorted(best, key=lambda t: -(t[2]["dev"] / max(1, min(t[2]["npos"], t[2]["nneg"]))))
    print("\ntop 10 by ratio dev/min(n+,n-):")
    for sc, d, st in ratio[:10]:
        r = st["dev"] / max(1, min(st["npos"], st["nneg"]))
        print(f"  r={r:6.4f}  {d:40s} n={st['n']:4d} dev={st['dev']:8.3f} "
              f"n+={st['npos']:4d} n-={st['nneg']:4d} diam={st['diam']:4d}")


if __name__ == "__main__":
    main()

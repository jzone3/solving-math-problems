"""Machine sanity check of the domination lemma:

LEMMA. Let D' be obtained from D by subdividing one arc.  Then
tau(D') = tau(D) and nu(D') >= nu(D).  Hence if D packs (nu = tau), so does
every iterated subdivision of D — the 'replace weight-0 arcs by paths' family
is dominated by the all-plain-arcs instance.

Proof sketch (logged in NOTES.md): dicuts of D' are exactly dicuts of D with
the subdivided arc a replaced by one of its two halves; a packing of D lifts
by replacing a with both halves in the (unique) dijoin containing a.

This script tests the lemma on random digraphs, and additionally that adding
an arc never decreases nu (packings survive arc addition).
"""
import random

import core


def rand_digraph(rng):
    n = rng.randint(5, 9)
    m = rng.randint(n, 2 * n)
    arcs = []
    while len(arcs) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            arcs.append((u, v))
    # ensure weak connectivity by chaining
    for i in range(n - 1):
        if rng.random() < 0.5:
            arcs.append((i, i + 1))
        else:
            arcs.append((i + 1, i))
    return n, arcs


def main(trials=120, seed=7):
    rng = random.Random(seed)
    checked = 0
    for _ in range(trials):
        n, arcs = rand_digraph(rng)
        t, _ = core.tau(n, arcs)
        if t is None or t == 0:
            continue
        _, v = core.nu(n, arcs)
        i = rng.randrange(len(arcs))
        u, w_ = arcs[i]
        arcs2 = arcs[:i] + arcs[i + 1:] + [(u, n), (n, w_)]
        t2, _ = core.tau(n + 1, arcs2)
        _, v2 = core.nu(n + 1, arcs2)
        assert t2 == t, (n, arcs, i, t, t2)
        assert v2 >= v, (n, arcs, i, v, v2)
        # arc addition
        a, b = rng.randrange(n), rng.randrange(n)
        if a != b:
            arcs3 = arcs + [(a, b)]
            t3, _ = core.tau(n, arcs3)
            if t3 is not None and t3 > 0:
                _, v3 = core.nu(n, arcs3)
                assert v3 >= v, (n, arcs, (a, b), v, v3)
        checked += 1
    print(f"LEMMA CHECK PASS on {checked} random digraphs "
          "(tau preserved by subdivision, nu monotone under subdivision "
          "and arc addition)")


if __name__ == "__main__":
    main()

"""Meet-in-the-middle exhaustive search for cases with 2 or 3 full orbits.

Decomposition per case: the design is (short orbits) + (optional inf orbit)
+ 1 or 2 finite full orbits. We enumerate the small side exhaustively and
resolve the last finite full orbit(s) by dictionary lookup on the forced
complement mask, iterating over the first full orbit when there are two.

For the (18,6) Z17+inf case we cut the A1 iteration by the multiplier group
(units of Z17 are automorphisms fixing inf and permuting translation orbits):
WLOG one finite full orbit has multiplier-canonical mask.

Exhaustiveness: every design within the ansatz decomposes uniquely into
orbits, so some branch of the enumeration finds it.
"""
import sys, time, itertools
from collections import defaultdict
from diffsearch import Engine, cyclic_group, product_group
from run_case import expand
from pmdlib import check_pmd


def gen_full(eng, with_inf):
    return eng.full_orbit_candidates(with_inf)


def units(m):
    from math import gcd
    return [u for u in range(1, m) if gcd(u, m) == 1]


def mult_mask(eng, block, u, m):
    b2 = tuple('inf' if x == 'inf' else (x * u) % m for x in block)
    return eng.block_mask(b2)


def run(name, group, k, use_inf, n_finite_full, use_multiplier=False, mod=None):
    els, add, neg = group
    eng = Engine(els, add, neg, k, use_inf)
    v = len(els) + (1 if use_inf else 0)
    t0 = time.time()
    A = gen_full(eng, False)          # finite full orbits
    B = gen_full(eng, True) if use_inf else []
    S = eng.short_orbit_candidates()
    print(f"[{name}] v={v} k={k} |A|={len(A)} |B|={len(B)} |S|={len(S)} gen {time.time()-t0:.0f}s", flush=True)
    target = (1 << eng.n_items) - 1

    Adict = defaultdict(list)
    for c in A:
        Adict[c[1]].append(c)

    # enumerate small-side combos: subsets of shorts (any multiset of distinct
    # masks with disjoint coverage) + one B if use_inf, such that remaining
    # coverage is exactly n_finite_full * (k per t pattern) -- we just require
    # the complement to be fillable by full orbits, checked via lookup.
    # Shorts: try all subsets with pairwise-disjoint masks (small |S|).
    short_combos = [(0, [])]
    for i, c in enumerate(S):
        new = []
        for m0, lst in short_combos:
            if not (m0 & c[1]):
                new.append((m0 | c[1], lst + [c]))
        short_combos += new
    # keep only combos whose per-t residual count is divisible appropriately:
    # residual per t must equal n_finite_full*k + (k-2 if use_inf else 0)
    nz = len(eng.nonzero)
    def per_t_count(mask, t):
        seg = (mask >> ((t - 1) * nz)) & ((1 << nz) - 1)
        return bin(seg).count('1')
    need = n_finite_full * k + (k - 2 if use_inf else 0)
    combos = []
    for m0, lst in short_combos:
        if all(nz - per_t_count(m0, t) == need for t in range(1, k)):
            combos.append((m0, lst))
    print(f"[{name}] short combos with correct residual: {len(combos)}", flush=True)

    canonA = None
    if use_multiplier:
        us = units(mod)
        canon_set = []
        for c in A:
            mm = min(mult_mask(eng, c[0], u, mod) for u in us)
            if mm == c[1]:
                canon_set.append(c)
        canonA = canon_set
        print(f"[{name}] canonical A candidates: {len(canonA)} / {len(A)}", flush=True)

    sols = []
    t1 = time.time()
    Bs = B if use_inf else [None]
    for m0, lst in combos:
        if n_finite_full == 1:
            for b in Bs:
                base = m0 | (b[1] if b else 0)
                if b and (m0 & b[1]):
                    continue
                rem = target & ~base
                if rem in Adict:
                    sols.append(lst + ([b] if b else []) + [Adict[rem][0]])
        elif n_finite_full == 2:
            A1s = canonA if use_multiplier else A
            for a1 in A1s:
                if a1[1] & m0:
                    continue
                pm = m0 | a1[1]
                for b in Bs:
                    base = pm | (b[1] if b else 0)
                    if b and ((pm) & b[1]):
                        continue
                    rem = target & ~base
                    if rem in Adict:
                        sols.append(lst + ([b] if b else []) + [a1, Adict[rem][0]])
                        break
                if sols:
                    break
        if sols:
            break
    print(f"[{name}] search {time.time()-t1:.0f}s, solutions: {len(sols)}", flush=True)
    if sols:
        cands = sols[0]
        print("  base blocks:", [c[0] for c in cands])
        idxs = list(range(len(cands)))
        design = expand(eng, idxs, cands)
        ok, msg = check_pmd(design, v, k, 1)
        print("  verify:", msg, flush=True)
    else:
        print(f"[{name}] EXHAUSTIVE NEGATIVE within ansatz", flush=True)
    return sols


CASES = {
    "15_6_Z15":    (cyclic_group(15), 6, False, 2, False, 15),
    "15_6_Z14inf": (cyclic_group(14), 6, True, 1, False, 14),
    "16_6_Z16":    (cyclic_group(16), 6, False, 2, False, 16),
    "16_6_Z15inf": (cyclic_group(15), 6, True, 1, False, 15),
    "16_6_Z2Z8":   (product_group([2, 8]), 6, False, 2, False, None),
    "16_6_Z4Z4":   (product_group([4, 4]), 6, False, 2, False, None),
    "16_6_Z2Z2Z4": (product_group([2, 2, 4]), 6, False, 2, False, None),
    "16_6_Z2222":  (product_group([2, 2, 2, 2]), 6, False, 2, False, None),
    "18_6_Z17inf": (cyclic_group(17), 6, True, 2, True, 17),
    "18_6_Z18":    (cyclic_group(18), 6, False, 2, False, 18),
    "18_6_Z3Z6":   (product_group([3, 6]), 6, False, 2, False, None),
    "15_7_Z15":    (cyclic_group(15), 7, False, 2, False, 15),
    "15_7_Z14inf": (cyclic_group(14), 7, True, 1, False, 14),
}

if __name__ == "__main__":
    name = sys.argv[1]
    g, k, ui, nf, um, mod = CASES[name]
    run(name, g, k, ui, nf, use_multiplier=um, mod=mod)

"""Run one difference-method exhaustive case. Usage:
   python3 run_case.py <case>
Cases defined in CASES below. Prints all engine-level solutions (or NONE),
and machine-verifies any solution found with pmdlib.check_pmd.
"""
import sys, time
from diffsearch import Engine, cyclic_group, product_group
from pmdlib import check_pmd


def expand(engine, chosen, candidates):
    """Expand chosen base blocks into the full design over the group."""
    els, add = engine.els, engine.add
    blocks = []
    for ci in chosen:
        block, mask, kind = candidates[ci]
        if kind == 'full':
            shifts = els
        else:
            _, s, r, d = kind
            # coset reps of <s>: greedily pick
            sub = set()
            x = engine.zero
            while x not in sub:
                sub.add(x)
                x = add(x, s)
            reps, seen = [], set()
            for g in els:
                cos = frozenset(add(g, h) for h in sub)
                if cos not in seen:
                    seen.add(cos)
                    reps.append(g)
            shifts = reps
        for g in shifts:
            blocks.append(tuple('inf' if x == 'inf' else add(x, g) for x in block))
    return blocks


def run(name, group, k, use_inf, find_all=False):
    els, add, neg = group
    eng = Engine(els, add, neg, k, use_inf)
    v = len(els) + (1 if use_inf else 0)
    t0 = time.time()
    cands = eng.full_orbit_candidates(with_inf=False)
    if use_inf:
        cands += eng.full_orbit_candidates(with_inf=True)
    cands += eng.short_orbit_candidates()
    t1 = time.time()
    print(f"[{name}] v={v} k={k} candidates={len(cands)} (gen {t1-t0:.1f}s)")
    sols = eng.solve(cands, find_all=find_all)
    t2 = time.time()
    print(f"[{name}] solve time {t2-t1:.1f}s, solutions found: {len(sols)}")
    for sol in sols[:5]:
        base = [cands[ci][0] for ci in sol]
        print("  base blocks:", base)
        design = expand(eng, sol, cands)
        ok, msg = check_pmd(design, v, k, 1)
        print("  verify:", msg)
    if not sols:
        print(f"[{name}] EXHAUSTIVE NEGATIVE within ansatz")
    return sols


CASES = {
    # sanity: known-existing PMDs
    "7_6_Z7":      (cyclic_group(7), 6, False),
    "13_6_Z13":    (cyclic_group(13), 6, False),
    "8_7_Z7inf":   (cyclic_group(7), 7, True),
    # open k=6 cases
    "9_6_Z9":      (cyclic_group(9), 6, False),
    "9_6_Z8inf":   (cyclic_group(8), 6, True),
    "9_6_Z3Z3":    (product_group([3, 3]), 6, False),
    "12_6_Z11inf": (cyclic_group(11), 6, True),
    "12_6_Z12":    (cyclic_group(12), 6, False),
    "12_6_Z2Z6":   (product_group([2, 6]), 6, False),
    "15_6_Z15":    (cyclic_group(15), 6, False),
    "15_6_Z14inf": (cyclic_group(14), 6, True),
    "16_6_Z16":    (cyclic_group(16), 6, False),
    "16_6_Z15inf": (cyclic_group(15), 6, True),
    "16_6_Z2Z8":   (product_group([2, 8]), 6, False),
    "16_6_Z4Z4":   (product_group([4, 4]), 6, False),
    "16_6_Z2Z2Z4": (product_group([2, 2, 4]), 6, False),
    "16_6_Z2222":  (product_group([2, 2, 2, 2]), 6, False),
    "18_6_Z18":    (cyclic_group(18), 6, False),
    "18_6_Z17inf": (cyclic_group(17), 6, True),
    "18_6_Z3Z6":   (product_group([3, 6]), 6, False),
    # open k=7 cases
    "14_7_Z14":    (cyclic_group(14), 7, False),
    "14_7_Z13inf": (cyclic_group(13), 7, True),
    "15_7_Z15":    (cyclic_group(15), 7, False),
    "15_7_Z14inf": (cyclic_group(14), 7, True),
}

if __name__ == "__main__":
    name = sys.argv[1]
    g, k, ui = CASES[name]
    run(name, g, k, ui)

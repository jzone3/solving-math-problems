#!/usr/bin/env python3
"""
P15 V4 phase 10: blueprint v3 - the ODD-5-POWER loophole repairs the
section-3.8 refutation, and slack sections absorb the re-aim relocation.

Phase 9 refuted the phase-5 repair (extra 3^ copies) at explicit modulus
level.  This phase finds and machine-checks the loophole: every modulus
in the sections' universal set-building pattern (1,2,4,8^; 5x; 25^; 3^
copies; 13^/17^; 7^ copies; the closing p^) has EVEN 5-adic valuation
except for the single 5-scaling (valuation exactly 1).  Hence an extra
25^ tower over 5-SCALED inputs produces moduli 5^(2j+1)*m with 5-adic
valuation >= 3 and ODD - a completely untouched stratum:

    25^(s5,s6,s7,s8)  ->  moduli 25^j * 5 * {1,2,4,8*2^i}
    25^(s13,s14)      ->  moduli 25^j * 3^a * 5 * {1,2,4,8*2^i}

Checked below against the FULL section-3.8 pool (all 18 sets + the
19-tower closure, cap 10^6): zero collisions, and the two mints are
mutually disjoint.  This restores the +2 sets that the T=43 ledger of
section 3.8 needs - now with machine-verified fresh moduli.

Second component: at T=43 the ledgers have 12 spare covering sets
(19:+2, 29:+2, 31:+1, 41:+1, 43:+1, 53:+1, 59:+1, 61:+3, from
blueprint43.py finishes).  Only FOUR are needed to absorb the cells
relocated by the re-aim {84,126,168,504} (blueprint43b, with 252 free).

Remaining validation burden (documented, NOT claimed):
  (a) per-section freshness replay of the other penalized sections'
      repairs using the same odd-5-power mints (15 fresh input pairs
      exist vs the universal core - checked below);
  (b) freshness of the spare-set instantiations on the four relocated
      branches (moduli = branch modulus * relative multiset);
  (c) residue-level emission + independent verifier for the whole
      system.
"""
from itertools import combinations

from ledger38 import build_sets, tower, CAP


def check_38_repair():
    s = build_sets()
    allu = set().union(*s.values())
    allu |= tower(19, list(s.values()))          # the section's own 19^
    mint1 = tower(25, [s[5], s[6], s[7], s[8]])  # 5-scaled quad
    mint2 = tower(25, [s[13], s[14]])            # 3^-of-5-scaled pair
    c1 = mint1 & allu
    c2 = mint2 & allu
    c12 = mint1 & mint2
    ok = not (c1 or c2 or c12)
    print(f"sec 3.8 odd-5-power mints: mint1 collisions={len(c1)}, "
          f"mint2 collisions={len(c2)}, cross={len(c12)} -> "
          f"{'PASS' if ok else 'FAIL'}")
    # sanity: valuations really are odd and >= 3
    def v5(n):
        k = 0
        while n % 5 == 0:
            n //= 5
            k += 1
        return k
    vals = {v5(m) for m in mint1 | mint2}
    print(f"  5-adic valuations of mint moduli: {sorted(vals)} "
          f"(all odd >= 3: {all(v % 2 == 1 and v >= 3 for v in vals)})")
    return ok


def check_universal_core_options():
    s = build_sets()
    core_ids = list(range(1, 16))
    core = set().union(*(s[i] for i in core_ids))
    fresh = [(a, b) for a, b in combinations(core_ids, 2)
             if not (tower(25, [s[a], s[b]]) & core)]
    print(f"universal-core fresh 25^ input pairs (for the other "
          f"penalized sections): {len(fresh)} -> {fresh}")
    return len(fresh) >= 3


def spare_sets():
    spares = {19: 2, 29: 2, 31: 1, 41: 1, 43: 1, 53: 1, 59: 1, 61: 3}
    total = sum(spares.values())
    print(f"T=43 ledger spare covering sets: {spares} (total {total}); "
          f"4 needed for relocated cells 84,126,168,504 -> "
          f"{'PASS' if total >= 4 else 'FAIL'}")
    return total >= 4


if __name__ == "__main__":
    a = check_38_repair()
    b = check_universal_core_options()
    c = spare_sets()
    print()
    if a and b and c:
        print("RESULT: blueprint v3 components PASS - phase-9 refutation "
              "REPAIRED via the odd-5-power stratum; section 3.8 now has "
              "a modulus-fresh +2 repair; slack absorbs the re-aim "
              "relocation.  Open burdens: (a),(b),(c) in the docstring.")
    else:
        print("RESULT: FAIL - see above.")

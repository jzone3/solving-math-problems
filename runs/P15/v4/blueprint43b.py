#!/usr/bin/env python3
"""
P15 V4 phase 7: the RE-AIM lemma and the relocation-growth obstruction.

LEMMA (machine-verified below): the dead 42-cell is exactly covered by
re-aiming five of Owens's OWN moduli - the multiples of 42 in his 7-layer:

    a* + 42*0 (mod 84),  a* + 42*0 (mod 126),  a* + 42*1 (mod 168),
    a* + 42*5 (mod 252), a* + 42*7 (mod 504)

(using the classic distinct-moduli cover of Z: 0(2), 0(3), 1(4), 5(6),
7(12), scaled by 42). So a T=43 system does NOT need any modulus that is
free in Owens's system to cover the 42-cell - it can steal used ones.

OBSTRUCTION (the reason this alone is not a solution): stealing relocates
the holes to the five cells those moduli previously covered, and any
distinct-moduli cover of Z has density >= 4/3 within the 7-smooth cascade
(1/2+1/3+1/4+1/6+1/12 = 4/3), so pure relocation GROWS the total hole
measure by 4/3 per cascade level:

    1/42 = 0.02381  ->  16/504 = 0.03175  ->  ...

Termination therefore requires routing the relocated holes into branches
where the primes >= 11 have genuine spare capacity. Unlike the flat
42-cell (which sits in the third 7^-entry where nothing else operates),
the five relocated cells carry 2/3-adic structure at depths 84..504 -
exactly the kind of cells the repaired ledgers' extra tower copies
(blueprint43.py) are designed to absorb. Quantitatively the growth factor
4/3 must be beaten by section absorption within O(1) cascade levels;
skeleton43.py shows the 7-smooth skeleton itself has NO slack (Owens is
density-perfect: 0.6292 used vs 0.6293 ceiling at T=42), so all
absorption must come from the >= 11 sections.

This replaces the refuted 13th section (NEW 42-hole via 97) of
blueprint43.py with a re-aim + relocation scheme whose validation burden
is the SAME as the other 12 repaired ledgers (fresh-support modulus
tracking), rather than the impossible free-modulus tower construction.
"""
from math import lcm


def verify_reaim(a_star=2, verbose=True):
    congs = [(a_star + 42 * 0, 84),
             (a_star + 42 * 0, 126),
             (a_star + 42 * 1, 168),
             (a_star + 42 * 5, 252),
             (a_star + 42 * 7, 504)]
    L = 42
    for _, m in congs:
        L = lcm(L, m)
    bad = [x for x in range(a_star, a_star + L, 42)
           if not any(x % m == a % m for a, m in congs)]
    distinct = len({m for _, m in congs}) == len(congs)
    inside = all((a - a_star) % 42 == 0 for a, m in congs)
    ok = (not bad) and distinct and inside
    if verbose:
        print(f"re-aim congruences: {congs}")
        print(f"cover class {a_star} (mod 42) over lcm {L}: {not bad}")
        print(f"distinct moduli: {distinct}; classes inside cell: {inside}")
        print(f"{'PASS' if ok else 'FAIL'}: LEMMA - {{84,126,168,252,504}} "
              f"re-aimed exactly cover the 42-cell")
    return ok


def owens_usage_check():
    """Confirm all five moduli really are used by Owens (else they would
    already be free and section 15 analysis would have found them)."""
    from owens_smooth import used_smooth
    U = used_smooth(10**4)
    rows = [(m, "USED" if m in U else "FREE") for m in
            (84, 126, 168, 252, 504)]
    print("Owens usage of the re-aim moduli:", rows)
    return all(v == "USED" for _, v in rows)


def relocation_growth():
    from fractions import Fraction as F
    cell = F(1, 42)
    relocated = sum(F(1, m) for m in (84, 126, 168, 252, 504))
    print(f"hole measure: 42-cell = {cell} = {float(cell):.5f} -> "
          f"relocated = {relocated} = {float(relocated):.5f} "
          f"(growth x{float(relocated / cell):.4f})")
    return relocated


if __name__ == "__main__":
    ok = verify_reaim()
    used_ok = owens_usage_check()
    relocation_growth()
    print()
    if ok and used_ok:
        print("RESULT: re-aim lemma PASS; 42-cell coverable by Owens's own "
              "moduli. Open validation burden: absorb the five relocated "
              "cells (measure 16/504) in the >=11 sections - same burden "
              "class as the 12 repaired ledgers, replacing the refuted "
              "free-modulus 13th section.")
    else:
        print("RESULT: check FAILED - see above.")

"""Patch route for T=43, phase 6: quantify the TRUE free-modulus budget
after the faithful section-3.4 enumeration (owens_smooth.py), and test
how far the 42-hole can be covered.

Inner coordinates: x = a* + 42k; a congruence k = r (mod n) is realized
by actual modulus M = n*g with g | 42, gcd(M,42) = g, M >= 43, M not used
by Owens.  Two regimes:

(A) 7-smooth free moduli.  Faithful enumeration shows at 7-tower level
    k >= 2 the free multipliers are exactly {1,2,3,4,5}: actual moduli
    7^k * t.  Inner n and per-level free counts (j = k-1 >= 1):
        n = 7^j        : 3 free (t = 1,2,3 -> g = 7,14,21)
        n = 2*7^j      : 1 free (t = 4 -> g = 14)
        n = 5*7^j      : 1 free (t = 5 -> g = 7)
    Per-level inner density: 3/7^j*(1/7)... total free 7-adic density
        sum_j (3 + 1/2 + 1/5) / 7^j = 3.7 / 6 = 0.61666...  < 1.

(B) Safe new-prime moduli (prime factor >= 97, never used by Owens):
    any inner n divisible by such a prime, with mu(n) = number of g | 42
    with gcd(n*g,42) = g and n*g >= 43 realizations (up to 8).

So the patch reduces to: cover Z by (A)-classes (density 0.6167 max)
plus a covering of the remainder using inner moduli with min modulus 97
and multiplicity <= 8 (regime B).  This script measures greedy progress.
"""

from itertools import count

SAFE_PRIMES = [97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149,
               151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
               211, 223, 227, 229, 233, 239, 241, 251]


def mu(n):
    """free realizations of inner n when n's only Owens-collision risk is
    the gcd condition (true when n has a prime >= 97)."""
    from math import gcd
    c = 0
    for g in (1, 2, 3, 6, 7, 14, 21, 42):
        if gcd(n * g, 42) == g and n * g >= 43:
            c += 1
    return c


def greedy_measure(J=3, primes=SAFE_PRIMES, verbose=True):
    """Exact uncovered-fraction accounting.

    Step 1: apply the (A) 7-adic structure for levels 1..J, nested so that
    each level's classes sit inside the previous remainder:
      level j covers, inside each remaining branch cell, the fractions
      3/7 (n=7^j), and within one remaining 7-cell the 2- and 5-slivers.
    Exact per-level remainder factor: 1 - 3/7 - 1/14 - 1/35 = 33/70 for
    j = 1; for j >= 2 the 2/5-slivers no longer align cleanly, so we use
    the conservative 4/7 factor plus the two slivers where they fit:
    remainder_j = remainder_{j-1} * 33/70 (optimistic alignment: the
    2- and 5-slivers CAN be re-aimed each level because the free moduli
    2*7^j and 5*7^j are independent classes; alignment inside remainder
    works iff remainder is a union of cells mod 7^j - true by induction
    when we only remove whole subcells; the slivers break this, so we
    report BOTH bounds).

    Step 2: cover remainder cells with regime-B moduli, multiplicity
    mu(n), greedily by density, and report the uncovered fraction.
    """
    from fractions import Fraction as F
    r_opt = F(1)
    r_con = F(1)
    for j in range(1, J + 1):
        r_opt *= F(33, 70)
        r_con *= F(4, 7)
    if verbose:
        print(f"(A) after {J} 7-adic levels: remainder in "
              f"[{float(r_opt):.6f}, {float(r_con):.6f}]")

    # (B): remainder is a union of cells mod 7^J (conservative view).
    # Cover one cell mod 7^J: it is a copy of Z; available inner moduli
    # for the cell: q, q^2, q*q', 2q, ... times 7^J -> multiplicity
    # mu(7^J * n_B) = 4 for n_B coprime to 42 (g must absorb the 7).
    # Wait: mu(7^J * q): g in {7,14,21,42} all satisfy gcd; 4 free.
    # Density available inside one cell from squarefree products of the
    # first P safe primes with towers:
    dens = F(0)
    used = 0
    # single primes with towers q^i and 2/3/5/7-smooth multipliers s
    # (s*7^J*q free as long as s*q has the >=97 prime: always). mu = 4
    # for each distinct actual modulus... enumerate n_B <= NCAP formed
    # from safe primes times {1..50} smooth part, density mu(n)/n each,
    # capped at full coverage per n (can't exceed with mu classes).
    NCAP = 10**7
    items = []
    smooth = [s for s in range(1, 200)
              if all(p in (2, 3, 5, 7) for p in _factor(s))]
    for q in primes:
        for i in (1, 2):
            base = q ** i
            if base > NCAP:
                break
            for s in smooth:
                n = base * s
                if n > NCAP:
                    break
                items.append(n)
        for q2 in primes:
            if q2 <= q:
                continue
            if q * q2 <= NCAP:
                for s in smooth:
                    n = q * q2 * s
                    if n > NCAP:
                        break
                    items.append(n)
    for n in sorted(set(items)):
        m = 4  # realizations of 7^J * n
        dens += F(m, n)
        used += m
        if dens >= 1:
            break
    print(f"(B) naive density budget inside one cell: "
          f"{float(dens):.4f} with {used} moduli "
          f"({'reaches' if dens >= 1 else 'BELOW'} 1)")
    return r_opt, r_con, dens


def _factor(n):
    f = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            f.add(d)
            n //= d
        d += 1
    if n > 1:
        f.add(n)
    return f


if __name__ == "__main__":
    for J in (1, 2, 3, 4, 6):
        greedy_measure(J)
        print()

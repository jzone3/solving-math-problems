#!/usr/bin/env python3
"""Independent, from-first-principles implementation of the BBMST distortion sieve
(Balister-Bollobas-Morris-Sahasrabudhe-Tiba, arXiv:1811.03547, Theorems 3.1 + 3.2),
written from the paper's statements (NOT ported from any other code base), to
independently certify the non-covering lemmas used for Erdos #273 (P18).

Theorem 3.1: let A = {A_d : d in D} be a finite collection of arithmetic progressions,
p_1 < ... < p_n the primes dividing Q = lcm(D), and delta_1, ..., delta_n in [0, 1/2].
With nu(m) = prod_{p_j | m} 1/(1 - delta_j) and N_i = {d in D : d | Q_i, d does not divide
Q_{i-1}} (moduli whose largest prime factor is p_i), Theorem 3.2 gives

    M_i^(1) <= A_i := sum_{d = m p_i^j in N_i}  p_i^{-j} nu(m)/m        (m | Q_{i-1}, j >= 1)
    M_i^(2) <= B_i := sum_{d1 = m1 p_i^{j1}, d2 = m2 p_i^{j2} in N_i}
                         p_i^{-(j1+j2)} nu(lcm(m1, m2)) / lcm(m1, m2)

and if  eta := sum_i min(A_i, B_i / (4 delta_i (1 - delta_i))) < 1  then A does NOT cover Z.

Soundness for a *pool* of moduli: every term is a sum of nonnegative contributions of
individual moduli (pairs), so for any subcollection A' of the pool, eta(A') <= eta(pool).
Distinct-moduli coverings from the pool are subcollections. Hence eta(pool) < 1 certifies
that NO covering system uses only moduli from the pool.

All certification arithmetic is exact (Fraction); floats are used only to *search* for good
deltas, which are then snapped to rationals with denominator 5040 and re-certified exactly.

Usage:
  python3 bbmst_independent.py L <L>          # pool = {m | L : m+1 prime >= 5}
  python3 bbmst_independent.py P <Pmax>       # pool = {p-1 : 5 <= p <= Pmax}  (Theorem A check)
"""
import sys
from fractions import Fraction
from math import gcd
from sympy import isprime, divisors, primerange, factorint

def eta_exact(pool, deltas, primes):
    """Exact eta for the pool given rational deltas (dict prime -> Fraction)."""
    fact = {d: factorint(d) for d in pool}
    def nu(m):
        r = Fraction(1)
        for q in factorint(m):
            r *= 1 / (1 - deltas[q])
        return r
    eta = Fraction(0)
    per_level = []
    for i, p in enumerate(primes):
        Ni = [d for d in pool if max(fact[d]) == p]
        if not Ni:
            per_level.append((p, None, None, Fraction(0)))
            continue
        A = Fraction(0)
        parts = []
        for d in Ni:
            j = fact[d][p]
            m = d // p**j
            parts.append((m, j))
            A += Fraction(1, p**j) * nu(m) / m
        B = Fraction(0)
        for (m1, j1) in parts:
            for (m2, j2) in parts:
                l = m1 * m2 // gcd(m1, m2)
                B += Fraction(1, p**(j1 + j2)) * nu(l) / l
        dlt = deltas[p]
        term = A if dlt == 0 else min(A, B / (4 * dlt * (1 - dlt)))
        eta += term
        per_level.append((p, A, B, term))
    return eta, per_level

def optimize(pool):
    """Coordinate-descent float search for deltas, then exact certification."""
    fact = {d: factorint(d) for d in pool}
    primes = sorted({q for d in pool for q in fact[d]})
    # float eta for speed
    def eta_float(dl):
        deltas = dict(zip(primes, dl))
        def nu(m):
            r = 1.0
            for q in factorint(m):
                r /= (1 - deltas[q])
            return r
        tot = 0.0
        for p in primes:
            Ni = [d for d in pool if max(fact[d]) == p]
            if not Ni:
                continue
            A = 0.0
            parts = []
            for d in Ni:
                j = fact[d][p]
                m = d // p**j
                parts.append((m, j))
                A += nu(m) / (m * p**j)
            B = 0.0
            for (m1, j1) in parts:
                for (m2, j2) in parts:
                    l = m1 * m2 // gcd(m1, m2)
                    B += nu(l) / (l * p**(j1 + j2))
            dlt = deltas[p]
            term = A if dlt <= 0 else min(A, B / (4 * dlt * (1 - dlt)))
            tot += term
        return tot
    import os, random
    n = len(primes)
    starts = [[0.25] * n]
    rng = random.Random(int(os.environ.get("SEED", "0")))
    for _ in range(int(os.environ.get("RESTARTS", "0"))):
        starts.append([rng.uniform(0, 0.5) for _ in range(n)])
    grid = [i / 40 for i in range(0, 21)]   # 0 .. 0.5
    def descend(dl0):
        dl, best = dl0[:], eta_float(dl0)
        for _ in range(6):
            improved = False
            for k in range(n):
                for g in grid:
                    trial = dl[:]
                    trial[k] = g
                    v = eta_float(trial)
                    if v < best - 1e-12:
                        best, dl = v, trial
                        improved = True
            if not improved:
                break
        # progressive refinement around the coarse optimum
        for step in (0.01, 0.002, 0.0004, 1 / 5040):
            for _ in range(4):
                improved = False
                for k in range(n):
                    for g in (dl[k] - 2 * step, dl[k] - step, dl[k] + step, dl[k] + 2 * step):
                        if not 0 <= g <= 0.5:
                            continue
                        trial = dl[:]
                        trial[k] = g
                        v = eta_float(trial)
                        if v < best - 1e-13:
                            best, dl = v, trial
                            improved = True
                if not improved:
                    break
        return dl, best
    dl, best = descend(starts[0])
    for s in starts[1:]:
        dl2, b2 = descend(s)
        if b2 < best:
            dl, best = dl2, b2
    # snap to /5040 rationals and certify exactly
    deltas = {p: Fraction(round(d * 5040), 5040) for p, d in zip(primes, dl)}
    for p in deltas:
        deltas[p] = min(max(deltas[p], Fraction(0)), Fraction(1, 2))
    eta, levels = eta_exact(pool, deltas, primes)
    return primes, deltas, eta, levels, best

def main():
    mode, arg = sys.argv[1], int(sys.argv[2])
    if mode == "L":
        pool = sorted(m for m in divisors(arg) if m > 1 and isprime(m + 1) and m + 1 >= 5)
        label = f"moduli dividing L={arg}"
    else:
        pool = sorted(p - 1 for p in primerange(5, arg + 1))
        label = f"pool {{p-1 : 5 <= p <= {arg}}}"
    print(f"{label}: |pool|={len(pool)} budget={float(sum(Fraction(1,m) for m in pool)):.5f}")
    primes, deltas, eta, levels, fbest = optimize(pool)
    print("deltas:", {p: str(deltas[p]) for p in primes})
    print(f"float-search eta ~ {fbest:.8f}; EXACT eta = {eta} = {float(eta):.8f}")
    if eta < 1:
        print(f"CERTIFIED (exact rationals): eta < 1 -> no covering system of Z uses only "
              f"moduli from this pool (each at most once, any residues). [{label}]")
    else:
        print("NOT certified: eta >= 1 (undecided by this sieve / these deltas)")

if __name__ == "__main__":
    main()

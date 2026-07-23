#!/usr/bin/env python3
"""
P15 V4 phase 8b: REFUTATION of the fresh-prime full-split patch
architecture (and consistency check against Hough's theorem).

Tempting scheme: after removing the unique modulus-42 congruence the
residual is one class H mod 42.  Split H mod 42C (C smooth) into C
sub-classes; for each sub-class B pick a fresh prime q and cover the q
children of B by q congruences with distinct moduli D*q, D | 42C
(child_r of B is CONTAINED in the class c_r mod D*q with c_r = B mod D,
r mod q -- that inclusion is real and machine-checked below).  Overlap
with the rest of Owens is allowed, moduli D*q are Owens-free (q >= 97).
If this worked it would iterate T -> T+1 forever, contradicting Hough's
theorem (min modulus <= 616,000).  The flaw is a CAPACITY/PRIME-RANGE
mismatch, quantified here:

  * per class B a prime q needs q distinct divisors D | 42C, so
        q <= tau(42C);
  * distinct primes are needed per class (each prime's divisor ladder
    D*q is used up by ~one class), and freeness vs Owens needs q >= 97;
  * hence at most  pi(tau(42C)) - pi(96)  classes are patchable, while
    the number of classes is C itself -- and C >= 2^(Omega(tau(42C)))
    grows exponentially in tau.  The scheme covers O(log C) of the C
    classes.  It can never close.

This restores the section-17 verdict against pure patch architectures
in a sharper, architecture-independent-looking form: exact closure
demands hole-CLASS concentration <= #usable fresh primes in
[97, tau(window)], while the corrected smooth fuel (0.936 < 1,
freefuel.py) guarantees a residual of measure >= 0.064 spread over
Omega(C) window classes.
"""
from math import gcd


def tau(n):
    t = 1
    d = 2
    while d * d <= n:
        e = 0
        while n % d == 0:
            n //= d
            e += 1
        t *= e + 1
        d += 1
    if n > 1:
        t *= 2
    return t


def divisors(n):
    ds = [1]
    d = 2
    while d * d <= n:
        if n % d == 0:
            e = 0
            m = n
            while m % d == 0:
                m //= d
                e += 1
            ds = [x * d**k for x in ds for k in range(e + 1)]
            n = m
        d += 1
    if n > 1:
        ds = [x * n**k for x in ds for k in range(2)]
    return sorted(set(ds))


def check_child_inclusion():
    """The per-child inclusion IS valid (that part of the scheme is
    sound): child of B under prime q is contained in a class mod D*q."""
    m0, C, q = 42, 60, 97
    beta = 5                       # class B = beta mod m0*C
    W = m0 * C
    ok = True
    ds = divisors(W)[:q]
    for r in range(q):
        D = ds[r % len(ds)]
        # c_r = CRT(beta mod D, r mod q)
        inv = pow(D % q, -1, q)
        c = beta + D * (((r - beta) * inv) % q)
        # verify child subset: sample x in child -> x in class c mod D*q
        for t in range(3):
            # x ≡ beta (mod W), x ≡ r (mod q)
            invW = pow(W % q, -1, q)
            x = beta + W * (((r - beta) * invW) % q) + W * q * t
            if x % (D * q) != c % (D * q):
                ok = False
    print(f"child-inclusion soundness (m0=42, C=60, q=97): "
          f"{'PASS' if ok else 'FAIL'}")
    return ok


def capacity_table():
    """The capacity flaw: classes C vs usable primes in [97, tau(42C)]."""
    def primes_in(a, b):
        return [n for n in range(a, b + 1)
                if n > 1 and all(n % i for i in range(2, int(n**0.5) + 1))]

    print("\n   C (classes)   tau(42C)   usable primes in [97,tau]   "
          "patchable/needed")
    for C in (60, 1260, 2520, 5040, 30240, 720720, 61261200):
        t = tau(42 * C)
        ps = primes_in(97, t)
        print(f"   {C:11d}   {t:8d}   {len(ps):3d} {ps[:6]}"
              f"{'...' if len(ps) > 6 else ''}"
              f"          {len(ps)}/{C}")
    print("\n=> patchable classes ~ pi(tau(42C)) = O(log C); needed = C.")
    print("   The fresh-prime full-split architecture NEVER closes -")
    print("   consistent with Hough (else T -> T+1 would iterate to")
    print("   arbitrarily large minimum modulus).")


if __name__ == "__main__":
    ok = check_child_inclusion()
    capacity_table()
    print("\nRESULT:", "refutation established (soundness PASS + "
          "capacity shortfall demonstrated)" if ok else "CHECK FAILED")

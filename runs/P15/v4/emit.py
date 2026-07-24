#!/usr/bin/env python3
"""
P15 V4 phase 15: residue-level EMITTER for the Nielsen/Owens arrow
calculus - the sound validation route identified in phase 14.

Semantics (Nielsen JNT 2009, sec. 2):
  * a "system" is a finite list of congruences (r, n) covering Z;
  * q^(a_1..a_{q-1}) at depth n with auxiliary integer p (coprime to q):
      - level k = 1..n: for j = 1..q-1, input a_j is placed on the class
        (j*q^(k-1) + prev) (mod q^k)  [the recursion class shifts by the
        surviving child each level; we use child 0 as survivor so the
        level-k classes are j*q^(k-1) (mod q^k) relative to the branch];
      - the last hole 0 (mod q^n) is filled with p classes:
        j (mod p) intersect 0 (mod q^(n+1-j)) ... following Nielsen's
        Example 1: classes j (mod p) ∩ q^(n-j') style; we implement the
        exact variant from his worked example: for j = 1..p, the class
        j (mod p) ∩ 0 (mod q^(n+1-j))  restricted inside 0 (mod q^n)
        needs n >= p-1; moduli p*q^(n+1-j)... to keep moduli distinct
        and the code simple we use his form: cover 0 (mod q^n) by
        j (mod p) ∩ 0 (mod q^(n exponent decreasing)).

Implementation detail: placing a system S (covering Z) on a class
(c mod M) yields {(c + M*r, M*n) for (r, n) in S}.

The finitization of 0 (mod q^n): Nielsen's Example 1 covers 3^4 (mod 3^4)
by j (mod 5) ∩ 3^(5-j) (mod 3^(5-j)), j = 1..5.  In general we cover
0 (mod q^n) by, for j = 1..p:  the class congruent to 0 mod q^(n-j+1)
... we implement exactly: classes (j mod p) ∩ (0 mod q^(n+1-j)) for
j = 1..p with n >= p-1.  Their union contains 0 (mod q^n) because any x
in 0 (mod q^n) has x ≡ j (mod p) for some 1 <= j <= p, and
q^(n+1-j) | q^n | x when j >= 1.  (For j = p we use residue 0 mod p ...
we CRT-merge each pair into a single congruence.)

Verification: independent coverage check via the recursive CRT verifier
from solutions/P15/verify.py, plus modulus distinctness.
"""
import sys
import os
from math import gcd

sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                "..", "..", "..", "solutions", "P15"))
from verify import covers  # noqa: E402


def crt(r1, n1, r2, n2):
    """Return (r, lcm) for the intersection, or None if empty."""
    g = gcd(n1, n2)
    if (r1 - r2) % g:
        return None
    l = n1 // g * n2
    # solve x = r1 mod n1, x = r2 mod n2
    m1 = n1 // g
    m2 = n2 // g
    inv = pow(m1 % m2, -1, m2) if m2 > 1 else 0
    t = ((r2 - r1) // g * inv) % m2 if m2 > 1 else 0
    return ((r1 + n1 * t) % l, l)


def place(system, c, M):
    """Place a Z-covering system on the class c (mod M)."""
    return [((c + M * r) % (M * n), M * n) for (r, n) in system]


def arrow(q, inputs, n, p):
    """q^(inputs) at depth n, finitized with auxiliary p (coprime to q).

    inputs: list of q-1 Z-covering systems.  Returns a Z-covering system.
    Survivor child at each level is 0 (mod q^k); input j covers the class
    j*q^(k-1) (mod q^k).
    """
    assert len(inputs) == q - 1
    assert n >= p - 1
    assert gcd(p, q) == 1
    out = []
    for k in range(1, n + 1):
        qk = q ** k
        for j in range(1, q):
            out += place(inputs[j - 1], j * q ** (k - 1), qk)
    # finitize hole 0 (mod q^n): for j = 1..p cover (j mod p) n (0 mod q^(n+1-j))
    for j in range(1, p + 1):
        e = n + 1 - j
        merged = crt(j % p, p, 0, q ** max(e, 0))
        assert merged is not None
        out.append(merged)
    return out


ONE = [(0, 1)]


def main():
    # Nielsen Example 1: S = 3^(1, 2^), with 2^ at p=5, n=5 and the outer
    # 3^ at p=5, n=4.
    C = arrow(2, [ONE], 5, 5)
    print(f"2^ (p=5, n=5): {len(C)} cosets; "
          f"covers Z: {covers(list(C))}; "
          f"distinct moduli: {len(set(m for _, m in C)) == len(C)}")
    S = arrow(3, [ONE, C], 4, 5)
    print(f"3^(1,2^) (p=5, n=4): {len(S)} cosets; "
          f"covers Z: {covers(list(S))}; "
          f"distinct moduli: {len(set(m for _, m in S)) == len(S)}")
    ok = covers(list(C)) and covers(list(S))
    dist = (len(set(m for _, m in S)) == len(S)
            and len(set(m for _, m in C)) == len(C))
    print()
    print("RESULT: " + ("residue-level emitter validated against "
          "Nielsen's worked examples (coverage + distinctness PASS)"
          if ok and dist else "FAIL"))


if __name__ == "__main__":
    main()

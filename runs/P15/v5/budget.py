"""Reciprocal-sum budget analysis for covering systems with min modulus >= N.

Necessary condition: if congruences a_i mod m_i (distinct m_i >= N) cover Z,
then sum 1/m_i >= 1.  If all moduli are p_k-smooth, the max available budget is
    B(X, N) = prod_{p <= X} p/(p-1)  -  sum_{m < N, m X-smooth} 1/m  - 1   (excluding m=1)
We compute the minimal prime bound X for which B >= 1, for N = 40, 42, 43, 50.
Everything in exact rationals.
"""
from fractions import Fraction
def primerange(a, b):
    sieve = bytearray([1]) * b
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(b ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(a, b) if sieve[i]]


def smooth_below(primes, N):
    """All primes-smooth integers in [2, N)."""
    vals = [1]
    for p in primes:
        new = []
        for v in vals:
            x = v * p
            while x < N:
                new.append(x)
                x *= p
        vals += new
    return sorted(v for v in set(vals) if v > 1)


def budget(primes, N):
    total = Fraction(1)
    for p in primes:
        total *= Fraction(p, p - 1)
    total -= 1  # exclude m=1
    for m in smooth_below(primes, N):
        total -= Fraction(1, m)
    return total


def main():
    allp = list(primerange(2, 200))
    for N in (40, 42, 43, 50):
        print(f"--- min modulus N = {N} ---")
        for k in range(1, len(allp) + 1):
            ps = allp[:k]
            b = budget(ps, N)
            if b >= 1:
                print(f"  budget crosses 1 at primes up to {ps[-1]} "
                      f"({k} primes): B = {float(b):.4f}")
                break
        # budget with the prime sets actually used in the literature
    for N, X, who in ((40, 103, "Nielsen 2009"), (42, 89, "Owens 2014"),
                      (43, 89, "hypothetical 43 w/ Owens primes"),
                      (43, 97, "hypothetical 43 w/ primes<=97"),
                      (43, 103, "hypothetical 43 w/ primes<=103"),
                      (43, 127, "hypothetical 43 w/ primes<=127")):
        ps = list(primerange(2, X + 1))
        b = budget(ps, N)
        print(f"N={N}, primes<= {X} ({who}): budget = {float(b):.4f} "
              f"(excess over 1: {float(b-1):+.4f})")


if __name__ == "__main__":
    main()

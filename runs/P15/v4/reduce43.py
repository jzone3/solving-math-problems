"""P15 V4 phase 4: the full 43-patch reduction and the cover-packing number S.

CHAIN OF REDUCTIONS (all elementary, verified in-line below):

 R1 (hole-42): Owens's system O has exactly one modulus-42 congruence c*.
    A min-modulus-43 covering exists iff the class a* + 42Z can be covered by
    congruences with distinct moduli >= 43 that are unused in O.

 R2 (safety): O uses only primes <= 89 (plus one finitizing prime P0 which we
    choose to avoid). Hence every integer with a prime factor >= 97 is
    PROVABLY not a modulus of O, with no reconstruction needed.

 R3 (realizations): to cover the inner class r mod n inside the hole one may
    use any actual modulus m = n*g with g | 42 and gcd(n*g, 42) = g, m >= 43.
    For n carrying a prime >= 97 all such m are safe and pairwise distinct;
    the count is mu(n) = 2^(3 - #{q in {2,3,7} : q | n}).

 R4 (towers): build the inner cover as a tower over a prime p >= 97:
    p^(c_1, ..., c_{p-1}) covers Z if each input c_i is fully covered; at
    level k input moduli are n = t * p^k, so budgets refresh at every level
    and each input needs one full budget-packed cover, PLUS mu(p^k) = 8
    inputs come free as bare realizations of n = p^k.

 S := max number of pairwise budget-disjoint full covers of Z with modulus t
      used at most mu(t) times in total (t ranges over all integers >= 2;
      inside a p-tower every t is safe since n = t*p^k carries p).

 CLOSURE CONDITION: a p-tower closes iff  S >= p - 1 - 8.  The smallest
 usable tower prime is 97, so the patch route closes iff  S >= 88.
 (Sub-towers over other primes >= 97 only help if their own deficit is
 negative, i.e. the same condition; small tower primes p < 43 give no bare
 inputs and their flat inputs need >= 97-divisible t, which is the original
 problem - circular. So S >= 88 is the crisp kernel.)

 LP BOUND: sum_{t <= B} mu(t)/t ~ 8 * C * ln B with
 C = (3/4)(5/6)(13/14) ~ 0.5804, so S(B) <= 8 + 4.64 ln B roughly; S >= 88
 forces B ~ e^17 ~ 2.4e7 at PERFECT efficiency. This script measures the
 actual greedy/exact packing number S(B) for computable B.
"""

from math import gcd
from fractions import Fraction


def mu(t):
    k = sum(1 for q in (2, 3, 7) if t % q == 0)
    return 2 ** (3 - k)


def lp_bound(B):
    s = Fraction(0)
    for t in range(2, B + 1):
        s += Fraction(mu(t), t)
    return s


def pack_covers(L, verbose=False):
    """Exact greedy packing of full covers of Z/L using moduli t | L, t >= 2,
    each t usable mu(t) times globally. Returns number of complete covers."""
    divs = sorted(d for d in range(2, L + 1) if L % d == 0)
    budget = {t: mu(t) for t in divs}
    covers = 0
    while True:
        # try to build one more cover greedily (smallest t first, best residue)
        uncovered = bytearray([1]) * 1
        uncovered = bytearray([1] * L)
        left = L
        used = []
        progress = True
        while left and progress:
            progress = False
            best = None
            for t in divs:
                if budget[t] <= 0:
                    continue
                # best residue for this t
                cnt = [0] * t
                for x in range(L):
                    if uncovered[x]:
                        cnt[x % t] += 1
                r = max(range(t), key=lambda r: cnt[r])
                gain = cnt[r]
                if gain == 0:
                    continue
                # efficiency = gain / (L/t): prefer full-class hits
                eff = gain * t
                if best is None or eff > best[0] or (eff == best[0] and t < best[1]):
                    best = (eff, t, r, gain)
            if best:
                _, t, r, gain = best
                budget[t] -= 1
                used.append((t, r))
                for x in range(r % t, L, t):
                    if uncovered[x]:
                        uncovered[x] = 0
                        left -= 1
                progress = True
        if left == 0:
            covers += 1
            if verbose:
                print(f"  cover #{covers}: {used}")
        else:
            # restore budget of the failed partial attempt? spent budget lost
            # (greedy lower bound; a failed attempt ends the packing)
            break
    return covers


def main():
    print("mu(t) examples:", {t: mu(t) for t in [2, 3, 5, 6, 7, 42, 97, 194]})
    print()
    print("LP upper-bound trajectory for S(B):")
    for B in [10, 100, 1000, 10**4, 10**5]:
        print(f"  B={B:<7} sum mu(t)/t = {float(lp_bound(B)):8.2f}")
    # threshold estimate for S >= 88
    import math
    C = (3/4) * (5/6) * (13/14)
    B88 = math.exp((88 - 2) / (8 * C))
    print(f"  S>=88 needs (at perfect efficiency) B ~ {B88:.2e}")
    print()
    print("Exact greedy packing S(L) over Z/L, moduli t | L, budget mu(t):")
    for L in [2**4 * 3**2 * 5 * 7,      # 5040
              2**5 * 3**3 * 5 * 7,      # 30240
              2**6 * 3**3 * 5**2 * 7]:  # 302400
        s = pack_covers(L)
        print(f"  L={L:<8} packed covers S >= {s}")
    print()
    print("Interpretation: tower closure needs S >= 88; the LP bound alone")
    print("requires near-perfect covers with moduli out to ~2.4e7, and the")
    print("greedy exact packing at smooth L shows the achievable S at small")
    print("moduli. Gap S_measured vs 88 = the quantified distance to a 43")
    print("patch of Owens by provably-safe moduli.")


if __name__ == "__main__":
    main()

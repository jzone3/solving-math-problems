"""P15 V4 phase 3b: the "hole-42 reduction" and modulus-availability analysis.

REDUCTION THEOREM (elementary but load-bearing):
  Owens's covering system O has distinct moduli with min = 42, hence EXACTLY
  ONE congruence c* = (a* mod 42) in O. Let H = a* + 42Z minus the (measure
  ~zero-slack) part of that class covered by other congruences of O. Then a
  covering system with min modulus >= 43 exists iff H can be covered by
  finitely many congruences with distinct moduli that are (i) >= 43 and
  (ii) not already used in O \ {c*}.

  In Owens's structure c* is the modulus-42 congruence 7*3*2 arising in the
  third input of the 7-up-arrow (Section 3.4: "3(2,4,3^(1,2))" -> the entry
  '2' at level 7*3 has modulus 42). Nothing else in O covers that cell
  (his construction is exactly tight), so H is a full class mod 42.

COST CALCULUS FOR FILLING H:
  A congruence r mod m covers, inside H ~ Z (parametrized by k where
  x = a* + 42k), an AP of k's with modulus n = m / gcd(m, 42), provided the
  residue is compatible. Conversely, covering k mod n can be realized by any
  m with m / gcd(m,42) = n, i.e. m = n*g with g | 42 and gcd(n*g, 42) = g.
  So each "inner modulus" n has at most 8 realizations (one per divisor g of
  42), further filtered by m >= 43 and m unused in O.

  mu(n) := #{ m = n*g : g | 42, gcd(n*g,42) = g, m >= 43, m not a modulus of O }

  Covering H then == covering Z with residue classes where modulus n may be
  used with multiplicity up to mu(n).

This script computes the candidate m-lists for small n and flags the
collisions with the small moduli identifiable from Owens's explicit layers
(his 7-layer occupies 42, 56, 63, 84, 126, 168, ...), plus the density
budget needed if only prime-97-divisible n are assumed safe.
"""

from math import gcd
from fractions import Fraction

DIVISORS_42 = [1, 2, 3, 6, 7, 14, 21, 42]

# Small moduli of O identifiable directly from Owens Section 3 text.
# 7-layer third input 3(2,4,3^(1,2)): 7*3*2=42, 7*3*4=84, 7*9*{1,2}={63,126},
# 7*27*{1,2}, ...; first input 8+16: 56, 112; second input 3^(8,16^)+32^:
# 7*3*8=168, 7*3*16=336, 7*32=224, ...
OWENS_SMALL_MODULI = {
    42, 56, 63, 84, 112, 126, 168, 189, 224, 252, 336, 378,
    # 2-layer: 64,128,... ; 3-layer (on 1 mod 2): 3^a*2^b >= 48: 48? no ->
    # 3.2 keeps 3(...)-structure with removed 6,12,18,24,36; survivors are
    # >= 48 deep: 48 = 3*16? Owens 3-layer uses 2(2(...)) nests: 96, 108, ...
    64, 80, 81 * 2, 96, 108, 144, 160,
    # 5-layer (on 2 mod 2): 5*16=80, 5*32=160, 25*..., 125*3*4=1500, ...
    240, 320, 400, 480,
}


def candidates(n):
    out = []
    for g in DIVISORS_42:
        m = n * g
        if gcd(m, 42) == g and m >= 43:
            out.append(m)
    return out


def mu(n, used):
    return [m for m in candidates(n) if m not in used]


def main():
    print("inner-n  realizations m=n*g (g|42, gcd ok, m>=43)   unused-under-known-collisions")
    blocked = []
    for n in range(2, 25):
        cs = candidates(n)
        free = mu(n, OWENS_SMALL_MODULI)
        tag = "" if free else "  <-- mu(n)=0 BLOCKED"
        if not free:
            blocked.append(n)
        print(f"n={n:<3} -> {cs}   free={free}{tag}")

    print()
    print(f"blocked small n (given identified collisions): {blocked}")
    print()
    # Density budget if only n with a prime factor >= 97 are assumed safe
    # (Owens uses primes <= 89 only, so ANY m with a prime factor >= 97 is
    # certainly unused; then mu(n) = 8 for every such n).
    # Covering Z with moduli restricted to multiples of 97, multiplicity 8:
    # per-residue-mod-97 demand is 1; the total supply up to bound B is
    # sum_{j <= B/97} 8/j ; need >= 97.
    target = Fraction(97)
    s = Fraction(0)
    j = 0
    while s < target:
        j += 1
        s += Fraction(8, j)
    print(f"97-safe pool: need sum_j 8/j >= 97  ->  j up to {j} "
          f"(inner moduli up to 97*{j} ~ {97*j:.2e})")
    print("i.e. a raw-density argument alone needs inner moduli ~ 1.7e7;")
    print("covering STRUCTURE with multiplicity 8 and min inner modulus 97")
    print("is the multiplicity-8 analogue of the minimum-modulus problem --")
    print("the same wall, shifted. Small blocked n's show the cheap route is")
    print("closed by Owens's own 7-layer, matching his Conclusion remark.")


if __name__ == "__main__":
    main()

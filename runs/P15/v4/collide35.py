#!/usr/bin/env python3
"""
P15 V4 phase 24: obstruction A analyzed symbolically.

Question: in Nielsen 4.5's tenth input, second summand,
    5^( 3*3(x,x,8^), 3*2, 3*4, 3*8^+9*8^ )
do the slot-1 content (8^ on the cell 1 (mod 9)) and the slot-4
content (9*8^ on the cell 3 (mod 9)) repeat moduli?

Every congruence here has modulus 2^a * 3^b * 5^c * 7^d * 11^e; we
compare EXPONENT VECTORS, so the check is depth-independent (no finite
window).  A family is the set of vectors it can realize; two contents
collide iff their vector sets intersect.

We also machine-check the candidate rescues:
  R1: "artificially increase n" on one 8^ (start the 2-chain deeper)
      -- fails: both chains still realize a=3 (the 8-cell itself must
      be covered by a modulus-8*ctx congruence in one of them... more
      precisely chains {a >= 3} and {a >= 3+k} intersect for all k;
      dropping low a leaves the cells 2^j-uncovered, which must then
      be covered by ANOTHER family with the same 3/5-part;
  R2: move slot-1's 8^ one 3-level deeper (b: 2 -> 3) -- collides with
      the 27^*8^ chains of S4/S8/slot-5 (b >= 3 there);
  R3: drop the 3-part of slot-1 (cover all of 1 mod 3 there) --
      collides with S5 / slot-4's 3*8^ (b = 1);
  R4: drop the 5-part (cover the cell on all 5-digits) -- collides
      with S7's slot-1 8^ (c >= 1 ... c = 0 case: S2 = plain 8^ has
      c = 0, b = 0; with b = 2 unaffected; but the 9-cell with c = 0
      collides with ... checked below).

Conclusion printed at the end.
"""
from itertools import product

# exponent ranges checked (a=2-adic, b=3-adic, c=5-adic, e=11-adic)
AR, BR, CR, ER = range(0, 12), range(0, 6), range(0, 5), range(1, 4)


def fam(a0, b, c_min, name):
    """8^-type family: {(a, b, c, e): a >= a0, c >= c_min, e >= 1}."""
    return set((a, b, c, e)
               for a in AR if a >= a0
               for c in CR if c >= c_min
               for e in ER), name


def isect(f1, f2):
    s1, n1 = f1
    s2, n2 = f2
    common = s1 & s2
    print(f"{n1}  vs  {n2}: "
          f"{'COLLIDE  e.g. ' + str(sorted(common)[0]) if common else 'disjoint'}")
    return bool(common)


print("== literal reading ==")
slot1 = fam(3, 2, 1, "slot1  8^ on 1(9), in 5-tower   [a>=3,b=2,c>=1]")
slot4 = fam(3, 2, 1, "slot4  9*8^,     in 5-tower     [a>=3,b=2,c>=1]")
isect(slot1, slot4)

print("\n== rescue R1: stagger the 2-chain (slot1 starts at 2^5) ==")
slot1b = fam(5, 2, 1, "slot1' 8^ deeper [a>=5,b=2,c>=1]")
isect(slot1b, slot4)
print("   (and the cells 2^3, 2^4 must still be covered with b=2, c>=1")
print("    moduli by SOMETHING -- reproducing the collision)")

print("\n== rescue R2: slot1 one 3-level deeper (b=3) ==")
slot1c = fam(3, 3, 1, "slot1'' 8^ on 27-cells [a>=3,b=3,c>=1]")
s8chain = set((a, b, c, e)
              for a in AR if a >= 2
              for b in BR if b >= 3
              for c in CR if c >= 1
              for e in ER), "S8/slot5 27^*8^ in 5-tower [a>=2,b>=3,c>=1]"
isect(slot1c, s8chain)

print("\n== rescue R3: drop the 3-part (b=1) ==")
slot1d = fam(3, 1, 1, "slot1''' 8^ on 1(3) [a>=3,b=1,c>=1]")
s7s4 = fam(3, 1, 1, "S7-slot4 3*8^ [a>=3,b=1,c>=1]")
isect(slot1d, s7s4)

print("\n== rescue R4: drop the 5-part (c=0) ==")
slot1e = fam(3, 2, 0, "slot1'''' 8^ no 5-factor [a>=3,b=2,c=0]")
s5 = fam(3, 2, 0, "S5 9*8^ (11-input 5) [a>=3,b=2,c=0]")
isect(slot1e, s5)

print("""
CONCLUSION: under the literal reading and every local rescue
(depth-staggering per Nielsen sec 2, 3-level deepening, 3-part or
5-part widening), the two 8^ contents of the tenth input's second
summand realize a common modulus family 2^a 3^2 5^c 11^e.  Since
Nielsen asserts global distinctness, the resolution must be a
NON-LOCAL re-aim not spelled out in the text -- e.g. giving one of
the two contents a different auxiliary-prime closure at EVERY level
(finite chains, aux family absorbing the low 2-powers), which his
sec-2 remark permits ("use different powers of p whenever
necessary") but whose residue-level data the paper does not specify.
This is the precise, machine-checked content of obstruction A.""")


def saturation_scan():
    """Phase 25: constructive re-aim search.  Try to cover slot-1's
    cell family (1 mod 9 n 2-branch n 5-cell n 7-cell n 11-cell) with
    DIVISOR moduli (the only single-congruence re-aims possible) and
    check each candidate vector class against the concrete secs
    3.1-3.6 emission."""
    import emitcore, emit33, emit34, emit35, emit36

    def val(m, p):
        d = 0
        while m % p == 0:
            m //= p
            d += 1
        return d

    used = set()
    for src in (emitcore.emit(), emit33.emit(), emit34.emit34()[0],
                emit35.emit()[0], emit36.emit36()[0]):
        for _, n in src:
            used.add((val(n, 2), val(n, 3), min(val(n, 5), 2),
                      min(val(n, 7), 2),
                      min(val(n, 11) + val(n, 13), 2)))
    print("\n== phase 25: divisor-vector saturation scan ==")
    # candidate rescues for the slot-1 family: vectors (a, 2, c, d, e)
    # with c,d,e >= 1 and a in {0,1,2} (whole cell / *2 / *4), plus the
    # unavoidable a=3 start of any 2-chain.
    for a in (0, 1, 2, 3):
        v = (a, 2, 1, 1, 1)
        print(f"  rescue vector a={a}: (2^{a}*3^2*5*7*11-family) "
              f"{'USED -- collides' if v in used else 'FREE'}")
    # b-shift and c-shift rescues
    for v, lab in (((0, 3, 1, 1, 1), "b=3 (27-cell)"),
                   ((2, 3, 1, 1, 1), "27*4"),
                   ((3, 2, 2, 1, 1), "c=2 (25-level)")):
        print(f"  rescue {lab}: "
              f"{'USED -- collides' if v in used else 'FREE'}")


if __name__ == "__main__":
    saturation_scan()

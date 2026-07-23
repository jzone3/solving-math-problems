"""P15 V4 phase 5: a full COUNTING-LEVEL blueprint for T=43.

Goal: propagate the T=43 penalty (loss of the single modulus-42 congruence,
7*3*2, which pre-covered the '2'-part of the third 7-up-arrow input on the
whole 2 mod 2 branch) through ALL 12 Owens ledgers, repair each ledger using
(a) extra tower copies drawn from unused pool support and (b) the fresh
primes 97-113 (Owens's scheme stops at 89), and add a new section covering
the 42-hole itself.

Penalty model:
  * every 7-up-arrow copy on the 2 mod 2 branch whose stated 'need' relied on
    the third-input pre-cover pays +1 set per copy (the 2-part of 3(2,4,...)
    must now be filled by a pool set placed at level 7^k*3*m with m >= 15);
  * drop rules: for finishing prime P, drop seed sets s with P*s < 43
    (vs < 42) - only affects P = 41 (41*1 = 41 < 43: set 1 now dropped) and
    P = 42-composites (none are finishers);
  * sections on the 1 mod 2 branch (3.11) or using 7-savings from other
    sources (3.4's 9*4 for 3.11; 25-tricks in 3.15, 3.18) pay no penalty:
    those savings come from moduli 9*4 = 36-level structures at level >= 43
    once multiplied by 7^k... CAREFUL: 9*4 = 36 < 43! The §3.4 filler "9*4"
    has bare modulus 36 - ALSO ILLEGAL at T=43. Same for any helper with
    bare modulus in [42, 43): only 42 itself. Helpers 36 < 42 were already
    illegal at T=42 - Owens's 9*4 must therefore sit at level 7*9*4 = 252
    (inside the 7^), which is fine at 43 too. Only the literal modulus 42
    dies. (7*3*2 = 42 is the unique casualty: the only 89-smooth integer in
    [42, 43) is 42.)

Repair search per ledger: allow extra copies of any tower already legal in
the section (each copy consumes `need` sets of headroom in construction
order), and allow recruiting one new prime q in {97,...} as a final
splitter (61/67-style doubling: two new primes cover one extra hole,
q-tower filled with the section's full pool + doubling).

Output: a pass/fail table for the repaired T=43 blueprint plus the exact
extra-set requirements per section. This is COUNTING-LEVEL evidence (the
modulus-collision semantics of each repair still needs explicit-modulus
validation - NOTES 12d), not a witness.
"""

from branchgame import Ledger


def build_43():
    results = []

    # ---- 3.8 prime 19, T=43: three 7^ copies cost 6; repair = 2 extra 3^
    # copies fed by post-17^ pool sets (disjoint support from first five).
    L = Ledger("3.8 prime 19 (T=43, repaired)")
    L.seed(4, "1,2,4,8^")
    L.mul(5, "with 5 and 25^")
    L.fill(11, 1, 9)
    L.fill(3, 5, 2, "five 3^ copies (support: sets 1-10)")
    L.fill(13, 1, 12)
    L.fill(17, 1, 16)
    L.fill(3, 2, 2, "REPAIR: 2 extra 3^ copies (support: sets 11-14; "
           "3^k*m moduli new - needs explicit check)")
    L.fill(7, 3, 6, "penalty: 42-congruence dead -> need 6 each; 18 <= 19")
    L.finish(19, 18, 2, "20+... usable")
    results.append(L)

    # ---- 3.10 prime 29, T=43: the four 7^-combination sets used
    # 7^(_,_,x,...) - the 'x' in the third slot is the dead pre-cover:
    # +1 per combination set (4 sets) and +1 for the final B-set.
    L = Ledger("3.10 prime 29 (T=43, repaired)")
    L.seed(10)
    L.mul(5)
    L.mul(1, "25^ pair set")
    L.fill(17, 1, 16)
    L.mul(4, "four 7^-combination sets (each now needs +1 filler)")
    L.fill(3, 2, 2, "REPAIR: fillers for 4 combo sets + B-set: use 2 extra "
           "3^ copies as the +5 filler supply (support sets 17-20)")
    L.fill(11, 2, 10)
    L.fill(23, 1, 22)
    L.fill(13, 2, 12)
    L.fill(19, 2, 13)
    L.mul(1, "B-set (17^ with first sixteen)")
    L.finish(29, 28, 1)
    results.append(L)

    # ---- 3.11 prime 31: on 1 mod 2 branch; its 7-saving comes from 9*4
    # placed at level 7*36 >= 43: NO penalty. Unchanged from T=42 (PASS).
    L = Ledger("3.11 prime 31 (T=43, unchanged)")
    L.seed(14)
    L.fill(5, 3, 4)
    L.mul(1, "C")
    L.fill(7, 3, 5, "saving from 9*4 at level 252: legal at 43")
    L.mul(1, "C + 7^ combo")
    L.fill(11, 3, 7)
    L.fill(13, 2, 12)
    L.fill(17, 2, 13)
    L.fill(19, 1, 18)
    L.fill(23, 1, 22)
    L.fill(29, 1, 28)
    L.finish(31, 30, 1)
    results.append(L)

    # ---- 3.12 prime 37: 'only three inputs needed' on 8-hole branch came
    # from 3.4's fills; the third-input part relied on 42 -> need 4 per copy.
    L = Ledger("3.12 prime 37 (T=43, repaired)")
    L.seed(5)
    L.mul(4)
    L.mul(8)
    L.fill(25, 2, 1)
    L.fill(25, 2, 4, "REPAIR: two extra 25^ copies (conservative cost 4)")
    L.fill(7, 4, 4, "penalty: need 4 not 3 per copy; REPAIR: 4 copies not 6")
    L.fill(13, 2, 12)
    L.fill(19, 2, 13)
    L.fill(29, 1, 28)
    L.fill(31, 1, 30)
    L.fill(11, 3, 10)
    L.fill(17, 2, 16)
    L.fill(23, 1, 22)
    L.finish(37, 36, 1)
    results.append(L)

    # ---- 3.13 prime 41: T=43 drop rule change: 41*1 = 41 < 43 (was legal
    # headroom at 42? no: 41 < 42 too - unchanged); 7^ copies at full 5 with
    # third-input saving? Text: 'thirty sets fill six copies of 7^' = need 5
    # -> penalty +1 -> need 6.
    L = Ledger("3.13 prime 41 (T=43, repaired)")
    L.seed(4)
    L.mul(6, "3 and 9^")
    L.fill(11, 1, 10)
    L.fill(13, 1, 11)
    L.mul(12, "prime 5")
    L.mul(3, "25^")
    L.fill(19, 2, 13)
    L.fill(29, 1, 28)
    L.fill(7, 5, 6, "penalty: 6 per copy; REPAIR: 5 copies not 6")
    L.fill(31, 1, 30)
    L.fill(17, 2, 16)
    L.fill(37, 1, 36)
    L.fill(23, 2, 19)
    L.fill(3, 1, 2, "REPAIR: 1 extra 3^ copy to replace lost 6th 7^ set")
    L.finish(41, 40, 1)
    results.append(L)

    # ---- 3.14 prime 43: five 7^ copies at need 6 (penalty).
    L = Ledger("3.14 prime 43 (T=43, repaired)")
    L.seed(4)
    L.mul(5)
    L.fill(11, 1, 9)
    L.mul(15)
    L.fill(3, 2, 2, "REPAIR: two extra 3^ copies")
    L.fill(7, 4, 6, "penalty need 6; REPAIR: 4 copies not 5")
    L.fill(31, 1, 30)
    L.fill(29, 1, 28)
    L.fill(17, 2, 16)
    L.fill(23, 1, 22)
    L.fill(37, 1, 30)
    L.fill(13, 3, 12)
    L.fill(19, 3, 13)
    L.finish(43, 42, 0, "43*1 = 43 >= 43 ok")
    results.append(L)

    # ---- 3.15 prime 47: 7^ saving here is the 25-trick (level 7*25 = 175
    # legal) -> NO 42-penalty on the special input, but the base 25 sets
    # include the §3.14 construction (already repaired independently).
    L = Ledger("3.15 prime 47 (T=43, unchanged)")
    L.seed(25)
    L.mul(7, "7^/25^ trick (levels >= 175: legal)")
    L.fill(17, 2, 16)
    L.fill(29, 1, 28)
    L.fill(31, 1, 30)
    L.fill(13, 3, 12)
    L.fill(19, 3, 13)
    L.fill(41, 1, 40)
    L.fill(43, 1, 42)
    L.fill(23, 2, 22)
    L.finish(47, 46, 0)
    results.append(L)

    # ---- 3.16 prime 53: 'third 7-input already covered' - dead saving:
    # six 7^ copies at need 6 instead of 5.
    L = Ledger("3.16 prime 53 (T=43, repaired)")
    L.seed(4)
    L.mul(4)
    L.mul(16)
    L.fill(125, 2, 1)
    L.fill(125, 2, 1, "REPAIR: two extra 125^ copies")
    L.fill(19, 2, 13)
    L.fill(29, 1, 28)
    L.fill(31, 1, 29)
    L.fill(7, 5, 6, "penalty: need 6; REPAIR: 5 copies not 6")
    L.fill(13, 3, 12)
    L.fill(37, 1, 36)
    L.fill(11, 4, 10)
    L.fill(41, 1, 40)
    L.fill(43, 1, 42)
    L.fill(47, 1, 46)
    L.fill(23, 2, 22)
    L.fill(17, 3, 16)
    L.finish(53, 52, 0)
    results.append(L)

    # ---- 3.17 prime 59: 'only three 7-inputs needed' - the other three
    # savings: first input (8+16, level 7*8 = 56 legal), second (level >= 56),
    # third = dead -> need 4 per copy.
    L = Ledger("3.17 prime 59 (T=43, repaired)")
    L.seed(5)
    L.mul(7)
    L.mul(13)
    L.fill(25, 3, 1)
    L.fill(25, 3, 1, "REPAIR: three extra 25^ copies")
    L.fill(29, 1, 28)
    L.fill(23, 1, 22)
    L.fill(7, 8, 4, "penalty: need 4 not 3; REPAIR: 8 copies not 10")
    L.fill(41, 1, 40)
    L.fill(11, 4, 10)
    L.fill(43, 1, 42)
    L.fill(47, 1, 46)
    L.fill(37, 1, 36)
    L.fill(17, 3, 16)
    L.fill(13, 4, 12)
    L.fill(19, 3, 13)
    L.finish(59, 58, 0)
    results.append(L)

    # ---- 3.18 prime 61 (and 67/89 doubling): 7^ needs 2 -> 3 (its saving
    # cites 25(x,x,x,_,x) - legal - AND the third-input x - dead).
    L = Ledger("3.18 prime 61 (T=43, repaired)")
    L.seed(28)
    L.fill(29, 1, 28)
    L.fill(31, 1, 29)
    L.fill(7, 9, 3, "penalty: need 3 not 2")
    L.fill(19, 3, 13)
    L.fill(37, 1, 36)
    L.fill(41, 1, 40)
    L.fill(43, 1, 42)
    L.fill(23, 2, 22)
    L.fill(47, 1, 46)
    L.fill(17, 3, 16)
    L.fill(13, 4, 12)
    L.fill(53, 1, 52)
    L.fill(11, 6, 9)
    L.fill(59, 1, 58)
    L.finish(61, 60, 0)
    results.append(L)

    # ---- 3.19 primes 71/73: single 7^ at need 5 -> 6 (third-input saving).
    L = Ledger("3.19 prime 71 (T=43, repaired)")
    L.seed(5)
    L.mul(12)
    L.fill(7, 1, 6, "penalty; REPAIR: reorder after 3/9^ minting")
    L.fill(17, 1, 16)
    L.fill(19, 1, 18)
    L.fill(11, 2, 10)
    L.fill(13, 2, 11)
    L.mul(30)
    L.fill(53, 1, 52)
    L.fill(47, 1, 46)
    L.fill(43, 1, 42)
    L.fill(41, 1, 40)
    L.fill(59, 1, 58)
    L.fill(37, 1, 36)
    L.fill(31, 2, 30)
    L.fill(61, 1, 60)
    L.fill(23, 3, 21)
    L.fill(29, 3, 22)
    L.fill(67, 1, 66)
    L.finish(71, 70, 0)
    results.append(L)

    # ---- 3.20 primes 79/83: 7^ needs 2 -> 3 (same third-input reliance on
    # the 32-hole branch: '7^ only needs two inputs' cites 3.4 savings incl.
    # the dead one).
    L = Ledger("3.20 prime 79 (T=43, repaired)")
    L.seed(7)
    L.mul(7)
    L.fill(3, 3, 2, "REPAIR: three extra 3^ copies")
    L.fill(7, 4, 3, "penalty: need 3 not 2; REPAIR: 4 copies not 7")
    L.mul(26)
    L.fill(47, 1, 46)
    L.fill(17, 3, 16)
    L.fill(11, 5, 10)
    L.fill(29, 2, 28)
    L.fill(59, 1, 58)
    L.fill(53, 1, 52)
    L.fill(61, 1, 60)
    L.fill(31, 2, 30)
    L.fill(13, 5, 12)
    L.fill(67, 1, 66)
    L.fill(23, 3, 22)
    L.fill(19, 4, 18)
    L.fill(71, 1, 70)
    L.fill(73, 1, 72)
    L.finish(79, 78, 0)
    results.append(L)

    # ---- NEW SECTION: the 42-hole itself (class formerly covered by 7*3*2).
    # It lives on branch 2 mod 2, third 7-input, '2'-part of the 3-tuple:
    # branch = one class mod 7^k*3*2 at every level k >= 1 (an up-arrow's
    # worth of cells, like the 79/83 hole). Fill with new primes 97 + 101
    # (doubling): build the pool exactly as in 3.20 (same branch depth
    # structure: seeds 1,2,4,8,16^ on this branch; 3-classes: the sibling
    # inputs; 5 fully free here).
    # KEY STRUCTURAL FACT: in the 7-up-arrow, the third-input content
    # 3(2,4,3^(1,2)) recurs at every level k with moduli 7^k*3*m; only the
    # k = 1 instance of the '2' entry has modulus 42 < 43. So the 42-hole is
    # ONE FLAT CLASS mod 42 (matching the hole-42 reduction in hole42.py),
    # and deeper 2-, 3-, 5-, AND 7-structure inside it is entirely free.
    L = Ledger("NEW 42-hole via 97 (T=43)")
    L.seed(4, "1,2,4,8^ (deeper 2-chain inside the hole)")
    L.mul(6, "3 and 9^ (deeper 3-structure free)")
    L.mul(12, "7 and 49^ (deeper 7-levels free inside the k=1 cell!)")
    L.fill(11, 1, 10)
    L.fill(13, 1, 12)
    L.fill(17, 1, 16)
    L.fill(19, 1, 18)
    L.fill(23, 1, 22)
    L.fill(25, 3, 1, "25^ copies")
    L.mul(37, "5 and 25^ on 30 pre-5 sets")
    L.fill(29, 1, 28)
    L.fill(31, 1, 30)
    L.fill(37, 1, 36)
    L.fill(41, 1, 40)
    L.fill(43, 1, 42)
    L.fill(47, 1, 46)
    L.fill(53, 1, 52)
    L.fill(59, 1, 58)
    L.fill(61, 1, 60)
    L.fill(67, 1, 66)
    L.fill(71, 1, 70)
    L.fill(73, 1, 72)
    L.fill(79, 1, 78)
    L.fill(11, 8, 10, "extra 11^ copies (fresh support)")
    L.fill(13, 6, 12, "extra 13^ copies")
    L.fill(83, 1, 82)
    L.fill(89, 1, 88)
    L.finish(97, 96, 0, "97*1 = 97 >= 43: no drops")
    results.append(L)

    return results


if __name__ == "__main__":
    print("#### T=43 counting-level blueprint (penalties + repairs) ####\n")
    rs = build_43()
    ok = all(L.report() for L in rs)
    print(f"T=43 blueprint: {'ALL LEDGERS PASS (counting level)' if ok else 'DEFICITS REMAIN'}")

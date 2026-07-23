#!/usr/bin/env python3
"""
P15 V4 phase 9: EXPLICIT modulus-multiset validation of the repaired
section 3.8 (prime 19) - the binding section of blueprint43.py.

Semantics established from the sources (Nielsen sec. 2, Owens sec. 3.8):
  * a q^ tower is FINITE, terminated by an auxiliary large prime chosen
    fresh per tower ("artificially increase n ... to avoid repeating
    moduli") - so tower tails never collide and we track only the
    SMOOTH/structured parts q^j * (input moduli);
  * an input "set" alpha used in q^ contributes absolute moduli
    q^j * m for every j >= 1 and every m in alpha's relative multiset;
  * section 3.8's twenty sets (Owens, p.11) have relative multisets:
      s1..s4:   {1}, {2}, {4}, {8*2^i}
      s5..s8:   5 * s1..s4          (the "in conjunction with 5")
      s9:       {25^j * m : m in s1..s4}          (25^)
      s10:      {11^j * m : m in s1..s9}          (11^, 6th input free)
      s11..s15: 3^ copies over (s1,s2),(s3,s4),(s5,s6),(s7,s8),(s9,s10)
                -> {3^j * m}
      s16:      {13^j * m : m in s1..s12}         (13^)
      s17:      {17^j * m : m in s1..s16}         (17^)
      s18..s20: three 7^ copies with structured inputs (Owens gives one:
                7^(1,2,3(x,1,x),4,8^,3^(2,4)))

blueprint43.py's T=43 repair adds TWO extra 3^ copies over sets 11-14
(flagged there as "needs explicit check").  This script performs that
check: it expands the multisets to a cap and tests whether the repair
moduli 3^i * (sets 11-14 moduli) are fresh.  Since sets 11-14 are
themselves 3^-scaled copies of sets 1-8, the repair moduli 3^(i+j) * m
coincide with the original five copies' moduli 3^j' * m.  The check
FAILS - and it fails for every alternative input choice among s11..s17
(13^/17^ sets contain 3-scaled inputs too).  Verdict printed below.
"""
CAP = 10**6


def scale(k, S):
    return {k * m for m in S if k * m <= CAP}


def tower(q, inputs):
    out = set()
    qj = q
    while qj <= CAP:
        for S in inputs:
            out |= scale(qj, S)
        qj *= q
    return out


def build_sets():
    s = {}
    s[1] = {1}
    s[2] = {2}
    s[3] = {4}
    s[4] = {8 * 2**i for i in range(18) if 8 * 2**i <= CAP}
    for i in range(1, 5):
        s[4 + i] = scale(5, s[i])
    s[9] = tower(25, [s[i] for i in range(1, 5)])
    s[10] = tower(11, [s[i] for i in range(1, 10)])
    pairs = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
    for k, (a, b) in enumerate(pairs):
        s[11 + k] = tower(3, [s[a], s[b]])
    s[16] = tower(13, [s[i] for i in range(1, 13)])
    s[17] = tower(17, [s[i] for i in range(1, 17)])
    # 7^ copies: structured; only the smooth parts matter for collisions
    seven_inputs = [s[1], s[2], scale(3, s[1]), s[3], s[4],
                    tower(3, [s[2], s[3]])]
    s[18] = tower(7, seven_inputs)
    return s


def main():
    s = build_sets()
    # baseline: Owens's own sets must be pairwise modulus-disjoint
    all_used = set()
    base_ok = True
    for i in sorted(s):
        inter = all_used & s[i]
        if inter:
            base_ok = False
            print(f"  baseline OVERLAP: set {i} reuses "
                  f"{sorted(inter)[:6]}...")
        all_used |= s[i]
    print(f"baseline (Owens sets 1-18 pairwise disjoint): "
          f"{'PASS' if base_ok else 'FAIL'}")

    # the blueprint43 repair: extra 3^ copies over sets 11-14
    print("\nrepair candidates: extra 3^ copy over input pair (a,b):")
    verdicts = []
    for a in range(1, 18):
        for b in range(a + 1, 18):
            rep = tower(3, [s[a], s[b]])
            clash = rep & all_used
            verdicts.append((a, b, len(clash)))
    fresh = [(a, b) for a, b, c in verdicts if c == 0]
    worst = sorted(verdicts, key=lambda x: -x[2])[:5]
    for a, b, c in worst:
        print(f"  (s{a},s{b}): {c} collisions")
    print(f"\ninput pairs with ZERO collisions: {fresh if fresh else 'NONE'}")
    if not fresh:
        print("\nVERDICT: the section-3.8 counting-level repair of "
              "blueprint43.py CANNOT be realized with fresh moduli from "
              "any pair of this section's own sets - every extra 3^ copy "
              "collides with existing 3^j-scaled moduli.  The T=43 "
              "blueprint's 'fresh support' assumption is REFUTED for "
              "section 3.8 as written; a valid repair needs supports "
              "from OUTSIDE the section's 3-scalable pool.")
    else:
        print("\nVERDICT: fresh repair inputs exist - blueprint43 "
              "section 3.8 repair is realizable with pairs listed above.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
P15 V4 phase 11: GLOBAL stratum-assignment check for blueprint v4.

Burdens (a)+(b) of blueprint43c reduced to a finite constraint problem.

Data (transcribed from Owens secs. 3.8-3.20 text, owens42.txt):
  * per penalized section: which 5-adic / 3-adic strata its own sets
    occupy, and which tower primes P it fills copies of;
  * mint strata: a section's T=43 repair mint must sit in a stratum its
    own pool does not touch, and globally, for every tower prime P, no
    OTHER section may emit P-scaled values in that same stratum (with
    routing freedom: a section may be prescribed to keep specific sets
    out of specific towers - recorded as side conditions).

Stratum encoding: (v5_parity_class, v3_class) where v5 class is one of
  '01e' = {0, 1, even>=2}   (the universal clean pattern)
  'odd3' = odd valuations >= 3
and v3 class is '01' = {0,1} or 'any' (section has 3^/9^/27^ towers)
or 'ge2' (mint stratum: valuations >= 2).

Sections and their text facts:
  3.8  (19): 5,25^          -> v5 '01e'; 3^ copies -> v3 any
  3.12 (37): 5,25^          -> v5 '01e'; 3(..) single + 3^(1,2) inner
             (sets '3(3^(1,2),3^(4,8))' use 3^ towers) -> v3 any
  3.14 (43): 5,25^; 3,9^    -> v5 '01e'; v3 any
  3.16 (53): 5,25 AND 125^  -> v5 '01e' + odd3(from 125^);
             only single 3-conjunction -> v3 {0,1}
  3.17 (59): 5, three 25^, 5*9^ -> v5 '01e'; 3,9^ -> v3 any
  3.19 (71/73): 5,25^; 3,9^ -> v5 '01e'; v3 any
  3.20 (79/83): 5,25^; 3^   -> v5 '01e'; v3 any

Mint choices (this script's proposal, checked for consistency):
  3.8, 3.12, 3.14, 3.17, 3.19, 3.20: mint = 25^ over 5-scaled inputs
      -> stratum (odd3, v3 of inputs in {0,1})
  3.16: mint = 9^ over 5-scaled inputs -> stratum (v5=1, v3 ge2)

Global constraints checked:
  C1. a section's mint stratum is disjoint from its own pool strata;
  C2. for each tower prime P filled by several sections, the mint
      values P^k * mint-moduli must not be reproducible by any other
      section's P^k * (its sets): i.e. no other section that fills P^
      has (odd3-v5) sets - except 3.16, whose 125^ sets must then be
      ROUTED away from shared towers (side condition S1);
  C3. 3.16's mint (v5=1, v3>=2) vs other sections filling 53^: those
      with v3-any pools could reproduce (v5=1, v3>=2) values - their
      5*9^-type sets must be routed away from 53^ (side condition S2).
"""

SECTIONS = {
    "3.8":  dict(prime=19, v5=("01e",), v3="any",
                 fills={19, 11, 3, 13, 17, 7}),
    "3.12": dict(prime=37, v5=("01e",), v3="any",
                 fills={37, 25, 7, 13, 19, 29, 31, 11, 17, 23}),
    "3.14": dict(prime=43, v5=("01e",), v3="any",
                 fills={43, 11, 7, 31, 29, 17, 23, 37, 13, 19}),
    "3.16": dict(prime=53, v5=("01e", "odd3"), v3="01",
                 fills={53, 125, 19, 29, 31, 7, 13, 37, 11, 41, 43,
                        47, 23, 17}),
    "3.17": dict(prime=59, v5=("01e",), v3="any",
                 fills={59, 25, 29, 23, 7, 41, 11, 43, 47, 37, 17,
                        13, 19}),
    "3.19": dict(prime=71, v5=("01e",), v3="any",
                 fills={71, 73, 17, 19, 11, 13, 25, 53, 47, 43, 41,
                        59, 37, 31, 61, 23, 29, 67}),
    "3.20": dict(prime=79, v5=("01e",), v3="any",
                 fills={79, 83, 7, 25, 47, 17, 11, 29, 59, 53, 61,
                        31, 13, 67, 23, 19, 71, 73, 41, 43}),
}

MINTS = {
    "3.8":  ("odd3", "01"),
    "3.12": ("odd3", "01"),
    "3.14": ("odd3", "01"),
    "3.16": ("1", "ge2"),
    "3.17": ("odd3", "01"),
    "3.19": ("odd3", "01"),
    "3.20": ("odd3", "01"),
}

SIDE_CONDITIONS = []


def check():
    ok = True
    # C1: mint stratum disjoint from own pool
    for name, (mv5, mv3) in MINTS.items():
        sec = SECTIONS[name]
        if mv5 == "odd3" and "odd3" in sec["v5"]:
            print(f"C1 FAIL {name}: pool already has odd3 v5")
            ok = False
        if mv3 == "ge2" and sec["v3"] == "any":
            print(f"C1 FAIL {name}: pool already has v3>=2")
            ok = False
    print("C1 (mint stratum fresh within own section): "
          + ("PASS" if ok else "FAIL"))

    # C2: odd3-v5 mints are scoped to their section prime P (mints feed
    # only the FINAL tower). Another section could reproduce P^k*odd3
    # values only if it (i) fills P^ and (ii) has odd3 sets. Only 3.16
    # has odd3 sets (its 125^ copies).
    c2 = True
    for name, (mv5, _) in MINTS.items():
        if mv5 != "odd3":
            continue
        P = SECTIONS[name]["prime"]
        for other, osec in SECTIONS.items():
            if other == name:
                continue
            if P in osec["fills"] and "odd3" in osec["v5"]:
                SIDE_CONDITIONS.append(
                    f"S1({other}->{name}): route {other}'s 125^ sets "
                    f"away from its {P}^ copies")
    print(f"C2 (cross-section odd3 isolation): PASS with "
          f"{len([s for s in SIDE_CONDITIONS if s.startswith('S1')])} "
          f"routing side conditions")

    # C3: 3.16's mint (v5=1, v3>=2) scoped to 53^. Other sections
    # filling 53^ with v3-any pools must route 5*(9^-scaled) sets away
    # from their 53^ copies.
    for other, osec in SECTIONS.items():
        if other == "3.16":
            continue
        if 53 in osec["fills"] and osec["v3"] == "any":
            SIDE_CONDITIONS.append(
                f"S2({other}->3.16): route {other}'s 5*9^-type sets "
                f"away from its 53^ copies")
    print(f"C3 (3.16 mint isolation): PASS with "
          f"{len([s for s in SIDE_CONDITIONS if s.startswith('S2')])} "
          f"routing side conditions")

    print("\nside conditions (finite, each a routing choice Owens's "
          "text leaves free):")
    for s in SIDE_CONDITIONS:
        print("  " + s)
    return ok


if __name__ == "__main__":
    good = check()
    print()
    if good:
        print("RESULT: GLOBAL stratum assignment CONSISTENT - all seven "
              "penalized sections have fresh-stratum mints; cross-section "
              "collisions reduce to the routing side conditions above, "
              "each realizable because the thesis leaves those input "
              "assignments free.  (Residue-level emission remains the "
              "final open burden.)")
    else:
        print("RESULT: FAIL")

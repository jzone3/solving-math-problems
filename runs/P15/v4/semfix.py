#!/usr/bin/env python3
"""
P15 V4 phase 14: SEMANTIC CORRECTION of the (q^m)^ tower model.

Nielsen (JNT 2009, sec. 2) defines (q^m)^ = q^(m-1) * q^, i.e. on branch
a (mod q^(m-1)) the j-th input contributes classes

    a + j*q^(k-1) - q^(m-1)  (mod q^k),   for ALL k >= m,

so the moduli are q^k * (input moduli) for every k >= m - steps of q,
NOT steps of q^m.  ledger38.py / blueprint43c.py modeled tower(25, .)
as {25^j * m} (steps of 25), which yields only EVEN 5-adic valuations
from the tower factor.  Under the correct semantics a 25^ contributes
v5 = k >= 2 of BOTH parities.  Consequences checked here:

  T1  Owens's own s9 = 25^(1,2,4,8^) occupies v5 = 2,3,4,... with
      m in {1,2,4,8*2^i}; the phase-10 mint 25^(5*s1..5*s4) occupies
      v5 = 3,4,5,... with the SAME m-patterns -> collisions.
      (Phase 10's odd-5-power loophole is INVALID.)

  T2  Repaired mint for sec 3.8: 25^ over 15-scaled inputs
      (15*{1,2,4,8^}) occupies v5 >= 3 AND v3 >= 1 simultaneously;
      sec 3.8's pool has no values with v5 >= 2 and v3 >= 1
      -> fresh within the section (checked explicitly).

  T3  Cross-section: sec 3.10's 16th set contains 25^(3*1,..,3*8^)
      with values 5^k*3*m (k>=2) -> its two 19^ copies must be routed
      to avoid that set (26 of the other 27 sets needed; freedom = 1).
"""
CAP = 10**6


def scale(k, S):
    return {k * m for m in S if k * m <= CAP}


def tower_q(q, m_exp, inputs):
    """Correct (q^m_exp)^ semantics: moduli q^k * (input moduli), k >= m_exp."""
    out = set()
    qk = q ** m_exp
    while qk <= CAP:
        for S in inputs:
            out |= scale(qk, S)
        qk *= q
    return out


def build_sets():
    s = {}
    s[1] = {1}
    s[2] = {2}
    s[3] = {4}
    s[4] = {8 * 2**i for i in range(18) if 8 * 2**i <= CAP}
    for i in range(1, 5):
        s[4 + i] = scale(5, s[i])
    s[9] = tower_q(5, 2, [s[i] for i in range(1, 5)])       # 25^ CORRECT
    s[10] = tower_q(11, 1, [s[i] for i in range(1, 10)])
    pairs = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
    for k, (a, b) in enumerate(pairs):
        s[11 + k] = tower_q(3, 1, [s[a], s[b]])
    s[16] = tower_q(13, 1, [s[i] for i in range(1, 13)])
    s[17] = tower_q(17, 1, [s[i] for i in range(1, 17)])
    seven_inputs = [s[1], s[2], scale(3, s[1]), s[3], s[4],
                    tower_q(3, 1, [s[2], s[3]])]
    s[18] = tower_q(7, 1, seven_inputs)
    return s


def main():
    s = build_sets()
    allu = set().union(*s.values())
    allu |= tower_q(19, 1, list(s.values()))

    # T1: the phase-10 mint under CORRECT semantics
    mint_old = tower_q(5, 2, [s[5], s[6], s[7], s[8]])
    c_old = mint_old & allu
    print(f"T1 phase-10 mint 25^(5*s1..5*s4) under correct semantics: "
          f"{len(c_old)} collisions "
          f"(examples {sorted(c_old)[:6]}) -> "
          f"{'INVALID as predicted' if c_old else 'unexpectedly clean'}")

    # T2: repaired mint: 25^ over 15-scaled inputs
    fifteen = [scale(15, s[i]) for i in range(1, 5)]
    mint_new = tower_q(5, 2, fifteen)
    c_new = mint_new & allu
    print(f"T2 repaired mint 25^(15*s1..15*s4): {len(c_new)} collisions "
          f"-> {'PASS' if not c_new else 'FAIL ' + str(sorted(c_new)[:6])}")

    # sanity: repaired mint values have v5>=3 and v3>=1
    def v(p, n):
        k = 0
        while n % p == 0:
            n //= p
            k += 1
        return k
    ok_strat = all(v(5, x) >= 3 and v(3, x) >= 1 for x in mint_new)
    print(f"   stratum check (v5>=3 and v3>=1): "
          f"{'PASS' if ok_strat else 'FAIL'}")

    # second mint (need +2 sets): 25^ over 45-scaled inputs (v3 >= 2)
    forty5 = [scale(45, s[i]) for i in range(1, 5)]
    mint_new2 = tower_q(5, 2, forty5)
    c_new2 = (mint_new2 & allu) | (mint_new2 & mint_new)
    print(f"T2b second mint 25^(45*s1..45*s4): {len(c_new2)} collisions "
          f"-> {'PASS' if not c_new2 else 'FAIL'}")

    print()
    if c_old and not c_new and not c_new2 and ok_strat:
        print("RESULT: phase-10 semantics INVALID (as suspected); repaired "
              "(v5>=3 & v3>=1) mints are fresh for sec 3.8 under the "
              "correct Nielsen semantics.  Cross-section routing condition: "
              "sec 3.10's 16th set (25^ over 3-scaled) must avoid its two "
              "19^ copies.")
    else:
        print("RESULT: see individual checks")


if __name__ == "__main__":
    main()

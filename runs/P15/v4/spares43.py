#!/usr/bin/env python3
"""
P15 V4 phase 12: burden (b) - freshness of the spare-set instantiations
on the four relocated cells {84, 126, 168, 504}.

Mechanism: the re-aim (blueprint43b) steals four Owens moduli
{84,126,168,504}; their original cells become holes of total measure
1/36.  The T=43 ledgers carry 12 spare covering sets; four are donated
(from sections with slack, avoiding 3.16) and aimed at these cells.

Instantiation: each donated spare set is built as an odd-5-stratum mint
(25^ tower over 5-scaled inputs) inside its donor section (final prime
P in {19, 29, 61}), then aimed at cell a (mod c), c in
{84,126,168,504}.  Its absolute moduli are then

        c * P^k * 5^(2j+1) * m     (m 2/3-smooth, j>=1, k>=1).

Freshness argument (machine-checked below):
  * all four cell moduli c are 5-free, so v5 of every spare modulus is
    odd and >= 3;
  * Owens's ONLY moduli with odd v5 >= 3 are (i) sec 3.3/3.4's
    125-structures 5^(3j)*3^a*2^b - which carry NO prime factor >= 11,
    and (ii) sec 3.16's 53-scaled 125^ values - which carry the factor
    53;
  * spare moduli carry a factor P in {19,29,61} and no factor 53,
    hence cannot equal either family.  QED at the stratum level.

The script verifies the arithmetic facts underlying the argument
explicitly up to a cap.
"""

CAP = 10**7


def v(p, n):
    k = 0
    while n % p == 0:
        n //= p
        k += 1
    return k


def gen_smooth(primes, cap):
    vals = [1]
    for p in primes:
        out = []
        for x in vals:
            while x <= cap:
                out.append(x)
                x *= p
        vals = out
    return set(vals)


def main():
    cells = [84, 126, 168, 504]
    donors = [19, 29, 61, 61]

    # fact 1: cells are 5-free
    f1 = all(c % 5 for c in cells)
    print(f"F1 cells 5-free: {'PASS' if f1 else 'FAIL'}")

    # fact 2: spare moduli c*P^k*5^(2j+1)*m have odd v5 >= 3 and a
    # factor P>=11 distinct from 53
    spare = set()
    for c, P in zip(cells, donors):
        for k in (1, 2):
            for j in (1, 2):
                for m in sorted(gen_smooth((2, 3), 64)):
                    x = c * P**k * 5**(2*j+1) * m
                    if x <= CAP:
                        spare.add(x)
    f2 = all(v(5, x) >= 3 and v(5, x) % 2 == 1 and x % 53 for x in spare)
    print(f"F2 spare moduli odd v5>=3, no 53 factor "
          f"({len(spare)} values <= {CAP}): {'PASS' if f2 else 'FAIL'}")

    # fact 3: Owens's odd-v5 families cannot collide
    fam1 = set()  # 5^(3j)*3^a*2^b with 3j odd
    for j in (1, 3):
        for m in gen_smooth((2, 3), CAP // 5**(3*j) + 1):
            x = 5**(3*j) * m
            if x <= CAP:
                fam1.add(x)
    fam2 = set()  # 53^k * 5^(3j) * m, m 2/3-smooth, 3j odd
    for k in (1, 2):
        for j in (1,):
            for m in gen_smooth((2, 3), CAP // (53**k * 5**(3*j)) + 1):
                x = 53**k * 5**(3*j) * m
                if x <= CAP:
                    fam2.add(x)
    c1 = spare & fam1
    c2 = spare & fam2
    print(f"F3 spare vs Owens odd-v5 families: fam1 collisions="
          f"{len(c1)}, fam2 collisions={len(c2)}: "
          f"{'PASS' if not (c1 or c2) else 'FAIL'}")

    # fact 4: donor slack suffices avoiding 3.16 (slack table from the
    # T=43 ledgers, blueprint43d finishes)
    slack = {19: 2, 29: 2, 31: 1, 41: 1, 43: 1, 59: 1, 61: 3}  # no 53
    from collections import Counter
    need = Counter(donors)
    f4 = all(slack.get(P, 0) >= n for P, n in need.items())
    print(f"F4 donor slack (avoiding 3.16/53): {dict(need)} vs "
          f"{slack}: {'PASS' if f4 else 'FAIL'}")

    ok = f1 and f2 and not (c1 or c2) and f4
    print()
    print("RESULT: " + ("burden (b) discharged at the stratum level - "
          "spare-set instantiations on the relocated cells are globally "
          "fresh" if ok else "FAIL"))


if __name__ == "__main__":
    main()

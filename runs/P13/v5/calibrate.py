"""Calibrate our PMD semantics against published designs (Abel & Bennett,
Des. Codes Cryptogr. 40 (2006) 211-224, Lemmas 4.4 and 4.8).

If our check_pmd verifies the published (v,6,2)- and (v,6,3)-PMDs, our
t-apart encoding matches the literature's.
"""
from pmdlib import check_pmd, develop, multiply, INF

I = INF
ok_all = True


def run(name, blocks, v, lam):
    global ok_all
    ok, msg = check_pmd(blocks, v, 6, lam)
    print(f"{name}: {msg}")
    ok_all &= ok


# ---- lambda = 2 (Lemma 4.4) ----
# v=9: Z8 + inf, add only multiples of 2 (mod 8)
b9 = [(0, 6, 2, 5, 4, 3), (5, 1, 7, 6, 3, 4), (0, 2, 4, 3, 1, I),
      (5, 7, 1, 4, 2, I), (0, 1, 6, 2, 5, I), (5, 6, 3, 7, 2, I)]
run("(9,6,2) Z8+inf", develop(b9, 8, increments=[0, 2, 4, 6]), 9, 2)

# v=10: Z10, add only multiples of 2 (mod 10)
b10 = [(0, 2, 6, 5, 8, 1), (5, 3, 7, 6, 1, 4), (0, 2, 8, 6, 3, 9),
       (5, 1, 3, 7, 8, 6), (0, 7, 4, 9, 1, 6), (5, 2, 3, 8, 4, 7)]
run("(10,6,2) Z10", develop(b10, 10, increments=[0, 2, 4, 6, 8]), 10, 2)

# v=12: Z11 + inf, full development
b12 = [(0, 2, 5, 10, 9, I), (0, 4, 5, 7, 2, I), (0, 5, 4, 1, 10, 7),
       (0, 6, 7, 5, 8, 4)]
run("(12,6,2) Z11+inf", develop(b12, 11), 12, 2)

# v=15: Z14 + inf
b15 = [(0, 2, 7, 8, 3, I), (0, 4, 9, 12, 11, I), (0, 6, 4, 11, 7, 1),
       (0, 6, 10, 5, 2, 4), (0, 11, 12, 5, 13, 2)]
run("(15,6,2) Z14+inf", develop(b15, 14), 15, 2)

# v=16: Z16
b16 = [(0, 4, 10, 9, 12, 3), (0, 1, 6, 4, 15, 9), (0, 11, 8, 2, 1, 13),
       (0, 4, 12, 1, 10, 8), (0, 2, 4, 5, 1, 7)]
run("(16,6,2) Z16", develop(b16, 16), 16, 2)

# v=18: Z17 + inf
b18 = [(0, 1, 7, 12, 3, I), (0, 10, 13, 16, 14, I), (0, 8, 10, 2, 15, 11),
       (0, 2, 9, 6, 7, 1), (0, 4, 8, 7, 12, 5), (0, 7, 2, 13, 10, 8)]
run("(18,6,2) Z17+inf", develop(b18, 17), 18, 2)

# ---- lambda = 3 (Lemma 4.8) ----
# v=12: Z11 + inf
c12 = [(0, 3, 7, 4, 8, I), (0, 3, 2, 9, 8, I), (0, 5, 8, 9, 6, I),
       (0, 5, 1, 3, 9, 10), (0, 6, 4, 10, 9, 7), (0, 8, 10, 4, 2, 9)]
run("(12,6,3) Z11+inf", develop(c12, 11), 12, 3)

# v=18: Z17 + inf
c18 = [(0, 7, 9, 8, 12, I), (0, 6, 7, 4, 11, I), (0, 15, 8, 16, 11, I),
       (0, 1, 4, 9, 3, 11), (0, 5, 3, 6, 2, 16), (0, 5, 11, 2, 15, 10),
       (0, 13, 11, 3, 7, 1), (0, 2, 11, 15, 8, 3), (0, 9, 12, 14, 8, 7)]
run("(18,6,3) Z17+inf", develop(c18, 17), 18, 3)

print("ALL PASS" if ok_all else "SOME FAILED")

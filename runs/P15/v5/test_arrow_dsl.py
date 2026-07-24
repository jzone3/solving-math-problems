"""DSL vs the paper's worked examples."""
from arrow_dsl import Ctx, One, Split, Hole, Arrow, subcell


def cls(expr):
    ctx = Ctx(1)
    expr.eval(ctx, 0, 1)
    return ctx


# 2( , 2(2( , 1), )) = 6 (mod 8)
c = cls(Split(2, [None, Split(2, [Split(2, [None, One()]), None])]))
assert c.out == [(6, 8)], c.out
# 3( , 2(1, ), ) = 5 (mod 6)
c = cls(Split(3, [None, Split(2, [One(), None]), None]))
assert c.out == [(5, 6)], c.out
# 3( , , 2(2( , 1), )) = 3 (mod 12)
c = cls(Split(3, [None, None, Split(2, [Split(2, [None, One()]), None])]))
assert c.out == [(3, 12)], c.out

# 2^arrow with p=5, n=5: the set C in eq (1)
c = cls(Arrow(2, [One()], p=5, n=5))
want = {(1, 2), (2, 4), (4, 8), (8, 16), (16, 32),
        (96, 160), (32, 80), (8, 40), (4, 20), (0, 10)}
assert set(c.out) == want, sorted(c.out)

# Example 1: 3^arrow(1, 2^arrow) with outer p=5, n=4; inner 2^arrows p=5
ctx = Ctx(1)
Arrow(3, [One(), Arrow(2, [One()], p=5, n=5)], p=5, n=4).eval(ctx, 0, 1)
out = set(ctx.out)
assert (1, 3) in out and (3, 9) in out and (9, 27) in out and (27, 81) in out
# tails: j (mod 5) /\ 3^(5-j) (mod 3^(5-j))
for j in range(1, 6):
    m = 3 ** (5 - j) * 5
    found = [x for x in out if x[1] == m]
    assert found, (j, m)
# full verification: it must cover Z exactly when inner arrows get fresh mods
from math import gcd
lcm = 1
for _, m in ctx.out:
    lcm = lcm // gcd(lcm, m) * m
mods = [m for _, m in ctx.out]
assert len(set(mods)) == len(mods), "dup moduli in Example 1"
if lcm < 10 ** 7:
    unc = [x for x in range(lcm)
           if not any(x % m == r for r, m in ctx.out)]
    assert not unc, f"{len(unc)} uncovered, e.g. {unc[:5]}"
print("lcm", lcm, "classes", len(ctx.out))
print("ALL DSL TESTS PASS")

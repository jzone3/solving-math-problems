from arrow_dsl import Ctx
from fractions import Fraction
import nielsen40 as N
from symbolic import _subtract

ctx = Ctx(40)
N.sec41(ctx); N.sec42(ctx); N.sec43(ctx); N.sec44(ctx)
regions = N._materialize_regions(ctx, depth=5)
rem = [(1, 4)]
for r, m in regions:
    rem = _subtract(rem, r, m)
rem.sort(key=lambda c: c[1])
print(len(rem), "cells; total measure", float(sum(Fraction(1,m) for _,m in rem)*4))
from collections import Counter
print(Counter(m for _, m in rem))
for c in rem[:40]:
    print(c, "mod9:", c[0]%9, "mod27:", c[0]%27)

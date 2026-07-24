"""childN exp12: abstract W* statement (implies W1B for tree-like 2-balls):

For integer star config (x,y,dk,dl) with m_i=(y+sum dk)/x, m_j=(x+sum dl)/y,
z1=(s-2)^2+x m_i+y m_j-2xy, and premise arg44_e <= z1:
maximize  w = sum_k (t-y)(t+y-4) + y(m_j-y) + sum_k t*m_k - y*sum_k t
            + sum_l (u-x)(u+x-4) + x(m_i-x) + sum_l u*m_l - x*sum_l u
subject to, per i-side neighbor k of degree t:
  t*m_k integer, m_k >= (x+t-1)/t,
  arg44_ik = 2((x-1)^2+(t-1)^2+m_i m_k - x t) <= z1        [1-ball premise]
  (pendant t=1: m_k = x exactly, constraint must hold else vacuous)
Claim W*: w_max <= 0.
"""
import sys
from fractions import Fraction
from itertools import combinations_with_replacement as cwr

def side_max(ds, X, Y, mX, z1):
    """max of sum_k [(t-Y)(t+Y-4) + t(m_k - Y)] over caps; None if vacuous."""
    tot = Fraction(0)
    for t in ds:
        lo = Fraction(X + t - 1, t)
        cap = (Fraction(z1, 2) - (X - 1) ** 2 - (t - 1) ** 2 + X * t) / mX
        if t == 1:
            mk = Fraction(X)
            if cap < mk:
                return None
        else:
            # floor cap to multiples of 1/t
            mk = Fraction((cap * t).__floor__(), t)
            if mk < lo:
                return None
        tot += (t - Y) * (t + Y - 4) + t * (mk - Y)
    return tot

def main(xmax, dmax):
    bad = []
    tot = 0
    wmaxall = None
    for x in range(1, xmax + 1):
        for y in range(1, x + 1):
            if x + y < 3:
                continue
            for dk in cwr(range(1, dmax + 1), x - 1):
                mi = Fraction(y + sum(dk), x)
                for dl in cwr(range(1, dmax + 1), y - 1):
                    mj = Fraction(x + sum(dl), y)
                    s = x + y
                    z1 = (s - 2) ** 2 + x * mi + y * mj - 2 * x * y
                    a44e = 2 * ((x - 1) ** 2 + (y - 1) ** 2 + mi * mj - x * y)
                    if a44e > z1:
                        continue
                    wi = side_max(dk, x, y, mi, z1)
                    if wi is None:
                        continue
                    wj = side_max(dl, y, x, mj, z1)
                    if wj is None:
                        continue
                    w = wi + wj + y * (mj - y) + x * (mi - x)
                    tot += 1
                    if wmaxall is None or w > wmaxall[0]:
                        wmaxall = (w, x, y, dk, dl)
                    if w > 0:
                        bad.append((x, y, dk, dl, w))
            print(f"x={x} y={y} bad={len(bad)} wmax={wmaxall}", flush=True)
    print("TOTAL bad:", len(bad), "of", tot)
    for b in bad[:100]:
        print(b)

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 6,
         int(sys.argv[2]) if len(sys.argv) > 2 else 10)

"""childN exp10: abstract star-config scan for the exceptional set of the
(B)/(W=) certificate.

Star config: x,y>=1, degree multisets dk (x-1 values), dl (y-1 values),
m_i=(y+sum dk)/x, m_j=(x+sum dl)/y.
Per-neighbor i-side contribution (m_k-free), from exp9:
  c_i(t) = [-t^3 + (m_i+x+2) t^2 + (rho/2 - (x-1)^2 - 1 - 4 m_i) t]/m_i
           + y(4 - m_j - y)
Q(rho) = sum_k c_i(d_k) + sum_l c_j(d_l) + (s-3)(z1 - rho)
window: arg44_e <= rho < z1 (nonempty iff arg44_e < z1_e <=> delta_e > 0).
R := Q(z1).  c_rho := 3 - s/2 - y/(2 m_i) - x/(2 m_j).
Exceptional iff (c_rho > 0 and R > 0) or (c_rho <= 0 and Q(arg44_e) >= 0).
Scan x,y <= XMAX, degrees <= DMAX, and report exceptional configs.
"""
import sys
from fractions import Fraction
from itertools import combinations_with_replacement as cwr

XMAX = 6
DMAX = 8

def Qparts(x, y, dk, dl):
    mi = Fraction(y + sum(dk), x)
    mj = Fraction(x + sum(dl), y)
    s = x + y
    z1 = (s - 2) ** 2 + x * mi + y * mj - 2 * x * y
    a44 = 2 * ((x - 1) ** 2 + (y - 1) ** 2 + mi * mj - x * y)
    if a44 >= z1:
        return None  # window empty: never heavy via own constraint
    def csum(ds, X, Y, mI, mJ):
        tot = Fraction(0)
        for t in ds:
            tot += (Fraction(-t**3 + (mI + X + 2) * t**2, 1)
                    + (Fraction(1, 2) * RHO_PLACE - (X - 1) ** 2 - 1 - 4 * mI) * t) / mI \
                   + Y * (4 - mJ - Y)
        return tot
    # build Q as affine in rho manually
    # coefficient of rho: sum_k d_k/(2 mi) + sum_l d_l/(2 mj) - (s-3)
    crho = Fraction(sum(dk), 1) / (2 * mi) + Fraction(sum(dl), 1) / (2 * mj) - (s - 3)
    # Q0 = Q(0):
    def c0(ds, X, Y, mI, mJ):
        tot = Fraction(0)
        for t in ds:
            tot += Fraction(-t**3 + (mI + X + 2) * t**2 - ((X - 1)**2 + 1 + 4*mI) * t, 1) / mI \
                   + Y * (4 - mJ - Y)
        return tot
    Q0 = c0(dk, x, y, mi, mj) + c0(dl, y, x, mj, mi) + (s - 3) * z1
    Qa = Q0 + crho * a44
    Rv = Q0 + crho * z1
    return mi, mj, z1, a44, crho, Qa, Rv

def main():
    exc = []
    for x in range(1, XMAX + 1):
        for y in range(1, x + 1):
            if x + y < 3:
                continue
            for dk in cwr(range(1, DMAX + 1), x - 1):
                for dl in cwr(range(1, DMAX + 1), y - 1):
                    r = Qparts(x, y, dk, dl)
                    if r is None:
                        continue
                    mi, mj, z1, a44, crho, Qa, Rv = r
                    bad = (crho > 0 and Rv > 0) or (crho <= 0 and Qa >= 0)
                    if bad:
                        exc.append((x, y, dk, dl, float(crho), float(Qa), float(Rv)))
    print(f"exceptional configs: {len(exc)}")
    for e in exc[:80]:
        print(e)

RHO_PLACE = None  # unused
if __name__ == "__main__":
    main()

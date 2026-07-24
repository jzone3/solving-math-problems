"""Fast float version of exp10 with exact Fraction recheck of near-exceptional
configs. Scan x >= y, degrees <= DMAX. Exceptional iff
(c_rho>0 and R>0) or (c_rho<=0 and Q(arg44_e)>=0), window nonempty (a44<z1)."""
import sys
from fractions import Fraction
from itertools import combinations_with_replacement as cwr

XMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 6
DMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 8

def parts(x, y, dk_sum, dk_sq, dk_cu, dl_sum, dl_sq, dl_cu, F=float):
    mi = F(y + dk_sum) / x
    mj = F(x + dl_sum) / y
    s = x + y
    z1 = (s - 2) ** 2 + x * mi + y * mj - 2 * x * y
    a44 = 2 * ((x - 1) ** 2 + (y - 1) ** 2 + mi * mj - x * y)
    if a44 >= z1:
        return None
    crho = F(dk_sum) / (2 * mi) + F(dl_sum) / (2 * mj) - (s - 3)
    Q0 = ((-dk_cu + (mi + x + 2) * dk_sq - ((x - 1) ** 2 + 1 + 4 * mi) * dk_sum) / mi
          + (x - 1) * y * (4 - mj - y)
          + (-dl_cu + (mj + y + 2) * dl_sq - ((y - 1) ** 2 + 1 + 4 * mj) * dl_sum) / mj
          + (y - 1) * x * (4 - mi - x)
          + (s - 3) * z1)
    Qa = Q0 + crho * a44
    Rv = Q0 + crho * z1
    return crho, Qa, Rv, z1, a44

def main():
    exc = []
    for x in range(1, XMAX + 1):
        for y in range(1, x + 1):
            if x + y < 3:
                continue
            dks = [(sum(d), sum(t * t for t in d), sum(t ** 3 for t in d), d)
                   for d in cwr(range(1, DMAX + 1), x - 1)]
            dls = [(sum(d), sum(t * t for t in d), sum(t ** 3 for t in d), d)
                   for d in cwr(range(1, DMAX + 1), y - 1)]
            for ks, kq, kc, dk in dks:
                for ls, lq, lc, dl in dls:
                    r = parts(x, y, ks, kq, kc, ls, lq, lc)
                    if r is None:
                        continue
                    crho, Qa, Rv, z1, a44 = r
                    bad = (crho > 1e-9 and Rv > -1e-6) or (crho <= 1e-9 and Qa >= -1e-6)
                    if bad:
                        re = parts(x, y, ks, kq, kc, ls, lq, lc, F=Fraction)
                        crho, Qa, Rv, z1, a44 = re
                        if (crho > 0 and Rv > 0) or (crho <= 0 and Qa >= 0):
                            exc.append((x, y, dk, dl, crho, Qa, Rv, z1, a44))
            print(f"x={x} y={y} done, exc so far {len(exc)}", flush=True)
    print(f"TOTAL exceptional: {len(exc)}")
    for e in exc:
        print(e)

if __name__ == "__main__":
    main()

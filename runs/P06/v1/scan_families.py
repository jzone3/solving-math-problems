"""
P06/V1: closed-form scans of star-like families for conjecture 129.

For each family we have closed-form formulas for
  dev^2 = Var(deg)+avgdeg    and    R = sum_{uv in E} 1/sqrt(d_u d_v)
in terms of the parameters (validated against the adjacency-based harness
for small parameters). We then sweep parameters to large n and report the
maximum of score = dev - R.
"""
import math
import sys

sys.path.insert(0, ".")
import harness as H


def dev_of_degcounts(pairs):
    # pairs: list of (degree, count)
    n = sum(c for _, c in pairs)
    m2 = sum(d * c for d, c in pairs)
    s2 = sum(d * d * c for d, c in pairs)
    var = (s2 + m2) / n - (m2 / n) ** 2
    return math.sqrt(max(var, 0.0))


# ---- closed forms: (name, param iterator, formula fn -> (dev, R, n), builder for x-check)

def f_star(n):
    dev = dev_of_degcounts([(n - 1, 1), (1, n - 1)])
    R = (n - 1) / math.sqrt(n - 1)
    return dev, R


def f_double_star(a, b):
    dev = dev_of_degcounts([(a + 1, 1), (b + 1, 1), (1, a + b)])
    R = a / math.sqrt(a + 1) + b / math.sqrt(b + 1) + 1 / math.sqrt((a + 1) * (b + 1))
    return dev, R


def f_spider(k, ell):
    if ell == 1:
        return f_star(k + 1)
    # center deg k, k*(ell-1) internal deg 2, k leaves deg 1
    dev = dev_of_degcounts([(k, 1), (2, k * (ell - 1)), (1, k)])
    R = k / math.sqrt(2 * k) + k * (ell - 2) / 2 + k / math.sqrt(2)
    return dev, R


def f_star_pp(kl, kp, ell):
    # kl leaves + kp paths of length ell (>=2) at center
    c = kl + kp
    dev = dev_of_degcounts([(c, 1), (1, kl + kp), (2, kp * (ell - 1))])
    R = kl / math.sqrt(c) + kp / math.sqrt(2 * c) + kp * (ell - 2) / 2 + kp / math.sqrt(2)
    return dev, R


def f_complete_split(n, k):
    # k dominating (deg n-1), n-k independent (deg k)
    dev = dev_of_degcounts([(n - 1, k), (k, n - k)])
    R = (k * (k - 1) / 2) / (n - 1) + k * (n - k) / math.sqrt((n - 1) * k)
    return dev, R


def f_pineapple(q, p):
    # v0: deg q-1+p ; q-1 clique vertices deg q-1 ; p pendants deg 1
    d0 = q - 1 + p
    dev = dev_of_degcounts([(d0, 1), (q - 1, q - 1), (1, p)])
    R = ((q - 1) * (q - 2) / 2) / (q - 1) + (q - 1) / math.sqrt(d0 * (q - 1)) + p / math.sqrt(d0)
    return dev, R


def f_kite(q, ell):
    # clique K_q + path of length ell at v0
    if ell == 0:
        d = [(q - 1, q)]
        R = (q * (q - 1) / 2) / (q - 1)
        return dev_of_degcounts(d), R
    d0 = q
    if ell == 1:
        dev = dev_of_degcounts([(d0, 1), (q - 1, q - 1), (1, 1)])
        R = ((q - 1) * (q - 2) / 2) / (q - 1) + (q - 1) / math.sqrt(d0 * (q - 1)) + 1 / math.sqrt(d0)
        return dev, R
    dev = dev_of_degcounts([(d0, 1), (q - 1, q - 1), (2, ell - 1), (1, 1)])
    R = ((q - 1) * (q - 2) / 2) / (q - 1) + (q - 1) / math.sqrt(d0 * (q - 1)) \
        + 1 / math.sqrt(2 * d0) + (ell - 2) / 2 + 1 / math.sqrt(2)
    return dev, R


def f_double_broom(ell, a, b):
    if ell < 2:
        raise ValueError
    da, db = a + 1 if ell > 1 else a + b, b + 1
    if ell == 2:
        dev = dev_of_degcounts([(a + 1, 1), (b + 1, 1), (1, a + b)])
        R = a / math.sqrt(a + 1) + b / math.sqrt(b + 1) + 1 / math.sqrt((a + 1) * (b + 1))
        return dev, R
    # ends deg a+1 / b+1, ell-2 internal deg 2, a+b leaves
    dev = dev_of_degcounts([(a + 1, 1), (b + 1, 1), (2, ell - 2), (1, a + b)])
    R = a / math.sqrt(a + 1) + b / math.sqrt(b + 1)
    if ell == 3:
        R += 1 / math.sqrt(2 * (a + 1)) + 1 / math.sqrt(2 * (b + 1))
    else:
        R += 1 / math.sqrt(2 * (a + 1)) + 1 / math.sqrt(2 * (b + 1)) + (ell - 3) / 2
    return dev, R


def xcheck():
    cases = [
        ("star", f_star(7), H.star(7)),
        ("dstar", f_double_star(4, 6), H.double_star(4, 6)),
        ("spider", f_spider(5, 3), H.spider(5, 3)),
        ("starpp", f_star_pp(6, 3, 4), H.star_pendant_paths(6, 3, 4)),
        ("csplit", f_complete_split(11, 4), H.complete_split(11, 4)),
        ("pine", f_pineapple(6, 9), H.pineapple(6, 9)),
        ("kite", f_kite(6, 5), H.kite(6, 5)),
        ("dbroom", f_double_broom(5, 3, 7), H.double_broom(5, 3, 7)),
    ]
    ok = True
    for name, (dev, R), adj in cases:
        dv, Rv = H.dev_eig(adj), H.randic(adj)
        if abs(dev - dv) > 1e-9 or abs(R - Rv) > 1e-9:
            ok = False
            print(f"XCHECK FAIL {name}: formula ({dev},{R}) vs graph ({dv},{Rv})")
    print("xcheck", "PASS" if ok else "FAIL")
    return ok


def sweep():
    best = []

    def rec(name, params, dev, R):
        best.append((dev - R, dev / R, name, params))

    for n in list(range(3, 1000)) + [10**4, 10**5, 10**6, 10**8]:
        rec("star", (n,), *f_star(n))
    for a in [1, 2, 3, 5, 10, 30, 100, 1000, 10**4, 10**5]:
        for b in [1, 2, 3, 5, 10, 30, 100, 1000, 10**4, 10**5]:
            rec("double_star", (a, b), *f_double_star(a, b))
    for k in [2, 3, 5, 10, 50, 200, 1000, 10**4, 10**5]:
        for ell in [1, 2, 3, 5, 10, 100, 1000]:
            rec("spider", (k, ell), *f_spider(k, ell))
    for kl in [0, 1, 5, 20, 100, 1000, 10**4]:
        for kp in [1, 2, 5, 20, 100, 1000]:
            for ell in [2, 3, 5, 20, 200]:
                rec("star_pp", (kl, kp, ell), *f_star_pp(kl, kp, ell))
    for n in [10, 30, 100, 300, 1000, 10**4, 10**5, 10**6]:
        for k in range(1, 60):
            if k < n:
                rec("csplit", (n, k), *f_complete_split(n, k))
        for frac in [0.1, 0.25, 0.5, 0.75, 0.9]:
            k = max(1, int(n * frac))
            rec("csplit", (n, k), *f_complete_split(n, k))
    for q in [3, 5, 10, 30, 100, 1000, 10**4]:
        for p in [1, 3, 10, 100, 1000, 10**4, 10**5, 10**6]:
            rec("pineapple", (q, p), *f_pineapple(q, p))
        for ell in [0, 1, 2, 5, 50, 1000]:
            rec("kite", (q, ell), *f_kite(q, ell))
    for ell in [2, 3, 4, 10, 100, 1000]:
        for a in [1, 5, 30, 300, 10**4]:
            for b in [1, 5, 30, 300, 10**4]:
                rec("double_broom", (ell, a, b), *f_double_broom(ell, a, b))

    best.sort(reverse=True)
    print("\ntop 25 by score = dev - R  (positive => counterexample):")
    for s, ratio, name, params in best[:25]:
        print(f"  {s:+.6f}  ratio={ratio:.6f}  {name}{params}")


if __name__ == "__main__":
    assert xcheck()
    sweep()

"""6-cell (3 left + 3 right) symmetric bipartite quotient perturbations.

Base: L_i -- R_j entry pattern with row sums d (bipartite d-regular => equality).
Entries: q[i][j] = base[i][j] + p[i][j], base rows summing to d built from small
integers u,v:  base = [[d-u-v, u, v], [u, d-u-v, v], [v, v, d-2v]] variants.
Symmetric 6x6 quotient => realizable (equal large even cell sizes).

Per-instance exact analysis (integer entries, series in eps = 1/d, exact
rational coefficients).  Random + structured sampling.  A candidate = all edge
gaps' leading coefficients <= 0 with max edge strictly negative.
"""
import itertools
import random
import sympy as sp
from perturb import d, eps, mu_series, edge_gap_series

random.seed(16)
ORDER = 3


def build(q):
    """q: 3x3 integer-in-d sympy entries for L_i x R_j block."""
    Z = sp.zeros(3, 3)
    Q = sp.Matrix(q)
    return sp.Matrix(sp.BlockMatrix([[Z, Q], [Q.T, Z]]))


def analyze_instance(q, tag):
    B = build(q)
    try:
        mu_s = mu_series(B, ORDER)
    except AssertionError as e:
        print(f"{tag}: SKIP ({e})")
        return None
    out = {}
    for bound in (44, 46):
        keys = []
        for (ij, g) in edge_gap_series(B, bound, mu_s, ORDER):
            coeffs = tuple(sp.Rational(sp.nsimplify(sp.expand(g).coeff(eps, k)))
                           for k in range(ORDER))
            keys.append((ij, coeffs))
        mx_ij, mx = max(keys, key=lambda t: t[1])
        lead = next((c for c in mx if c != 0), sp.Integer(0))
        out[bound] = (mx_ij, mx, lead)
        if lead < 0:
            print(f"{tag}: CANDIDATE bound {bound}: q={q} max edge {mx_ij} coeffs {mx}")
    return out


def main():
    n_neg = 0
    results = []
    # structured: u,v in small range, perturb one or two entries
    cases = []
    for u, v in [(1, 1), (2, 1), (1, 2), (2, 2), (3, 1)]:
        base = [[d - u - v, u, v], [u, d - u - v, v], [v, v, d - 2 * v]]
        for (i, j), delta in itertools.product(
                itertools.product(range(3), repeat=2), (-1, 1, 2)):
            q = [row[:] for row in base]
            q[i][j] = q[i][j] + delta
            cases.append((q, f"struct u={u} v={v} p[{i}][{j}]+={delta}"))
    # random small symmetric-in-pattern perturbations of several bases
    for k in range(80):
        u, v = random.randint(1, 3), random.randint(1, 3)
        base = [[d - u - v, u, v], [u, d - u - v, v], [v, v, d - 2 * v]]
        q = [[base[i][j] + random.randint(-2, 2) for j in range(3)] for i in range(3)]
        cases.append((q, f"rand#{k} u={u} v={v}"))
    for q, tag in cases:
        r = analyze_instance(q, tag)
        if r is None:
            continue
        summ = {b: (str(r[b][0]), [str(c) for c in r[b][1]]) for b in r}
        results.append((tag, summ))
        if any(r[b][2] < 0 for b in r):
            n_neg += 1
    print(f"\ndone: {len(results)} instances analyzed, {n_neg} candidates with "
          f"negative leading max-edge gap")


if __name__ == "__main__":
    main()

"""A subgroup of Aut(H_3) acting on the 63 secants, from semilinear maps of PG(2,9)
preserving the unital X^4+Y^4+Z^4=0: coordinate permutations (S_3), diagonal maps
diag(a,b,c) with a^4=b^4=c^4 (mod scalars), and the Frobenius x -> x^3.
Order 6 * 16 * 2 = 192.
"""
from itertools import product, permutations
from h3 import (ELTS, ZERO, ONE, mul, add, INV, normalize, secants, line_pts,
                unital_set, idx)

def frob(u):  # x -> x^3 on GF(9): (a+bx)^3 = a - b x  (char 3, x^2=-1 => x^3 = -x)
    return (u[0], (-u[1]) % 3)

FOURTH_ROOTS = [u for u in ELTS if u != ZERO and mul(mul(u, u), mul(u, u)) == ONE]
assert len(FOURTH_ROOTS) == 4

def apply_point(M, sigma, p):
    q = tuple(frob(c) for c in p) if sigma else p
    out = []
    for row in M:
        s = ZERO
        for m, c in zip(row, q):
            s = add(s, mul(m, c))
        out.append(s)
    return normalize(tuple(out))

def secant_perm(M, sigma):
    """Permutation of secant indices induced by point map (image of a line =
    line through images of two of its points)."""
    perm = {}
    pt_to_secants = {}
    for l in secants:
        pts = sorted(line_pts[l] & unital_set)[:2]
        imgs = [apply_point(M, sigma, p) for p in pts]
        # find the secant containing both images
        target = None
        for l2 in secants:
            if imgs[0] in line_pts[l2] and imgs[1] in line_pts[l2]:
                target = l2
                break
        assert target is not None
        perm[idx[l]] = idx[target]
    assert len(set(perm.values())) == 63
    return tuple(perm[i] for i in range(63))

def generate_group():
    perms = set()
    for pi in permutations(range(3)):
        for a, b in product(FOURTH_ROOTS, repeat=2):
            diag = [a, b, ONE]
            M = [[ZERO] * 3 for _ in range(3)]
            for r in range(3):
                M[r][pi[r]] = diag[r]
            for sigma in (0, 1):
                perms.add(secant_perm(M, sigma))
    return sorted(perms)

if __name__ == "__main__":
    g = generate_group()
    print("group elements:", len(g))

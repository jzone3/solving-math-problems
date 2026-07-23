"""Full automorphism group of H_3 acting on the 63 secants: PGammaU(3,3), order 12096.
Generators: the 192-element monomial subgroup from aut.py plus unitary matrices found by
random search (M preserving the Hermitian form h(x,y) = sum x_i y_i^3, i.e. M^T M^(3) = I
up to scalar), closed under composition (BFS).
"""
import random
from itertools import product
from h3 import ELTS, ZERO, ONE, mul, add
from aut import generate_group, secant_perm

def conj(u):  # x -> x^3
    return (u[0], (-u[1]) % 3)

def mat_mul(A, B):
    return [[sum_gf([mul(A[i][k], B[k][j]) for k in range(3)]) for j in range(3)]
            for i in range(3)]

def sum_gf(xs):
    s = ZERO
    for x in xs:
        s = add(s, x)
    return s

def is_unitary(M):
    # M^T * M^(3) == lambda * I for some scalar lambda != 0
    Mc = [[conj(M[i][j]) for j in range(3)] for i in range(3)]
    Mt = [[M[j][i] for j in range(3)] for i in range(3)]
    P = mat_mul(Mt, Mc)
    lam = P[0][0]
    if lam == ZERO:
        return False
    for i in range(3):
        for j in range(3):
            if P[i][j] != (lam if i == j else ZERO):
                return False
    return True

def find_unitary(rng, count):
    found = []
    nz = [e for e in ELTS]
    while len(found) < count:
        M = [[nz[rng.randrange(9)] for _ in range(3)] for _ in range(3)]
        if is_unitary(M):
            # skip monomial matrices (already have them)
            nonzeros = sum(1 for r in M for c in r if c != ZERO)
            if nonzeros > 3:
                found.append(M)
    return found

def full_group(verbose=False):
    base = set(generate_group())
    rng = random.Random(1)
    for M in find_unitary(rng, 3):
        for sigma in (0, 1):
            base.add(secant_perm(M, sigma))
    # BFS closure
    gens = list(base)
    group = set(gens)
    frontier = list(gens)
    while frontier:
        new = []
        for g in frontier:
            for h in gens:
                gh = tuple(g[h[i]] for i in range(63))
                if gh not in group:
                    group.add(gh)
                    new.append(gh)
        frontier = new
        if verbose:
            print(len(group), flush=True)
    return sorted(group)

if __name__ == "__main__":
    g = full_group(verbose=False)
    print("full group order:", len(g))

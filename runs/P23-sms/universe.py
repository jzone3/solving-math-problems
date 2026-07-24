"""Build a FIXED exact geometric point universe U for the constructive P23 search.

Design (see NOTES.md):
  U_k = all points reachable by <= k unit steps from the origin, where a "unit step"
  is one of a finite set D of exact unit vectors closed under the dihedral group D6
  (rotation by omega = e^{i pi/3} and complex conjugation).

  D = { omega^j : j=0..5 }                       (hexagonal / triangular-lattice steps)
    U { rho   * omega^j : j=0..5 }               (Moser-rotation steps, cos=5/6, sin=sqrt11/6)
    U { rhobar* omega^j : j=0..5 }               (conjugate, keeps D reflection-closed)

  omega = 1/2 + (sqrt3/2) i     rho = 5/6 + (sqrt11/6) i     both exact units.

Everything lives in the real multi-quadratic field Q(sqrt3, sqrt11) (primes (3,11)),
handled exactly by mfield.MField.  No floating point enters any decision; to_float is
only a prefilter for the O(n^2) edge scan.

Why this universe: the Moser spindle is
  {0, 1, omega, 1+omega, rho, rho*omega, rho*(1+omega)}
(the spindle-closing distance |(1+omega) - rho*(1+omega)| = 1 because cos(rot)=5/6).
Every one of those 7 points is a sum of <= 2 vectors from D, so the Moser spindle is a
subgraph of U_2 -- the REQUIRED sanity target (smallest 4-chromatic UDG).

Output: a pickle {points, edges, perms, primes} where
  points : list of (x,y), x,y field elements (tuples of Fractions over the 2^k basis)
  edges  : sorted list of (i,j) index pairs at exact unit distance
  perms  : list of index permutations for the D6 symmetries that map U_k onto itself
"""
import sys, os, pickle, math
from fractions import Fraction as F
from mfield import MField


def build_field():
    return MField((3, 11))


def unit_directions(fld):
    """The 18 exact unit steps, as (x,y) field-element pairs."""
    # basis order for primes (3,11): mask 0->1, 1->sqrt3, 2->sqrt11, 3->sqrt33
    def el(*pairs):
        v = [F(0)] * fld.N
        for mask, coef in pairs:
            v[mask] = F(coef)
        return tuple(v)

    one = fld.ONE
    zero = fld.ZERO
    omega = (el((0, F(1, 2))), el((1, F(1, 2))))          # 1/2 + sqrt3/2 i
    rho = (el((0, F(5, 6))), el((2, F(1, 6))))            # 5/6 + sqrt11/6 i
    rhob = (el((0, F(5, 6))), el((2, F(-1, 6))))          # conjugate
    e0 = (one, zero)                                      # 1 + 0 i

    def cmul(a, b):
        ax, ay = a
        bx, by = b
        rx = fld.sub(fld.mul(ax, bx), fld.mul(ay, by))
        ry = fld.add(fld.mul(ax, by), fld.mul(ay, bx))
        return (rx, ry)

    # rotations by omega^j applied to a seed
    def orbit(seed):
        out = []
        cur = seed
        for _ in range(6):
            out.append(cur)
            cur = cmul(cur, omega)
        return out

    dirs = []
    dirs += orbit(e0)      # omega^j
    dirs += orbit(rho)     # rho * omega^j
    dirs += orbit(rhob)    # rhobar * omega^j
    # dedupe exactly (some may coincide? they should not, but be safe)
    seen = {}
    uniq = []
    for d in dirs:
        if d not in seen:
            seen[d] = 1
            uniq.append(d)
    # sanity: all are unit vectors
    for d in uniq:
        n2 = fld.add(fld.mul(d[0], d[0]), fld.mul(d[1], d[1]))
        assert n2 == fld.ONE, ("non-unit direction", d)
    return uniq, omega


def build_ball(fld, dirs, k):
    """U_k: all sums of <= k directions from dirs, plus origin. Exact dedupe."""
    origin = (fld.ZERO, fld.ZERO)
    frontier = {origin}
    allpts = {origin}
    for _ in range(k):
        nf = set()
        for p in frontier:
            for d in dirs:
                q = (fld.add(p[0], d[0]), fld.add(p[1], d[1]))
                if q not in allpts:
                    allpts.add(q)
                    nf.add(q)
        frontier = nf
        if not frontier:
            break
    return sorted(allpts)


def compute_edges(fld, points):
    """Exact unit-distance edges. Float prefilter then exact norm2 == 1 confirm."""
    n = len(points)
    fx = [(fld.to_float(p[0]), fld.to_float(p[1])) for p in points]
    # bucket grid for prefilter
    cell = 1.0
    grid = {}
    for i, (x, y) in enumerate(fx):
        c = (int(math.floor(x / cell)), int(math.floor(y / cell)))
        grid.setdefault(c, []).append(i)
    edges = []
    ONE = fld.ONE
    for i, (x, y) in enumerate(fx):
        ci, cj = int(math.floor(x / cell)), int(math.floor(y / cell))
        cand = []
        for a in range(ci - 1, ci + 2):
            for b in range(cj - 1, cj + 2):
                cand += grid.get((a, b), [])
        for j in cand:
            if j <= i:
                continue
            dx = x - fx[j][0]
            dy = y - fx[j][1]
            d2 = dx * dx + dy * dy
            if abs(d2 - 1.0) > 1e-6:
                continue
            # exact confirmation
            n2 = fld.norm2(points[i], points[j])
            if n2 == ONE:
                edges.append((i, j))
    edges.sort()
    return edges


def symmetry_perms(fld, points):
    """Index permutations for D6 elements that map the point set onto itself."""
    idx = {p: i for i, p in enumerate(points)}

    def el(*pairs):
        v = [F(0)] * fld.N
        for mask, coef in pairs:
            v[mask] = F(coef)
        return tuple(v)

    omega = (el((0, F(1, 2))), el((1, F(1, 2))))

    def rot(p):  # multiply complex point by omega
        x, y = p
        rx = fld.sub(fld.mul(x, omega[0]), fld.mul(y, omega[1]))
        ry = fld.add(fld.mul(x, omega[1]), fld.mul(y, omega[0]))
        return (rx, ry)

    def conj(p):
        x, y = p
        return (x, tuple(-c for c in y))

    perms = []
    # 6 rotations, and 6 rotations composed with reflection
    for reflect in (False, True):
        for r in range(6):
            perm = []
            ok = True
            for p in points:
                q = conj(p) if reflect else p
                for _ in range(r):
                    q = rot(q)
                j = idx.get(q)
                if j is None:
                    ok = False
                    break
                perm.append(j)
            if ok and len(set(perm)) == len(perm):
                perms.append(perm)
    return perms


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    out = sys.argv[2] if len(sys.argv) > 2 else f"U_k{k}.pkl"
    fld = build_field()
    dirs, _ = unit_directions(fld)
    print(f"[universe] primes=(3,11) |D|={len(dirs)} k={k}")
    pts = build_ball(fld, dirs, k)
    print(f"[universe] |U_{k}| = {len(pts)} points")
    edges = compute_edges(fld, pts)
    print(f"[universe] {len(edges)} exact unit edges "
          f"(avg deg {2*len(edges)/max(1,len(pts)):.2f})")
    perms = symmetry_perms(fld, pts)
    print(f"[universe] {len(perms)} D6 symmetry permutations preserve U")
    with open(out, "wb") as f:
        pickle.dump({"points": pts, "edges": edges, "perms": perms,
                     "primes": (3, 11), "k": k}, f)
    print(f"[universe] wrote {out}")


if __name__ == "__main__":
    main()

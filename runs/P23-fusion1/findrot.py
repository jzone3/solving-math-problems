"""Which rotations do Heule's earlier graphs use?

Parts' universe is A u omega_4 B with A the lattice (a + b sqrt33 + i(c sqrt3 +
d sqrt11))/12 and omega_4 = (7 + i sqrt15)/8.  Heule's 510/517/529 sit entirely
inside it, but 553, 610, 633, 803, 826 and 874 do not: about half of 803's
points are in neither copy.  Those graphs therefore carry geometry that no pool
in this run has contained, and the rotation that produces it is worth knowing --
it is a new copy to add to the candidate universe.

Rotations of the form omega = (2t-1 + i sqrt(4t-1)) / (2t) stay in
Q(sqrt3, sqrt5, sqrt11) exactly when 4t-1 is one of 3, 5, 11, 15, 33, 55, 165,
i.e. t in {1, 3/2, 3, 4, 17/2, 14, 83/2}.  This tests all of them, their
conjugates and their squares, exactly.
"""
from fractions import Fraction as Fr

import mfield

F = mfield.MField([3, 5, 11])
MASK = {3: 1, 5: 2, 11: 4, 15: 3, 33: 5, 55: 6, 165: 7}


def elt(pairs):
    v = [Fr(0)] * 8
    for m, c in pairs.items():
        v[m] = c
    return tuple(v)


def cmul(a, b):
    (x, y), (u, v) = a, b
    return (F.sub(F.mul(x, u), F.mul(y, v)), F.add(F.mul(x, v), F.mul(y, u)))


def conj(a):
    return (a[0], tuple(-c for c in a[1]))


def in_lattice(p):
    x, y = p
    if any(x[m] for m in range(8) if m not in (0, 5)):
        return False
    if any(y[m] for m in range(8) if m not in (1, 4)):
        return False
    return all((12 * c).denominator == 1 for c in (x[0], x[5], y[1], y[4]))


def omega(r):
    """omega for 4t-1 = r, i.e. t = (r+1)/4."""
    t = Fr(r + 1, 4)
    return (elt({0: (2 * t - 1) / (2 * t)}), elt({MASK[r]: 1 / (2 * t)}))


ROTS = {}
for r in (3, 5, 11, 15, 33, 55, 165):
    w = omega(r)
    ROTS[f'w[{r}]'] = w
    ROTS[f'w[{r}]~'] = conj(w)
    ROTS[f'w[{r}]^2'] = cmul(w, w)
    ROTS[f'w[{r}]^2~'] = conj(cmul(w, w))

if __name__ == '__main__':
    import sys
    for name in sys.argv[1:] or ['553', '610', '633', '803', '826', '874']:
        g = mfield.load_vtx(F, f'/home/ubuntu/p23heule/vtx/{name}.vtx')
        base = [i for i, p in enumerate(g) if not in_lattice(p)]
        hits = []
        for lbl, w in ROTS.items():
            c = sum(1 for i in base if in_lattice(cmul(g[i], conj(w))))
            if c:
                hits.append((c, lbl))
        hits.sort(reverse=True)
        left = len(base) - sum(c for c, _ in hits[:1])
        print(f'{name}: {len(g)} pts, {len(base)} outside the base lattice; '
              f'best rotations {hits[:4]}')

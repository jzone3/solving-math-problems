"""Extract the translation that de Grey/Heule's earlier graphs use.

`findrot.py` showed 803/826/874 have ~half their points outside both A and
omega[15]A, yet all difference vectors of that outside part lie in
omega[15]*lattice, and all of them share one fractional offset: the outside part
is a **translated** rotated copy, T + omega[15]*A.  Parts' universe pins the
rotation centre at the origin, so this translation is a degree of freedom no
pool in this run has had.

Prints T exactly and saves it for pool construction.
"""
import pickle
from fractions import Fraction as Fr

import sympy as sp

import findrot as R
import mfield

F = R.F
W = R.ROTS['w[15]']


def lattice_part(u):
    """Split u = (x, y) into (lattice point, fractional remainder)."""
    x, y = u
    a = [Fr(0)] * 8
    b = [Fr(0)] * 8
    for m in (0, 5):
        a[m] = Fr(int(12 * x[m]), 12)
    for m in (1, 4):
        b[m] = Fr(int(12 * y[m]), 12)
    lat = (tuple(a), tuple(b))
    rem = (F.sub(x, tuple(a)), F.sub(y, tuple(b)))
    return lat, rem


def shift_of(name):
    g = mfield.load_vtx(F, f'/home/ubuntu/p23heule/vtx/{name}.vtx')
    out = [p for p in g
           if not R.in_lattice(p) and not R.in_lattice(R.cmul(p, R.conj(W)))]
    _, rem = lattice_part(R.cmul(out[0], R.conj(W)))
    T = R.cmul(rem, W)
    # every outside point must now sit in T + omega*lattice
    ok = sum(1 for p in out
             if R.in_lattice(R.cmul((F.sub(p[0], T[0]), F.sub(p[1], T[1])),
                                    R.conj(W))))
    return T, len(out), ok


if __name__ == '__main__':
    res = {}
    for name in ('803', '826', '874'):
        T, n, ok = shift_of(name)
        print(f'{name}: {ok}/{n} outside points in T + omega[15]*A with '
              f'T = ({sp.sstr(F.to_sympy(T[0]))}, {sp.sstr(F.to_sympy(T[1]))})',
              flush=True)
        res[name] = T
    pickle.dump(res, open('tshift.pkl', 'wb'))

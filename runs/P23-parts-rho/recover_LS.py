"""Recover Parts' L374 and S136 in integer lattice coordinates from the
509-vertex witness (solutions/P23/v509e2442.vtx): G509 = L374 union rho*S136,
rho = omega_4 = (7 + i sqrt15)/8, sharing the origin.

Validates: |L|=374, |S|=136, edges(L)=1860, edges(S)=564, cross edges = 18,
total = 2442, and every cross edge passes lattice.cross_is_unit(u, v, t=4).
Writes LS.pkl = {'L': [...tuples...], 'S': [...tuples...]}.
"""
import os
import pickle
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "solutions", "P23"))
import field  # noqa: E402
import lattice  # noqa: E402

# masks in field.py basis: bit0=3, bit1=5, bit2=11 -> 1:sqrt3 2:sqrt5 3:sqrt15 4:sqrt11 5:sqrt33
RHO_CONJ_RE = tuple(F(7, 8) if i == 0 else F(0) for i in range(8))
RHO_CONJ_IM = tuple(F(-1, 8) if i == 3 else F(0) for i in range(8))  # -sqrt15/8


def cplx_mul(pr, pi, qr, qi):
    return (field.sub(field.mul(pr, qr), field.mul(pi, qi)),
            field.add(field.mul(pr, qi), field.mul(pi, qr)))


def as_lattice(pr, pi):
    """(a,b,c,d) ints if z=(a+b s33+i(c s3+d s11))/12, else None."""
    vals = {}
    for name, vec, masks in (("re", pr, (0, 5)), ("im", pi, (1, 4))):
        for m in range(8):
            if vec[m] != 0 and m not in masks:
                return None
        for m in masks:
            x = vec[m] * 12
            if x.denominator != 1:
                return None
            vals[(name, m)] = int(x)
    return (vals[("re", 0)], vals[("re", 5)], vals[("im", 1)], vals[("im", 4)])


def main():
    base = os.path.join(os.path.dirname(__file__), "..", "..", "solutions", "P23")
    pts = field.load_vtx(os.path.join(base, "v509e2442.vtx"))
    L, S, idx = [], [], {}
    for k, (pr, pi) in enumerate(pts):
        p = as_lattice(pr, pi)
        if p is not None:
            L.append(p)
            idx[k] = ("L", p)
        else:
            qr, qi = cplx_mul(pr, pi, RHO_CONJ_RE, RHO_CONJ_IM)
            q = as_lattice(qr, qi)
            assert q is not None, f"vertex {k} in neither lattice"
            S.append(q)
            idx[k] = ("S", q)
    # origin is shared: it parses as native; add to S too
    assert (0, 0, 0, 0) in L
    S.append((0, 0, 0, 0))
    print(f"L: {len(L)}  S: {len(S)}")
    assert len(L) == 374 and len(S) == 136

    for p in L + S:
        assert lattice.check_lattice(p), p

    eL = [(i, j) for i in range(len(L)) for j in range(i + 1, len(L))
          if lattice.is_unit(L[i], L[j])]
    eS = [(i, j) for i in range(len(S)) for j in range(i + 1, len(S))
          if lattice.is_unit(S[i], S[j])]
    # cross pairs involving the shared origin are already counted inside eL
    # (|u - rho*0| = |u|) or eS (|0 - rho*v| = |v|), so exclude the origin here
    O = (0, 0, 0, 0)
    cross = [(i, j) for i in range(len(L)) for j in range(len(S))
             if L[i] != O and S[j] != O and lattice.cross_is_unit(L[i], S[j], 4)]
    print(f"edges L: {len(eL)}  S: {len(eS)}  cross: {len(cross)}  "
          f"total: {len(eL) + len(eS) + len(cross)}")
    assert len(eL) == 1860 and len(eS) == 564
    assert len(eL) + len(eS) + len(cross) == 2442

    kinds = {}
    for i, j in cross:
        n1 = lattice.norm144(L[i])
        n2 = lattice.norm144(S[j])
        kinds.setdefault((n1, n2), []).append((i, j))
    print("cross-edge kinds (144|u|^2 as (N,M), 144|v|^2):")
    for k, v in sorted(kinds.items()):
        print(f"  {k}: {len(v)} edges")

    with open(os.path.join(os.path.dirname(__file__), "LS.pkl"), "wb") as f:
        pickle.dump({"L": L, "S": S}, f)
    print("wrote LS.pkl")


if __name__ == "__main__":
    main()

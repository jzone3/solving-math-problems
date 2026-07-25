#!/usr/bin/env python3
"""Recover Parts' L374 / S136 decomposition from the published 509 witness."""
import os
import pickle
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "runs", "P23-fusion1"))
from mfield import MField, load_vtx

from mring import lattice_point, orbit_representative


VTX = os.path.join(ROOT, "solutions", "P23", "v509e2442.vtx")
OUT = os.path.join(HERE, "decomp509.pkl")
FIELD = MField((3, 5, 11))
ONE = (FIELD.ONE, FIELD.ZERO)


def cmul(z, w):
    return (FIELD.sub(FIELD.mul(z[0], w[0]), FIELD.mul(z[1], w[1])),
            FIELD.add(FIELD.mul(z[0], w[1]), FIELD.mul(z[1], w[0])))


def csub(z, w):
    return (FIELD.sub(z[0], w[0]), FIELD.sub(z[1], w[1]))


def cinv(z):
    n = FIELD.add(FIELD.mul(z[0], z[0]), FIELD.mul(z[1], z[1]))
    ni = FIELD.inv(n)
    return (FIELD.mul(z[0], ni), FIELD.scal(-1, FIELD.mul(z[1], ni)))


def cpow(z, k):
    if k < 0:
        return cpow(cinv(z), -k)
    out, base = ONE, z
    while k:
        if k & 1:
            out = cmul(out, base)
        base = cmul(base, base)
        k >>= 1
    return out


def fpoint(x, y):
    return (x, y)


ETA = fpoint(
    (F(0), F(0), F(0), F(0), F(0), F(1, 6), F(0), F(0)),
    (F(0), F(1, 6), F(0), F(0), F(0), F(0), F(0), F(0)),
)
RHO = fpoint(
    (F(7, 8), F(0), F(0), F(0), F(0), F(0), F(0), F(0)),
    (F(0), F(0), F(0), F(1, 8), F(0), F(0), F(0), F(0)),
)


def subtract_center(pts, center):
    return [csub(p, center) for p in pts]


def recover(pts):
    """Search every witness vertex as center and plausible orientations."""
    # rho and its conjugate cover both orientations; their inverses are used
    # because we map a point back into the unrotated ring.
    rho_choices = (RHO, (RHO[0], FIELD.scal(-1, RHO[1])))
    for ci, center in enumerate(pts):
        normalized = subtract_center(pts, center)
        for k in range(-12, 13):
            eta_k = cpow(ETA, k)
            rotated = [cmul(eta_k, p) for p in normalized]
            L = [lattice_point(p, FIELD) for p in rotated]
            if sum(x is not None for x in L) != 374:
                continue
            for rho in rho_choices:
                back = cmul(eta_k, cinv(rho))
                S = [lattice_point(cmul(back, p), FIELD) for p in normalized]
                if sum(x is not None for x in S) != 136:
                    continue
                lidx = {i for i, x in enumerate(L) if x is not None}
                sidx = {i for i, x in enumerate(S) if x is not None}
                lset = {L[i] for i in lidx}
                sset = {S[i] for i in sidx}
                if len(lset) == 374 and len(sset) == 136 and len(lidx & sidx) == 1:
                    return {
                        "center_index": ci,
                        "center": center,
                        "eta_power": k,
                        "rho": "rho" if rho == RHO else "conjugate(rho)",
                        "L": frozenset(lset),
                        "S": frozenset(sset),
                        "L_indices": frozenset(lidx),
                        "S_indices": frozenset(sidx),
                    }
    return None


# Column M in table tl (L374, M6A/B), and column M6A in table ts.  The
# published {M} ranges are used for the four non-column-M rows: this witness
# is another member of Parts' minimal set.
TL = {
    (0, 0, 0, 0): 1, (4, 0, 0, 0): 6, (0, 0, 4, 0): 6,
    (12, 0, 0, 0): 6, (0, 0, 0, 4): 3, (0, 0, 8, 0): 6,
    (0, 0, 12, 0): 6, (0, 0, 2, 2): (6, 8), (6, 2, 0, 0): 12,
    (2, 0, 0, 2): 12, (6, 0, 0, 2): 12, (0, 0, 6, 6): 6,
    (10, 0, 0, 2): 6, (0, 2, 2, 0): 12, (4, 0, 0, 4): 12,
    (14, 0, 0, 2): 6, (0, 2, 6, 0): 12, (0, 0, 2, 6): 6,
    (6, 0, 10, 0): 12, (6, 0, 0, 6): 12, (0, 4, 4, 0): 12,
    (2, 0, 4, 2): 24, (12, 2, 2, 0): 12, (2, 0, 6, 4): (0, 8),
    (4, 0, 2, 2): 24, (4, 0, 6, 2): 12, (2, 0, 8, 2): 12,
    (8, 0, 2, 2): 24, (8, 0, 6, 2): 12, (6, 2, 4, 0): 12,
    (2, 0, 2, 4): 8, (10, 0, 4, 2): 12, (8, 0, 4, 4): 12,
    (4, 0, 10, 2): (0, 4), (10, 0, 2, 4): 10, (6, 2, 8, 0): (8, 12),
    (14, 0, 2, 4): 12,
}
TS = {
    (0, 0, 0, 0): 1, (0, 0, 4, 0): 6, (0, 0, 8, 0): 3,
    (0, 4, 0, 0): 4, (6, 2, 0, 0): 12, (0, 2, 2, 0): 12,
    (0, 2, 6, 0): 12, (0, 0, 2, 6): 12, (6, 0, 0, 6): 12,
    (0, 4, 4, 0): 12, (12, 2, 2, 0): 3, (6, 2, 4, 0): 14,
    (6, 0, 4, 6): 9, (0, 2, 4, 6): 24,
}


def counts(vertices):
    out = {}
    for v in vertices:
        r = orbit_representative(v)
        out[r] = out.get(r, 0) + 1
    return out


def compare(label, actual, expected):
    print(f"\n{label} orbit comparison:")
    all_keys = list(expected)
    for key in all_keys:
        got = actual.get(key, 0)
        bound = expected[key] if isinstance(expected[key], tuple) else (expected[key], expected[key])
        status = "MATCH" if bound[0] <= got <= bound[1] else "MISMATCH"
        paper = expected[key] if bound[0] != bound[1] else bound[0]
        print(f"  {key}: recovered={got}, paper={paper} [{status}]")
    extras = {k: v for k, v in actual.items() if k not in expected}
    if extras:
        print("  EXTRA recovered orbits:", extras)
    missing = {k: v for k, v in expected.items() if k not in actual}
    if missing:
        print("  MISSING paper orbits:", sorted(missing))
    return not extras and not missing and all(
        (v[0] <= actual.get(k, 0) <= v[1]) if isinstance(v, tuple)
        else actual.get(k, 0) == v for k, v in expected.items())


def main():
    pts = load_vtx(FIELD, VTX)
    if len(pts) != 509:
        raise RuntimeError(f"expected 509 points, got {len(pts)}")
    result = recover(pts)
    if result is None:
        print("DECOMPOSITION FAILED")
        return 1
    with open(OUT, "wb") as f:
        pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"DECOMPOSITION PASS: center index {result['center_index']}, "
          f"eta^{result['eta_power']}, orientation {result['rho']}")
    print("L vertices:", len(result["L"]), "S vertices:", len(result["S"]),
          "shared witness vertices:", len(result["L_indices"] & result["S_indices"]))
    ok_l = compare("L374 / table tl column M", counts(result["L"]), TL)
    ok_s = compare("S136 / table ts column M6A", counts(result["S"]), TS)
    print(f"\nCached decomposition: {OUT}")
    return 0 if ok_l and ok_s else 2


if __name__ == "__main__":
    raise SystemExit(main())

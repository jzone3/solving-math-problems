"""Assembly accounting: which gadget cycles are realizable INSIDE the lattice?

Type-J spindle: shared vertex b=0, mono-pair endpoints a=Delta1, c=Delta2 with
|a|=d1, |c|=d2 (mono distances) and |a-c|=1 (closing unit edge). For the union
of two lattice-embedded gadget graphs to overlap in more than b, both Delta1
and Delta2 must be lattice vectors. This script enumerates, for pairs of
gadget distances, all lattice-realizable closing configurations.

Also: same-pair composition (mono-pair + non-mono-pair at the SAME distance
and SAME endpoints) — always lattice-realizable when the distance is; the
question there is gadget existence, tested by scan_property.py.
"""
from fractions import Fraction as F
from itertools import product
import sys

from pools import find_radius_points
from lattice import int_to_frac, sub, is_dist2, to_float

# gadget distances (squared) from Parts' Table 1 + candidates
MONO = {"8/3": F(64, 9), "8/sqrt3": F(64, 3)}
NONMONO = {"3": F(9), "7/3": F(49, 9), "5/3": F(25, 9), "1/3": F(1, 9),
           "sqrt(11/3)": F(11, 3)}
TRIPLE_SIDES = {"sqrt7": F(7), "sqrt5": F(5), "sqrt3": F(3),
                "sqrt(5/3)": F(5, 3), "1/sqrt3": F(1, 3)}


def closing_configs(d2a, d2b, close2=F(1)):
    """Lattice vectors D1, D2 with |D1|^2=d2a, |D2|^2=d2b, |D1-D2|^2=close2."""
    A = find_radius_points(d2a)
    B = find_radius_points(d2b)
    out = []
    for u in A:
        pu = int_to_frac(u)
        for v in B:
            pv = int_to_frac(v)
            if is_dist2(pu, pv, close2):
                out.append((u, v))
    return out


if __name__ == "__main__":
    print("== Type-J spindle closings (mono d1 + mono d2 + unit edge) ==")
    names = list(MONO.items())
    for i in range(len(names)):
        for j in range(i, len(names)):
            (na, da), (nb, db) = names[i], names[j]
            cfg = closing_configs(da, db)
            print("mono %s + mono %s : %d lattice configurations" % (na, nb, len(cfg)))
            for c in cfg[:3]:
                print("   e.g.", c, [to_float(int_to_frac(t)) for t in c])

    print()
    print("== Lattice representability of each gadget distance ==")
    for name, d2 in {**MONO, **NONMONO}.items():
        pts = find_radius_points(d2)
        print("d=%s: %d lattice difference vectors" % (name, len(pts)))

    print()
    print("== Mixed cycles: mono d + nonmono d' with d''=|D1-D2| also a gadget ==")
    # A cycle (mono-pair a-b) + (non-mono-pair a-c)?? For reference we also
    # enumerate mono+mono closings with closing distance equal to each
    # non-mono gadget distance (cycle of 2 mono-pairs + 1 non-mono-pair).
    for nc, c2 in NONMONO.items():
        for i in range(len(names)):
            for j in range(i, len(names)):
                (na, da), (nb, db) = names[i], names[j]
                cfg = closing_configs(da, db, c2)
                if cfg:
                    print("mono %s + mono %s closed by non-mono %s : %d configs"
                          % (na, nb, nc, len(cfg)))

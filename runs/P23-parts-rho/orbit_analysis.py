"""Analyze the orbit structure of Parts' L374 / S136 (from LS.pkl):
which order-24 orbits are used, and how full each orbit is.
"""
import pickle

import lattice


def orbit_key(p):
    return min(lattice.orbit24(p))


def analyze(name, pts):
    orbs = {}
    for p in pts:
        orbs.setdefault(orbit_key(p), []).append(p)
    print(f"== {name}: {len(pts)} points in {len(orbs)} orbits")
    full = partial = 0
    for k in sorted(orbs, key=lambda k: (lattice.norm144(k), k)):
        sz = len(lattice.orbit24(k))
        used = len(orbs[k])
        n144 = lattice.norm144(k)
        tag = "FULL" if used == sz else f"{used}/{sz}"
        if used == sz:
            full += 1
        else:
            partial += 1
        print(f"  orbit {k} |144z^2|={n144} size={sz} used={tag}")
    print(f"  full={full} partial={partial}")
    return orbs


def main():
    d = pickle.load(open("LS.pkl", "rb")); L, S = d["L"], d["S"]
    analyze("L374", L)
    analyze("S136", S)


if __name__ == "__main__":
    main()

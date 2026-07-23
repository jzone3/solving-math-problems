"""Precompute all minimal second-HC-forcing chord sets of size <= 3 (up to the
dihedral group, expanded back to all images) and write them to blocking_<n>.txt,
one set per line as 'u1,v1 u2,v2 ...'. Seeding these as clauses removes the
bulk of CEGAR rounds for the SAT attack.
"""
import sys, itertools
from sat_cegar import second_hc

def canon(n, S):
    best = None
    for r in range(n):
        for sgn in (1, -1):
            T = tuple(sorted(tuple(sorted(((sgn*u+r) % n, (sgn*v+r) % n))) for u, v in S))
            if best is None or T < best:
                best = T
    return best

def main(n):
    chords = [(u, v) for u in range(n) for v in range(u+2, n) if not (u == 0 and v == n-1)]
    seen = set()
    out = []
    for size in (1, 2, 3):
        for S in itertools.combinations(chords, size):
            c = canon(n, S)
            if c in seen:
                continue
            seen.add(c)
            if second_hc(n, list(S)) is None:
                continue
            # minimal? all proper subsets must NOT force a second HC
            if any(second_hc(n, list(T)) is not None
                   for k in range(1, size) for T in itertools.combinations(S, k)):
                continue
            out.append(c)
    with open(f"blocking_{n}.txt", "w") as f:
        for S in out:
            f.write(" ".join(f"{u},{v}" for u, v in S) + "\n")
    print(f"n={n}: {len(out)} minimal blocking orbits (size<=3)", flush=True)

if __name__ == "__main__":
    main(int(sys.argv[1]))

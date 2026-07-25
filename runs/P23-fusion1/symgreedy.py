"""Orbit-batched greedy minimization (symmetry-aware, Parts-style).

W_t = P_t union omega_t P_t carries the involutions tau3 (z -> -conj z),
tau4 (z -> conj z) and the Galois map conj33 (sqrt33 -> -sqrt33); all three are
verified graph automorphisms of W_16.  Random batch-8 deletion (greedy8.py)
tears symmetric structures apart one vertex at a time; deleting a whole
automorphism orbit at once removes structurally equivalent vertices together,
which is how Parts reduces by orbits.  Falls back to 4-2-1 splitting when an
orbit cannot go.

Usage: POOL=wt_16.pkl python3 symgreedy.py <seed> <start.pkl> [<tag>]
"""
import pickle
import random
import sys

import lattice as L
from coremin import solve_core

POOL_PTS = None


def orbits(pts):
    """Partition vertex indices into orbits of <tau3, tau4, conj33>."""
    idx = {p: i for i, p in enumerate(pts)}
    seen, out = set(), []
    for i, (t, p) in enumerate(pts):
        if i in seen:
            continue
        cur = {(t, p)}
        while True:
            new = set(cur)
            for tt, q in cur:
                for f in (L.tau3, L.tau4, L.conj33, L.neg):
                    new.add((tt, f(q)))
            if new == cur:
                break
            cur = new
        orb = sorted(idx[x] for x in cur if x in idx)
        seen.update(orb)
        out.append(orb)
    return out


def attempt(S, batch, rnd, tag):
    cand = set(S) - set(batch)
    if len(cand) <= 4:
        return None
    try:
        st, keep = solve_core(cand, seed=rnd.randrange(10 ** 6),
                              timeout=3600, tag=tag)
    except Exception:
        return None
    return keep if st == "UNSAT" else None


def greedy(S, seed, tag, orbs):
    rnd = random.Random(seed)
    S = set(S)
    passno = 0
    while True:
        passno += 1
        removed = 0
        order = list(orbs)
        rnd.shuffle(order)
        for orb in order:
            group = [v for v in orb if v in S]
            if not group:
                continue
            res = attempt(S, group, rnd, tag)
            if res is not None:
                S = res
                removed += len(group)
                print(f"{tag} pass{passno}: -{len(group)} (orbit) -> {len(S)}",
                      flush=True)
                pickle.dump(sorted(S), open(f"sym_{tag}.pkl", "wb"))
                continue
            stack = [group[:len(group) // 2], group[len(group) // 2:]] \
                if len(group) > 1 else []
            while stack:
                g = [v for v in stack.pop() if v in S]
                if not g:
                    continue
                res = attempt(S, g, rnd, tag)
                if res is not None:
                    S = res
                    removed += len(g)
                    print(f"{tag} pass{passno}: -{len(g)} -> {len(S)}", flush=True)
                    pickle.dump(sorted(S), open(f"sym_{tag}.pkl", "wb"))
                elif len(g) > 1:
                    h = len(g) // 2
                    stack.append(g[:h])
                    stack.append(g[h:])
        print(f"{tag} pass{passno} done removed={removed} n={len(S)}", flush=True)
        if removed == 0:
            break
    print(f"{tag} FINAL {len(S)}", flush=True)
    pickle.dump(sorted(S), open(f"sym_{tag}.pkl", "wb"))


if __name__ == "__main__":
    import coremin
    orbs = orbits(coremin.allpts)
    print(f"orbits: {len(orbs)} (sizes "
          f"{sorted({len(o) for o in orbs})})", flush=True)
    greedy(pickle.load(open(sys.argv[2], "rb")), int(sys.argv[1]),
           sys.argv[3] if len(sys.argv) > 3 else f"s{sys.argv[1]}", orbs)

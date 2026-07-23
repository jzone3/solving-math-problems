"""Engine D: exact cell-tree greedy over the divisor lattice.

Different encoding from the flat-array greedy (greedy_cover.py): the uncovered
set is a collection of disjoint CRT cells (a mod M), M | N, instead of a bool
array of length N.  This removes the memory wall entirely: N can be ~1e13, so
the modulus palette can include 17, 19, 3^5, 5^3, 7^2, ... simultaneously --
qualitatively richer than anything reachable with flat arrays (max ~5e9).

Greedy step for modulus d (processed ascending):
  for each uncovered cell (a, M): let g = gcd(M, d).  The cell meets residue r
  mod d iff r = a (mod g), and then contributes N/lcm(M,d) elements.  So
  coverage counts are uniform on each class a mod g: accumulate weight[g][a%g]
  += N/lcm(M,d).  Total count for residue r: sum over g of weight[g][r%g].
  Maximize by descending the divisor chain of d over levels g.
  After choosing r: split every compatible cell against (r, d): the cell
  (a, M) splits into its sub-cells mod lcm(M,d); the one matching r mod d is
  removed; the others stay (they are cells mod lcm(M,d)).

Cell count is monitored; splitting is lazy (cells stay as coarse as possible).
"""
import argparse
import json
import random
import sys
import time
from math import gcd

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]


def factorize(n):
    f = {}
    for p in PRIMES:
        while n % p == 0:
            f[p] = f.get(p, 0) + 1
            n //= p
    assert n == 1, "non-smooth N"
    return f


def divisors(n):
    f = factorize(n)
    divs = [1]
    for p, e in f.items():
        divs = [d * p**k for d in divs for k in range(e + 1)]
    return sorted(divs)


def crt(r1, m1, r2, m2):
    g = gcd(m1, m2)
    assert (r1 - r2) % g == 0
    l = m1 // g * m2
    inv = pow(m1 // g, -1, m2 // g) if m2 // g > 1 else 0
    x = (r1 + (m1 // g) * ((r2 - r1) // g * inv % (m2 // g))) % l
    return x, l


def greedy_tree(N, L, divs, rng=None, verbose=True, cell_cap=30_000_000):
    """Returns (chosen list, uncovered_element_count, cells)."""
    cells = {(0, 1): True}  # dict as ordered set of (a, M)
    chosen = []
    usable = [d for d in divs if L <= d <= N]
    order = sorted(usable)
    for idx, d in enumerate(order):
        if not cells:
            break
        # accumulate weights per (g, a mod g)
        weight = {}
        for (a, M) in cells:
            g = gcd(M, d)
            l = M // g * d
            w = N // l
            key = a % g
            wg = weight.setdefault(g, {})
            wg[key] = wg.get(key, 0) + w
        # find r mod d (approximately) maximizing sum_g weight[g][r % g],
        # via beam search over partial CRT constraints (r mod m), m | d,
        # processing g's in decreasing order of total mass.  The beam scores
        # are lower bounds; final scores are evaluated exactly.
        gs = sorted(weight.keys(), key=lambda g: -sum(weight[g].values()))
        BEAM, TOPK = 48, 12
        beam = [(0, 0, 1)]  # (score_lb, r, m)
        for g in gs:
            top = sorted(weight[g].items(), key=lambda kv: -kv[1])[:TOPK]
            nxt = {}
            for sc, r, m in beam:
                gm = gcd(g, m)
                for key, w in top:
                    if (r - key) % gm != 0:
                        continue
                    nr, nm = crt(r, m, key, g)
                    if (nr, nm) not in nxt or sc + w > nxt[(nr, nm)]:
                        nxt[(nr, nm)] = sc + w
                # allow skipping g (residue may miss all its top keys)
                if (r, m) not in nxt or sc > nxt[(r, m)]:
                    nxt[(r, m)] = sc
            beam = sorted(((v, r, m) for (r, m), v in nxt.items()),
                          reverse=True)[:BEAM]
        pool = {r % d for _, r, m in beam}
        if rng is not None:
            pool |= {rng.randrange(d) for _ in range(16)}
        best_r, best_w = -1, -1
        for r in pool:
            w = sum(weight[g].get(r % g, 0) for g in gs)
            if w > best_w:
                best_w, best_r = w, r
        if best_w <= 0:
            continue
        r = best_r
        # split cells against (r, d)
        new_cells = {}
        for (a, M) in cells:
            g = gcd(M, d)
            if (a - r) % g != 0:
                new_cells[(a, M)] = True
                continue
            l = M // g * d
            if l == M:
                # cell entirely inside class? cell (a,M), d | M: covered iff
                # a % d == r % d (g == d)
                continue  # g==d, matched -> fully covered
            # split cell into sub-cells mod l; remove the one hitting r mod d
            hit, _ = crt(a, M, r, d)
            step = M
            n_sub = l // M
            for t in range(n_sub):
                sub = (a + t * step) % l
                if sub != hit:
                    new_cells[(sub, l)] = True
        cells = new_cells
        chosen.append((r, d))
        if len(cells) > cell_cap:
            raise MemoryError(f"cell blowup {len(cells)}")
        if verbose and (idx % 100 == 0 or d == order[-1]):
            unc = sum(N // M for _, M in cells)
            print(f"  d={d} ({idx+1}/{len(order)}): cells {len(cells)}, "
                  f"uncovered {unc} ({unc/N:.2e})", flush=True)
    unc = sum(N // M for _, M in cells)
    return chosen, unc, cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--factors", required=True,
                    help="e.g. 2^7,3^4,5^2,7^2,11,13,17")
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--restarts", type=int, default=1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    N = 1
    for tok in a.factors.split(","):
        if "^" in tok:
            p, e = tok.split("^")
            N *= int(p) ** int(e)
        else:
            N *= int(tok)
    divs = divisors(N)
    print(f"N={N} ({len(divs)} divisors, "
          f"{len([d for d in divs if d >= a.L])} usable >= {a.L})", flush=True)
    best = None
    t0 = time.time()
    for it in range(a.restarts):
        rng = random.Random(a.seed + it) if (a.seed + it) else None
        try:
            chosen, unc, cells = greedy_tree(N, a.L, divs, rng=rng)
        except MemoryError as e:
            print(f"restart {it}: {e}", flush=True)
            continue
        print(f"restart {it}: {len(chosen)} classes, uncovered {unc}, "
              f"{time.time()-t0:.1f}s", flush=True)
        if best is None or unc < best[1]:
            best = (chosen, unc)
        if unc == 0:
            break
    if best and best[1] == 0:
        chosen = best[0]
        mods = [m for _, m in chosen]
        assert len(set(mods)) == len(mods)
        print(f"SUCCESS: covering of Z_{N} with min modulus {min(mods)} "
              f"using {len(chosen)} classes")
        out = a.out or f"witness_D_L{a.L}_N{N}.json"
        with open(out, "w") as f:
            json.dump({"N": N, "L": a.L,
                       "congruences": [[r, d] for r, d in chosen]}, f)
        print(f"wrote {out}")
    else:
        print(f"FAILED: best uncovered {best[1] if best else 'n/a'}")
        sys.exit(1)


if __name__ == "__main__":
    main()

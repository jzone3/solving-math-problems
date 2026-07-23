#!/usr/bin/env python3
"""Nielsen/Owens-style symbolic constructor: greedy cover of Z by congruence
classes with distinct moduli >= m, holes tracked as exact cosets (a mod M)
with arbitrary-precision M. No explicit Z_N arrays, so lcm can reach 10^13+.

Model: uncovered set = list of disjoint cosets. Each chosen class (b mod d)
covers, inside each hole (a, M) with b = a (mod gcd(d, M)), exactly one coset
mod L = lcm(M, d); the hole splits into L/M cosets of which one is removed.
Moduli are p-smooth numbers >= m, each used at most once, tried in ascending
order; residue b chosen by weighted CRT greedy over the holes it can hit,
with a fragmentation cap (skip splitting holes where L/M > frag_cap by
steering b away when possible).

Usage: coset_cover.py m [max_mod] [frag_cap] [out.json]
"""
import heapq, json, math, sys
from fractions import Fraction


def gen_smooth(primes, limit):
    """All numbers <= limit whose prime factors are in primes, ascending."""
    heap = [1]
    seen = {1}
    out = []
    while heap:
        v = heapq.heappop(heap)
        out.append(v)
        for p in primes:
            w = v * p
            if w <= limit and w not in seen:
                seen.add(w)
                heapq.heappush(heap, w)
    return out


def factorize(n, primes):
    f = {}
    for p in primes:
        while n % p == 0:
            f[p] = f.get(p, 0) + 1
            n //= p
        if n == 1:
            break
    assert n == 1
    return f


def crt_pair(a1, m1, a2, m2):
    """Solve x=a1 (m1), x=a2 (m2); moduli coprime."""
    inv = pow(m1, -1, m2)
    return (a1 + m1 * ((a2 - a1) * inv % m2)) % (m1 * m2)


def merge_holes(holes, primes):
    """Repeatedly merge full sibling families: if for some prime p | M all p
    cosets a+j*(M//p) (mod M) are present, replace them by (a mod M//p)."""
    changed = True
    while changed:
        changed = False
        by_parent = {}
        for (a, M) in holes:
            for p in primes:
                if M % p == 0:
                    Mp = M // p
                    by_parent.setdefault((a % Mp, Mp, p), []).append((a, M))
        for (ap, Mp, p), members in by_parent.items():
            if len(set(members)) == p and all(h in holes for h in members):
                for h in set(members):
                    holes.discard(h)
                holes.add((ap, Mp))
                changed = True
    return holes


def merge_around(holes, h, primes):
    a, M = h
    changed = True
    while changed:
        changed = False
        for p in primes:
            if M % p:
                continue
            Mp = M // p
            fam = [(a % Mp + j * Mp, M) for j in range(p)]
            if all(x in holes for x in fam):
                for x in fam:
                    holes.discard(x)
                holes.add((a % Mp, Mp))
                a, M = a % Mp, Mp
                changed = True
                break


def run(m, max_mod=10**7, frag_cap=64, out=None, density_stop=Fraction(0),
        primes=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
                59, 61, 67, 71, 73, 79, 83, 89, 97)):
    b2 = 1
    while b2 < m:
        b2 *= 2
    frag_cap = max(frag_cap, b2)
    smooth = [d for d in gen_smooth(primes, max_mod) if d >= m]
    holes = {(0, 1)}          # cosets (a, M), disjoint
    cover = []
    density = Fraction(1)
    used = set()
    for d in smooth:
        if not holes:
            break
        df = factorize(d, primes)
        # weighted CRT greedy: choose b mod d prime-by-prime to maximize the
        # density of holes that remain compatible (b = a mod gcd(d, M)),
        # skipping holes whose split factor L/M would exceed frag_cap
        cands = []
        for (a, M) in holes:
            g = math.gcd(d, M)
            L = d // g * M
            split = L // M
            if split > frag_cap:
                continue
            cands.append((a, M, g, L))
        if not cands:
            continue
        b, bmod = 0, 1
        for p, e in sorted(df.items()):
            pe = p ** e
            # weight per residue r mod pe: density of still-compatible holes
            # whose constraint mod p^k (k<=e) matches r
            wts = {}
            for (a, M, g, L) in cands:
                # constraint of hole on b modulo p^min(e, vp(M))
                k = 0
                Mv = M
                while Mv % p == 0 and k < e:
                    Mv //= p
                    k += 1
                pk = p ** k
                if k == 0:
                    continue
                r = a % pk
                wts[(pk, r)] = wts.get((pk, r), 0.0) + 1.0 / L
            # choose residue mod pe maximizing satisfied weight
            best_r, best_w = 0, -1.0
            rcands = {rr for (pk, rr) in wts} | {0}
            for r in rcands:
                wsum = 0.0
                for (pk, rr), wv in wts.items():
                    if r % pk == rr:
                        wsum += wv
                if wsum > best_w:
                    best_r, best_w = r, wsum
            # keep only holes still compatible with best_r
            kept = []
            for (a, M, g, L) in cands:
                pk = math.gcd(pe, M)
                if pk == 1 or best_r % pk == a % pk:
                    kept.append((a, M, g, L))
            cands = kept
            b = crt_pair(b, bmod, best_r, pe)
            bmod *= pe
        assert bmod == d
        # compute actual coverage and update holes
        newly = []
        removed = []
        gain = Fraction(0)
        for (a, M) in holes:
            g = math.gcd(d, M)
            if b % g != a % g:
                continue
            L = d // g * M
            if L // M > frag_cap:
                continue
            # covered coset inside hole: x = a (M), x = b (d) -> coset mod L
            # split hole into L/M cosets mod L: a + j*M, keep all except the
            # one congruent to b mod d
            removed.append((a, M))
            gain += Fraction(1, L)
            for j in range(L // M):
                aa = a + j * M
                if aa % d == b % d:
                    continue
                newly.append((aa, L))
        if gain == 0:
            continue
        for h in removed:
            holes.discard(h)
        holes.update(newly)
        for h in set(newly):
            if h in holes:
                merge_around(holes, h, primes)
        cover.append((b, d))
        used.add(d)
        density -= gain
        if len(cover) % 50 == 0 or density == 0:
            print(f"n={len(cover)} d={d} density={float(density):.3e} "
                  f"holes={len(holes)}", flush=True)
        if density <= density_stop:
            break
    print(f"DONE cover={len(cover)} density={float(density):.3e} "
          f"holes={len(holes)} residual_exact={density}", flush=True)
    if not holes:
        print(f"COVERED min_mod={min(n for _, n in cover)}", flush=True)
        if out:
            json.dump({"m": m, "cover": [[a, n] for a, n in
                                         sorted(cover, key=lambda x: x[1])]},
                      open(out, "w"))
    return cover, holes, density


if __name__ == "__main__":
    m = int(sys.argv[1])
    max_mod = int(sys.argv[2]) if len(sys.argv) > 2 else 10**7
    frag_cap = int(sys.argv[3]) if len(sys.argv) > 3 else 64
    out = sys.argv[4] if len(sys.argv) > 4 else None
    run(m, max_mod, frag_cap, out)

#!/usr/bin/env python3
"""
P15 V4 phase 2b: counting builder with CRT-COMPONENT class representation.

Same semantics as cover3.py (exact big-int hole-class counts, structured
congruences, pool kills with Hall prefix condition), but a hole class is a
vector of residues mod p_i^{e_i} (the window's prime powers) instead of a
single residue mod C. This removes the int64 window ceiling that destroyed
alignment, which is the decisive resource (holes concentrated in sparse
sublattices make each modulus cover far more than its 1/m density).

Witness recipe (JSON): per level {p, window_before: {p: e}, congs: [[m,a]],
window_after: {p: e}, kills: {class_key_repr: count}} — replayable by
solutions/P15/verify4.py.
"""
import argparse, json, time
from heapq import heappush, heappop

import numpy as np


def primes_upto(a, b):
    return [n for n in range(a, b)
            if n > 1 and all(n % d for d in range(2, int(n**0.5) + 1))]


def count_divisors_below(fact, bound):
    primes = sorted(fact)
    cnt = 0
    def rec(i, prod):
        nonlocal cnt
        if i == len(primes):
            cnt += 1
            return
        p, v = primes[i], prod
        for _ in range(fact[p] + 1):
            if v >= bound:
                break
            rec(i + 1, v)
            v *= p
    rec(0, 1)
    return cnt


def divisors_capped(fact, cap):
    divs = [1]
    for p, e in fact.items():
        divs = [d * p**k for d in divs for k in range(e + 1) if d * p**k <= cap]
    return sorted(set(divs))


class Builder:
    def __init__(self, T, hcap=2_000_000, mcap=2_000_000, verbose=True,
                 seed=0, survivor=True):
        self.T = T
        self.hcap = hcap
        self.mcap = mcap
        self.verbose = verbose
        self.survivor = survivor
        self.rng = np.random.default_rng(seed)
        self.win = {}          # window: prime -> exponent (v_p == v_p(M))
        self.wprimes = []      # ordered primes of window
        self.comps = None      # (H, len(wprimes)) int64 residues mod p^e
        self.counts = [1]      # exact big ints, len H
        self.Nfact = {}
        self.used = set()
        self.kills_total = 0
        self.recipe = []
        self.n_congs = 0

    def log(self, *a):
        if self.verbose:
            print(*a, flush=True)

    def pool(self):
        D = 1
        for e in self.Nfact.values():
            D *= e + 1
        return D - count_divisors_below(self.Nfact, self.T) - self.kills_total

    def key_for(self, comps, mfact):
        """Vector of combined residues mod m for given cells (mixed radix)."""
        key = np.zeros(comps.shape[0], dtype=np.int64)
        for p, k in mfact.items():
            i = self.wprimes.index(p)
            key = key * p**k + comps[:, i] % p**k
        return key

    def process(self, p, remaining=()):
        T = self.T
        t0 = time.time()
        if self.Nfact.get(p, 0) != self.win.get(p, 0):
            raise RuntimeError(f"window lost prime {p}")
        H = len(self.counts)
        e_old = self.win.get(p, 0)
        if p not in self.win:
            self.win[p] = 0
            self.wprimes.append(p)
            pad = np.zeros((H, 1), dtype=np.int64)
            self.comps = pad if self.comps is None else np.hstack([self.comps, pad])
        pi = self.wprimes.index(p)
        # split: child comp_p = r_p + p^e_old * s, s = 0..p-1
        cells = np.repeat(self.comps, p, axis=0)
        s = np.tile(np.arange(p, dtype=np.int64), H)
        cells[:, pi] += p**e_old * s
        ccounts = [n for n in self.counts for _ in range(p)]
        self.win[p] = e_old + 1
        self.Nfact[p] = self.Nfact.get(p, 0) + 1

        nC = cells.shape[0]
        maxbits = max(n.bit_length() for n in ccounts)
        shift = max(0, maxbits - 500)
        w = np.array([float(n >> shift) if (n >> shift) else 5e-324
                      for n in ccounts])
        act = np.ones(nC, dtype=bool)
        if self.survivor and p > 2:
            sv = int(self.rng.integers(p))
            wsc = np.where(s == sv, 0.0, w)
        else:
            wsc = w

        # candidate moduli: divisors of window product, >= T, unused, with
        # v_p >= 1 OR any (plain window divisors also fine)
        winfact = dict(self.win)
        cands = [m for m in divisors_capped(winfact, self.mcap)
                 if m >= T and m not in self.used]

        def mfact_of(m):
            f = {}
            for q in self.wprimes:
                k = 0
                while m % q == 0:
                    m //= q
                    k += 1
                if k:
                    f[q] = k
            return f

        facts = {m: mfact_of(m) for m in cands}
        key_cache = {}
        def keys(m):
            if m not in key_cache:
                if len(key_cache) > 48:
                    key_cache.pop(next(iter(key_cache)))
                key_cache[m] = self.key_for(cells, facts[m])
            return key_cache[m]

        def best(m):
            km = keys(m)
            vals, inv = np.unique(km, return_inverse=True)
            g = np.bincount(inv, weights=act * wsc, minlength=len(vals))
            k = int(g.argmax())
            return float(g[k]), int(vals[k])

        heap = []
        for m in cands:
            gain, a = best(m)
            if gain > 0:
                heappush(heap, (-gain, self.rng.random(), m))
        chosen = []
        while heap:
            _, _, m = heappop(heap)
            gain, a = best(m)
            if gain <= 0:
                continue
            if heap and -heap[0][0] > gain * 1.0000001:
                heappush(heap, (-gain, self.rng.random(), m))
                continue
            act &= keys(m) != a
            self.used.add(m)
            # store residue in CRT-mixed-radix key form (verifier replays same)
            chosen.append((int(m), int(a)))

        # survivors -> new hole classes
        idx = np.nonzero(act)[0]
        cells = cells[idx]
        ccounts = [ccounts[i] for i in idx.tolist()]
        # merge identical classes
        if len(cells):
            order = np.lexsort(cells.T)
            cells = cells[order]
            ccounts = [ccounts[i] for i in order.tolist()]
            uniq = np.ones(len(cells), dtype=bool)
            uniq[1:] = np.any(cells[1:] != cells[:-1], axis=1)
            newcells, newcounts = [], []
            for i, u in enumerate(uniq.tolist()):
                if u:
                    newcells.append(cells[i])
                    newcounts.append(ccounts[i])
                else:
                    newcounts[-1] += ccounts[i]
            cells = np.array(newcells, dtype=np.int64)
            ccounts = newcounts

        # window truncation under class pressure: reduce exponent of the
        # least useful prime (largest prime, not needed by remaining levels)
        rem = set(remaining)
        trunc = []
        while len(ccounts) > self.hcap:
            cand = sorted((q for q in self.win if self.win[q] > 0),
                          key=lambda q: (q in rem and self.win.get(q, 0) <=
                                         self.Nfact.get(q, 0), -q))
            q = None
            for c in cand:
                if c in rem:
                    continue
                q = c
                break
            if q is None:
                q = cand[0]
            qi = self.wprimes.index(q)
            self.win[q] -= 1
            trunc.append(q)
            cells[:, qi] %= q ** self.win[q]
            order = np.lexsort(cells.T)
            cells = cells[order]
            ccounts = [ccounts[i] for i in order.tolist()]
            uniq = np.ones(len(cells), dtype=bool)
            uniq[1:] = np.any(cells[1:] != cells[:-1], axis=1)
            nc, nn = [], []
            for i, u in enumerate(uniq.tolist()):
                if u:
                    nc.append(cells[i])
                    nn.append(ccounts[i])
                else:
                    nn[-1] += ccounts[i]
            cells = np.array(nc, dtype=np.int64)
            ccounts = nn

        # pool kills, smallest classes first
        # Hall headroom: future structured congruences are bounded by the
        # candidate pool per level (~few hundred); reserve conservatively
        reserve = len(self.used) + 400 * len(remaining)
        budget = self.pool() - reserve
        kills = []
        if budget > 0 and ccounts:
            order = sorted(range(len(ccounts)), key=lambda i: ccounts[i])
            keep = np.ones(len(ccounts), dtype=bool)
            for i in order:
                if budget <= 0:
                    break
                k = min(ccounts[i], budget)
                kills.append((cells[i].tolist(), str(k)))
                budget -= k
                ccounts[i] -= k
                if ccounts[i] == 0:
                    keep[i] = False
            cells = cells[keep]
            ccounts = [n for n in ccounts if n > 0]
        nk = sum(int(k) for _, k in kills)
        self.kills_total += nk

        self.comps = cells if len(ccounts) else np.zeros((0, len(self.wprimes)),
                                                         dtype=np.int64)
        self.counts = ccounts
        self.n_congs += len(chosen)
        self.recipe.append({
            "p": p, "congs": chosen, "trunc": trunc, "kills": kills,
            "wprimes": list(self.wprimes),
            "window_after": {str(q): e for q, e in self.win.items()},
        })
        tot = sum(ccounts) if ccounts else 0
        dens = sum(1.0 / m for m, _ in chosen)
        self.log(f"p={p}: {len(chosen)} congs (dens {dens:.3f}), "
                 f"kills~1e{max(0, len(str(nk)) - 1)}, classes={len(ccounts)}, "
                 f"holes~1e{max(0, len(str(tot)) - 1)}, "
                 f"pool~1e{max(0, len(str(self.pool())) - 1)}, "
                 f"t={time.time()-t0:.0f}s")
        return tot


CONFIGS = {
    "C": [2]*12 + [3]*8 + [5]*5 + [7]*3 + [11]*2 + [13]*2 + [17]*2 +
         [19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83,
          89, 97, 101, 103],
    "F": [2]*9 + [3]*6 + [5]*4 + [7]*3 + [11]*2 + [13]*2 + [17, 19, 23, 29,
          31, 37, 41] + primes_upto(43, 200),
    # interleaved orders (classical constructions interleave prime powers)
    "K": [2, 2, 2, 2, 3, 2, 3, 2, 3, 5, 2, 3, 5, 7, 5, 7, 11, 13, 17],
    "K2": [2, 2, 2, 2, 3, 2, 3, 2, 3, 5, 2, 3, 5, 7, 2, 3, 5, 7, 11, 2, 3,
           11, 13, 13, 17, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
           67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113],
}


def run(T, levels, out=None, seed=0, hcap=2_000_000, survivor=True):
    b = Builder(T, seed=seed, hcap=hcap, survivor=survivor)
    for i, p in enumerate(levels):
        tot = b.process(p, remaining=levels[i + 1:])
        if tot == 0:
            b.log("ALL HOLES ELIMINATED — construction complete!")
            break
    Hf = sum(b.counts) if b.counts else 0
    ok = Hf == 0
    print(f"FINAL T={T}: holes digits={len(str(Hf))} (zero={Hf == 0}), "
          f"structured={b.n_congs}, kills~1e{max(0, len(str(b.kills_total)) - 1)}, "
          f"SUCCESS={ok}")
    if out:
        with open(out, "w") as f:
            json.dump({"T": T, "levels": levels, "recipe": b.recipe,
                       "H_final": str(Hf), "success": ok,
                       "Nfact": {str(p): e for p, e in b.Nfact.items()}}, f)
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--T", type=int, default=14)
    ap.add_argument("--config", default="C")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--hcap", type=int, default=2_000_000)
    ap.add_argument("--no-survivor", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    run(args.T, CONFIGS[args.config], out=args.out, seed=args.seed,
        hcap=args.hcap, survivor=not args.no_survivor)

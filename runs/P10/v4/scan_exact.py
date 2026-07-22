"""V4 exact scan: structured families with closed-form Laplacian spectra.

Scans (all exact rational arithmetic, no floating point):
  A. Kneser K(n,k), Johnson J(n,k), Hamming H(d,q) over large parameter grids,
     plus their complements.
  B. Complete multipartite graphs: ALL partitions of n for n <= NMAX_PART.
  C. All threshold graphs up to n <= NMAX_THRESH (equality reference / sanity).
  D. Joins of pairs (and cones/iterated joins) over a library of base specs.

Reports global minimum deficit  min_t [ m + t(t+1)/2 - S_t ]  per family.
Any negative deficit = counterexample to Brouwer's conjecture.
"""
import sys, time, itertools
from fractions import Fraction
sys.path.insert(0, '.')
from spectra import (Spec, empty_graph, complete_graph, join, complement, kneser,
                     johnson, hamming, complete_multipartite, threshold_graph,
                     disjoint_union, worst, worst_fast)

NEAR_MISS = Fraction(1)  # log any nonneg deficit < 1 at nontrivial t

results = []  # (family, name, n, m, mindef, argt)

def record(family, name, spec, fast=True):
    d, t = (worst_fast(spec) if fast else worst(spec))
    results.append((family, name, spec.n, spec.m, d, t))
    if d < 0:
        print(f"!!! COUNTEREXAMPLE {family} {name} n={spec.n} t={t} deficit={d}")
    elif d < NEAR_MISS:
        print(f"  near-miss {family} {name} n={spec.n} m={spec.m} t={t} deficit={d}")
    return d, t


def summarize(family):
    fam = [r for r in results if r[0] == family]
    if not fam:
        return
    best = min(fam, key=lambda r: r[4])
    print(f"[{family}] scanned {len(fam)}; min deficit = {best[4]} "
          f"at {best[1]} (n={best[2]}, t={best[5]})")


def partitions(n, maxp=None):
    if maxp is None:
        maxp = n
    if n == 0:
        yield []
        return
    for p in range(min(n, maxp), 0, -1):
        for rest in partitions(n - p, p):
            yield [p] + rest


t0 = time.time()

# --- A. Kneser / Johnson / Hamming + complements -------------------------------
for nn in range(5, 41):
    for k in range(2, nn // 2 + 1):
        sp = kneser(nn, k)
        record("kneser", f"K({nn},{k})", sp)
        record("kneser-c", f"cK({nn},{k})", complement(sp))
for nn in range(4, 31):
    for k in range(2, nn // 2 + 1):
        sp = johnson(nn, k)
        record("johnson", f"J({nn},{k})", sp)
        record("johnson-c", f"cJ({nn},{k})", complement(sp))
for d in range(2, 13):
    for q in range(2, 9):
        if q ** d > 10 ** 7:
            continue
        sp = hamming(d, q)
        record("hamming", f"H({d},{q})", sp)
        record("hamming-c", f"cH({d},{q})", complement(sp))
for f in ("kneser", "kneser-c", "johnson", "johnson-c", "hamming", "hamming-c"):
    summarize(f)
print(f"-- phase A done {time.time()-t0:.1f}s", flush=True)

# --- B. Complete multipartite: all partitions of n ------------------------------
for n in range(3, 41):
    for parts in partitions(n):
        if len(parts) < 2:
            continue
        record("multipartite", f"K{parts}", complete_multipartite(parts))
summarize("multipartite")
print(f"-- phase B done {time.time()-t0:.1f}s", flush=True)

# --- C. All threshold graphs up to n=18 (equality reference) --------------------
worst_thresh = None
for n in range(2, 19):
    for bits in range(2 ** (n - 1)):
        seq = [(bits >> i) & 1 for i in range(n - 1)]
        if not any(seq):
            continue
        sp = threshold_graph(seq)
        d, t = worst_fast(sp)
        if d < 0:
            print(f"!!! COUNTEREXAMPLE threshold {seq} t={t} d={d}")
        if worst_thresh is None or d < worst_thresh[0]:
            worst_thresh = (d, seq, t)
print(f"[threshold n<=18] min deficit = {worst_thresh[0]} (expected 0, equality class); "
      f"seq={worst_thresh[1]} t={worst_thresh[2]}")
print(f"-- phase C done {time.time()-t0:.1f}s", flush=True)

# --- D. Joins over a base library -----------------------------------------------
base = []
for n in range(1, 16):
    base.append((f"E{n}", empty_graph(n)))
    base.append((f"K{n}", complete_graph(n)))
for nn in range(5, 13):
    for k in range(2, nn // 2 + 1):
        base.append((f"Kn({nn},{k})", kneser(nn, k)))
        base.append((f"J({nn},{k})", johnson(nn, k)))
for d in range(2, 5):
    base.append((f"H({d},2)", hamming(d, 2)))
base.append(("H(2,3)", hamming(2, 3)))
base.append(("H(2,4)", hamming(2, 4)))
base += [(f"c[{nm}]", complement(sp)) for nm, sp in base if sp.m > 0]

# pairwise joins
for (na, a), (nb, b) in itertools.combinations_with_replacement(base, 2):
    if a.n + b.n > 200:
        continue
    record("join2", f"{na}v{nb}", join(a, b))
summarize("join2")
print(f"-- phase D2 done {time.time()-t0:.1f}s", flush=True)

# triple joins over a reduced library (the tight regime: stacking joins)
small = [(nm, sp) for nm, sp in base if sp.n <= 40]
for (na, a), (nb, b), (nc, c) in itertools.combinations_with_replacement(small, 3):
    if a.n + b.n + c.n > 90:
        continue
    record("join3", f"{na}v{nb}v{nc}", join(join(a, b), c))
summarize("join3")
print(f"-- phase D3 done {time.time()-t0:.1f}s", flush=True)

# iterated cones over interesting bases (cone = join with K1)
for nm, sp in base:
    cur, cn = sp, nm
    for i in range(1, 26):
        cur = join(cur, empty_graph(1))
        cn = f"cone^{i}({nm})"
        record("cones", cn, cur)
summarize("cones")

# disjoint unions joined with cliques/empties: G = (aK_p u E_q) v K_r patterns
for p in range(2, 9):
    for a in range(1, 7):
        for q in range(0, 6):
            g = disjoint_union(
                Spec(a * p, a * (p * (p - 1) // 2),
                     [(Fraction(p), a * (p - 1)), (Fraction(0), a)]),
                empty_graph(q)) if q else \
                Spec(a * p, a * (p * (p - 1) // 2),
                     [(Fraction(p), a * (p - 1)), (Fraction(0), a)])
            for r in range(1, 26):
                record("unionjoin", f"({a}K{p}uE{q})vK{r}", join(g, complete_graph(r)))
            for s in range(1, 26):
                record("unionjoin", f"({a}K{p}uE{q})vE{s}", join(g, empty_graph(s)))
summarize("unionjoin")
print(f"-- all done {time.time()-t0:.1f}s")

gmin = min(results, key=lambda r: r[4])
print(f"GLOBAL MIN over {len(results)} specs: family={gmin[0]} name={gmin[1]} "
      f"n={gmin[2]} m={gmin[3]} t={gmin[5]} deficit={gmin[4]}")
nm = sorted([r for r in results if r[4] < NEAR_MISS], key=lambda r: r[4])[:40]
print("Top near-misses (deficit < 1):")
for r in nm:
    print("  ", r)

#!/usr/bin/env python3
"""P06 V4 supplementary search beyond exhaustive range (Graffiti 129).

Key reduction: dev(Laplacian) depends only on the degree sequence D:
    dev(D)^2 = (sum d^2 + 2m)/n - (2m/n)^2.
So G violates 129 iff  dev(D) > R(G) >= Rmin(D) := min Randic index over
realizations of D.  We search degree sequences maximizing
    gap(D) = dev(D) - Rmin_heur(D),
where Rmin_heur is: assortative Havel-Hakimi realization followed by
2-swap local search minimizing R (degree-preserving rewiring).
Hill-climbing over graphical degree sequences, multi-start from perturbed
K_k U t K_1 sequences (the exact-equality family) and random sequences.
Any gap > 0 candidate would then be exactly verified.
"""
import math, random, sys

def dev(D):
    n = len(D); m = sum(D)/2
    var = (sum(d*d for d in D) + 2*m)/n - (2*m/n)**2
    return math.sqrt(max(var, 0.0))

def is_graphical(D):
    D = sorted(D, reverse=True)
    if sum(D) % 2 or D and (D[0] >= len(D) or D[-1] < 0):
        return False
    # Erdos-Gallai
    pref = 0
    for k in range(1, len(D)+1):
        pref += D[k-1]
        rhs = k*(k-1) + sum(min(d, k) for d in D[k:])
        if pref > rhs: return False
    return True

def havel_hakimi_assortative(D):
    """Connect highest-degree vertices to each other (minimizes R roughly)."""
    n = len(D)
    rem = sorted(((d, i) for i, d in enumerate(D)), reverse=True)
    rem = [[d, i] for d, i in rem]
    adj = set()
    while True:
        rem.sort(reverse=True)
        d, v = rem[0]
        if d == 0: break
        if d > len(rem)-1: return None
        for k in range(1, d+1):
            u = rem[k][1]
            if rem[k][0] == 0: return None
            a, b = min(u, v), max(u, v)
            if (a, b) in adj: return None
            adj.add((a, b))
            rem[k][0] -= 1
        rem[0][0] = 0
    return adj

def randic(D, adj):
    return sum(1.0/math.sqrt(D[u]*D[v]) for u, v in adj)

def rmin_local(D, adj, iters=4000, rng=random):
    """2-swap local search minimizing R."""
    adj = set(adj)
    edges = list(adj)
    def w(u, v): return 1.0/math.sqrt(D[u]*D[v])
    cur = sum(w(u, v) for u, v in adj)
    for _ in range(iters):
        (a, b), (c, d) = rng.sample(edges, 2)
        if len({a, b, c, d}) < 4: continue
        # try swap to (a,c),(b,d) or (a,d),(b,c)
        for (p, q), (r, s) in (((a, c), (b, d)), ((a, d), (b, c))):
            p, q = min(p, q), max(p, q); r, s = min(r, s), max(r, s)
            if (p, q) in adj or (r, s) in adj: continue
            delta = w(p, q) + w(r, s) - w(a, b) - w(c, d)
            if delta < -1e-15:
                adj.discard((a, b)); adj.discard((c, d))
                adj.add((p, q)); adj.add((r, s))
                edges = list(adj)
                cur += delta
                break
    return cur

def gap(D, rng, iters=4000):
    D = [d for d in D]  # keep zeros (isolated vertices matter for dev)
    if not is_graphical(D): return None
    core = D
    adj = havel_hakimi_assortative(core)
    if adj is None: return None
    r = rmin_local(core, adj, iters=iters, rng=rng)
    return dev(D) - r

def perturb(D, n_max, rng):
    D = D[:]
    op = rng.random()
    if op < 0.3 and len(D) < n_max:
        D.append(rng.randint(0, max(D) if D else 1))
    elif op < 0.4 and len(D) > 4:
        D.pop(rng.randrange(len(D)))
    else:
        i = rng.randrange(len(D))
        D[i] = max(0, min(len(D)-1, D[i] + rng.choice((-2, -1, 1, 2))))
    if sum(D) % 2:  # fix parity
        j = rng.randrange(len(D))
        D[j] = max(0, min(len(D)-1, D[j] + rng.choice((-1, 1))))
    return D

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    n_max = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    budget = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
    rng = random.Random(seed)
    best_overall = -1e18; best_D = None
    starts = []
    for k in range(4, min(n_max, 26)):
        base = [k-1]*k + [0]*max(0, min(n_max-k, k-2))
        starts.append(base)
    for _ in range(30):
        n = rng.randint(6, n_max)
        starts.append([rng.randint(0, n-1) for _ in range(n)])
    it_per = max(200, budget // max(1, len(starts)))
    for D0 in starts:
        D = D0[:]
        g = gap(D, rng)
        if g is None: g = -1e18
        for _ in range(it_per):
            D2 = perturb(D, n_max, rng)
            g2 = gap(D2, rng)
            if g2 is not None and (g2 > g or rng.random() < 0.02):
                D, g = D2, g2
            if g > best_overall:
                best_overall, best_D = g, sorted(D, reverse=True)
                print(f"best gap={g:.6f} n={len(D)} D={best_D}", flush=True)
                if g > 1e-9:
                    print("CANDIDATE VIOLATION (verify exactly!)", flush=True)
    print(f"FINAL best gap={best_overall:.6f} D={best_D}")

if __name__ == "__main__":
    main()

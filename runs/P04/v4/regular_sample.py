"""Wave 2c: mass sampling in the minimal-counterexample zone (delta >= 6, n >= 13).
Random d-regular graphs (d even) via pairing model + simplicity rejection.
Any minimal counterexample lives here (Fuchs-Gellert-Heinrich).
"""
import random, sys, time
import mincyc as M


def random_regular(n, d, rng, swaps_factor=20):
    """Start from circulant C_n(1..d/2) and randomize by double-edge swaps."""
    E = set()
    for v in range(n):
        for s in range(1, d // 2 + 1):
            E.add((min(v, (v + s) % n), max(v, (v + s) % n)))
    E = list(E)
    m = len(E)
    for _ in range(swaps_factor * m):
        i, j = rng.randrange(m), rng.randrange(m)
        if i == j:
            continue
        (a, b), (c, e) = E[i], E[j]
        if rng.random() < 0.5:
            p, q = (a, c), (b, e)
        else:
            p, q = (a, e), (b, c)
        p = (min(p), max(p))
        q = (min(q), max(q))
        if p[0] == p[1] or q[0] == q[1]:
            continue
        Eset = set(E)
        if p in Eset or q in Eset:
            continue
        E[i], E[j] = p, q
    return sorted(E)


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    samples = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    rng = random.Random(seed)
    lf = open(f"regular_s{seed}.txt", "a")
    combos = [(13, 6), (13, 8), (13, 10), (14, 6), (14, 8), (14, 10),
              (15, 6), (15, 8), (15, 10), (16, 6), (16, 8), (16, 10),
              (17, 6), (17, 8), (18, 6), (18, 8), (19, 6), (20, 6)]
    stats = {}
    t0 = time.time()
    for s in range(samples):
        n, d = combos[s % len(combos)]
        E = random_regular(n, d, rng)
        if E is None or not M.is_eulerian_simple(n, E):
            continue
        K = (n - 1) // 2
        ok, _ = M.decomposable_within(n, E, K, 300)
        key = (n, d)
        stats[key] = stats.get(key, 0) + 1
        if ok is False:
            lf.write(f"*** WITNESS *** n={n} d={d} edges={E}\n")
            lf.flush()
            print("WITNESS", n, d, E, flush=True)
            return
        if ok is None:
            lf.write(f"TIMEOUT n={n} d={d} edges={E}\n")
            lf.flush()
        if s % 500 == 0:
            msg = f"s={s} t={time.time()-t0:.0f}s stats={stats}"
            print(msg, flush=True)
            lf.write(msg + "\n")
            lf.flush()
    lf.write(f"=== done samples={samples} stats={stats} (all feasible) ===\n")
    lf.flush()
    print("done", stats)


if __name__ == "__main__":
    main()

"""Wave 2: exhaustive Hajos check over structured algebraic Eulerian families.

Families:
  A. ALL connected Eulerian circulants C_n(S), 13 <= n <= nmax:
     S subseteq {1..floor(n/2)}; degree = 2|S| - [n even and n/2 in S];
     require even degree at every vertex (so n/2 in S only allowed if n odd - i.e.
     never - or it gives odd degree; exclude n/2 for even n), connectivity
     gcd(S u {n}) == 1.  Includes Paley graphs and complements of cycles.
  B. Blow-ups: C_k[empty_t] (lexicographic product of a cycle with t independent
     vertices, 2t-regular) and C_k[K_t] variants with even degree.
  C. Triangular/Johnson graphs T(m) = L(K_m) for even m (2(m-2)-regular).

Every graph: check decomposable_within(n, E, K); log any infeasibility (witness).
"""
import itertools, math, sys, time
import mincyc as M


def circulant(n, S):
    E = set()
    for v in range(n):
        for s in S:
            E.add((min(v, (v + s) % n), max(v, (v + s) % n)))
    return sorted(E)


def check_and_log(name, n, E, lf, time_limit=600.0):
    K = (n - 1) // 2
    if not M.is_eulerian_simple(n, E):
        return "skip"
    t0 = time.time()
    ok, _ = M.decomposable_within(n, E, K, time_limit)
    dt = time.time() - t0
    deg = [0] * n
    for u, v in E:
        deg[u] += 1
        deg[v] += 1
    line = (f"{name} n={n} m={len(E)} deg={min(deg)}..{max(deg)} K={K} "
            f"feas={ok} t={dt:.1f}s")
    print(line, flush=True)
    lf.write(line + "\n")
    lf.flush()
    if ok is False:
        lf.write(f"*** WITNESS *** {name} edges={E}\n")
        lf.flush()
        return "WITNESS"
    return "ok" if ok else "timeout"


def main():
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    done = set()
    try:
        with open(f"circulants_n{nmax}.txt") as f:
            for line in f:
                if line.startswith("C"):
                    done.add(line.split(" n=")[0])
    except FileNotFoundError:
        pass
    lf = open(f"circulants_n{nmax}.txt", "a")
    count = 0
    for n in range(13, nmax + 1):
        half = n // 2
        gens = [s for s in range(1, half + 1)
                if not (n % 2 == 0 and s == half)]  # exclude n/2 for even n (odd deg)
        for r in range(1, len(gens) + 1):
            for S in itertools.combinations(gens, r):
                if math.gcd(n, math.gcd(*S) if len(S) > 1 else S[0]) != 1:
                    continue  # disconnected
                name = f"C{n}{tuple(S)}"
                if name in done:
                    continue
                E = circulant(n, S)
                res = check_and_log(name, n, E, lf)
                if res == "WITNESS":
                    return
                if res != "skip":
                    count += 1
    lf.write(f"=== circulants done nmax={nmax} checked={count} ===\n")
    print("done", count)


if __name__ == "__main__":
    main()

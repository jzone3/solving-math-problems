"""V2 attack 4: rotation-symmetric chord completions.

Any 4-regular 1H graph = C_n + chord 2-factor. A rotation i -> i+k (k | n) maps
C_n to itself, so a chord set invariant under it is consistent with unique
hamiltonicity (the automorphism fixes the unique HC setwise). Search over
rotation-invariant chord sets: chords are orbits {(i+t*k, j+t*k) : t} of size
n/gcd; every vertex needs chord-degree exactly 2. DFS over orbit additions,
checking HC count == 1 exactly (cutoff 2) after each addition (monotone, so
sound & complete within the symmetric family).

Usage: python3 symmetric.py n k [budget_s]
"""
import sys, time
from hcutil import hc_count

def orbit(n, k, u, v):
    """Chord orbit of (u,v) under i->i+k mod n; returns frozenset of edges."""
    es = set()
    t = 0
    while True:
        a, b = (u + t*k) % n, (v + t*k) % n
        e = (min(a, b), max(a, b))
        if e in es and t > 0:
            break
        es.add(e)
        t += k
        if t >= n * 2:
            break
    return frozenset(es)

def all_orbits(n, k):
    """Distinct chord orbits (no cycle edges, no loops)."""
    seen = set()
    out = []
    for u in range(k):
        for v in range(n):
            if v == u or (v - u) % n in (1, n - 1):
                continue
            ob = orbit(n, k, u, v)
            if ob not in seen:
                seen.add(ob)
                out.append(ob)
    return out

def chord_deg(n, edges):
    d = [0] * n
    for u, v in edges:
        d[u] += 1
        d[v] += 1
    return d

def search(n, k, budget):
    t0 = time.time()
    cyc = [(i, (i + 1) % n) for i in range(n)]
    cyc = [(min(e), max(e)) for e in cyc]
    orbits = all_orbits(n, k)
    best = [2 * n]
    stats = {"nodes": 0}

    def dfs(chords, start):
        stats["nodes"] += 1
        if time.time() - t0 > budget:
            return "timeout"
        d = chord_deg(n, chords)
        rem = sum(2 - x for x in d)
        if rem < best[0]:
            best[0] = rem
        if all(x == 2 for x in d):
            with open("WITNESS.txt", "a") as f:
                f.write(f"SYMM n={n} k={k} edges={sorted(set(cyc) | set(chords))}\n")
            print(f"!!! WITNESS n={n} k={k} !!!", flush=True)
            return "found"
        res = "done"
        for i in range(start, len(orbits)):
            ob = orbits[i]
            if any(e in set(chords) for e in ob):
                continue
            nd = chord_deg(n, list(chords) + list(ob))
            if any(x > 2 for x in nd):
                continue
            newch = list(chords) + list(ob)
            if hc_count(n, cyc + newch, cutoff=2) == 1:
                r = dfs(newch, i + 1)
                if r in ("found", "timeout"):
                    return r
                if r == "aborted":
                    res = "aborted"
        return res

    r = dfs([], 0)
    print(f"n={n} k={k} orbits={len(orbits)} result={r} "
          f"best_rem={best[0]} nodes={stats['nodes']} t={time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    n, k = int(sys.argv[1]), int(sys.argv[2])
    budget = float(sys.argv[3]) if len(sys.argv) > 3 else 600
    search(n, k, budget)

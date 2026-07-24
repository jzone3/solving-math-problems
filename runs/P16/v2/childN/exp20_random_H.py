"""Random search for smaller Conjecture-H counterexamples: random trees and
sparse connected graphs n in 11..39, exact interval check."""
import random
import sys
from fractions import Fraction
from collections import deque

def analyze_H(adj, n):
    deg = [len(adj[v]) for v in range(n)]
    m = [Fraction(sum(deg[u] for u in adj[v]), deg[v]) for v in range(n)]
    E = sorted({tuple(sorted((u, v))) for u in range(n) for v in adj[u]})
    nbrs = {e: [] for e in E}
    byv = {}
    for e in E:
        for v in e:
            byv.setdefault(v, []).append(e)
    for e in E:
        seen = set()
        for v in e:
            for f in byv[v]:
                if f != e and f not in seen:
                    seen.add(f)
                    nbrs[e].append(f)
    degL = {e: len(nbrs[e]) for e in E}
    z1 = {e: sum(degL[f] for f in nbrs[e]) for e in E}
    s = {e: deg[e[0]] + deg[e[1]] for e in E}
    zs = {e: sum(sum(s[f2] for f2 in [f]) * 0 + 0 for f in []) for e in E}
    zs = {e: sum(sum(s[g] for g in nbrs[f]) for f in nbrs[e]) for e in E}
    a44 = {e: 2 * ((deg[e[0]] - 1) ** 2 + (deg[e[1]] - 1) ** 2
                   + m[e[0]] * m[e[1]] - deg[e[0]] * deg[e[1]]) for e in E}
    R = max(a44.values())
    LO = HI = None
    ok0 = True
    for e in E:
        sig, kap = z1[e] - R, zs[e] - R * s[e]
        if sig > 0:
            v = Fraction(-kap) / sig
            HI = v if HI is None or v < HI else HI
        elif sig < 0:
            v = Fraction(-kap) / sig
            LO = v if LO is None or v > LO else LO
        elif kap > 0:
            ok0 = False
    smin = min(s.values())
    return ok0 and (HI is None or ((LO is None or LO <= HI) and HI > -smin))

def random_tree(n, skew):
    adj = {0: set()}
    for v in range(1, n):
        if random.random() < skew and v > 3:
            # prefer attaching to high-degree vertices (spiky trees)
            u = max(range(v), key=lambda t: len(adj[t]) + random.random() * 3)
        else:
            u = random.randrange(v)
        adj.setdefault(v, set()).add(u)
        adj[u].add(v)
    return adj

def main(iters=200000):
    best = None
    for it in range(iters):
        n = random.randint(11, 39)
        adj = random_tree(n, random.random())
        if not analyze_H(adj, n):
            if best is None or n < best[0]:
                E = sorted({tuple(sorted((u, v))) for u in range(n) for v in adj[u]})
                best = (n, E)
                print(f"H-counterexample n={n}: {E}", flush=True)
    print("best:", best[0] if best else None)

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 200000)

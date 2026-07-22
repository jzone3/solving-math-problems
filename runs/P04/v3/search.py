"""V3 main search: hunt for a Hajos counterexample at n=13..16 with the SAT
decider. For each candidate simple connected Eulerian graph G on n vertices,
ask SAT whether G decomposes into <= floor((n-1)/2) cycles. UNSAT => witness.

Candidate pools (biased toward the known minimum-counterexample structure:
3-connected, delta >= 6, dense):
  - random dense Eulerian graphs with delta >= 6 (parity-fix by toggling
    a random perfect pairing of odd-degree vertices),
  - all Eulerian circulants,
  - parity-preserving perturbations of tight graphs (K_n, tight hits found
    during the run): symmetric difference with a cycle of the ambient K_n.

Every graph found tight (min = bound, i.e. UNSAT at k-1) is logged as a
near-miss seed and perturbed further.
"""

import argparse
import random
import sys
import time
from itertools import combinations

import networkx as nx

from sat_decider import decompose_le_k


def g6(G):
    return nx.to_graph6_bytes(G, header=False).decode().strip()


def is_candidate(G, n, min_deg):
    return (G.number_of_nodes() == n
            and nx.is_connected(G)
            and all(d % 2 == 0 and d >= min_deg for _, d in G.degree()))


def random_eulerian_dense(n, min_deg, rng, p=None):
    p = p if p is not None else rng.uniform(0.55, 0.95)
    for _ in range(200):
        G = nx.gnp_random_graph(n, p, seed=rng.randint(0, 10**9))
        odd = [v for v in G.nodes if G.degree(v) % 2 == 1]
        rng.shuffle(odd)
        for i in range(0, len(odd), 2):
            u, v = odd[i], odd[i + 1]
            if G.has_edge(u, v):
                G.remove_edge(u, v)
            else:
                G.add_edge(u, v)
        if is_candidate(G, n, min_deg):
            return G
    return None


def eulerian_circulants(n):
    """All circulants C_n(S) with even degrees, connected."""
    half = [s for s in range(1, n // 2 + 1)]
    out = []
    for r in range(1, len(half) + 1):
        for S in combinations(half, r):
            G = nx.circulant_graph(n, S)
            if nx.is_connected(G) and all(d % 2 == 0 for _, d in G.degree()):
                out.append((S, G))
    return out


def perturb(G, n, rng, tries=50):
    """Toggle edges of a random cycle of K_n (parity-preserving); keep simple,
    connected, Eulerian."""
    for _ in range(tries):
        L = rng.choice([3, 4, 5, 6])
        verts = rng.sample(range(n), L)
        H = G.copy()
        for i in range(L):
            u, v = verts[i], verts[(i + 1) % L]
            if H.has_edge(u, v):
                H.remove_edge(u, v)
            else:
                H.add_edge(u, v)
        if nx.is_connected(H) and all(d % 2 == 0 for _, d in H.degree()):
            return H
    return None


def check(G, n, log, tag, check_tight=False):
    edges = list(G.edges())
    k = (n - 1) // 2
    t0 = time.time()
    sat, _ = decompose_le_k(n, edges, k)
    dt = time.time() - t0
    if not sat:
        print(f"*** COUNTEREXAMPLE CANDIDATE *** n={n} m={len(edges)} "
              f"{tag} g6={g6(G)}", flush=True)
        with open(log, "a") as f:
            f.write(f"COUNTEREXAMPLE n={n} m={len(edges)} tag={tag} g6={g6(G)}\n")
        return "CE"
    if check_tight:
        sat2, _ = decompose_le_k(n, edges, k - 1)
        if not sat2:
            with open(log, "a") as f:
                f.write(f"TIGHT n={n} m={len(edges)} tag={tag} g6={g6(G)} t={dt:.1f}s\n")
            return "TIGHT"
    return "OK"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--mode", choices=["random", "circulant", "perturb-tight"],
                    default="random")
    ap.add_argument("--count", type=int, default=1000)
    ap.add_argument("--min-deg", type=int, default=6)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--tight-every", type=int, default=20,
                    help="check tightness on every t-th graph")
    ap.add_argument("--log", default=None)
    args = ap.parse_args()
    n = args.n
    log = args.log or f"search_n{n}_{args.mode}.log"
    rng = random.Random(args.seed)
    stats = {"OK": 0, "TIGHT": 0, "CE": 0}
    t0 = time.time()

    if args.mode == "circulant":
        cands = eulerian_circulants(n)
        print(f"n={n}: {len(cands)} Eulerian circulants", flush=True)
        for i, (S, G) in enumerate(cands):
            r = check(G, n, log, f"circ{S}", check_tight=True)
            stats[r] += 1
            if (i + 1) % 25 == 0:
                print(f"[{i+1}/{len(cands)}] {stats} {time.time()-t0:.0f}s", flush=True)
    elif args.mode == "perturb-tight":
        # start from tight seeds: K_n plus tight graphs recorded in logs
        seeds = [nx.complete_graph(n)]
        import glob
        for lf in glob.glob(f"search_n{n}_*.log"):
            for line in open(lf):
                if line.startswith("TIGHT"):
                    s = line.split("g6=")[1].strip()
                    seeds.append(nx.from_graph6_bytes(s.encode()))
        print(f"n={n}: {len(seeds)} tight seeds", flush=True)
        i = 0
        while i < args.count:
            G = rng.choice(seeds)
            H = perturb(G, n, rng)
            if H is None:
                continue
            # random walk: perturb a few more times
            for _ in range(rng.randint(0, 3)):
                H2 = perturb(H, n, rng)
                if H2 is not None:
                    H = H2
            r = check(H, n, log, "perturb", check_tight=True)
            stats[r] += 1
            if r == "TIGHT":
                seeds.append(H)
            i += 1
            if i % 50 == 0:
                print(f"[{i}/{args.count}] {stats} seeds={len(seeds)} "
                      f"{time.time()-t0:.0f}s", flush=True)
    else:
        for i in range(args.count):
            G = random_eulerian_dense(n, args.min_deg, rng)
            if G is None:
                continue
            r = check(G, n, log, "rand",
                      check_tight=(i % args.tight_every == 0))
            stats[r] += 1
            if (i + 1) % 50 == 0:
                print(f"[{i+1}/{args.count}] {stats} {time.time()-t0:.0f}s", flush=True)

    print(f"DONE n={n} mode={args.mode} {stats} total={time.time()-t0:.0f}s", flush=True)
    with open(log, "a") as f:
        f.write(f"SUMMARY n={n} mode={args.mode} {stats} time={time.time()-t0:.0f}s\n")


if __name__ == "__main__":
    main()

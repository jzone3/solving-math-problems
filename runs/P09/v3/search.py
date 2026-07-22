#!/usr/bin/env python3
"""P09 Bollobas-Nikiforov, V3: fixed-omega annealed edge-flip search.

Conjecture (Bollobas-Nikiforov, JCTB 97 (2007), Conj. 1): for G != K_n with
m edges and clique number w:
    lam1^2 + lam2^2 <= 2m(1 - 1/w).

V3 framing: sweep fixed omega in {3..8}. Keep omega EXACTLY fixed during the
search by (a) planting a K_omega whose edges are never removed, and (b)
rejecting any edge-addition that would create a K_{omega+1}. Score to
maximize: ratio = (lam1^2 + lam2^2) / (2m(1-1/w)).  ratio > 1 => counterexample.

Adjacency stored as bitsets (python ints); eigenvalues via numpy eigvalsh.
"""
import argparse, json, math, random, time
import numpy as np


def popcount(x):
    return bin(x).count("1")


def has_clique(adj, mask, k):
    """Does the vertex set `mask` contain a k-clique?"""
    if k == 0:
        return True
    if popcount(mask) < k:
        return False
    while mask:
        v = (mask & -mask).bit_length() - 1
        mask &= mask - 1  # exclude v from future picks (branch: v in clique or not)
        if has_clique(adj, adj[v] & mask, k - 1):
            return True
        if popcount(mask) < k:
            return False
    return False


def creates_bigger_clique(adj, u, v, w):
    """If edge (u,v) is added, does a K_{w+1} appear? i.e. N(u)&N(v) has K_{w-1}."""
    return has_clique(adj, adj[u] & adj[v], w - 1)


def score(A, m, w):
    ev = np.linalg.eigvalsh(A)
    l1, l2 = ev[-1], ev[-2]
    bound = 2.0 * m * (1.0 - 1.0 / w)
    return (l1 * l1 + l2 * l2) / bound if bound > 0 else 0.0, l1, l2


def adj_to_matrix(adj, n):
    A = np.zeros((n, n))
    for i in range(n):
        row = adj[i]
        while row:
            j = (row & -row).bit_length() - 1
            row &= row - 1
            A[i, j] = 1.0
    return A


def edges_of(adj, n):
    return [(i, j) for i in range(n) for j in range(i + 1, n) if adj[i] >> j & 1]


def anneal(n, w, iters, seed, T0=0.02, T1=0.0003, p_init=None):
    rng = random.Random(seed)
    planted = {(i, j) for i in range(w) for j in range(i + 1, w)}
    adj = [0] * n
    for (i, j) in planted:
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    p = p_init if p_init is not None else rng.uniform(0.2, 0.8)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if (i, j) not in planted]
    rng.shuffle(pairs)
    for (i, j) in pairs:
        if rng.random() < p and not creates_bigger_clique(adj, i, j, w):
            adj[i] |= 1 << j
            adj[j] |= 1 << i
    A = adj_to_matrix(adj, n)
    m = int(A.sum()) // 2
    cur, l1, l2 = score(A, m, w)
    best = (cur, list(adj), m, l1, l2)
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / max(1, iters - 1))
        i, j = rng.sample(range(n), 2)
        if i > j:
            i, j = j, i
        if (i, j) in planted:
            continue
        present = adj[i] >> j & 1
        if present:
            adj[i] &= ~(1 << j); adj[j] &= ~(1 << i)
            A[i, j] = A[j, i] = 0.0
            m2 = m - 1
        else:
            if creates_bigger_clique(adj, i, j, w):
                continue
            adj[i] |= 1 << j; adj[j] |= 1 << i
            A[i, j] = A[j, i] = 1.0
            m2 = m + 1
        new, nl1, nl2 = score(A, m2, w)
        if new >= cur or rng.random() < math.exp((new - cur) / T):
            cur, m, l1, l2 = new, m2, nl1, nl2
            if cur > best[0]:
                best = (cur, list(adj), m, l1, l2)
                if cur > 1.0:
                    return best  # counterexample!
        else:  # revert
            if present:
                adj[i] |= 1 << j; adj[j] |= 1 << i
                A[i, j] = A[j, i] = 1.0
            else:
                adj[i] &= ~(1 << j); adj[j] &= ~(1 << i)
                A[i, j] = A[j, i] = 0.0
    return best


def verify_omega(adj, n, w):
    full = (1 << n) - 1
    return has_clique(adj, full, w) and not has_clique(adj, full, w + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--omega", type=int, required=True)
    ap.add_argument("--nmin", type=int, default=12)
    ap.add_argument("--nmax", type=int, default=40)
    ap.add_argument("--restarts", type=int, default=20)
    ap.add_argument("--iters", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    w = args.omega
    out = args.out or f"best_w{w}.json"
    rng = random.Random(args.seed)
    global_best = None
    t0 = time.time()
    for r in range(args.restarts):
        n = rng.randint(args.nmin, args.nmax)
        seed = rng.randrange(1 << 30)
        ratio, adj, m, l1, l2 = anneal(n, w, args.iters, seed)
        ok = verify_omega(adj, n, w)
        rec = {"omega": w, "n": n, "m": m, "ratio": ratio, "l1": l1, "l2": l2,
               "omega_verified": ok, "seed": seed, "edges": edges_of(adj, n)}
        if ok and (global_best is None or ratio > global_best["ratio"]):
            global_best = rec
            with open(out, "w") as f:
                json.dump(global_best, f)
        print(f"[w={w}] restart {r}: n={n} m={m} ratio={ratio:.5f} omega_ok={ok} "
              f"best={global_best['ratio']:.5f} t={time.time()-t0:.0f}s", flush=True)
        if global_best and global_best["ratio"] > 1.0:
            print("COUNTEREXAMPLE FOUND", flush=True)
            break
    print("DONE", json.dumps({k: global_best[k] for k in ("omega", "n", "m", "ratio")}), flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Blow-up limit attack for P09 (Bollobas-Nikiforov).

For a pattern graph H (no loops) with weights x on the simplex, the balanced
blow-up G = H[x*N] has (as N -> inf):
    lambda_1(G) ~ N * mu_1(B),  lambda_2(G) ~ N * mu_2(B)  (if mu_2 > 0),
    2m(G) ~ N^2 * (x^T A x),    omega(G) = omega(H)   (all x_i > 0),
where B = diag(sqrt(x)) A(H) diag(sqrt(x)). So the asymptotic ratio is
    R(H, x) = (mu_1(B)^2 + max(mu_2(B),0)^2) / (x^T A x * (1 - 1/omega(H))).
If R > 1 strictly for some H, x, then large integer blow-ups violate the
conjecture -> explicit counterexample. We maximize R over the simplex for
every pattern H with omega(H) >= 3 from geng, multi-restart projected
gradient (finite-diff free: uses eigenvector-based analytic gradient).

Note H itself is a blow-up of itself (x uniform), and every graph appears as
its own pattern; the sup over all H of max_x R(H,x) >= sup over all blow-up
sequences. Zero weights degenerate to induced subgraphs (allowed; omega can
drop, making the true bound easier -- we recompute omega on the support).
"""
import argparse, subprocess, sys
import numpy as np

sys.setrecursionlimit(100000)
from search import has_clique  # bitset clique query


def clique_number_adj(adjmask, n):
    full = (1 << n) - 1
    k = 1
    while k < n and has_clique(adjmask, full, k + 1):
        k += 1
    return k


def g6_to_adj(line):
    s = line.strip()
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for v in data[1:]:
        bits += [(v >> i) & 1 for i in range(5, -1, -1)]
    A = np.zeros((n, n))
    adjmask = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                A[i, j] = A[j, i] = 1.0
                adjmask[i] |= 1 << j
                adjmask[j] |= 1 << i
            idx += 1
    return A, adjmask, n


def ratio_and_grad(A, x, w):
    """R(x) and its gradient on the simplex tangent space."""
    sx = np.sqrt(x)
    B = A * np.outer(sx, sx)
    ev, V = np.linalg.eigh(B)
    mu1, mu2 = ev[-1], ev[-2]
    v1, v2 = V[:, -1], V[:, -2]
    q = x @ A @ x
    if q <= 0:
        return 0.0, np.zeros_like(x)
    num = mu1 * mu1 + (mu2 * mu2 if mu2 > 0 else 0.0)
    den = q * (1.0 - 1.0 / w)
    R = num / den
    # d mu_k / d x_i = v_k^T (dB/dx_i) v_k ; dB/dx_i = A_i-row/col * d sqrt term
    # B_{ab} = A_ab sqrt(x_a x_b): dB_ab/dx_i = A_ab sqrt(x_b/x_i)/2 [a=i] + sym
    g = np.zeros_like(x)
    eps = 1e-12
    for k, (mu, v) in enumerate([(mu1, v1), (mu2, v2)]):
        if k == 1 and mu2 <= 0:
            continue
        # v^T (dB/dx_i) v = v_i * (A @ (sqrt(x)*v))_i / sqrt(x_i)
        dmu = v * (A @ (sx * v)) / np.maximum(sx, eps)
        g += 2 * mu * dmu / den
    g -= num / den * (2 * (A @ x)) / q
    g -= g.mean()  # project onto simplex tangent
    return R, g


def maximize(A, adjmask, n, restarts, iters, rng):
    best = (0.0, None)
    for r in range(restarts):
        x = rng.dirichlet(np.ones(n)) if r else np.full(n, 1.0 / n)
        for it in range(iters):
            supp = x > 1e-9
            # omega on the support of x (zero-weight parts vanish)
            if supp.all():
                w = clique_number_adj(adjmask, n)
            else:
                idx = [int(i) for i in np.where(supp)[0]]
                mask = 0
                for i in idx:
                    mask |= 1 << i
                sub = [adjmask[i] & mask for i in range(n)]
                w = 1
                while w < len(idx) and has_clique(sub, mask, w + 1):
                    w += 1
            if w < 2:
                break
            if w == 2:
                break  # triangle-free: proved case
            R, g = ratio_and_grad(A, x, w)
            if R > best[0]:
                best = (R, x.copy())
            step = 0.1 / (1 + it * 0.02)
            x = x + step * g
            x = np.maximum(x, 0)
            s = x.sum()
            if s <= 0:
                break
            x /= s
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--part", default=None, help="res/mod for geng")
    ap.add_argument("--restarts", type=int, default=6)
    ap.add_argument("--iters", type=int, default=120)
    ap.add_argument("--report", type=float, default=0.999)
    args = ap.parse_args()
    cmd = ["nauty-geng", "-q", str(args.n)]
    if args.part:
        cmd.append(args.part)
    rng = np.random.default_rng(12345)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    count = 0
    gmax = (0.0, None, None)
    for line in proc.stdout:
        A, adjmask, n = g6_to_adj(line)
        w = clique_number_adj(adjmask, n)
        if w < 3 or w == n:
            continue  # proved cases (triangle-free; complete multipartite handled too but keep)
        count += 1
        R, x = maximize(A, adjmask, n, args.restarts, args.iters, rng)
        if R > gmax[0]:
            gmax = (R, line.strip(), x)
        if R > 1 + 1e-7:
            print(f"VIOLATION-CANDIDATE {line.strip()} R={R:.12f} x={list(x)}",
                  flush=True)
        elif R > args.report:
            print(f"near {line.strip()} R={R:.9f}", flush=True)
    print(f"DONE n={args.n} patterns={count} maxR={gmax[0]:.12f} "
          f"at {gmax[1]} x={None if gmax[2] is None else [round(v,5) for v in gmax[2]]}",
          flush=True)


if __name__ == "__main__":
    main()

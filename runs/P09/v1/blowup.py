#!/usr/bin/env python3
"""Weighted-blowup (graphon-regime) search for the Bollobas-Nikiforov conjecture.

For a profile graph H with vertex weights w on the simplex, the balanced blowup
G_n (parts of size ~ n*w_i, independent sets inside parts, complete bipartite
between parts joined in H) satisfies, as n -> infinity:

    lambda_1(G_n)/n -> mu_1(S),  lambda_2(G_n)/n -> max(mu_2(S), 0)
    m(G_n)/n^2     -> e_w = (1/2) sum_{i!=j} A_ij w_i w_j
    omega(G_n)      = omega(H)

where S = diag(sqrt(w)) A_H diag(sqrt(w)).  The conjecture in this regime says

    mu_1^2 + max(mu_2,0)^2 <= 2 e_w (1 - 1/omega(H)).

We maximize ratio(w) = (mu1^2 + mu2plus^2) / (2 e_w (1 - 1/omega(H))) over the
weight simplex by projected gradient ascent with random restarts, for every
connected profile H on 3..nmax vertices (geng).  ratio > 1 + eps for any (H, w)
would give an asymptotic counterexample (and by continuity a finite one).

Gradient: with x = sqrt(w), S = diag(x) A diag(x), and unit eigvec v_k of S,
d mu_k / d x_i = 2 v_k[i] * (A diag(x) v_k)[i].
"""
import sys, subprocess
import numpy as np

EPS = 1e-6


def g6_to_A(s):
    data = [ord(c) - 63 for c in s.strip()]
    n = data[0]
    bits = []
    for ch in data[1:]:
        bits.extend((ch >> k) & 1 for k in range(5, -1, -1))
    A = np.zeros((n, n))
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                A[i, j] = A[j, i] = 1.0
            idx += 1
    return A


def max_clique_A(A):
    n = len(A)
    adj = [0] * n
    for i in range(n):
        for j in range(n):
            if A[i, j]:
                adj[i] |= 1 << j
    best = 0

    def expand(P, size):
        nonlocal best
        if not P:
            best = max(best, size)
            return
        if size + bin(P).count('1') <= best:
            return
        v = P.bit_length() - 1
        expand(P & adj[v], size + 1)
        expand(P & ~(1 << v), size)

    expand((1 << n) - 1, 0)
    return best


def ratio_and_grad(A, w, om):
    x = np.sqrt(w)
    S = A * np.outer(x, x)
    vals, vecs = np.linalg.eigh(S)
    mu1, mu2 = vals[-1], vals[-2]
    v1, v2 = vecs[:, -1], vecs[:, -2]
    ew = 0.5 * w @ A @ w
    denom = 2.0 * ew * (1.0 - 1.0 / om)
    mu2p = max(mu2, 0.0)
    num = mu1 * mu1 + mu2p * mu2p
    R = num / denom
    # gradients wrt w_i (via x): dmu/dw_i = dmu/dx_i / (2 x_i)
    Ax = A * x  # A diag(x)
    g_num = 2 * mu1 * (v1 * (Ax @ v1)) / np.maximum(x, 1e-12)
    if mu2p > 0:
        g_num += 2 * mu2 * (v2 * (Ax @ v2)) / np.maximum(x, 1e-12)
    g_den = 2.0 * (A @ w) * (1.0 - 1.0 / om)
    grad = (g_num * denom - num * g_den) / (denom * denom)
    return R, grad


def project_simplex(v):
    u = np.sort(v)[::-1]
    css = np.cumsum(u) - 1
    ind = np.arange(1, len(v) + 1)
    cond = u - css / ind > 0
    rho = ind[cond][-1]
    theta = css[cond][-1] / rho
    return np.maximum(v - theta, 0)


def optimize(A, om, restarts, iters, rng):
    n = len(A)
    best = -1.0
    bestw = None
    for r in range(restarts):
        w = rng.dirichlet(np.ones(n)) if r else np.ones(n) / n
        step = 0.1
        Rprev = -1
        for _ in range(iters):
            w = np.maximum(w, 1e-9)
            w /= w.sum()
            R, g = ratio_and_grad(A, w, om)
            if R < Rprev - 1e-12:
                step *= 0.5
                if step < 1e-7:
                    break
            Rprev = R
            w = project_simplex(w + step * g)
        if Rprev > best:
            best, bestw = Rprev, w.copy()
    return best, bestw


def main_stdin():
    """Read g6 profiles from stdin (one per line); used for parallel n=9 runs."""
    restarts = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    rng = np.random.default_rng(int(sys.argv[4]) if len(sys.argv) > 4 else 0)
    best = (-1, None, None)
    cnt = 0
    for line in sys.stdin:
        A = g6_to_A(line)
        om = max_clique_A(A)
        R, w = optimize(A, om, restarts, iters, rng)
        cnt += 1
        if R > best[0]:
            best = (R, line.strip(), w)
        if R > 1 + EPS:
            print(f"VIOLATION?! H={line.strip()} omega={om} ratio={R:.9f} w={w}", flush=True)
    print(f"[stdin] profiles={cnt} best_ratio={best[0]:.9f} H={best[1]} w={np.round(best[2],4)}")


def main():
    if sys.argv[1] == 'stdin':
        return main_stdin()
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    restarts = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 250
    rng = np.random.default_rng(2026)
    globalbest = (-1, None, None)
    for n in range(3, nmax + 1):
        # -c connected suffices: blowup ratio of disconnected H is dominated by
        # one component (lambda1, lambda2 both from best component's blowup or
        # split across components == disjoint-union case already searched finitely;
        # still, run connected profiles which carry the graphon-regime content).
        proc = subprocess.Popen(['nauty-geng', '-qc', str(n)], stdout=subprocess.PIPE, text=True)
        cnt = 0
        nbest = (-1, None, None)
        for line in proc.stdout:
            A = g6_to_A(line)
            om = max_clique_A(A)
            if om == n:  # complete profile: blowup = complete multipartite (proved class), still check
                pass
            R, w = optimize(A, om, restarts, iters, rng)
            cnt += 1
            if R > nbest[0]:
                nbest = (R, line.strip(), w)
            if R > 1 + EPS:
                print(f"VIOLATION?! n={n} H={line.strip()} omega={om} ratio={R:.9f} w={w}")
        print(f"[n={n}] profiles={cnt} best_ratio={nbest[0]:.9f} H={nbest[1]} w={np.round(nbest[2],4)}", flush=True)
        if nbest[0] > globalbest[0]:
            globalbest = nbest
    print("GLOBAL BEST:", globalbest[0], globalbest[1], np.round(globalbest[2], 5))


if __name__ == '__main__':
    main()

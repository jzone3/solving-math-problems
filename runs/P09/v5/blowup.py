"""Continuous relaxation over blowup families (new encoding).

For a pattern graph H and vertex weights x >= 0, sum x = 1, the independent-set
blowup H[x] (as size N -> inf with parts ~ x_i N) has:
  lam_k(H[x])/N -> mu_k, the k-th largest eigenvalue of B = D^{1/2} A_H D^{1/2},
     D = diag(x)   (nonzero spectrum of the weighted quotient),
  2m/N^2 -> x^T A_H x,   omega(H[x]) = omega(H).
So BN restricted to arbitrarily large blowups of H is equivalent to
  f_H(x) = mu_1^2 + mu_2^2 - (1 - 1/omega(H)) * x^T A x <= 0  for all x in simplex.
If max_x f_H(x) > 0 for ANY pattern H, a finite counterexample exists (rational x,
large N). We maximize f_H over the simplex (projected gradient + random restarts)
for ALL connected pattern graphs H with 4 <= |H| <= 8 and omega(H) >= 3
(omega=2 blowups are triangle-free: proved; also covered anyway for |H|<=7).

Usage: python3 blowup.py <n> [res] [mod]
"""
import sys, subprocess
import numpy as np
from core import max_clique

def g6_to_adj(line, n):
    nb = n * (n - 1) // 2
    nbytes = (nb + 5) // 6
    arr = np.frombuffer(line[1:1 + nbytes], dtype=np.uint8) - 63
    bits = ((arr[:, None] >> np.arange(5, -1, -1)[None, :]) & 1).reshape(-1)[:nb]
    A = np.zeros((n, n))
    k = 0
    for j in range(1, n):
        for i in range(j):
            A[i, j] = A[j, i] = bits[k]; k += 1
    return A

def f_and_grad(A, x, coef):
    sx = np.sqrt(x)
    B = A * np.outer(sx, sx)
    w, V = np.linalg.eigh(B)
    mu1, mu2 = w[-1], w[-2]
    v1, v2 = V[:, -1], V[:, -2]
    quad = x @ A @ x
    f = max(mu1, 0) ** 2 + max(mu2, 0) ** 2 - coef * quad
    # d mu / d x_i  for B = diag(sx) A diag(sx):
    # dB/dx_i = (1/(2 sx_i)) (e_i sx^T A_i-row sym) -> use v^T dB v = v_i/sx_i * (A (sx*v))_i
    g = np.zeros_like(x)
    for mu, v in ((mu1, v1), (mu2, v2)):
        if mu > 0:
            Av = A @ (sx * v)
            with np.errstate(divide="ignore", invalid="ignore"):
                dmu = np.where(sx > 1e-12, v * Av / sx, 0.0)
            g += 2 * mu * dmu
    g -= coef * 2 * (A @ x)
    return f, g

def maximize(A, coef, rng, restarts=12, iters=400):
    n = A.shape[0]
    best = -1e9
    for r in range(restarts):
        x = rng.dirichlet(np.ones(n)) if r else np.ones(n) / n
        lr = 0.05
        for t in range(iters):
            f, g = f_and_grad(A, x, coef)
            # project gradient onto simplex tangent, step, re-project
            g = g - g.mean()
            x = x + lr * g
            x = np.maximum(x, 0)
            s = x.sum()
            if s < 1e-12:
                break
            x /= s
        f, _ = f_and_grad(A, x, coef)
        best = max(best, f)
    return best

def run(n, res=0, mod=1):
    rng = np.random.default_rng(res + 1)
    cmd = ["nauty-geng", "-cq", str(n)]
    if mod > 1:
        cmd.append(f"{res}/{mod}")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    total = 0; checked = 0; worst = -1e9; best_name = None
    for line in p.stdout:
        total += 1
        A = g6_to_adj(line.strip(), n)
        w = max_clique(A)
        if w < 3 or w >= n:
            continue
        checked += 1
        coef = 1 - 1 / w
        f = maximize(A, coef, rng)
        if f > worst:
            worst = f; best_name = line.strip().decode()
            if f > 1e-7:
                print(f"BLOWUP VIOLATION?! n={n} g6={best_name} f={f}", flush=True)
        if checked % 500 == 0:
            print(f"... n={n} {res}/{mod}: {total} seen {checked} optimized worst={worst:+.6f} ({best_name})", flush=True)
    print(f"SUMMARY blowup n={n} {res}/{mod}: total={total} optimized={checked} max_f={worst:+.6f} at {best_name}", flush=True)

if __name__ == "__main__":
    n = int(sys.argv[1])
    res = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    mod = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    run(n, res, mod)

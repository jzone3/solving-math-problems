"""Regress the exact ground state h* (Perron of diag(T)^{-1}B) against local
invariants, on the 627 hard graphs + 921 near-equality graphs at n<=8.

Within each graph normalize h* so that sum h*_i d_i / sum d_i^2 = 1 (best
scale match to d), then regress y_i := log(h*_i/d_i) on features:
  1, log d, log m, sig, t_i (=sum (sig_i+sig_j) w_ij), s2 (2-step deg sum/d),
  msig (avg sigma of neighbors), excess = t_i - 1.
"""
import numpy as np
from common import g6_to_adj, build, perron_h

hard = list(np.load("hard_g6.npy")) + list(np.load("neareq_g6.npy"))
hard = sorted(set(hard))
rows = []
ys = []
for g6 in hard:
    G = build(g6_to_adj(g6))
    rho, h = perron_h(G["B"], G["T"])
    d, m, sig, w, edges = G["d"], G["m"], G["sig"], G["w"], G["edges"]
    n = G["n"]
    t = np.zeros(n)
    for k, (i, j) in enumerate(edges):
        t[i] += (sig[i] + sig[j]) * w[k]
        t[j] += (sig[i] + sig[j]) * w[k]
    scale = (h @ d) / (d @ d)
    h = h / scale
    msig = (G["A"] @ sig) / d
    s2 = (G["A"] @ (G["A"] @ d)) / d  # avg over neighbors of s_j
    for i in range(n):
        ys.append(np.log(h[i] / d[i]))
        rows.append([1.0, np.log(d[i]), np.log(m[i]), sig[i], t[i],
                     msig[i], np.log(s2[i]), t[i] - 1.0 if t[i] > 1 else 0.0])

X = np.array(rows); y = np.array(ys)
names = ["1", "log d", "log m", "sig", "t", "msig", "log s2", "(t-1)+"]
coef, res, *_ = np.linalg.lstsq(X, y, rcond=None)
pred = X @ coef
print("R2 =", 1 - np.var(y - pred) / np.var(y))
for nm, c in zip(names, coef):
    print(f"  {nm:8s} {c:+.4f}")
print("rms residual", np.sqrt(np.mean((y - pred) ** 2)), "  std y", y.std())

# simple sub-models
for cols, lab in [([0, 1], "log d"), ([0, 2], "log m"), ([0, 1, 2], "log d + log m"),
                  ([0, 4], "t"), ([0, 1, 2, 4], "log d+log m+t")]:
    c2, *_ = np.linalg.lstsq(X[:, cols], y, rcond=None)
    p2 = X[:, cols] @ c2
    print(lab, "R2 =", round(1 - np.var(y - p2) / np.var(y), 4), np.round(c2, 3))

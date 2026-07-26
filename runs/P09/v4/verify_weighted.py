#!/usr/bin/env python3
"""Standalone check of the weighted witness in flow_weighted_witness.txt.

Claim verified here: the NAIVE WEIGHTED ANALOGUE of Bollobas-Nikiforov,

    l1(W)^2 + l2(W)^2  <=  2m(W) * t(W),
    2m(W) = sum_ij W_ij,   t(W) = max_{x in simplex} x^T W x,

is FALSE for symmetric W with entries in [0,1]: the 16x16 matrix in
flow_weighted_witness.txt has l1^2+l2^2 - 2m*t > 0.

NOTE: this does NOT contradict the (graph) Bollobas-Nikiforov conjecture.
Graphs converging to a fractional-valued W have clique number -> infinity,
so the graph inequality's rhs tends to 2m, not to 2m*t(W).  t(W) equals
1 - 1/omega exactly only for 0/1 adjacency matrices (Motzkin-Straus).

t(W) is computed EXACTLY (up to linear-algebra roundoff, with a safety
margin) by enumerating all 2^16 support sets: any maximizer of x^T W x on
the simplex is a stationary point on the interior of some face, i.e.
solves W_S x = c 1, x >= 0, sum x = 1 on its support S.

Dependencies: numpy only.  Prints PASS if the strict violation holds with
margin > 1e-6.
"""
import numpy as np

rows = [l.split() for l in open("flow_weighted_witness.txt").read().splitlines() if l.strip()]
W = np.array([[float(x) for x in r] for r in rows])
n = W.shape[0]
assert W.shape == (n, n) and np.allclose(W, W.T) and n == 16
assert np.all(W >= 0) and np.all(W <= 1) and np.allclose(np.diag(W), 0)

ev = np.linalg.eigvalsh(W)
l1, l2 = ev[-1], ev[-2]
two_m = W.sum()

t = 0.0
for mask in range(1, 1 << n):
    S = [i for i in range(n) if mask >> i & 1]
    k = len(S)
    if k == 1:
        continue
    A = W[np.ix_(S, S)]
    try:
        y = np.linalg.solve(A, np.ones(k))
    except np.linalg.LinAlgError:
        continue
    s = y.sum()
    if abs(s) < 1e-12:
        continue
    x = y / s
    if (x < -1e-9).any():
        continue
    x = np.clip(x, 0, None)
    x /= x.sum()
    val = x @ A @ x
    if val > t:
        t = val
# also sample the simplex densely as a safety net (can only raise t)
rng = np.random.default_rng(0)
for _ in range(200000):
    x = rng.dirichlet(np.ones(n))
    val = x @ W @ x
    if val > t:
        t = val

gap = l1 * l1 + l2 * l2 - two_m * t
print(f"n={n}  l1={l1:.10f}  l2={l2:.10f}  2m={two_m:.6f}  t={t:.10f}")
print(f"gap = l1^2+l2^2 - 2m*t = {gap:.10f}")
if gap > 1e-6:
    print("PASS: the naive weighted (Motzkin-Straus) analogue of Bollobas-Nikiforov is violated by this W")
    print("      (no bearing on the graph conjecture; see docstring)")
else:
    print("FAIL")

"""Machine-check: dev(L)^2 == (sum d^2 + 2m)/n - (2m/n)^2 on random graphs."""
import numpy as np

rng = np.random.default_rng(0)
for trial in range(200):
    n = rng.integers(3, 30)
    p = rng.uniform(0.05, 0.9)
    A = (rng.random((n, n)) < p).astype(float)
    A = np.triu(A, 1)
    A = A + A.T
    d = A.sum(axis=1)
    L = np.diag(d) - A
    eig = np.linalg.eigvalsh(L)
    var_eig = np.mean((eig - eig.mean()) ** 2)
    m = d.sum() / 2
    var_formula = (np.sum(d ** 2) + 2 * m) / n - (2 * m / n) ** 2
    assert abs(var_eig - var_formula) < 1e-8, (n, var_eig, var_formula)
print("PASS: dev(L)^2 = (sum d^2 + 2m)/n - (2m/n)^2 on 200 random graphs")

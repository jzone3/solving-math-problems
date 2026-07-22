"""Adversarial test of the Case-1 lemma (pure degree-sequence statement):

  LEMMA?  If 8m^2 >= A n  (A = sum d(d+1), 2m = sum d, 0 <= d_i <= n-1)
          then 4m^2 >= A * exp( (1/2m) * sum d_i ln d_i ).

(If true, combined with R >= m * GM(edge weights) it proves Case 1 of WoW 129:
 4mR >= A in the dense regime.)
Continuous relaxation, random multi-start projected gradient / scipy SLSQP,
maximize g = ln A + H - ln(4m^2) subject to the density constraint.
Positive g found => lemma false (then check graphicality); else supports lemma.
"""
import numpy as np
from scipy.optimize import minimize

rng = np.random.default_rng(1)

def neg_g(d, n):
    d = np.clip(d, 1e-9, n - 1)
    m2 = d.sum()
    A = (d * d).sum() + m2
    H = (d * np.log(d)).sum() / m2
    return -(np.log(A) + H - np.log(m2 * m2))

def constraint(d, n):
    d = np.clip(d, 1e-9, n - 1)
    m2 = d.sum()
    A = (d * d).sum() + m2
    return 2 * m2 * m2 - A * n   # >= 0

worst = None
for n in [6, 10, 20, 50, 100, 300]:
    best = -1e18
    bestd = None
    for trial in range(60):
        d0 = rng.uniform(0.5, n - 1, size=n)
        res = minimize(neg_g, d0, args=(n,),
                       constraints=[{'type': 'ineq', 'fun': constraint, 'args': (n,)}],
                       bounds=[(1e-6, n - 1)] * n,
                       method='SLSQP', options={'maxiter': 500, 'ftol': 1e-12})
        val = -res.fun
        if constraint(res.x, n) > -1e-6 and val > best:
            best = val; bestd = np.sort(np.clip(res.x, 0, n-1))[::-1]
    print(f"n={n}: max g = {best:.9f}  top degrees {np.round(bestd[:6],3)} "
          f"low {np.round(bestd[-3:],3)}")
    if worst is None or best > worst[0]:
        worst = (best, n)
print("overall max g:", worst)

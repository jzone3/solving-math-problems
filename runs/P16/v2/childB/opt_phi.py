"""For graphs where the power-family fails, optimize over ALL positive concave
phi (values at the finite set of relevant points, concavity as linear
constraints) to minimize F(phi) = max_e [d_i phi(m_i)/phi(d_j) + d_j phi(m_j)/phi(d_i) - 2].
If even optimal phi cannot get F <= max term - 2, the edge-CW/Jensen family
cannot prove the bound.
"""
import numpy as np, math, sys
from scipy.optimize import minimize
from harness import graphs, g6_adj

def graph_data(g6):
    A = g6_adj(g6); nn = A.shape[0]
    d = A.sum(1); m = A @ d / d
    E = [(i, j) for i in range(nn) for j in range(i + 1, nn) if A[i, j]]
    return d, m, E

def targets(d, m, E):
    a44 = [2*((d[i]-1)**2+(d[j]-1)**2+m[i]*m[j]-d[i]*d[j]) for i, j in E]
    a46 = [2*(d[i]**2+d[j]**2)-16*d[i]*d[j]/(m[i]+m[j])+4 for i, j in E]
    s44 = max(math.sqrt(x) if x >= 0 else -math.inf for x in a44)
    s46 = max(math.sqrt(x) if x >= 0 else -math.inf for x in a46)
    return s44, s46

def optimal_F(d, m, E):
    pts = sorted(set(list(d) + list(m)))
    idx = {p: k for k, p in enumerate(pts)}
    K = len(pts)
    # variables: u = log phi(pts). concavity of phi (not log phi!) constraints:
    # for consecutive triples p1<p2<p3: (p3-p2)phi1 + (p2-p1)phi3 <= (p3-p1)phi2
    def F(u):
        phi = np.exp(u)
        return max(d[i]*phi[idx[m[i]]]/phi[idx[d[j]]] + d[j]*phi[idx[m[j]]]/phi[idx[d[i]]] - 2
                   for i, j in E)
    cons = []
    for k in range(1, K - 1):
        p1, p2, p3 = pts[k-1], pts[k], pts[k+1]
        def con(u, k=k, c1=(p3-p2), c3=(p2-p1), c2=(p3-p1)):
            phi = np.exp(u)
            return c2*phi[k] - c1*phi[k-1] - c3*phi[k+1]
        cons.append({"type": "ineq", "fun": con})
    best = math.inf
    rng = np.random.default_rng(0)
    for trial in range(12):
        a0 = rng.uniform(0, 1)
        u0 = a0 * np.log(pts)
        r = minimize(F, u0, constraints=cons, method="SLSQP",
                     options={"maxiter": 400, "ftol": 1e-10})
        if r.fun < best: best = r.fun
    return best

def run(nmax):
    avals = [i/20 for i in range(21)]
    fails44 = []; fails46 = []
    for n in range(2, nmax + 1):
        for g6 in graphs(n):
            d, m, E = graph_data(g6)
            s44, s46 = targets(d, m, E)
            Fg = min(max(d[i]*m[i]**a/d[j]**a + d[j]*m[j]**a/d[i]**a - 2 for i, j in E)
                     for a in avals)
            if Fg > s46 + 1e-9: fails46.append(g6)
            if Fg > s44 + 1e-9: fails44.append(g6)
    print(f"grid-fail counts: 44={len(fails44)} 46={len(fails46)}")
    for tag, fails, tsel in (("46", fails46, 1), ("44", fails44, 0)):
        still = []
        for g6 in fails:
            d, m, E = graph_data(g6)
            t = targets(d, m, E)[tsel]
            Fopt = optimal_F(d, m, E)
            if Fopt > t + 1e-7:
                still.append((g6, Fopt - t))
        print(f"bound {tag}: {len(still)} graphs where even OPTIMAL concave phi fails")
        for g, gap in sorted(still, key=lambda x: -x[1])[:10]:
            print("   ", g, f"deficit {gap:.4g}")

if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 8)

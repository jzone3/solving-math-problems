"""childJ exp5: numeric verification of new identities, exhaustive n<=7 + random.

I1: sigma_e = (s_e-2)^2 + T_e - R,  T_e = d_i m_i + d_j m_j - 2 d_i d_j
I2: arg44_e = (s_e-2)^2 + (d_i-d_j)^2 + 2(m_i m_j - d_i d_j)
I3: T_e = sum_{k~i,k!=j}(d_k-d_j) + sum_{l~j,l!=i}(d_l-d_i)
I4: (A_L^2 1)_e = (s_e-2)^2 + T_e
"""
import numpy as np

from common import graphs, g6_adj, graph_data, arg44, line_graph_adj

bad = 0
tot = 0
for n in range(3, 8):
    for g6 in graphs(n):
        A = g6_adj(g6)
        d, m, E = graph_data(A)
        R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
        AL = line_graph_adj(E)
        s = np.array([d[i] + d[j] for i, j in E])
        z1 = AL @ (AL @ np.ones(len(E)))
        nbr = [np.nonzero(A[i])[0] for i in range(len(d))]
        for a, (i, j) in enumerate(E):
            tot += 1
            T = d[i] * m[i] + d[j] * m[j] - 2 * d[i] * d[j]
            ok1 = abs((z1[a] - R) - ((s[a] - 2) ** 2 + T - R)) < 1e-8
            ok2 = abs(arg44(d[i], d[j], m[i], m[j]) -
                      ((s[a] - 2) ** 2 + (d[i] - d[j]) ** 2 +
                       2 * (m[i] * m[j] - d[i] * d[j]))) < 1e-8
            T3 = (sum(d[k] - d[j] for k in nbr[i] if k != j) +
                  sum(d[l] - d[i] for l in nbr[j] if l != i))
            ok3 = abs(T - T3) < 1e-8
            ok4 = abs(z1[a] - ((s[a] - 2) ** 2 + T)) < 1e-8
            if not (ok1 and ok2 and ok3 and ok4):
                bad += 1
                print("BAD", g6, a, ok1, ok2, ok3, ok4)
print(f"identity check: {tot} edges, bad={bad}")

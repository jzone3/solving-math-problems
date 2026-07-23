"""childD: search for structured certificates y>0 with (A_L^2 y)_e <= arg46(e) y_e
for all edges (pointwise second-order certificate => Bound 46). delta>=2 graphs.
Candidates:
  edge-form y_e = f(local data);  vertex-form y = R^T x  (uses A_L^2 R^T x = R^T (Q-2I)^2 x).
Report per-candidate: #graphs failing, worst relative deficit.
"""
import numpy as np, subprocess, sys, math

def graphs(n, extra="-d2"):
    p = subprocess.Popen(f"nauty-geng -qc {extra} {n}", shell=True,
                         stdout=subprocess.PIPE, text=True)
    for line in p.stdout:
        yield line.strip()

def g6_adj(g6):
    data = [ord(c) - 63 for c in g6]
    n = data[0]
    bits = []
    for v in data[1:]:
        bits += [(v >> k) & 1 for k in range(5, -1, -1)]
    A = np.zeros((n, n))
    idx = 0
    for j in range(1, n):
        for i in range(j):
            A[i, j] = A[j, i] = bits[idx]
            idx += 1
    return A

def build(g6):
    A = g6_adj(g6)
    n = A.shape[0]
    d = A.sum(1)
    m = A @ d / d
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]
    E = len(edges)
    arg = np.array([2*(d[i]**2+d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j]) + 4 for i, j in edges])
    AL = np.zeros((E, E))
    for a in range(E):
        ia, ja = edges[a]
        for b in range(a+1, E):
            if len({ia, ja} & {edges[b][0], edges[b][1]}):
                AL[a, b] = AL[b, a] = 1
    return A, d, m, edges, arg, AL

CANDS = ["one", "s", "s2", "p", "sqrtarg", "arg", "smm", "smm2",
         "x1", "xd", "xdm", "xd2", "xsq"]

def yvec(c, d, m, edges, arg, A):
    if c == "one": return np.ones(len(edges))
    if c == "s":   return np.array([d[i]+d[j] for i,j in edges])
    if c == "s2":  return np.array([(d[i]+d[j])**2 for i,j in edges])
    if c == "p":   return np.array([d[i]*d[j] for i,j in edges])
    if c == "sqrtarg": return np.sqrt(arg)
    if c == "arg": return arg.copy()
    if c == "smm": return np.array([d[i]+d[j]+m[i]+m[j] for i,j in edges])
    if c == "smm2":return np.array([(d[i]+d[j]+m[i]+m[j])**2 for i,j in edges])
    # vertex forms y = R^T x
    if c == "x1":  x = np.ones(len(d))
    elif c == "xd":  x = d
    elif c == "xdm": x = d + m
    elif c == "xd2": x = d*d
    elif c == "xsq": x = np.sqrt(d)
    return np.array([x[i]+x[j] for i,j in edges])

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    stats = {c: [0, 0.0, None] for c in CANDS}
    cnt = 0
    for n in range(3, nmax + 1):
        for g6 in graphs(n):
            A, d, m, edges, arg, AL = build(g6)
            B = AL @ AL
            cnt += 1
            for c in CANDS:
                y = yvec(c, d, m, edges, arg, A)
                lhs = B @ y
                rel = ((lhs - arg*y)/(arg*y)).max()
                if rel > 1e-9:
                    stats[c][0] += 1
                    if rel > stats[c][1]:
                        stats[c][1] = rel; stats[c][2] = g6
    print(f"graphs: {cnt}")
    for c in CANDS:
        s = stats[c]
        print(f"{c}: fails={s[0]} worst_rel={s[1]:.4g} at {s[2]}")

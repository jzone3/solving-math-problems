"""Twitter graphic for the P07 (Graffiti/WoW 154) refutation."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import deque

def lollipop(a, ell):
    n = a + ell
    adj = [set() for _ in range(n)]
    for i in range(a):
        for j in range(i + 1, a):
            adj[i].add(j); adj[j].add(i)
    prev = a - 1
    for k in range(ell):
        v = a + k
        adj[prev].add(v); adj[v].add(prev)
        prev = v
    return adj

def dist_sum(adj):
    n = len(adj); S = 0
    for s in range(n):
        d = [-1] * n; d[s] = 0; q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if d[v] < 0:
                    d[v] = d[u] + 1; q.append(v)
        S += sum(d)
    return S  # ordered sum

def ratio(a, ell):
    adj = lollipop(a, ell)
    n = len(adj)
    m = a * (a - 1) // 2 + ell
    S = dist_sum(adj)
    mu = S / (n * n)  # full-matrix convention
    return 2 * m * mu * mu / n ** 3

fig = plt.figure(figsize=(11, 5.5), dpi=200)
fig.patch.set_facecolor("#0d1117")

# Left: the witness graph
ax = fig.add_axes([0.02, 0.05, 0.46, 0.78]); ax.axis("off")
rng = np.random.default_rng(7)
K = 18  # drawn clique (represents K_50)
th = np.linspace(0, 2 * np.pi, K, endpoint=False)
cx, cy = -2.2, 0
xs, ys = cx + np.cos(th), cy + np.sin(th)
for i in range(K):
    for j in range(i + 1, K):
        ax.plot([xs[i], xs[j]], [ys[i], ys[j]], color="#3fb950", lw=0.35, alpha=0.5, zorder=1)
ax.scatter(xs, ys, s=26, color="#3fb950", zorder=3)
P = 24  # drawn path (represents P_70)
px = np.linspace(cx + 1.05, 6.2, P)
py = 0.28 * np.sin(np.linspace(0, 3 * np.pi, P))
ax.plot(px, py, color="#58a6ff", lw=1.6, zorder=2)
ax.scatter(px, py, s=16, color="#58a6ff", zorder=3)
ax.annotate("clique $K_{50}$", (cx, -1.45), color="#3fb950", ha="center", fontsize=13)
ax.annotate("path, 70 edges", (3.6, -0.85), color="#58a6ff", ha="center", fontsize=13)
ax.set_xlim(-3.6, 6.6); ax.set_ylim(-1.9, 1.5)
ax.set_title("the counterexample: lollipop $L(K_{50}, P_{70})$,  $n=120$",
             color="white", fontsize=13, pad=10)

# Right: ratio vs n crossing 1
ax2 = fig.add_axes([0.56, 0.14, 0.40, 0.66])
ax2.set_facecolor("#0d1117")
ns, rs = [], []
for ntot in range(20, 301, 4):
    best = max(ratio(a, ntot - a) for a in range(3, ntot - 1, 3))
    ns.append(ntot); rs.append(best)
ax2.plot(ns, rs, color="#f78166", lw=2.2)
ax2.axhline(1, color="white", lw=1, ls="--", alpha=0.7)
ax2.axvline(120, color="#3fb950", lw=1, ls=":", alpha=0.9)
ax2.annotate("conjecture bound", (295, 1.03), color="white", fontsize=10, ha="right")
ax2.annotate("first violation\n$n=120$", (124, 0.42), color="#3fb950", fontsize=10)
ax2.set_xlabel("graph size $n$", color="white")
ax2.set_ylabel(r"$2m\mu^2 / n^3$  (best lollipop)", color="white")
ax2.tick_params(colors="white")
for s in ax2.spines.values():
    s.set_color("#444")
ax2.set_title("the bound fails — and keeps failing", color="white", fontsize=12)

fig.suptitle("Graffiti conjecture 154 (1986) is FALSE", color="white", fontsize=17, y=0.97)
fig.text(0.5, 0.015,
         "claim: spread of a graph's eigenvalues  ≤  n / (average distance)   —   equivalently  2m·μ²  ≤  n³",
         color="#9da7b1", fontsize=10.5, ha="center")
fig.savefig("/home/ubuntu/repos/solving-math-problems/social/p07_graffiti154.png",
            facecolor=fig.get_facecolor(), bbox_inches="tight")
print("saved")

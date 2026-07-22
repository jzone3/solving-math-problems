"""Twitter graphic for the P08 (Graffiti 39/40) proof."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(11, 5.5), dpi=200)
fig.patch.set_facecolor("#0d1117")

# Top: a graph with its geodesic highlighted
ax = fig.add_axes([0.03, 0.42, 0.94, 0.42]); ax.axis("off")
rng = np.random.default_rng(3)
d = 7
gx = np.linspace(0, 10, d + 1)
gy = np.zeros(d + 1)
extra = []
for i in range(1, d):
    for k in range(rng.integers(1, 3)):
        ex, ey = gx[i] + rng.normal(0, 0.35), rng.uniform(0.7, 1.3)
        extra.append((i, ex, ey))
for i, ex, ey in extra:
    ax.plot([gx[i], ex], [gy[i], ey], color="#8b949e", lw=1.0, alpha=0.8, zorder=1)
    for j, fx, fy in extra:
        if abs(i - j) == 1 and rng.random() < 0.5:
            ax.plot([ex, fx], [ey, fy], color="#8b949e", lw=0.8, alpha=0.5, zorder=1)
ax.plot(gx, gy, color="#f778ba", lw=3.0, zorder=2)
ax.scatter(gx, gy, s=60, color="#f778ba", zorder=3)
if extra:
    exs = np.array([(e[1], e[2]) for e in extra])
    ax.scatter(exs[:, 0], exs[:, 1], s=36, color="#8b949e", zorder=3)
ax.annotate("shortest path between the two farthest vertices\n= an induced path on diam+1 vertices",
            (5, -1.0), color="#f778ba", ha="center", fontsize=12)
ax.set_ylim(-1.6, 1.6)
ax.set_title("every graph contains its diameter as an induced path — that's the whole proof",
             color="white", fontsize=13, pad=8)

# Bottom: the inequality chain
ax2 = fig.add_axes([0.03, 0.04, 0.94, 0.30]); ax2.axis("off")
chain = [r"$\mathrm{dev}(D)$", r"$\dfrac{\mathrm{diam}}{2}$",
         r"$\left\lfloor\dfrac{\mathrm{diam}+1}{2}\right\rfloor$", r"$\min(n^+,\,n^-)$"]
why = ["spread of distance-matrix\nentries in $[0,\\mathrm{diam}]$\n(Popoviciu)",
       "", "path $P_{d+1}$ has $\\lfloor\\frac{d+1}{2}\\rfloor$ positive\nand negative eigenvalues\n+ Cauchy interlacing", ""]
xs = [0.07, 0.34, 0.60, 0.89]
for x, t in zip(xs, chain):
    ax2.text(x, 0.62, t, color="white", fontsize=19, ha="center", va="center")
for xm in [0.205, 0.47, 0.745]:
    ax2.text(xm, 0.62, "$\\leq$", color="#3fb950", fontsize=22, ha="center", va="center")
ax2.text(0.07, 0.13, why[0], color="#9da7b1", fontsize=9.5, ha="center")
ax2.text(0.72, 0.13, why[2], color="#9da7b1", fontsize=9.5, ha="center")

fig.suptitle("Graffiti conjectures 39 & 40 (1986) are TRUE — a 4-line proof after 30+ years",
             color="white", fontsize=15.5, y=0.97)
fig.text(0.5, 0.005,
         "claim: std-dev of a graph's distance matrix ≤ number of positive (39) / negative (40) adjacency eigenvalues",
         color="#9da7b1", fontsize=10, ha="center")
fig.savefig("/home/ubuntu/repos/solving-math-problems/social/p08_graffiti3940.png",
            facecolor=fig.get_facecolor(), bbox_inches="tight")
print("saved")

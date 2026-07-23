"""Twitter graphic for the P06 (WoW 698) proof."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(11, 5.5), dpi=200)
fig.patch.set_facecolor("#0d1117")

# Left: the equality case K_{3,4}
ax = fig.add_axes([0.02, 0.12, 0.40, 0.68]); ax.axis("off")
a, b = 3, 4
ya = np.linspace(0.25, 0.75, a)
yb = np.linspace(0.15, 0.85, b)
for i in range(a):
    for j in range(b):
        ax.plot([0.15, 0.85], [ya[i], yb[j]], color="#8b949e", lw=1.0, alpha=0.7, zorder=1)
ax.scatter([0.15] * a, ya, s=140, color="#3fb950", zorder=3)
ax.scatter([0.85] * b, yb, s=140, color="#58a6ff", zorder=3)
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_title("equality exactly at complete bipartite graphs", color="white", fontsize=12, pad=6)
ax.text(0.5, -0.06, r"$K_{a,b}$: spectrum $\{\pm\sqrt{ab},\,0,\dots\}$, so $s^- = \sqrt{ab} = R$",
        color="#9da7b1", fontsize=10.5, ha="center", transform=ax.transAxes)

# Right: the proof chain
ax2 = fig.add_axes([0.45, 0.10, 0.53, 0.70]); ax2.axis("off")
steps = [
    (r"$\lambda_1 \geq S/m$", "Rayleigh at $x=(\\sqrt{d_u})$"),
    (r"$m^2 \leq S \cdot R$", "Cauchy–Schwarz over the $m$ edges"),
    (r"$\lambda_1^2 + R^2 \;\geq\; 2\lambda_1 R \;\geq\; 2m$", "AM–GM"),
    (r"$s^{-2} = 2m - s^{+2} \leq 2m - \lambda_1^2 \leq R^2$", r"$\sum_i \lambda_i^2 = \mathrm{tr}(A^2) = 2m$"),
]
for k, (eq, why) in enumerate(steps):
    y = 0.92 - k * 0.26
    ax2.text(0.02, y, f"{k+1}.", color="#3fb950", fontsize=15, va="center")
    ax2.text(0.10, y, eq, color="white", fontsize=16, va="center")
    ax2.text(0.10, y - 0.10, why, color="#9da7b1", fontsize=9.5, va="center")

fig.suptitle("Graffiti conjecture 698 (~1990) is TRUE — negative-eigenvalue length ≤ Randić index",
             color="white", fontsize=14.5, y=0.97)
fig.text(0.5, 0.005,
         "claim: $\\sqrt{\\sum_{\\lambda_i<0}\\lambda_i^2}\\;\\leq\\;R(G)=\\sum_{uv\\in E}(d_u d_v)^{-1/2}$"
         "   —   the 2025 machine search of this item used the Laplacian (no negative eigenvalues): vacuous",
         color="#9da7b1", fontsize=10, ha="center")
fig.savefig("/home/ubuntu/repos/solving-math-problems/social/p06_wow698.png",
            facecolor=fig.get_facecolor(), bbox_inches="tight")
print("saved")

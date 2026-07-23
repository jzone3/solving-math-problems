"""Twitter graphic for the P13 (9,6,1)-PMD nonexistence result."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(11, 5.5), dpi=200)
fig.patch.set_facecolor("#0d1117")

# Left: 9 points with one directed 6-cycle block highlighted
ax = fig.add_axes([0.02, 0.10, 0.44, 0.72]); ax.axis("off"); ax.set_aspect("equal")
ang = np.linspace(0, 2 * np.pi, 10)[:-1] + np.pi / 2
px, py = np.cos(ang), np.sin(ang)
block = [0, 2, 4, 5, 7, 8]
for i in range(9):
    c = "#f778ba" if i in block else "#8b949e"
    ax.scatter(px[i], py[i], s=120, color=c, zorder=3)
for a, b in zip(block, block[1:] + block[:1]):
    ax.annotate("", xy=(px[b], py[b]), xytext=(px[a], py[a]),
                arrowprops=dict(arrowstyle="-|>", color="#f778ba", lw=2.2,
                                shrinkA=10, shrinkB=10))
ax.set_xlim(-1.35, 1.35); ax.set_ylim(-1.35, 1.35)
ax.set_title("a block = a directed 6-cycle on 9 points;\neach ordered pair (x,y) must appear at each\n'distance' 1..5 around some block exactly once",
             color="white", fontsize=11.5, pad=10)

# Right: verdict
ax2 = fig.add_axes([0.50, 0.08, 0.48, 0.76]); ax2.axis("off")
ax2.text(0.5, 0.88, "IMPOSSIBLE", color="#f85149", fontsize=34, ha="center",
         fontweight="bold")
lines = [
    ("kissat SAT solver: UNSAT", "#3fb950"),
    ("DRAT proof certificate: VERIFIED (drat-trim)", "#3fb950"),
    ("independent CP-SAT model: INFEASIBLE", "#3fb950"),
    ("exhaustive DFS: 0 designs", "#3fb950"),
    ("adversarial re-derivation: CONFIRMED", "#3fb950"),
    ("Lean 4 formalization: no_pmd_9_6_1 ✓", "#58a6ff"),
]
for k, (t, c) in enumerate(lines):
    ax2.text(0.06, 0.68 - 0.115 * k, "•", color=c, fontsize=14, va="center")
    ax2.text(0.11, 0.68 - 0.115 * k, t, color="white", fontsize=12.5, va="center")

fig.suptitle("no (9,6,1)-perfect Mendelsohn design exists — smallest open case, settled",
             color="white", fontsize=15.5, y=0.97)
fig.text(0.5, 0.005,
         "open in the standard design-theory references (Abel–Bennett 2006; 2009 survey) — now a theorem",
         color="#9da7b1", fontsize=10, ha="center")
fig.savefig("/home/ubuntu/repos/solving-math-problems/social/p13_pmd.png",
            facecolor=fig.get_facecolor(), bbox_inches="tight")
print("saved")

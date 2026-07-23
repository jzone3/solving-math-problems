"""Twitter graphic for the P14 balanced-ternary-design nonexistence results."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(11, 5.5), dpi=200)
fig.patch.set_facecolor("#0d1117")

# Left: a BTD-style 0/1/2 matrix with row/col/pair rules annotated
ax = fig.add_axes([0.03, 0.10, 0.46, 0.70]); ax.axis("off")
rng = np.random.default_rng(7)
V, B = 8, 12
M = rng.choice([0, 1, 2], size=(V, B), p=[0.45, 0.35, 0.2])
cols = {0: "#161b22", 1: "#1f6feb", 2: "#f778ba"}
for i in range(V):
    for j in range(B):
        ax.add_patch(plt.Rectangle((j, V - 1 - i), 0.92, 0.92,
                                   color=cols[M[i, j]]))
        if M[i, j]:
            ax.text(j + 0.46, V - 0.54 - i, str(M[i, j]), color="white",
                    ha="center", va="center", fontsize=9)
ax.set_xlim(-0.2, B + 0.2); ax.set_ylim(-0.6, V + 0.4)
ax.set_title("a balanced ternary design: every element appears in each\nblock 0, 1 or 2 times — with exact row, column and\npairwise-balance counts required everywhere",
             color="white", fontsize=11.5, pad=10)

# Right: the three killed instances
ax2 = fig.add_axes([0.53, 0.08, 0.45, 0.76]); ax2.axis("off")
ax2.text(0.5, 0.90, "ALL THREE: IMPOSSIBLE", color="#f85149", fontsize=24,
         ha="center", fontweight="bold")
inst = ["BTD(14,18; 7,1,9; 7,4)", "BTD(12,15; 6,2,10; 8,6)", "BTD(12,20; 4,3,10; 6,4)"]
for k, t in enumerate(inst):
    ax2.text(0.5, 0.70 - 0.13 * k, t, color="white", fontsize=15, ha="center",
             family="monospace")
for k, t in enumerate(["CP-SAT infeasible + kissat UNSAT (DRAT verified)",
                       "adversarial reviewer's own independent encoding:",
                       "UNSAT + certificates verified on all three"]):
    ax2.text(0.5, 0.26 - 0.09 * k, t, color="#3fb950", fontsize=11.5, ha="center")

fig.suptitle("three open balanced ternary designs proven nonexistent",
             color="white", fontsize=15.5, y=0.97)
fig.text(0.5, 0.005,
         "the explicit survivors of a dedicated 2025 computational campaign, open in the Handbook of Combinatorial Designs tables",
         color="#9da7b1", fontsize=10, ha="center")
fig.savefig("/home/ubuntu/repos/solving-math-problems/social/p14_btd.png",
            facecolor=fig.get_facecolor(), bbox_inches="tight")
print("saved")

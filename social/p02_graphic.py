"""Twitter graphic for the P02 (Brandt regular supergraph, West's version) refutation."""
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fractions import Fraction

G = nx.from_graph6_bytes(b"H?q`qjo")
assert G.number_of_nodes() == 9
# sanity: triangle-free, maximal, delta = 3 = n/3
import itertools
assert not any(G.has_edge(a, b) and G.has_edge(a, c) and G.has_edge(b, c)
               for a, b, c in itertools.combinations(G, 3))
assert min(d for _, d in G.degree()) == 3

fig = plt.figure(figsize=(11, 5.5), dpi=200)
fig.patch.set_facecolor("#0d1117")

ax = fig.add_axes([0.02, 0.06, 0.44, 0.76]); ax.axis("off")
pos = nx.kamada_kawai_layout(G)
for u, v in G.edges():
    ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color="#8b949e", lw=1.4, zorder=1)
deg = dict(G.degree())
cols = ["#f78166" if deg[v] == 4 else "#58a6ff" for v in G.nodes()]
xy = np.array([pos[v] for v in G.nodes()])
ax.scatter(xy[:, 0], xy[:, 1], s=260, c=cols, zorder=2, edgecolors="white", linewidths=0.8)
for v in G.nodes():
    ax.annotate(str(deg[v]), pos[v], color="black", ha="center", va="center",
                fontsize=10, zorder=3, fontweight="bold")
ax.set_title("9 vertices, triangle-free, maximal,\nmin degree exactly n/3 = 3 (numbers = degrees)",
             color="white", fontsize=12.5, pad=8)

ax2 = fig.add_axes([0.50, 0.05, 0.48, 0.80]); ax2.axis("off")
lines = [
    ("the conjecture (West's open-problem list):", "#9da7b1", 11),
    ("\"clone vertices of any such graph and you can", "white", 13),
    ("  always make it regular\"", "white", 13),
    ("", "white", 8),
    ("for this graph: cloning vertex $v$ $x_v$ times needs", "#9da7b1", 11),
    (r"$\sum_{u \sim v} x_u = d$ for every $v$  —  a linear system.", "white", 13),
    ("", "white", 8),
    ("an exact Farkas certificate proves it has NO", "white", 13),
    ("solution with every $x_v \\geq 1$. no cloning works. ever.", "white", 13),
    ("", "white", 8),
    ("(Brandt's original strict version, min degree $> n/3$,", "#9da7b1", 10.5),
    ("is a theorem — the boundary case is where it breaks,", "#9da7b1", 10.5),
    ("and it breaks at the smallest possible size.)", "#9da7b1", 10.5),
]
y = 0.95
for t, c, fs in lines:
    ax2.text(0.02, y, t, color=c, fontsize=fs, va="top")
    y -= 0.075 if t else 0.035

fig.suptitle("Brandt's regular-supergraph conjecture (as recorded open since ~2002) fails at n = 9",
             color="white", fontsize=15, y=0.97)
fig.text(0.5, 0.012, "witness graph6: H?q`qjo   —   verifier: exact rational LP + Farkas certificate, solutions/P02/verify.py",
         color="#9da7b1", fontsize=9.5, ha="center")
fig.savefig("/home/ubuntu/repos/solving-math-problems/social/p02_brandt.png",
            facecolor=fig.get_facecolor(), bbox_inches="tight")
print("saved")

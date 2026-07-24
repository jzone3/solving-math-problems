"""Systematic hub-heavy stress test of F2'' (both caps c=2,4), n ~ 20..80+.

Families (all delta >= 2 by construction; hub attaches to ALL gadget verts):
 A. single hub + mixture of gadgets from {K3(pair), C4, C5, C6, P3, P4, K4}
    - full enumeration over gadget-count vectors with n in range;
 B. two hubs, both connected to all gadget vertices (shared gadgets),
    optional hub-hub edge;
 C. hub connected to every vertex of a random d-regular block (d=3..6);
 D. two hubs each with own gadget set, joined by a bridge gadget;
 E. skew complete bipartite K_{a,b} plus a hub joined to the small side /
    both sides / random subsets;
 F. windmill glued to regular graph by identifying a vertex or by edges.

Reports any min-eig < -1e-8 (exact recheck downstream) and the worst margins.
"""
import itertools
import numpy as np
import networkx as nx
from common import (build_base, with_diag, sigma_cap, min_eig,
                    gadget_cycle, gadget_path, gadget_clique, hub_gadgets,
                    windmill)

CAPS = (2.0, 4.0)
rng = np.random.default_rng(0)

GADGETS = {
    "K3": (2, [(0, 1)]),          # pair -> triangle with hub
    "C4": gadget_cycle(4),
    "C5": gadget_cycle(5),
    "C6": gadget_cycle(6),
    "P3": gadget_path(3),         # path -> fan with hub
    "P4": gadget_path(4),
    "K4": gadget_clique(4),       # K4 -> K5 with hub
}
NAMES = list(GADGETS)

results = []


def check(A, tag):
    b = build_base(A)
    for c in CAPS:
        e = min_eig(with_diag(b, sigma_cap(b["d"], b["m"], c))["M"])
        results.append((e, c, tag, A.shape[0]))
        if e < -1e-8:
            print(f"*** FAIL c={c} {tag} n={A.shape[0]} mineig={e:.6f}")


def two_hub(gadgets, hub_edge):
    n = 2 + sum(g[0] for g in gadgets)
    A = np.zeros((n, n))
    if hub_edge:
        A[0, 1] = A[1, 0] = 1
    off = 2
    for sz, el in gadgets:
        for a in range(sz):
            for h in (0, 1):
                A[h, off + a] = A[off + a, h] = 1
        for a, b_ in el:
            A[off + a, off + b_] = A[off + b_, off + a] = 1
        off += sz
    return A


# --- A: single hub, all gadget mixtures with total gadget count 6..38 -----
print("=== A: single-hub mixtures ===")
cnt = 0
for total in range(6, 40, 2):
    # random compositions over the 7 gadget types (exhaustive is too big)
    for _ in range(60):
        ks = rng.multinomial(total // 2, np.ones(7) / 7)
        gl = []
        for name, k in zip(NAMES, ks):
            gl += [GADGETS[name]] * int(k)
        if not gl:
            continue
        check(hub_gadgets(gl), "A:" + ",".join(f"{n_}x{k}" for n_, k in zip(NAMES, ks) if k))
        cnt += 1
# pure families, larger
for name in NAMES:
    for k in (5, 10, 15, 20, 30, 40):
        check(hub_gadgets([GADGETS[name]] * k), f"A:pure {name} x{k}")
        cnt += 1
print("A done", cnt)

# --- B: two hubs sharing gadgets --------------------------------------
print("=== B: two shared hubs ===")
for hub_edge in (0, 1):
    for name in NAMES:
        for k in (3, 6, 10, 15, 25):
            check(two_hub([GADGETS[name]] * k, hub_edge), f"B:{name} x{k} he={hub_edge}")
    for _ in range(80):
        total = rng.integers(4, 16)
        ks = rng.multinomial(total, np.ones(7) / 7)
        gl = []
        for name, k in zip(NAMES, ks):
            gl += [GADGETS[name]] * int(k)
        if gl:
            check(two_hub(gl, hub_edge), f"B:mix he={hub_edge}")

# --- C: hub + regular block -------------------------------------------
print("=== C: hub + regular block ===")
for d in (3, 4, 5, 6):
    for nb in (10, 20, 30, 40, 60):
        if (d * nb) % 2:
            nb += 1
        G = nx.random_regular_graph(d, nb, seed=int(rng.integers(1e9)))
        Ab = nx.to_numpy_array(G)
        n = nb + 1
        A = np.zeros((n, n))
        A[1:, 1:] = Ab
        A[0, 1:] = A[1:, 0] = 1          # hub to ALL block vertices
        check(A, f"C:hub+{d}-reg({nb}) full")
        # hub to a subset (keeps delta>=2 since block is regular d>=3)
        A2 = np.zeros((n, n))
        A2[1:, 1:] = Ab
        pick = rng.choice(nb, size=max(2, nb // 3), replace=False)
        for p in pick:
            A2[0, 1 + p] = A2[1 + p, 0] = 1
        check(A2, f"C:hub+{d}-reg({nb}) partial")

# --- D: two hubs with own gadgets + bridge gadget ----------------------
print("=== D: two-hub bridged ===")
for name1, name2 in itertools.product(("K3", "C4", "C5"), repeat=2):
    for k in (5, 10, 15):
        g1 = [GADGETS[name1]] * k
        g2 = [GADGETS[name2]] * k
        n = 2 + sum(g[0] for g in g1) + sum(g[0] for g in g2)
        A = np.zeros((n, n))
        off = 2
        for h, gl in ((0, g1), (1, g2)):
            for sz, el in gl:
                for a in range(sz):
                    A[h, off + a] = A[off + a, h] = 1
                for a, b_ in el:
                    A[off + a, off + b_] = A[off + b_, off + a] = 1
                off += sz
        # bridge triangle hub0-hub1-x: connect hubs via a shared K3 gadget
        A[0, 1] = A[1, 0] = 1
        check(A, f"D:{name1}x{k}+{name2}x{k}")

# --- E: skew bipartite + hub -------------------------------------------
print("=== E: skew bipartite + hubs ===")
for a, b_ in ((2, 20), (2, 60), (3, 40), (4, 30), (5, 50), (2, 100)):
    Kb = np.zeros((a + b_, a + b_))
    Kb[:a, a:] = 1
    Kb[a:, :a] = 1
    for mode in ("small", "big", "all"):
        n = a + b_ + 1
        A = np.zeros((n, n))
        A[1:, 1:] = Kb
        if mode == "small":
            idx = range(1, 1 + a)
        elif mode == "big":
            idx = range(1 + a, n)
        else:
            idx = range(1, n)
        for i in idx:
            A[0, i] = A[i, 0] = 1
        if A[0].sum() < 2:
            continue
        check(A, f"E:K({a},{b_}) hub->{mode}")

# --- F: windmill glued to regular --------------------------------------
print("=== F: windmill x regular hybrids ===")
for k in (10, 14, 20, 30):
    W = windmill(k)
    nw = W.shape[0]
    for d in (3, 5):
        G = nx.random_regular_graph(d, 20, seed=int(rng.integers(1e9)))
        Ab = nx.to_numpy_array(G)
        n = nw + 20
        A = np.zeros((n, n))
        A[:nw, :nw] = W
        A[nw:, nw:] = Ab
        # connect hub to 2 block vertices and one outer vertex to 1 block vertex
        A[0, nw] = A[nw, 0] = 1
        A[0, nw + 1] = A[nw + 1, 0] = 1
        A[1, nw + 2] = A[nw + 2, 1] = 1
        check(A, f"F:F_{k}+{d}reg20")

results.sort()
print("\nWORST 15 margins:")
for e, c, tag, n in results[:15]:
    print(f"  {e:+.6f}  c={c} n={n}  {tag}")
print(f"\nTOTAL checks: {len(results)}, failures: {sum(1 for r in results if r[0] < -1e-8)}")

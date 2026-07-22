"""Parameterized block-structure families for P05 V3.

Design idea: every class where Gallai-3 is *proved* (outerplanar, series-parallel,
Hamiltonian-block graphs, 2-trees, ...) has block trees whose blocks are 'path
friendly' (each block is traceable between any two attachment vertices, or the
block tree is a path). We therefore build graphs consisting of

    central 2-connected block B  +  three rooted 'arm' gadgets attached at
    three distinct cut vertices a, b, c of B,

choosing B non-Hamiltonian / non-traceable-between-attachments where possible,
and arms whose root-depth vs internal-length profile differs, so that the three
pairwise intersections of longest paths are pushed toward different blocks —
exactly the configuration the known proofs cannot handle.
"""
import subprocess
from itertools import combinations, combinations_with_replacement

from lp_core import edges_to_adj


# ---------------- arm gadgets: (name, k, edges, root=0) ----------------

def arm_path(d):
    return ("P%d" % d, d + 1, [(i, i + 1) for i in range(d)])


def arm_broom(d, t):
    """path of length d from root, then t pendant leaves at the far end."""
    edges = [(i, i + 1) for i in range(d)]
    k = d + 1
    for _ in range(t):
        edges.append((d, k))
        k += 1
    return ("B%d.%d" % (d, t), k, edges)


def arm_spider(d, a, b):
    """path of length d from root, then two branches of lengths a and b."""
    edges = [(i, i + 1) for i in range(d)]
    k = d + 1
    prev = d
    for _ in range(a):
        edges.append((prev, k)); prev = k; k += 1
    prev = d
    for _ in range(b):
        edges.append((prev, k)); prev = k; k += 1
    return ("S%d.%d.%d" % (d, a, b), k, edges)


def arm_cycle_tail(d, c):
    """path of length d from root ending in a cycle of length c."""
    edges = [(i, i + 1) for i in range(d)]
    k = d + 1
    cyc = [d] + list(range(k, k + c - 1))
    for i in range(len(cyc)):
        edges.append((cyc[i], cyc[(i + 1) % len(cyc)]))
    k += c - 1
    return ("C%d.%d" % (d, c), k, edges)


def arm_theta(d, p, q):
    """path of length d from root to a theta made of two internally disjoint
    paths of lengths p, q between two hub vertices."""
    edges = [(i, i + 1) for i in range(d)]
    k = d + 1
    hub1 = d
    hub2 = k; k += 1
    for ln in (p, q):
        prev = hub1
        for i in range(ln - 1):
            edges.append((prev, k)); prev = k; k += 1
        edges.append((prev, hub2))
    return ("T%d.%d.%d" % (d, p, q), k, edges)


def default_arm_library(max_size=8):
    lib = []
    for d in range(1, 6):
        lib.append(arm_path(d))
    for d in range(1, 4):
        for t in (2,):
            lib.append(arm_broom(d, t))
    for d in range(0, 3):
        for a in range(1, 4):
            for b in range(a, 4):
                lib.append(arm_spider(d, a, b))
    for d in range(0, 3):
        for c in (3, 4, 5):
            lib.append(arm_cycle_tail(d, c))
    lib.append(arm_theta(0, 2, 2))
    lib.append(arm_theta(1, 2, 2))
    lib.append(arm_theta(0, 2, 3))
    return [g for g in lib if g[1] <= max_size + 1]


# ---------------- central blocks via nauty-geng ----------------

def geng_graphs(n, args=("-C",)):
    """Yield (n, edge list) for all graphs from nauty-geng with given args
    (-C = 2-connected)."""
    cmd = ["nauty-geng", "-q"] + list(args) + [str(n)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    for line in out.split():
        yield graph6_to_edges(line)


def graph6_to_edges(g6):
    data = [ord(c) - 63 for c in g6]
    n = data[0]
    bits = []
    for x in data[1:]:
        for i in range(5, -1, -1):
            bits.append((x >> i) & 1)
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


# ---------------- assembly ----------------

def assemble(block, attach, arms):
    """block=(nb, edges); attach = tuple of distinct block vertices;
    arms = list of gadgets (name,k,edges), one per attach vertex (root=0
    identified with the attach vertex). Returns (n, adj, desc)."""
    nb, bedges = block
    edges = list(bedges)
    n = nb
    names = []
    for v, (name, k, aedges) in zip(attach, arms):
        # map arm vertex 0 -> v, arm vertex i>0 -> n + i - 1
        for (x, y) in aedges:
            xx = v if x == 0 else n + x - 1
            yy = v if y == 0 else n + y - 1
            edges.append((xx, yy))
        n += k - 1
        names.append("%s@%d" % (name, v))
    return n, edges_to_adj(n, edges), edges, "+".join(names)

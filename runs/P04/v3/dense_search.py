"""Targeted dense pool: densest Eulerian graphs = complements of sparse
"defect" graphs H on the same vertex set.

Odd n:  K_n is Eulerian; G = K_n - H is Eulerian iff every vertex loses an
        even number of edges, i.e. all degrees of H are even. We enumerate all
        H that are disjoint unions of cycles (degrees in {0,2}) up to iso, and
        optionally all even-degree H with max degree 4 up to a given edge
        count (via geng).
Even n: G = K_n - H Eulerian iff all degrees of H are odd (all 14 vertices
        must lose an odd number). Enumerate H with degrees in {1,3} via geng.

These are the most constrained instances: m/n close to (n-1)/2 forces every
decomposition to consist almost entirely of near-Hamiltonian cycles.
"""

import subprocess
import sys
import time
from itertools import combinations

import networkx as nx

from sat_decider import decompose_le_k
from search import check


def cycle_union_defects(n):
    """All disjoint unions of cycles on <= n vertices, up to iso: one graph
    per multiset of cycle lengths (parts >= 3 summing to <= n)."""
    out = []

    def parts(rem, minp, cur):
        out.append(list(cur))
        for p in range(minp, rem + 1):
            cur.append(p)
            parts(rem - p, p, cur)
            cur.pop()

    all_parts = []

    def gen(rem, minp, cur):
        if cur:
            all_parts.append(list(cur))
        for p in range(minp, rem + 1):
            cur.append(p)
            gen(rem - p, p, cur)
            cur.pop()

    gen(n, 3, [])
    graphs = []
    for ps in all_parts:
        H = nx.Graph()
        H.add_nodes_from(range(n))
        v = 0
        for p in ps:
            cyc = list(range(v, v + p))
            H.add_edges_from(zip(cyc, cyc[1:] + [cyc[0]]))
            v += p
        graphs.append((tuple(ps), H))
    return graphs


def geng_defects(n, degspec, maxedges):
    """Enumerate H via geng with given degree filter."""
    lo, hi = degspec
    cmd = ["nauty-geng", f"-d{lo}", f"-D{hi}", str(n), f"0:{maxedges}"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    for line in proc.stdout.splitlines():
        yield nx.from_graph6_bytes(line.strip().encode())


def main():
    n = int(sys.argv[1])
    mode = sys.argv[2] if len(sys.argv) > 2 else "auto"
    log = f"search_n{n}_dense.log"
    Kn = nx.complete_graph(n)
    stats = {"OK": 0, "TIGHT": 0, "CE": 0}
    t0 = time.time()
    cands = []
    if n % 2 == 1:
        for ps, H in cycle_union_defects(n):
            G = nx.difference(Kn, H)
            if nx.is_connected(G):
                cands.append((f"Kn-cyc{ps}", G))
        if mode == "geng4":
            seen = 0
            for H in geng_defects(n, (0, 4), 14):
                if any(d % 2 for _, d in H.degree()):
                    continue
                Hf = nx.Graph()
                Hf.add_nodes_from(range(n))
                Hf.add_edges_from(H.edges())
                G = nx.difference(Kn, Hf)
                if nx.is_connected(G):
                    cands.append((f"Kn-evenH{seen}", G))
                seen += 1
    else:
        cnt = 0
        for H in geng_defects(n, (1, 3), 21):
            if H.number_of_nodes() != n or any(d % 2 == 0 for _, d in H.degree()):
                continue
            G = nx.difference(Kn, H)
            if nx.is_connected(G):
                cands.append((f"Kn-oddH{cnt}", G))
            cnt += 1
    print(f"n={n}: {len(cands)} dense candidates", flush=True)
    for i, (tag, G) in enumerate(cands):
        r = check(G, n, log, tag, check_tight=True)
        stats[r] += 1
        if (i + 1) % 100 == 0:
            print(f"[{i+1}/{len(cands)}] {stats} {time.time()-t0:.0f}s", flush=True)
    print(f"DONE dense n={n} {stats} total={time.time()-t0:.0f}s", flush=True)
    with open(log, "a") as f:
        f.write(f"SUMMARY n={n} mode=dense {stats} time={time.time()-t0:.0f}s\n")


if __name__ == "__main__":
    main()

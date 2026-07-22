#!/usr/bin/env python3
"""Independent (differently-written) verifier for the n=13 pipeline.

For each H (graph6, n=12) on stdin: rebuild G = H + w (w joined to the
odd-degree vertices of H), apply the same class filters, and find a
decomposition of G into <= 6 cycles using a DIFFERENT method than
hajos_check.c: split an Eulerian circuit at repeated vertices, then locally
merge/retry; falls back to exact ILP (exact_min_decomp.check) if the
randomized splitting fails. Prints PASS/FAIL per graph and a summary.

Used to spot-check random samples of the C pipeline.
"""
import random
import sys
import networkx as nx
from exact_min_decomp import check as ilp_check


def eulerian_split_decomposition(G, bound, tries=500):
    nodes = list(G)
    for _ in range(tries):
        # random relabeling => random Eulerian circuit structure
        perm = nodes[:]
        random.shuffle(perm)
        rel = dict(zip(nodes, perm))
        inv = {v: k for k, v in rel.items()}
        H = nx.relabel_nodes(nx.MultiGraph(G), rel)
        circuit = [(inv[u], inv[v]) for (u, v) in
                   nx.eulerian_circuit(H, source=random.choice(perm))]
        cycles = split_circuit(circuit)
        if cycles is not None and len(cycles) <= bound:
            return cycles
    return None


def split_circuit(circuit):
    verts = [circuit[0][0]] + [v for (_, v) in circuit]
    cycles = []
    stack = []
    pos = {}
    for v in verts:
        if v in pos:
            i = pos[v]
            cyc = stack[i:] + [v]
            if len(cyc) >= 4:  # closed walk v..v with >=3 edges
                cycles.append(stack[i:])
            else:
                return None
            for w in stack[i:]:
                pos.pop(w, None)
            stack = stack[:i]
        stack.append(v)
        pos[v] = len(stack) - 1
    if len(stack) > 1:
        return None
    return cycles


def validate(G, cycles):
    used = set()
    cnt = 0
    for cyc in cycles:
        if len(cyc) < 3 or len(set(cyc)) != len(cyc):
            return False
        for i in range(len(cyc)):
            a, b = cyc[i], cyc[(i + 1) % len(cyc)]
            e = (min(a, b), max(a, b))
            if e in used or not G.has_edge(a, b):
                return False
            used.add(e)
            cnt += 1
    return cnt == G.number_of_edges()


def main():
    total = cand = passed = ilp_used = 0
    for line in sys.stdin:
        g6 = line.strip()
        if not g6:
            continue
        total += 1
        H = nx.from_graph6_bytes(g6.encode())
        odd = [v for v in H if H.degree(v) % 2 == 1]
        if len(odd) < 4:
            continue
        G = H.copy()
        G.add_node(12)
        for v in odd:
            G.add_edge(v, 12)
        if not (nx.is_connected(G) and nx.is_biconnected(G)):
            continue
        cand += 1
        cycles = eulerian_split_decomposition(G, 6)
        if cycles is not None and validate(G, cycles):
            passed += 1
        else:
            slots = ilp_check(nx.to_graph6_bytes(G, header=False)
                              .decode().strip())
            ilp_used += 1
            if slots is not None:
                passed += 1
            else:
                print("FAIL (no <=6-cycle decomposition!):", g6)
    print(f"total={total} candidates={cand} passed={passed} ilp_used={ilp_used}")
    print("PASS" if passed == cand else "FAIL")
    sys.exit(0 if passed == cand else 1)


if __name__ == "__main__":
    main()

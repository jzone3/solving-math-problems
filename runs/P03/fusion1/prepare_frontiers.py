"""Prepare exact reduced frontier graph lists from a nauty graph6 stream."""

import json
import sys

import networkx as nx


def main():
    target = sys.argv[1]
    kept = planar = not3ec = degree_mismatch = 0
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        graph = nx.from_graph6_bytes(line.encode())
        if target == "n18":
            if any(graph.degree(v) != 3 for v in graph):
                degree_mismatch += 1
                continue
            degree = [3] * 18
        elif target == "tau4n14a":
            degree = [4] * 4 + [3] * 10
            if sorted(dict(graph.degree()).values()) != sorted(degree):
                degree_mismatch += 1
                continue
        elif target == "tau4n14b":
            degree = [4] * 6 + [3] * 8
            if sorted(dict(graph.degree()).values()) != sorted(degree):
                degree_mismatch += 1
                continue
        else:
            raise SystemExit(f"unknown target {target}")
        if nx.check_planarity(graph)[0]:
            planar += 1
            continue
        if nx.edge_connectivity(graph) < 3:
            not3ec += 1
            continue
        edges = sorted((min(u, v), max(u, v)) for u, v in graph.edges())
        print(json.dumps({"g6": line, "edges": edges, "degrees": degree}))
        kept += 1
    print(
        f"kept={kept} planar={planar} not3ec={not3ec} "
        f"degree_mismatch={degree_mismatch}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()

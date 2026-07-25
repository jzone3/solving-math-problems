"""Filter a nauty d3--D4 stream into both n=14 tau=4 degree profiles."""

import json
import sys

import networkx as nx


def main():
    out_a, out_b = sys.argv[1:3]
    fa = open(out_a, "w")
    fb = open(out_b, "w")
    counts = {"a": 0, "b": 0, "planar": 0, "not3ec": 0, "other": 0}
    try:
        for raw in sys.stdin:
            line = raw.strip()
            if not line:
                continue
            graph = nx.from_graph6_bytes(line.encode())
            values = sorted(dict(graph.degree()).values())
            if values == [3] * 10 + [4] * 4:
                target, degrees, fh = "a", [4] * 4 + [3] * 10, fa
            elif values == [3] * 8 + [4] * 6:
                target, degrees, fh = "b", [4] * 6 + [3] * 8, fb
            else:
                counts["other"] += 1
                continue
            if nx.check_planarity(graph)[0]:
                counts["planar"] += 1
                continue
            if nx.edge_connectivity(graph) < 3:
                counts["not3ec"] += 1
                continue
            edges = sorted((min(u, v), max(u, v)) for u, v in graph.edges())
            fh.write(json.dumps({"g6": line, "edges": edges, "degrees": degrees}) + "\n")
            counts[target] += 1
    finally:
        fa.close()
        fb.close()
    print(" ".join(f"{key}={value}" for key, value in counts.items()), file=sys.stderr)


if __name__ == "__main__":
    main()

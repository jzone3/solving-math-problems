"""Filter cubic graph6 list to non-planar 3-edge-connected graphs; emit JSONL.
Usage: python3 prep_graphs.py < cubicN.g6 > keptN.jsonl"""
import sys
import json
import networkx as nx

kept = planar = not3ec = 0
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    G = nx.from_graph6_bytes(line.encode())
    if nx.check_planarity(G)[0]:
        planar += 1
        continue
    if nx.edge_connectivity(G) < 3:
        not3ec += 1
        continue
    kept += 1
    print(json.dumps({"g6": line, "edges": sorted(G.edges())}))
sys.stderr.write("kept=%d planar=%d not3ec=%d\n" % (kept, planar, not3ec))

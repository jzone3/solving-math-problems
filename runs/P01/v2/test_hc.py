"""Cross-check hc.c against brute force on random small graphs & multigraphs."""
import random
from hcutil import hc_count, hc_count_brute

random.seed(42)
for trial in range(300):
    n = random.randint(3, 8)
    edges = []
    # random simple-ish graph with possible parallel edges
    for u in range(n):
        for v in range(u + 1, n):
            for _ in range(random.choice([0, 0, 1, 1, 2])):
                edges.append((u, v))
    if not edges:
        continue
    a = hc_count(n, edges)
    b = hc_count_brute(n, edges)
    assert a == b, (n, edges, a, b)
print("ALL OK: 300 random multigraph cross-checks passed")
# cutoff semantics check
edges = [(u, v) for u in range(8) for v in range(u + 1, 8)]  # K8: 2520 HCs
print("K8 exact:", hc_count(8, edges), "cutoff5:", hc_count(8, edges, cutoff=5))

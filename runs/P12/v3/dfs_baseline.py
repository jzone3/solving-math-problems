#!/usr/bin/env python3
"""Plain randomized DFS baseline (no algebraic seed), for near-miss depth data."""
import random
import sys

sys.path.insert(0, ".")
from t2lib import dfs_t2

n = int(sys.argv[1]) if len(sys.argv) > 1 else 11
tb = float(sys.argv[2]) if len(sys.argv) > 2 else 14400
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 42
stats = {}
sol = dfs_t2(n, time_budget=tb, rng=random.Random(seed), stats=stats)
print("sol found:", sol is not None, "best depth:", stats.get("best"))
for r in stats.get("rows", []):
    print(" ", r)

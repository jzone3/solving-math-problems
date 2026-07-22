"""Decode kissat SAT output ('v' lines) into an n x n array using the .map file.
Usage: python3 decode.py n solver_output.txt cnf.map > square.txt
"""
import sys

n = int(sys.argv[1])
true_vars = set()
for line in open(sys.argv[2]):
    if line.startswith("v"):
        for tok in line.split()[1:]:
            v = int(tok)
            if v > 0:
                true_vars.add(v)

grid = [[None] * n for _ in range(n)]
for line in open(sys.argv[3]):
    vid, r, c, s = map(int, line.split())
    if vid in true_vars:
        assert grid[r][c] is None, f"double assign at {r},{c}"
        grid[r][c] = s

for row in grid:
    assert all(v is not None for v in row)
    print(" ".join(map(str, row)))

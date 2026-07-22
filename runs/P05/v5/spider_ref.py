#!/usr/bin/env python3
"""Reference (slow, trusted) implementation of the V5 spider-reduction test.

Condition tested for a core graph H:
  Do there exist distinct vertices a,b,c and paths
    P1 = maximum-length a-b path, P2 = maximum-length b-c path,
    P3 = maximum-length a-c path  (maximum among paths with those endpoints)
  with V(P1) & V(P2) & V(P3) == empty set?

If yes, attaching three pendant arms of suitable (always solvable) integer
lengths at a,b,c yields a connected graph with three longest paths having
empty intersection -- a counterexample to Gallai's 3-longest-paths question.
Arm lengths: choose L_a large, L_c = L_a - (M_bc - M_ab), L_b = L_c + (M_ac - M_ab),
then all three pair-sums L_x+L_y+M_xy are equal; make all >= n_H to dominate
one-arm paths.

Reads graph6 from stdin, prints any hits.
"""
import sys
from itertools import combinations


def parse_graph6(line):
    line = line.strip()
    data = [ord(c) - 63 for c in line]
    n = data[0]
    assert n < 63
    bits = []
    for v in data[1:]:
        bits.extend((v >> k) & 1 for k in range(5, -1, -1))
    adj = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    return n, adj


def all_max_paths_per_pair(n, adj):
    """best[(s,t)] = (maxlen, [vertex-masks of maximum s-t paths]), s<t."""
    best = {}

    def dfs(s, v, mask, length):
        for w in range(n):
            if adj[v] >> w & 1 and not mask >> w & 1:
                m2 = mask | 1 << w
                if s < w:
                    key = (s, w)
                    cur = best.get(key)
                    if cur is None or length + 1 > cur[0]:
                        best[key] = (length + 1, [m2])
                    elif length + 1 == cur[0]:
                        cur[1].append(m2)
                dfs(s, w, m2, length + 1)

    for s in range(n):
        dfs(s, s, 1 << s, 0)
    return best


def find_hit(n, adj):
    best = all_max_paths_per_pair(n, adj)
    for a, b, c in combinations(range(n), 3):
        l1 = best.get((a, b))
        l2 = best.get((b, c))
        l3 = best.get((a, c))
        if not (l1 and l2 and l3):
            continue
        for p1 in l1[1]:
            if p1 >> c & 1:
                continue
            for p2 in l2[1]:
                if p2 >> a & 1:
                    continue
                i12 = p1 & p2
                for p3 in l3[1]:
                    if p3 >> b & 1:
                        continue
                    if i12 & p3 == 0:
                        return (a, b, c, l1[0], l2[0], l3[0], p1, p2, p3)
    return None


def main():
    cnt = 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        n, adj = parse_graph6(line)
        hit = find_hit(n, adj)
        cnt += 1
        if hit:
            print("HIT", line, hit, flush=True)
    print(f"# processed {cnt} graphs", file=sys.stderr)


if __name__ == "__main__":
    main()

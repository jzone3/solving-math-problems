#!/usr/bin/env python3
"""Check whether each graph6 on stdin contains W = 'H?q`qjo' as a subgraph
(not necessarily induced). Used to test the observation that every boundary
counterexample found (n <= 18) contains W."""
import sys
from exact_check import g6_to_adj

W = 'H?q`qjo'
nw, AW = g6_to_adj(W)
adjW = [[j for j in range(nw) if AW[i][j]] for i in range(nw)]


def sub_iso(AH, nH):
    order = sorted(range(nw), key=lambda v: -len(adjW[v]))
    assign = [-1] * nw
    used = [False] * nH

    def bt(k):
        if k == nw:
            return True
        v = order[k]
        for c in range(nH):
            if used[c]:
                continue
            if all(assign[u] == -1 or AH[c][assign[u]] for u in adjW[v]):
                assign[v] = c
                used[c] = True
                if bt(k + 1):
                    return True
                assign[v] = -1
                used[c] = False
        return False
    return bt(0)


if __name__ == '__main__':
    for line in sys.stdin:
        g = line.split()[-1].strip()
        if not g:
            continue
        nH, AH = g6_to_adj(g)
        print(g, 'contains_W=%s' % sub_iso(AH, nH), flush=True)

#!/usr/bin/env python3
"""P16 v1: exhaustive enumeration of small quotient structures (k<=3) for
bounds 44/46. Reports the largest margins found (float screening only)."""
import heapq
import itertools
import sys

import search_quotient as sq


def run(which, NMAX2=30, BMAX=30, NMAX3=14):
    top = []

    def push(v, st):
        heapq.heappush(top, (v, st))
        if len(top) > 10:
            heapq.heappop(top)

    # k=1: b-regular graphs, mu <= rho(L_B)=... quotient is 1x1: L_B=[0]; useless
    # (mu lower bound from quotient is 0) -- skip.
    # k=2
    for n1 in range(1, NMAX2 + 1):
        for n2 in range(n1, NMAX2 + 1):
            for b11 in range(0, min(BMAX, n1 - 1) + 1):
                if b11 % 2 and n1 % 2:
                    continue
                for b22 in range(0, min(BMAX, n2 - 1) + 1):
                    if b22 % 2 and n2 % 2:
                        continue
                    for b12 in range(1, min(BMAX, n2) + 1):
                        if (n1 * b12) % n2:
                            continue
                        b21 = n1 * b12 // n2
                        if b21 > n1 or b21 > BMAX:
                            continue
                        n = [n1, n2]
                        B = [[b11, b12], [b21, b22]]
                        v = sq.margin(which, n, B)
                        if v is not None:
                            push(v, (n, B))
    print(f"[{which}] k=2 done; top:")
    for v, st in sorted(top, reverse=True):
        print(f"  margin={v:.6f} {st}")

    # k=3, smaller ranges
    top3 = []

    def push3(v, st):
        heapq.heappush(top3, (v, st))
        if len(top3) > 10:
            heapq.heappop(top3)

    R = range(1, NMAX3 + 1)
    for n1, n2, n3 in itertools.combinations_with_replacement(R, 3):
        n = [n1, n2, n3]
        offs = []
        for (i, j) in ((0, 1), (0, 2), (1, 2)):
            ch = [(0, 0)]
            for bij in range(1, n[j] + 1):
                if (n[i] * bij) % n[j] == 0 and n[i] * bij // n[j] <= n[i]:
                    ch.append((bij, n[i] * bij // n[j]))
            offs.append(ch)
        diags = []
        for i in range(3):
            d = [x for x in range(0, n[i]) if not (x % 2 and n[i] % 2)]
            diags.append(d[:6])
        for o01 in offs[0]:
            for o02 in offs[1]:
                for o12 in offs[2]:
                    for d1 in diags[0]:
                        for d2 in diags[1]:
                            for d3 in diags[2]:
                                B = [[d1, o01[0], o02[0]],
                                     [o01[1], d2, o12[0]],
                                     [o02[1], o12[1], d3]]
                                v = sq.margin(which, n, B)
                                if v is not None:
                                    push3(v, (n, [row[:] for row in B]))
    print(f"[{which}] k=3 done; top:")
    for v, st in sorted(top3, reverse=True):
        print(f"  margin={v:.6f} {st}")


if __name__ == "__main__":
    run(int(sys.argv[1]))

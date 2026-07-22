"""Focused omega=3 (K4-free) attack in the open pocket: non-dense, many triangles,
not 3-partite. Score = lam1^2 + lam2^2 - (4/3) m.

Part 1: parametric wheel blowups  I_a  join  C5[b1..b5]  (omega = 3, many triangles).
Part 2: annealing restricted to K4-free graphs (moves creating a K4 rejected).
Usage: python3 omega3.py wheel | anneal <n> <restarts> <steps> <seed>
"""
import sys, itertools
import numpy as np
from core import adj_from_edges, top2, max_clique

def wheel_blowup(a, bs):
    n = a + sum(bs)
    edges = []
    offs, s = [], a
    for b in bs:
        offs.append((s, s + b)); s += b
    for i in range(a):
        for lo, hi in offs:
            for v in range(lo, hi):
                edges.append((i, v))
    for c in range(5):
        lo1, hi1 = offs[c]; lo2, hi2 = offs[(c + 1) % 5]
        for u in range(lo1, hi1):
            for v in range(lo2, hi2):
                edges.append((u, v))
    return adj_from_edges(n, edges)

def wheel_scan(maxtot=40):
    best = (-1e9, None)
    for a in range(1, 13):
        for bs in itertools.product(range(1, 11), repeat=3):
            # symmetric pattern b = (x,y,z,y,x) to cut the space
            x, y, z = bs
            b5 = (x, y, z, y, x)
            if a + sum(b5) > maxtot:
                continue
            A = wheel_blowup(a, b5)
            l1, l2 = top2(A)
            m = A.sum() / 2
            s = l1 * l1 + l2 * l2 - (4 / 3) * m
            if s > best[0]:
                best = (s, (a, b5))
                print(f"new best {s:+.5f} a={a} bs={b5} (w={max_clique(A)})", flush=True)
    print("WHEEL BEST:", best)

def has_k4_with(A, i, j):
    # does edge (i,j) lie in a K4?
    common = np.nonzero(A[i] * A[j])[0]
    for a in range(len(common)):
        for b in range(a + 1, len(common)):
            if A[common[a], common[b]]:
                return True
    return False

def anneal_k4free(n, restarts, steps, seed):
    rng = np.random.default_rng(seed)
    gb = -1e9
    for r in range(restarts):
        A = np.zeros((n, n))
        # start from random triangle-rich K4-free: greedy random edges avoiding K4
        order = [(i, j) for i in range(n) for j in range(i + 1, n)]
        rng.shuffle(order)
        for (i, j) in order[: 3 * n]:
            A[i, j] = A[j, i] = 1
            if has_k4_with(A, i, j):
                A[i, j] = A[j, i] = 0
        def sc(A):
            l1, l2 = top2(A)
            return l1 * l1 + l2 * l2 - (4 / 3) * (A.sum() / 2)
        s = sc(A)
        best = s
        T0, T1 = 0.6, 0.005
        for t in range(steps):
            T = T0 * (T1 / T0) ** (t / steps)
            i, j = rng.integers(0, n, 2)
            if i == j:
                continue
            A[i, j] = A[j, i] = 1 - A[i, j]
            if A[i, j] and has_k4_with(A, i, j):
                A[i, j] = A[j, i] = 0
                continue
            s2 = sc(A)
            if s2 >= s or rng.random() < np.exp((s2 - s) / T):
                s = s2
                best = max(best, s)
            else:
                A[i, j] = A[j, i] = 1 - A[i, j]
        w = max_clique(A)
        print(f"K4free n={n} restart={r} best={best:+.5f} (final w={w})"
              + (" ***POSITIVE***" if best > 1e-9 else ""), flush=True)
        gb = max(gb, best)
    print(f"K4FREE GLOBAL BEST n={n}: {gb:+.5f}")

if __name__ == "__main__":
    if sys.argv[1] == "wheel":
        wheel_scan(int(sys.argv[2]) if len(sys.argv) > 2 else 40)
    else:
        anneal_k4free(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))

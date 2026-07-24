"""Locate minimal F2 counterexamples in windmill-like families.

Families:
 - F(k): k triangles sharing a hub (n = 2k+1)
 - Fp(k, p): hub + k triangles + p extra pendant-triangle... (kept simple)
 - W(k, c): hub joined to a disjoint union of k cycles C_c (c=3 gives F(k))
 - B(k): book = K_2 + k*K_1 is delta>=2: pages are 4-cycles? use K2 + kK1
   (two hubs adjacent, k vertices adjacent to both) n = k+2
 - KmK(k, q): hub + k copies of K_q (each clique vertex also hub-adjacent)
"""
import numpy as np
from common import build


def mineig(A):
    return np.linalg.eigvalsh(build(A)["M"])[0]


def hub_plus_cliques(k, q):
    n = 1 + k * q
    A = np.zeros((n, n))
    for t in range(k):
        vs = [1 + t * q + r for r in range(q)]
        for a in range(q):
            A[0, vs[a]] = A[vs[a], 0] = 1
            for b in range(a + 1, q):
                A[vs[a], vs[b]] = A[vs[b], vs[a]] = 1
    return A


def hub_plus_cycles(k, c):
    n = 1 + k * c
    A = np.zeros((n, n))
    for t in range(k):
        vs = [1 + t * c + r for r in range(c)]
        for a in range(c):
            A[vs[a], vs[(a + 1) % c]] = A[vs[(a + 1) % c], vs[a]] = 1
            A[0, vs[a]] = A[vs[a], 0] = 1
    return A


def book(k):
    n = k + 2
    A = np.zeros((n, n))
    A[0, 1] = A[1, 0] = 1
    for t in range(2, n):
        A[0, t] = A[t, 0] = A[1, t] = A[t, 1] = 1
    return A


print("windmill F(k) = hub+cycles(k,3):")
prev = None
for k in range(10, 20):
    e = mineig(hub_plus_cliques(k, 2))
    print(f"  k={k} n={2*k+1} mineig={e:.6f} {'FAIL' if e < -1e-9 else ''}")

print("books K2 + k K1:")
for k in [5, 10, 20, 40, 80, 160]:
    e = mineig(book(k))
    print(f"  k={k} n={k+2} mineig={e:.6f} {'FAIL' if e < -1e-9 else ''}")

print("hub + k K_3 (cliques q=3):")
for k in [4, 6, 8, 10, 12, 15, 20]:
    e = mineig(hub_plus_cliques(k, 3))
    print(f"  k={k} n={3*k+1} mineig={e:.6f} {'FAIL' if e < -1e-9 else ''}")

print("hub + k C_4:")
for k in [4, 6, 8, 10, 12, 15, 20]:
    e = mineig(hub_plus_cycles(k, 4))
    print(f"  k={k} n={4*k+1} mineig={e:.6f} {'FAIL' if e < -1e-9 else ''}")

print("hub + k C_5:")
for k in [4, 6, 8, 10, 12, 15, 20]:
    e = mineig(hub_plus_cycles(k, 5))
    print(f"  k={k} n={5*k+1} mineig={e:.6f} {'FAIL' if e < -1e-9 else ''}")

# mixed: j triangles + (k-j) C4's etc. — try small-n hybrids to beat n=33
def hub_mixed(tri, c4):
    parts = [3] * tri + [4] * c4
    n = 1 + sum(parts)
    A = np.zeros((n, n))
    pos = 1
    for c in parts:
        vs = list(range(pos, pos + c))
        pos += c
        for a in range(c):
            A[vs[a], vs[(a + 1) % c]] = A[vs[(a + 1) % c], vs[a]] = 1
            A[0, vs[a]] = A[vs[a], 0] = 1
    return A


print("minimal-n hunt (windmill + variants):")
best = (99, None)
for tri in range(0, 20):
    for c4 in range(0, 8):
        n = 1 + 3 * tri + 4 * c4
        if n > 33 or (tri == 0 and c4 == 0):
            continue
        e = mineig(hub_mixed(tri, c4))
        if e < -1e-9 and n < best[0]:
            best = (n, (tri, c4, e))
print("  best mixed:", best)

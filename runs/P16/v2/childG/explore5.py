"""childG exploration 5: mirror-doubling construction.

H1(G) := two disjoint copies of G plus an edge between the two copies of each
leaf.  Then delta(H1) >= 2, G subgraph of H1 so mu(G) <= mu(H1) <= RHS46(H1)
by Hyp D.  Question: RHS46(H1) <= RHS46(G)?
Also D1P: for Perron z of A_L(G), is z^T K z >= 0 (restricted D1) on leafy G?
Usage: explore5.py NMAX
"""
import numpy as np, subprocess, sys, math
from explore1 import graphs, g6_adj, t46, data

def rhs46_A(A):
    d = A.sum(1); m = A @ d / d
    n = A.shape[0]
    return max(t46(d[i], d[j], m[i], m[j])
               for i in range(n) for j in range(i+1, n) if A[i, j])

def mirror_double(A):
    n = A.shape[0]
    d = A.sum(1)
    B = np.zeros((2*n, 2*n))
    B[:n, :n] = A
    B[n:, n:] = A
    for i in range(n):
        if d[i] == 1:
            B[i, n+i] = B[n+i, i] = 1
    return B

def line_graph_A(A):
    n = A.shape[0]
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if A[i, j]]
    E = len(edges)
    R = np.zeros((n, E))
    for k, (i, j) in enumerate(edges):
        R[i, k] = R[j, k] = 1
    AL = R.T @ R - 2*np.eye(E)
    return AL, R, edges

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    worstH = (1e9, None); worstP = (1e9, None)
    for n in range(3, nmax+1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d = A.sum(1)
            if d.min() > 1:
                continue
            r46 = rhs46_A(A)
            H = mirror_double(A)
            slack = r46 - rhs46_A(H)
            if slack < worstH[0]: worstH = (slack, g6)
            # D1P
            AL, R, edges = line_graph_A(A)
            m = A @ d / d
            arg = np.array([2*(d[i]**2+d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j]) + 4
                            for i, j in edges])
            w, V = np.linalg.eigh(AL)
            z = np.abs(V[:, -1])
            val = float(arg @ (z*z) - w[-1]**2)
            if val < worstP[0]: worstP = (val, g6)
    print(f"H1 mirror-double: min (RHS46(G)-RHS46(H1)) = {worstH[0]:.6g} at {worstH[1]}")
    print(f"D1P Perron z^T K z: min = {worstP[0]:.6g} at {worstP[1]}")

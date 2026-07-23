"""Test: at the Perron-critical edge (i = argmax v of B=P^-1 Q P, j = argmax
v among N(i)), is term44/term46 >= rho(Q)? Also test other edge selections."""
import numpy as np, math, sys
from harness import graphs, g6_adj, term44, term46

def run(nmax):
    worst44 = (1e9, None); worst46 = (1e9, None)
    # also: best-edge-touching-i variants
    worst44i = (1e9, None); worst46i = (1e9, None)
    cnt = 0
    for n in range(2, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            nn = A.shape[0]
            d = A.sum(1); m = A @ d / d
            Q = np.diag(d) + A
            B = Q * (d[None, :] / d[:, None])  # B_ij = Q_ij d_j/d_i
            w, V = np.linalg.eig(B)
            k = np.argmax(w.real)
            rho = w[k].real
            v = np.abs(V[:, k].real)
            i = int(np.argmax(v))
            nbrs = [j for j in range(nn) if A[i, j]]
            j = max(nbrs, key=lambda x: v[x])
            t44 = term44(d[i], d[j], m[i], m[j])
            t46 = term46(d[i], d[j], m[i], m[j])
            if t44 - rho < worst44[0]: worst44 = (t44 - rho, g6)
            if t46 - rho < worst46[0]: worst46 = (t46 - rho, g6)
            # max term over edges incident to i
            t44i = max(term44(d[i], d[jj], m[i], m[jj]) for jj in nbrs)
            t46i = max(term46(d[i], d[jj], m[i], m[jj]) for jj in nbrs)
            if t44i - rho < worst44i[0]: worst44i = (t44i - rho, g6)
            if t46i - rho < worst46i[0]: worst46i = (t46i - rho, g6)
            cnt += 1
    print(f"graphs: {cnt}")
    print("Perron edge term44 - rho, min:", worst44)
    print("Perron edge term46 - rho, min:", worst46)
    print("best edge at Perron vertex term44 - rho, min:", worst44i)
    print("best edge at Perron vertex term46 - rho, min:", worst46i)

if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 8)

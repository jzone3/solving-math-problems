"""Scan candidate closed-form certificates h for the CW condition Mh >= 0
(entrywise), i.e. B h <= T*h, exhaustively over connected delta>=2 graphs.

Candidates must coincide (up to scale) with the ground state on regular
graphs (constant), since equality graphs pin rho = 1.  h = d does; so does
any h = d*f(local) with f == const on regular graphs.

Usage: h_scan.py nmax
"""
import sys
import numpy as np
from common import g6_to_adj, build, geng


def invariants(G):
    n, A, d, m, sig, w, edges = (G["n"], G["A"], G["d"], G["m"], G["sig"],
                                 G["w"], G["edges"])
    t = np.zeros(n)      # childF t_i = sum_{j~i} (sig_i+sig_j) w_ij
    td = np.zeros(n)     # degree-weighted: sum w_ij (sig_i d_i + sig_j d_j)/d_i
    W = np.zeros(n)
    for k, (i, j) in enumerate(edges):
        s = (sig[i] + sig[j]) * w[k]
        t[i] += s; t[j] += s
        td[i] += w[k] * (sig[i] * d[i] + sig[j] * d[j])
        td[j] += w[k] * (sig[i] * d[i] + sig[j] * d[j])
        W[i] += w[k]; W[j] += w[k]
    td = td / d
    T = G["T"]
    P = G["B"] / T[:, None]
    return dict(n=n, d=d, m=m, sig=sig, t=t, td=td, W=W, P=P, T=T)


CANDS = {
    "d":            lambda I: I["d"],
    "Pd":           lambda I: I["P"] @ I["d"],
    "P2d":          lambda I: I["P"] @ (I["P"] @ I["d"]),
    "d*max(t,1)":   lambda I: I["d"] * np.maximum(I["t"], 1.0),
    "d*max(td,1)":  lambda I: I["d"] * np.maximum(I["td"], 1.0),
    "d*t":          lambda I: I["d"] * np.maximum(I["t"], 1e-6),
    "d+sig":        lambda I: I["d"] + I["sig"],
    "T":            lambda I: I["T"],
    "d*m":          lambda I: I["d"] * I["m"],
    "sig*d":        lambda I: np.maximum(I["sig"], 1e-6) * I["d"],
    "d^2/T":        lambda I: I["d"] ** 2 / I["T"],
    "d*(1+(td-1)+)": lambda I: I["d"] * (1 + np.maximum(I["td"] - 1, 0)),
    "d/(2-td)":     lambda I: I["d"] / np.maximum(2 - I["td"], 1e-6),
    "d/(2-t)":      lambda I: I["d"] / np.maximum(2 - I["t"], 1e-6),
    "geo d,Pd":     lambda I: np.sqrt(I["d"] * (I["P"] @ I["d"])),
    "max(d,Pd)":    lambda I: np.maximum(I["d"], I["P"] @ I["d"]),
}


def main(nmax):
    fails = {k: 0 for k in CANDS}
    tot = 0
    for n in range(3, nmax + 1):
        for g6 in geng(n):
            tot += 1
            G = build(g6_to_adj(g6))
            I = invariants(G)
            M = G["M"]
            for k, f in CANDS.items():
                h = f(I)
                if h.min() <= 0 or (M @ h).min() < -1e-9:
                    fails[k] += 1
    print(f"total {tot} graphs, n<={nmax}")
    for k in sorted(fails, key=fails.get):
        print(f"  {k:15s} failures {fails[k]}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)

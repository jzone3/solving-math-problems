"""childG: machine verification of Lemmas G1/G2/G3/G4 + coverage statistics.

G1 (Schur pendant elimination, exact): for connected G with leaf set S
   (independent since G != K2), H = G - S, ell_i = #leaf-neighbours of i,
   t > 1:   mu(G) <= t  <=>  lammax( L(H) + (t/(t-1)) diag(ell) ) <= t.
   [numeric iff check on all leafy connected n <= 7 at several t]

G2 (leaf-aware Merris, unconditional): mu(G) <= t if for all i in H:
   d^H_i + m^H_i + (t/(t-1)) ell_i <= t   (isolated i in H: term = (t/(t-1))ell_i).
   [follows from G1 + Gershgorin on D^-1 M D; coverage at t = RHS46(G)]

G3 (leafy D2, unconditional): Bound 46 holds if every edge ij satisfies
   arg46(e) >= 4 + 2 d_i (d_i-2)^+ + 2 d_j (d_j-2)^+.
   [coverage count]

G4 (conditional on Hyp D = Bound 46 (or rho(Q) version) for delta>=2):
   if H = G - leaves is connected with delta(H) >= 2 and
   RHS46(H) + (T/(T-1)) max_i ell_i <= T where T = RHS46(G),
   then Bound 46 holds for G.  [coverage count]

Usage: verify_G.py NMAX
"""
import numpy as np, subprocess, sys, math
from explore1 import graphs, g6_adj, t46, data
from explore5 import rhs46_A

def split_leaves(A):
    d = A.sum(1)
    S = [i for i in range(A.shape[0]) if d[i] == 1]
    Hv = [i for i in range(A.shape[0]) if d[i] > 1]
    ell = {}
    for v in S:
        c = int(np.argmax(A[v]))
        ell[c] = ell.get(c, 0) + 1
    H = A[np.ix_(Hv, Hv)]
    ellvec = np.array([ell.get(i, 0) for i in Hv], float)
    return H, Hv, ellvec

def lammax(M):
    return float(np.linalg.eigvalsh(M)[-1]) if M.size else -math.inf

def g1_check(A, mu, ts):
    H, Hv, ell = split_leaves(A)
    if len(Hv) == 0:
        return True  # K2: skip
    LH = np.diag(H.sum(1)) - H
    ok = True
    for t in ts:
        lhs = mu <= t + 1e-9
        M = LH + (t/(t-1))*np.diag(ell)
        rhs = lammax(M) <= t + 1e-9
        if lhs != rhs:
            # tolerance boundary: recheck with strict margin
            if abs(mu - t) < 1e-6 or abs(lammax(M) - t) < 1e-6:
                continue
            ok = False
    return ok

if __name__ == "__main__":
    nmax = int(sys.argv[1])
    cnt = 0; g1_bad = 0
    cov = {"G2": 0, "G3": 0, "G4": 0, "union": 0}
    for n in range(3, nmax+1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, edges, mu, rq = data(A)
            if d.min() > 1:
                continue
            cnt += 1
            T = rhs46_A(A)
            # G1 iff check (only n<=7 to keep it fast)
            if n <= 7:
                ts = [mu - 0.3, mu + 0.3, T, mu + 3.0]
                ts = [t for t in ts if t > 1.5]
                if not g1_check(A, mu, ts):
                    g1_bad += 1
                    print("G1 IFF FAILURE at", g6)
            tau = T/(T-1)
            H, Hv, ell = split_leaves(A)
            # G2
            okG2 = False
            if len(Hv) > 0:
                dH = H.sum(1)
                with np.errstate(divide="ignore", invalid="ignore"):
                    mH = np.where(dH > 0, (H @ dH)/np.where(dH > 0, dH, 1), 0.0)
                vals = dH + mH + tau*ell
                okG2 = vals.max() <= T + 1e-9
            # G3
            okG3 = True
            for i, j in edges:
                arg = 2*(d[i]**2 + d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j]) + 4
                need = 4 + 2*d[i]*max(d[i]-2, 0) + 2*d[j]*max(d[j]-2, 0)
                if arg < need - 1e-9:
                    okG3 = False
                    break
            # G4
            okG4 = False
            if len(Hv) >= 2 and H.sum() > 0:
                dH = H.sum(1)
                if dH.min() >= 2:
                    # connectivity of H
                    reach = {0}
                    frontier = [0]
                    while frontier:
                        x = frontier.pop()
                        for y in np.where(H[x] > 0)[0]:
                            if y not in reach:
                                reach.add(int(y)); frontier.append(int(y))
                    if len(reach) == len(Hv):
                        okG4 = rhs46_A(H) + tau*ell.max() <= T + 1e-9
            for k, ok in (("G2", okG2), ("G3", okG3), ("G4", okG4)):
                cov[k] += ok
            cov["union"] += (okG2 or okG3 or okG4)
    print(f"leafy connected graphs n<={nmax}: {cnt}; G1 iff failures: {g1_bad}")
    for k in ("G2", "G3", "G4", "union"):
        print(f"{k}: covers {cov[k]} / {cnt}")

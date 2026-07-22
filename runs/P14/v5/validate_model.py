"""Validate every identity used in grand_ilp.py against explicit known BTDs.

For each test design (given as V x B multiplicity matrix), compute the actual
distributions (n_d, P_t, W-tuples, profiles E_p, oriented Y) and check EVERY
constraint of the grand model numerically. Any failure = bug in the model
(and would invalidate infeasibility conclusions).
"""
import itertools
from collections import Counter, defaultdict

def check_design(name, mat, V, B, r1, r2, R, K, L, verbose=True):
    fails = []
    def chk(label, lhs, rhs):
        if lhs != rhs:
            fails.append(f"{label}: {lhs} != {rhs}")
    theta = r1 + 4*r2 - L
    tau = theta + L*V
    # sanity of design itself
    for v in range(V):
        row = mat[v]
        chk(f"row{v} ones", sum(1 for x in row if x == 1), r1)
        chk(f"row{v} twos", sum(1 for x in row if x == 2), r2)
    for b in range(B):
        chk(f"col{b} sum", sum(mat[v][b] for v in range(V)), K)
    for v in range(V):
        for w in range(v+1, V):
            chk(f"pair{v},{w}", sum(mat[v][b]*mat[w][b] for b in range(B)), L)
    dmax = K//2
    d_of = [sum(1 for v in range(V) if mat[v][b] == 2) for b in range(B)]
    n = Counter(d_of)
    # pair types
    Pt = Counter()
    for v in range(V):
        for w in range(v+1, V):
            a = sum(1 for b in range(B) if mat[v][b] == 1 and mat[w][b] == 1)
            bb = sum(1 for b in range(B) if {mat[v][b], mat[w][b]} == {1, 2})
            c = sum(1 for b in range(B) if mat[v][b] == 2 and mat[w][b] == 2)
            chk(f"pairtype{v},{w}", a+2*bb+4*c, L)
            Pt[(a, bb, c)] += 1
    def C2(x): return x*(x-1)//2
    ds = range(dmax+1)
    chk("sum n_d", sum(n.values()), B)
    chk("sum d n_d", sum(d*n[d] for d in n), V*r2)
    chk("sum P", sum(Pt.values()), C2(V))
    chk("sum a P", sum(t[0]*Pt[t] for t in Pt), sum(C2(K-2*d)*n[d] for d in n))
    chk("sum b P", sum(t[1]*Pt[t] for t in Pt), sum(d*(K-2*d)*n[d] for d in n))
    chk("sum c P", sum(t[2]*Pt[t] for t in Pt), sum(C2(d)*n[d] for d in n))
    chk("sum s P", sum(sum(t)*Pt[t] for t in Pt), sum(C2(K-d)*n[d] for d in n))
    # W tuples over ordered block pairs
    Wc = Counter()
    for b in range(B):
        for b2 in range(B):
            if b == b2: continue
            n11 = sum(1 for v in range(V) if mat[v][b] == 1 and mat[v][b2] == 1)
            m12 = sum(1 for v in range(V) if mat[v][b] == 2 and mat[v][b2] == 1)
            m21 = sum(1 for v in range(V) if mat[v][b] == 1 and mat[v][b2] == 2)
            n22 = sum(1 for v in range(V) if mat[v][b] == 2 and mat[v][b2] == 2)
            Wc[(d_of[b], n11, m12, m21, n22)] += 1
            if L < 8:
                chk(f"n22<=1 b{b},{b2}", min(n22, 1), n22)
    def zval(tp): return tp[1]+2*(tp[2]+tp[3])+4*tp[4]
    def yval(tp): return tp[1]+tp[2]+tp[3]+tp[4]
    for d in ds:
        tps = [tp for tp in Wc if tp[0] == d]
        chk(f"W count d={d}", sum(Wc[tp] for tp in tps), (B-1)*n[d])
        chk(f"W n11 d={d}", sum(tp[1]*Wc[tp] for tp in tps), (K-2*d)*(r1-1)*n[d])
        chk(f"W m12 d={d}", sum(tp[2]*Wc[tp] for tp in tps), d*r1*n[d])
        chk(f"W m21 d={d}", sum(tp[3]*Wc[tp] for tp in tps), (K-2*d)*r2*n[d])
        chk(f"W n22 d={d}", sum(tp[4]*Wc[tp] for tp in tps), d*(r2-1)*n[d])
        chk(f"W z d={d}", sum(zval(tp)*Wc[tp] for tp in tps), (R*K-K-2*d)*n[d])
        chk(f"W y d={d}", sum(yval(tp)*Wc[tp] for tp in tps), (K-d)*(r1+r2-1)*n[d])
    chk("W C2(y) coupling", sum(C2(yval(tp))*Wc[tp] for tp in Wc),
        2*sum(C2(sum(t))*Pt[t] for t in Pt))
    chk("W C2(n22) coupling", sum(C2(tp[4])*Wc[tp] for tp in Wc),
        2*sum(C2(t[2])*Pt[t] for t in Pt))
    # profiles / oriented
    Ec = Counter(); Yc = Counter()
    for v in range(V):
        u = [0]*(dmax+1); w = [0]*(dmax+1)
        for b in range(B):
            if mat[v][b] == 1: u[d_of[b]] += 1
            elif mat[v][b] == 2: w[d_of[b]] += 1
        Ec[(tuple(u), tuple(w))] += 1
        for wv in range(V):
            if wv == v: continue
            a = sum(1 for b in range(B) if mat[v][b] == 1 and mat[wv][b] == 1)
            beta = sum(1 for b in range(B) if mat[v][b] == 2 and mat[wv][b] == 1)
            gam = sum(1 for b in range(B) if mat[v][b] == 1 and mat[wv][b] == 2)
            c = sum(1 for b in range(B) if mat[v][b] == 2 and mat[wv][b] == 2)
            Yc[((tuple(u), tuple(w)), (a, beta, gam, c))] += 1
    chk("sum E", sum(Ec.values()), V)
    for d in ds:
        chk(f"E u_d={d}", sum(p[0][d]*Ec[p] for p in Ec), (K-2*d)*n[d])
        chk(f"E w_d={d}", sum(p[1][d]*Ec[p] for p in Ec), d*n[d])
    for p in Ec:
        u, w = p
        A_ = sum(u[d]*(K-2*d-1) for d in ds)
        Dv = sum(w[d]*(K-2*d) for d in ds)
        Gv = sum(u[d]*d for d in ds)
        Cv = sum(w[d]*(d-1) for d in ds)
        yy = [(ot, Yc[(p, ot)]) for (pp, ot) in Yc if pp == p]
        chk(f"Y count p={p}", sum(c for _, c in yy), (V-1)*Ec[p])
        chk(f"Y a p={p}", sum(ot[0]*c for ot, c in yy), A_*Ec[p])
        chk(f"Y beta p={p}", sum(ot[1]*c for ot, c in yy), Dv*Ec[p])
        chk(f"Y gamma p={p}", sum(ot[2]*c for ot, c in yy), Gv*Ec[p])
        chk(f"Y c p={p}", sum(ot[3]*c for ot, c in yy), Cv*Ec[p])
    # orientation symmetry & 2P coupling
    ori = Counter()
    for (p, ot), cnt in Yc.items(): ori[ot] += cnt
    for ot in list(ori):
        rev = (ot[0], ot[2], ot[1], ot[3])
        chk(f"orient sym {ot}", ori[ot], ori[rev])
    unot = Counter()
    for ot, cnt in ori.items(): unot[(ot[0], ot[1]+ot[2], ot[3])] += cnt
    for t in Pt: chk(f"2P coupling {t}", unot[t], 2*Pt[t])
    # trace identities
    chk("T1", sum(zval(tp)**2*Wc[tp] for tp in Wc),
        (V-1)*theta**2 + tau**2 - sum((K+2*d)**2*n[d] for d in n))
    chk("T2", 2*sum(sum(t)**2*Pt[t] for t in Pt),
        sum(yval(tp)**2*Wc[tp] for tp in Wc) + sum((K-d)**2*n[d] for d in n) - V*(r1+r2)**2)
    chk("T3", 2*sum(t[0]**2*Pt[t] for t in Pt),
        sum(tp[1]**2*Wc[tp] for tp in Wc) + sum((K-2*d)**2*n[d] for d in n) - V*r1**2)
    chk("T4", 2*sum(t[2]**2*Pt[t] for t in Pt),
        sum(tp[4]**2*Wc[tp] for tp in Wc) + sum(d**2*n[d] for d in n) - V*r2**2)
    chk("T5", sum(ot[2]**2*c for (p, ot), c in Yc.items()),
        sum(d*(K-2*d)*n[d] for d in n) + sum(tp[1]*tp[4]*Wc[tp] for tp in Wc))
    chk("T6", V*r1*r2 + 2*sum(t[0]*t[2]*Pt[t] for t in Pt),
        sum(tp[2]**2*Wc[tp] for tp in Wc))
    chk("T8", sum(ot[1]*ot[2]*c for (p, ot), c in Yc.items()),
        sum(tp[2]*tp[3]*Wc[tp] for tp in Wc))
    chk("T10", sum((tp[1]+tp[2]+2*(tp[3]+tp[4]))**2*Wc[tp] for tp in Wc),
        V*(r1+r2)*(r1+4*r2) + 2*L*sum(sum(t)*Pt[t] for t in Pt) - B*K*K)
    chk("T11", V*r1*(r1+4*r2) + 2*L*sum(t[0]*Pt[t] for t in Pt),
        sum((K-2*d)**2*n[d] for d in n) + sum((tp[1]+2*tp[3])**2*Wc[tp] for tp in Wc))
    chk("T12", V*r2*(r1+4*r2) + 2*L*sum(t[2]*Pt[t] for t in Pt),
        sum(4*d*d*n[d] for d in n) + sum((tp[2]+2*tp[4])**2*Wc[tp] for tp in Wc))
    if fails:
        print(f"{name}: {len(fails)} FAILURES")
        for f in fails[:40]: print("   ", f)
    else:
        print(f"{name}: ALL IDENTITIES PASS")
    return not fails

if __name__ == "__main__":
    # BPTD(4; 1,8,9; 3,3,9; 4,7) from Kunkle-Sarvate
    cols = ["1122", "1134", "1144", "2234", "2244", "3312", "3312", "3344", "1234"]
    mat = [[0]*9 for _ in range(4)]
    for b, col in enumerate(cols):
        for ch in col:
            mat[int(ch)-1][b] += 1
    check_design("BTD(4,9;3,3,9;4,7)", mat, 4, 9, 3, 3, 9, 4, 7)
    # BTD(4,8;2,3,8;4,6) example (first variant) from Kunkle-Sarvate 93_01
    cols2 = ["1122", "1133", "1144", "2233", "2244", "3344", "1234", "1234"]
    mat2 = [[0]*8 for _ in range(4)]
    for b, col in enumerate(cols2):
        for ch in col:
            mat2[int(ch)-1][b] += 1
    check_design("BTD(4,8;2,3,8;4,6)", mat2, 4, 8, 2, 3, 8, 4, 6)

"""P14 V5: "grand" counting ILP = L1 + L2 + L3 + full two-point (second moment)
trace identities. Every constraint is an exact consequence of BTD existence;
INFEASIBLE => nonexistence proof. FEASIBLE => no conclusion.

Matrices: N = S + 2D (S=singles 0/1, D=doubles 0/1, disjoint supports),
A = S + D (support). Known Gram: N N^T = theta I + L J, theta = r1+4r2-L,
eigenvalues theta (V-1 times), tau = theta + LV.

Trace identities used (all sides linear in the distribution variables):
 T1: sum_{b!=b'} z^2            = (V-1)theta^2 + tau^2 - sum_d (K+2d)^2 n_d
     where z = n11 + 2(m12+m21) + 4 n22   [trace((N^T N)^2)]
 T2: 2 sum_t s_t^2 P_t          = sum_{b!=b'} y^2 + sum_d (K-d)^2 n_d - V(r1+r2)^2
     where s=a+b+c, y=n11+m12+m21+n22     [trace((A A^T)^2)]
 T3: 2 sum_t a_t^2 P_t          = sum_{b!=b'} n11^2 + sum_d (K-2d)^2 n_d - V r1^2
 T4: 2 sum_t c_t^2 P_t          = sum_{b!=b'} n22^2 + sum_d d^2 n_d - V r2^2
 T5: sum_Y gamma^2 Y            = sum_d d(K-2d) n_d + sum_{b!=b'} n11*n22
 T6: V r1 r2 + 2 sum_t a_t c_t P_t = sum_{b!=b'} m12^2
 T8: sum_Y beta*gamma Y         = sum_{b!=b'} m12*m21
 T10: sum_{b!=b'} y*z           = V(r1+r2)(r1+4r2) + 2L sum_t s_t P_t
                                   - sum_d (K-d)(K+2d) n_d
 T11: V r1(r1+4r2) + 2L sum_t a_t P_t = sum_d (K-2d)^2 n_d ... corrected below:
      trace(S S^T N N^T): V r1(r1+4r2) + L * 2 sum_t a_t P_t
        = sum_d (K-2d)^2 n_d + sum_{b!=b'} (n11+2*m21)^2
      wait diagonal of (S^T N)(N^T S): (S^T N)_{bb} = K-2d; handled explicitly.
 T12: trace(D D^T N N^T): V r2(r1+4r2) + 2L sum_t c_t P_t
        = sum_d (2d)^2 n_d + sum_{b!=b'} (m12+2*n22)^2
Forbidden configurations: n22 <= 1 for all instances (two blocks sharing two
common doubles would force a pair with 4c >= 8 > L).
For L=4: any common element pair of two blocks has s>=2; pair types restricted
to a+2b+4c=4 (automatic).
"""
import itertools
from collections import defaultdict
import pulp

INSTANCES = [
    ("I1", 14, 18, 7, 1, 9, 7, 4),
    ("I2", 12, 15, 6, 2, 10, 8, 6),
    ("I3", 12, 20, 4, 3, 10, 6, 4),
    ("I4", 14, 28, 8, 3, 14, 7, 6),
]

def C2(x): return x*(x-1)//2

def compositions(total, parts):
    if parts == 1:
        yield (total,); return
    for first in range(total+1):
        for rest in compositions(total-first, parts-1):
            yield (first,) + rest

def pair_types(L):
    return [(L-4*c-2*b, b, c) for c in range(L//4+1) for b in range((L-4*c)//2+1)]

def oriented_types(L):
    ots = []
    for c in range(L//4+1):
        rem = L-4*c
        for bg in range(rem//2+1):
            a = rem-2*bg
            for beta in range(bg+1):
                ots.append((a, beta, bg-beta, c))
    return ots

def solve(name, V, B, r1, r2, R, K, L, msg=False, timeLimit=1200):
    dmax = K//2
    ds = list(range(dmax+1))
    theta = r1+4*r2-L
    tau = theta + L*V
    ts = pair_types(L)
    ots = oriented_types(L)
    prob = pulp.LpProblem(f"grand_{name}", pulp.LpMinimize)
    n = {d: pulp.LpVariable(f"n_{d}", 0, B, cat="Integer") for d in ds}
    P = {t: pulp.LpVariable(f"P_{t}", 0, C2(V), cat="Integer") for t in ts}
    prob += 0
    # L1
    prob += pulp.lpSum(n.values()) == B
    prob += pulp.lpSum(d*n[d] for d in ds) == V*r2
    prob += pulp.lpSum(P.values()) == C2(V)
    prob += pulp.lpSum(t[0]*P[t] for t in ts) == pulp.lpSum(C2(K-2*d)*n[d] for d in ds)
    prob += pulp.lpSum(t[1]*P[t] for t in ts) == pulp.lpSum(d*(K-2*d)*n[d] for d in ds)
    prob += pulp.lpSum(t[2]*P[t] for t in ts) == pulp.lpSum(C2(d)*n[d] for d in ds)
    prob += pulp.lpSum(sum(t)*P[t] for t in ts) == pulp.lpSum(C2(K-d)*n[d] for d in ds)
    for d in ds:
        if K-d > V: prob += n[d] == 0
    # L2 ordered block-pair tuples (d, n11, m12, m21, n22), n22 <= 1
    tuples = []
    for d in ds:
        for n22 in range(0, min(d, 1)+1):
            for m12 in range(0, d-n22+1):
                for m21 in range(0, dmax-n22+1):
                    for n11 in range(0, K-2*d+1):
                        y = n11+m12+m21+n22
                        if y > K-d: continue
                        tuples.append((d, n11, m12, m21, n22))
    W = {tp: pulp.LpVariable(f"W_{'_'.join(map(str,tp))}", 0, B*(B-1), cat="Integer")
         for tp in tuples}
    def zval(tp): return tp[1] + 2*(tp[2]+tp[3]) + 4*tp[4]
    def yval(tp): return tp[1]+tp[2]+tp[3]+tp[4]
    for d in ds:
        tps = [tp for tp in tuples if tp[0] == d]
        prob += pulp.lpSum(W[tp] for tp in tps) == (B-1)*n[d]
        prob += pulp.lpSum(tp[1]*W[tp] for tp in tps) == (K-2*d)*(r1-1)*n[d]
        prob += pulp.lpSum(tp[2]*W[tp] for tp in tps) == d*r1*n[d]
        prob += pulp.lpSum(tp[3]*W[tp] for tp in tps) == (K-2*d)*r2*n[d]
        prob += pulp.lpSum(tp[4]*W[tp] for tp in tps) == d*(r2-1)*n[d]
        prob += pulp.lpSum(zval(tp)*W[tp] for tp in tps) == (R*K-K-2*d)*n[d]
        prob += pulp.lpSum(yval(tp)*W[tp] for tp in tps) == (K-d)*(r1+r2-1)*n[d]
    # transpose symmetry
    sig = defaultdict(list)
    for tp in tuples: sig[(tp[1], tp[2], tp[3], tp[4])].append(tp)
    for s in list(sig):
        sw = (s[0], s[2], s[1], s[3])
        if sw in sig and s < sw:
            prob += pulp.lpSum(W[tp] for tp in sig[s]) == pulp.lpSum(W[tp] for tp in sig[sw])
    # couplings to P
    prob += pulp.lpSum(C2(yval(tp))*W[tp] for tp in tuples) == 2*pulp.lpSum(C2(sum(t))*P[t] for t in ts)
    prob += pulp.lpSum(C2(tp[4])*W[tp] for tp in tuples) == 2*pulp.lpSum(C2(t[2])*P[t] for t in ts)
    # L3 element profiles
    us = [u for u in compositions(r1, dmax+1) if all(u[d] == 0 or K-2*d >= 1 for d in ds)]
    ws = [(0,)+w for w in compositions(r2, dmax)]
    profs = [(u, w) for u in us for w in ws]
    def quants(p):
        u, w = p
        A_ = sum(u[d]*(K-2*d-1) for d in ds)
        Dv = sum(w[d]*(K-2*d) for d in ds)
        Gv = sum(u[d]*d for d in ds)
        Cv = sum(w[d]*(d-1) for d in ds)
        return A_, Dv, Gv, Cv
    E = {p: pulp.LpVariable(f"E_{i}", 0, V, cat="Integer") for i, p in enumerate(profs)}
    Y = {(p, ot): pulp.LpVariable(f"Y_{i}_{j}", 0, V*(V-1), cat="Integer")
         for i, p in enumerate(profs) for j, ot in enumerate(ots)}
    prob += pulp.lpSum(E.values()) == V
    for d in ds:
        prob += pulp.lpSum(p[0][d]*E[p] for p in profs) == (K-2*d)*n[d]
        prob += pulp.lpSum(p[1][d]*E[p] for p in profs) == d*n[d]
    for p in profs:
        A_, Dv, Gv, Cv = quants(p)
        prob += pulp.lpSum(Y[(p, ot)] for ot in ots) == (V-1)*E[p]
        prob += pulp.lpSum(ot[0]*Y[(p, ot)] for ot in ots) == A_*E[p]
        prob += pulp.lpSum(ot[1]*Y[(p, ot)] for ot in ots) == Dv*E[p]
        prob += pulp.lpSum(ot[2]*Y[(p, ot)] for ot in ots) == Gv*E[p]
        prob += pulp.lpSum(ot[3]*Y[(p, ot)] for ot in ots) == Cv*E[p]
    for ot in ots:
        rev = (ot[0], ot[2], ot[1], ot[3])
        if ot < rev:
            prob += pulp.lpSum(Y[(p, ot)] for p in profs) == pulp.lpSum(Y[(p, rev)] for p in profs)
    for t in ts:
        orients = [ot for ot in ots if (ot[0], ot[1]+ot[2], ot[3]) == t]
        prob += pulp.lpSum(Y[(p, ot)] for p in profs for ot in orients) == 2*P[t]
    # ---- trace identities ----
    # T1
    prob += pulp.lpSum(zval(tp)**2*W[tp] for tp in tuples) == \
        (V-1)*theta**2 + tau**2 - pulp.lpSum((K+2*d)**2*n[d] for d in ds)
    # T2
    prob += 2*pulp.lpSum(sum(t)**2*P[t] for t in ts) == \
        pulp.lpSum(yval(tp)**2*W[tp] for tp in tuples) + \
        pulp.lpSum((K-d)**2*n[d] for d in ds) - V*(r1+r2)**2
    # T3
    prob += 2*pulp.lpSum(t[0]**2*P[t] for t in ts) == \
        pulp.lpSum(tp[1]**2*W[tp] for tp in tuples) + \
        pulp.lpSum((K-2*d)**2*n[d] for d in ds) - V*r1**2
    # T4
    prob += 2*pulp.lpSum(t[2]**2*P[t] for t in ts) == \
        pulp.lpSum(tp[4]**2*W[tp] for tp in tuples) + \
        pulp.lpSum(d**2*n[d] for d in ds) - V*r2**2
    # T5: sum_ordered gamma^2 via Y = sum_d d(K-2d) n_d + sum_{b!=b'} n11*n22
    prob += pulp.lpSum(ot[2]**2*Y[(p, ot)] for p in profs for ot in ots) == \
        pulp.lpSum(d*(K-2*d)*n[d] for d in ds) + \
        pulp.lpSum(tp[1]*tp[4]*W[tp] for tp in tuples)
    # T6: V r1 r2 + 2 sum a c P = sum m12^2 W
    prob += V*r1*r2 + 2*pulp.lpSum(t[0]*t[2]*P[t] for t in ts) == \
        pulp.lpSum(tp[2]**2*W[tp] for tp in tuples)
    # T8: sum_Y beta*gamma Y = sum_W m12*m21 W
    prob += pulp.lpSum(ot[1]*ot[2]*Y[(p, ot)] for p in profs for ot in ots) == \
        pulp.lpSum(tp[2]*tp[3]*W[tp] for tp in tuples)
    # T10 (corrected): trace(A A^T N N^T); (A^T N)_{bb'} = n11+m12+2(m21+n22), diag K
    prob += pulp.lpSum((tp[1]+tp[2]+2*(tp[3]+tp[4]))**2*W[tp] for tp in tuples) == \
        V*(r1+r2)*(r1+4*r2) + 2*L*pulp.lpSum(sum(t)*P[t] for t in ts) - B*K*K
    # T11: trace(SS^T NN^T) = V r1 (r1+4r2) + L*2*sum a_t P_t
    #      = sum_{b,b'} (S^T N)_{bb'} (N^T S)_{b'b};  (S^T N)_{bb'} = n11+2*m21(b,b'),
    #      (N^T S)_{b'b} = n11+2*m21(b,b') as well (see derivation), diag (K-2d)
    prob += V*r1*(r1+4*r2) + 2*L*pulp.lpSum(t[0]*P[t] for t in ts) == \
        pulp.lpSum((K-2*d)**2*n[d] for d in ds) + \
        pulp.lpSum((tp[1]+2*tp[3])**2*W[tp] for tp in tuples)
    # T12: trace(DD^T NN^T) = V r2 (r1+4r2) + 2L sum c_t P_t
    #      = sum_d (2d)^2 n_d + sum (m12+2 n22)^2 W
    prob += V*r2*(r1+4*r2) + 2*L*pulp.lpSum(t[2]*P[t] for t in ts) == \
        pulp.lpSum(4*d*d*n[d] for d in ds) + \
        pulp.lpSum((tp[2]+2*tp[4])**2*W[tp] for tp in tuples)
    solver = pulp.PULP_CBC_CMD(msg=msg, timeLimit=timeLimit)
    prob.solve(solver)
    return pulp.LpStatus[prob.status], n, P, prob

if __name__ == "__main__":
    for inst in INSTANCES:
        st, n, P, prob = solve(*inst)
        print(f"{inst[0]}: {st}", flush=True)
        if st == "Optimal":
            print(f"   n_d = { {d: int(v.value()) for d, v in n.items() if v.value() and v.value()>0.5} }")
            print(f"   P_t = { {t: int(v.value()) for t, v in P.items() if v.value() and v.value()>0.5} }")

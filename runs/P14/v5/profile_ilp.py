"""P14 V5: Level-3 counting ILP — element profiles x oriented neighbor types.

All constraints are exact double-counting consequences of BTD existence, so
INFEASIBLE => nonexistence proof. FEASIBLE => no conclusion.

Element profile p = ((u_d)_d, (w_d)_d): u_d = #blocks where v is SINGLE and the
block has d doubles total; w_d = #blocks where v is DOUBLE (block has d doubles,
d>=1, v among them). sum u = r1, sum w = r2.

Derived per-profile exact quantities:
  A(p) = sum_d u_d * (K-2d-1)     total both-single co-occurrence slots
  Dv(p) = sum_d w_d * (K-2d)      v-double/other-single slots
  Gv(p) = sum_d u_d * d           v-single/other-double slots
  Cv(p) = sum_d w_d * (d-1)       both-double slots

Oriented pair type ot=(a,beta,gamma,c): pair {v,w} co-occurs in a blocks both
single, beta blocks v double & w single, gamma blocks v single & w double, c
blocks both double; a + 2(beta+gamma) + 4c = Lambda.

Per element v (aggregated over elements sharing profile p via vars Y[p,ot]):
  sum_ot Y[p,ot] = (V-1) E_p
  sum a*Y = A(p) E_p ; sum beta*Y = Dv(p) E_p ; sum gamma*Y = Gv(p) E_p
  sum c*Y = Cv(p) E_p
Global:
  sum_p E_p = V ; sum_p u_d(p) E_p = (K-2d) n_d ; sum_p w_d(p) E_p = d n_d
  orientation symmetry: sum_p Y[p,(a,b,g,c)] = sum_p Y[p,(a,g,b,c)]
  sum over orientations mapping to unordered type t: sum = 2 P_t
Plus all Level-1 constraints on (n_d, P_t) (from counting_ilp: reimplemented here).
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

def oriented_types(L):
    ots = []
    for c in range(L//4+1):
        rem = L - 4*c
        for bg in range(rem//2+1):
            a = rem - 2*bg
            for beta in range(bg+1):
                ots.append((a, beta, bg-beta, c))
    return ots

def profiles(V, B, r1, r2, K):
    dmax = K//2
    ds = list(range(dmax+1))
    us = [u for u in compositions(r1, dmax+1)
          if all(u[d] == 0 or K-2*d >= 1 for d in ds)]
    # w_d only for d>=1 (v doubled => block has >=1 double)
    ws = [(0,)+w for w in compositions(r2, dmax)] if dmax >= 1 else [(0,)*(dmax+1)]
    out = []
    for u in us:
        for w in ws:
            # a block with d doubles has K-2d singles and d doubles;
            # #elements with u_d>0 etc. checked globally
            out.append((u, w))
    return out, ds

def profile_quants(p, K):
    u, w = p
    A = sum(u[d]*(K-2*d-1) for d in range(len(u)))
    Dv = sum(w[d]*(K-2*d) for d in range(len(w)))
    Gv = sum(u[d]*d for d in range(len(u)))
    Cv = sum(w[d]*(d-1) for d in range(len(w)))
    return A, Dv, Gv, Cv

def per_element_feasible(p, K, V, L, ots):
    """Quick LP-free integer feasibility of the per-element neighbor system for
    one element with profile p (used to prune profiles: E_p=0 if infeasible)."""
    A, Dv, Gv, Cv = profile_quants(p, K)
    # need y_ot >= 0 integers: sum y = V-1, sum a y = A, sum beta y = Dv,
    # sum gamma y = Gv, sum c y = Cv
    # small ILP via pulp? do a fast necessary check + tiny ILP
    prob = pulp.LpProblem("pe", pulp.LpMinimize)
    y = {ot: pulp.LpVariable(f"y{i}", 0, V-1, cat="Integer") for i, ot in enumerate(ots)}
    prob += 0
    prob += pulp.lpSum(y.values()) == V-1
    prob += pulp.lpSum(ot[0]*y[ot] for ot in ots) == A
    prob += pulp.lpSum(ot[1]*y[ot] for ot in ots) == Dv
    prob += pulp.lpSum(ot[2]*y[ot] for ot in ots) == Gv
    prob += pulp.lpSum(ot[3]*y[ot] for ot in ots) == Cv
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    return pulp.LpStatus[prob.status] == "Optimal"

def pair_types(L):
    ts = []
    for c in range(L//4+1):
        for b in range((L-4*c)//2+1):
            ts.append((L-4*c-2*b, b, c))
    return ts

def solve(name, V, B, r1, r2, R, K, L, msg=False, prune=True):
    dmax = K//2
    ds = list(range(dmax+1))
    ots = oriented_types(L)
    ts = pair_types(L)
    profs, _ = profiles(V, B, r1, r2, K)
    if prune:
        profs = [p for p in profs if per_element_feasible(p, K, V, L, ots)]
        if not profs:
            return "Infeasible(no feasible element profile)", None
    prob = pulp.LpProblem(f"P14L3_{name}", pulp.LpMinimize)
    n = {d: pulp.LpVariable(f"n_{d}", 0, B, cat="Integer") for d in ds}
    P = {t: pulp.LpVariable(f"P_{t}", 0, C2(V), cat="Integer") for t in ts}
    E = {p: pulp.LpVariable(f"E_{i}", 0, V, cat="Integer") for i, p in enumerate(profs)}
    Y = {(p, ot): pulp.LpVariable(f"Y_{i}_{j}", 0, V*(V-1), cat="Integer")
         for i, p in enumerate(profs) for j, ot in enumerate(ots)}
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
        if K - d > V:
            prob += n[d] == 0
    # profiles
    prob += pulp.lpSum(E.values()) == V
    for d in ds:
        prob += pulp.lpSum(p[0][d]*E[p] for p in profs) == (K-2*d)*n[d]
        prob += pulp.lpSum(p[1][d]*E[p] for p in profs) == d*n[d]
    for p in profs:
        A, Dv, Gv, Cv = profile_quants(p, K)
        prob += pulp.lpSum(Y[(p, ot)] for ot in ots) == (V-1)*E[p]
        prob += pulp.lpSum(ot[0]*Y[(p, ot)] for ot in ots) == A*E[p]
        prob += pulp.lpSum(ot[1]*Y[(p, ot)] for ot in ots) == Dv*E[p]
        prob += pulp.lpSum(ot[2]*Y[(p, ot)] for ot in ots) == Gv*E[p]
        prob += pulp.lpSum(ot[3]*Y[(p, ot)] for ot in ots) == Cv*E[p]
    # orientation symmetry + pair-type coupling
    for ot in ots:
        rev = (ot[0], ot[2], ot[1], ot[3])
        if ot < rev:
            prob += pulp.lpSum(Y[(p, ot)] for p in profs) == \
                    pulp.lpSum(Y[(p, rev)] for p in profs)
    for t in ts:
        orients = [ot for ot in ots if (ot[0], ot[1]+ot[2], ot[3]) == t]
        prob += pulp.lpSum(Y[(p, ot)] for p in profs for ot in orients) == 2*P[t]
    prob.solve(pulp.PULP_CBC_CMD(msg=msg))
    return pulp.LpStatus[prob.status], (n, P, E, profs, prob)

if __name__ == "__main__":
    for inst in INSTANCES:
        name = inst[0]
        st, data = solve(*inst)
        print(f"{name}: {st}", flush=True)
        if data and pulp.LpStatus and st == "Optimal":
            n, P, E, profs, prob = data
            nd = {d: int(v.value()) for d, v in n.items() if v.value() and v.value() > .5}
            pt = {t: int(v.value()) for t, v in P.items() if v.value() and v.value() > .5}
            ep = {i: (p, int(E[p].value())) for i, p in enumerate(profs)
                  if E[p].value() and E[p].value() > .5}
            print(f"   n_d = {nd}")
            print(f"   P_t = {pt}")
            print(f"   #profiles used = {len(ep)} of {len(profs)}")

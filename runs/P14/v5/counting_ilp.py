"""P14 V5: counting-relaxation ILPs for the 4 open BTD instances.

Every constraint below is a *proved* consequence of BTD existence (double-counting
identities). Hence: ILP infeasible => BTD does not exist (a nonexistence proof).
ILP feasible => no conclusion (the relaxation forgets most structure).

Levels:
  L1 (block/pair types):
    n_d = #blocks with exactly d doubled elements (0 <= d <= K//2)
    P_t = #pairs {v,w} of "type" t=(a,b,c): a blocks both-single, b blocks
          exactly-one-double, c blocks both-double; a+2b+4c = Lambda.
    Identities:
      sum n_d = B ;  sum d*n_d = V*r2
      sum P_t = C(V,2)
      sum a_t P_t = sum_d C(K-2d,2) n_d      (both-single co-occurrences)
      sum b_t P_t = sum_d d(K-2d) n_d        (mixed co-occurrences)
      sum c_t P_t = sum_d C(d,2) n_d         (both-double co-occurrences)
      sum (a+b+c)_t P_t = sum_d C(K-d,2) n_d (distinct-support pairs)
  L2 (ordered block-pair types, coupled to block doubles-count d):
    For ordered pairs (b,b'), b'!=b, classify the common support of b,b' by
    (n11, m12, m21, n22): #elements single-in-both, double-in-b & single-in-b',
    single-in-b & double-in-b', double-in-both.
    W[d,(n11,m12,m21,n22)] = #ordered pairs with first block of type d.
    Per-block-of-type-d row sums (exact identities):
      sum_tuple W[d,.] = (B-1) n_d
      sum n11*W[d,.] = (K-2d)(r1-1) n_d
      sum m12*W[d,.] = d*r1 n_d
      sum m21*W[d,.] = (K-2d)*r2 n_d
      sum n22*W[d,.] = d*(r2-1) n_d
    Symmetry: total of W over tuples with (m12,m21) swapped must match.
    Coupling to pair types (pairs {v,w} inside common support):
      sum_{d,tuple} C(y,2) W  = 2 * sum_t C(s_t,2) P_t,  y = n11+m12+m21+n22
    Coupling of inner products (z = n11 + 2(m12+m21) + 4 n22):
      sum z*W[d,.] = (R*K - K - 2d) n_d      (from column-sum identity)
    Additional per-pair sanity: for a pair of blocks, common pairs {v,w} both
    covered there contribute; for Lambda=4 designs, a pair {v,w} with c=1 has
    a=b=0 (4c=Lambda), i.e. supports of its two "double-blocks"... (captured
    in types since only feasible (a,b,c) are enumerated).
All variables integer >= 0.  Solved with CBC (exact rational-friendly sizes).
"""
import itertools, sys
import pulp

INSTANCES = [
    ("I1", 14, 18, 7, 1, 9, 7, 4),
    ("I2", 12, 15, 6, 2, 10, 8, 6),
    ("I3", 12, 20, 4, 3, 10, 6, 4),
    ("I4", 14, 28, 8, 3, 14, 7, 6),
]

def C2(x): return x*(x-1)//2

def pair_types(L):
    # (a,b,c) with a+2b+4c = L, a,b,c >= 0
    ts = []
    for c in range(L//4 + 1):
        for b in range((L-4*c)//2 + 1):
            a = L - 4*c - 2*b
            ts.append((a, b, c))
    return ts

def solve(name, V, B, r1, r2, R, K, L, extra=None, msg=False):
    dmax = K // 2
    ds = list(range(dmax + 1))
    prob = pulp.LpProblem(f"P14_{name}", pulp.LpMinimize)
    n = {d: pulp.LpVariable(f"n_{d}", 0, B, cat="Integer") for d in ds}
    ts = pair_types(L)
    P = {t: pulp.LpVariable(f"P_{t}", 0, C2(V), cat="Integer") for t in ts}
    prob += 0  # feasibility
    prob += pulp.lpSum(n.values()) == B
    prob += pulp.lpSum(d*n[d] for d in ds) == V*r2
    prob += pulp.lpSum(P.values()) == C2(V)
    prob += pulp.lpSum(t[0]*P[t] for t in ts) == pulp.lpSum(C2(K-2*d)*n[d] for d in ds)
    prob += pulp.lpSum(t[1]*P[t] for t in ts) == pulp.lpSum(d*(K-2*d)*n[d] for d in ds)
    prob += pulp.lpSum(t[2]*P[t] for t in ts) == pulp.lpSum(C2(d)*n[d] for d in ds)
    prob += pulp.lpSum(sum(t)*P[t] for t in ts) == pulp.lpSum(C2(K-d)*n[d] for d in ds)
    # a block with d doubles has K-2d singles >= 0 automatically (d <= K//2);
    # support size K-d <= V
    for d in ds:
        if K - d > V:
            prob += n[d] == 0
    # per-element neighbor-count feasibility (aggregate): each element v has
    # exactly V-1 neighbors; total (v,w,block) co-occurrence "slots":
    #   sum_t s_t P_t = sum_d C2(K-d) n_d   (already above)
    # ---- Level 2 ----
    tuples = []
    for d in ds:
        for n22 in range(0, min(d, dmax) + 1):
            for m12 in range(0, d - n22 + 1):
                for m21 in range(0, dmax - n22 + 1):
                    for n11 in range(0, K - 2*d - 0 + 1):
                        # common support y <= min(K-d, K-d') <= K-d
                        y = n11 + m12 + m21 + n22
                        if y > K - d:
                            continue
                        tuples.append((d, n11, m12, m21, n22))
    W = {tp: pulp.LpVariable(f"W_{'_'.join(map(str,tp))}", 0, B*(B-1), cat="Integer")
         for tp in tuples}
    for d in ds:
        tps = [tp for tp in tuples if tp[0] == d]
        prob += pulp.lpSum(W[tp] for tp in tps) == (B-1)*n[d]
        prob += pulp.lpSum(tp[1]*W[tp] for tp in tps) == (K-2*d)*(r1-1)*n[d]
        prob += pulp.lpSum(tp[2]*W[tp] for tp in tps) == d*r1*n[d]
        prob += pulp.lpSum(tp[3]*W[tp] for tp in tps) == (K-2*d)*r2*n[d]
        prob += pulp.lpSum(tp[4]*W[tp] for tp in tps) == d*(r2-1)*n[d]
        z_rhs = (R*K - K - 2*d)
        prob += pulp.lpSum((tp[1] + 2*(tp[2]+tp[3]) + 4*tp[4])*W[tp] for tp in tps) \
                == z_rhs*n[d]
    # transpose symmetry: number of ordered pairs with signature (n11,m12,m21,n22)
    # summed over d equals number with (n11,m21,m12,n22) summed over d
    from collections import defaultdict
    sig = defaultdict(list)
    for tp in tuples:
        sig[(tp[1], tp[2], tp[3], tp[4])].append(tp)
    for s in list(sig):
        sw = (s[0], s[2], s[1], s[3])
        if sw in sig and s < sw:
            prob += pulp.lpSum(W[tp] for tp in sig[s]) == pulp.lpSum(W[tp] for tp in sig[sw])
    # coupling: ordered block pairs both containing pair {v,w} in support
    prob += pulp.lpSum(C2(tp[1]+tp[2]+tp[3]+tp[4])*W[tp] for tp in tuples) \
            == 2*pulp.lpSum(C2(sum(t))*P[t] for t in ts)
    # coupling: both-double common pairs across two blocks:
    # sum over ordered block pairs of C2(n22) = 2*sum over pairs {v,w} of C2(c_vw)
    prob += pulp.lpSum(C2(tp[4])*W[tp] for tp in tuples) \
            == 2*pulp.lpSum(C2(t[2])*P[t] for t in ts)
    # coupling: (v,w) both in support of both blocks with v,w both double in both:
    # also mixed: sum over ordered pairs of m12*m21-ish is not exact; skip.
    if extra:
        extra(prob, n, P, W, ds, ts, tuples)
    solver = pulp.PULP_CBC_CMD(msg=msg)
    status = prob.solve(solver)
    st = pulp.LpStatus[prob.status]
    return st, n, P, prob

if __name__ == "__main__":
    for inst in INSTANCES:
        name = inst[0]
        st, n, P, prob = solve(*inst)
        print(f"{name}: {st}")
        if st == "Optimal":
            nd = {d: int(v.value()) for d, v in n.items() if v.value() and v.value() > 0.5}
            pt = {t: int(v.value()) for t, v in P.items() if v.value() and v.value() > 0.5}
            print(f"   n_d = {nd}")
            print(f"   P_t = {pt}")

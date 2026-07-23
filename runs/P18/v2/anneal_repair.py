#!/usr/bin/env python3
"""Hybrid simulated annealing + exact CP-SAT large-neighborhood repair for the
parity-reduced 'phase-B' problem: cover Z/N with DISTINCT moduli from
pool(N) = {m | N : m >= 3, 2m+1 prime} (m = 2 excluded), any residues.

A phase-B covering is a necessary half of any Erdos #273 witness. Incomplete search:
only success (E = 0, exactly re-verified) is a result.

Loop: greedy init -> Metropolis annealing (move = reassign one modulus's residue,
biased toward covering uncovered points) -> on stall, free the moduli with least
unique coverage and exact-repair them with CP-SAT against the uncovered set.

Usage: python3 anneal_repair.py N seconds [seed]
"""
import sys, time
import numpy as np
from sympy import isprime, divisors
from ortools.sat.python import cp_model

def build(N):
    return sorted(m for m in divisors(N) if m >= 3 and isprime(2 * m + 1))

class State:
    def __init__(self, N, P, rng):
        self.N, self.P, self.rng = N, P, rng
        self.res = {}
        self.cov = np.zeros(N, dtype=np.int16)
        # min-waste greedy init (ascending m)
        for m in P:
            unc = np.nonzero(self.cov == 0)[0]
            if len(unc) == 0:
                cnt = np.zeros(m, dtype=np.int64)
            else:
                cnt = np.bincount(unc % m, minlength=m)
            a = int(cnt.argmax())
            self.res[m] = a
            self.cov[a::m] += 1
        self.E = int((self.cov == 0).sum())

    def move_delta(self, m, a_new):
        a_old = self.res[m]
        if a_new == a_old:
            return 0
        lost = int((self.cov[a_old::m] == 1).sum())
        sl = self.cov[a_new::m]
        gained = int((sl == 0).sum())
        return lost - gained

    def apply(self, m, a_new):
        a_old = self.res[m]
        self.cov[a_old::m] -= 1
        self.cov[a_new::m] += 1
        self.res[m] = a_new
        self.E = int((self.cov == 0).sum())

def exact_repair(st, k=18, tlim=120.0):
    """Free k moduli with least unique coverage; CP-SAT optimal reassignment."""
    N, P = st.N, st.P
    uniq = []
    for m in P:
        a = st.res[m]
        uniq.append((int((st.cov[a::m] == 1).sum()), m))
    uniq.sort()
    freed = [m for _, m in uniq[:k]]
    for m in freed:
        st.cov[st.res[m]::m] -= 1
    unc = np.nonzero(st.cov == 0)[0]
    md = cp_model.CpModel()
    sel = {}
    covers = {int(x): [] for x in unc}
    for m in freed:
        cands = sorted(set(int(x) % m for x in unc))
        lits = []
        for a in cands:
            v = md.NewBoolVar(f"s{m}_{a}")
            sel[(m, a)] = v
            lits.append(v)
        md.AddAtMostOne(lits)
        for x in covers:
            covers[x].append(sel[(m, x % m)])
    miss = []
    for x, ls in covers.items():
        u = md.NewBoolVar(f"u{x}")
        md.AddBoolOr(ls + [u])
        miss.append(u)
    md.Minimize(sum(miss))
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = tlim
    sol.parameters.num_workers = 8
    stt = sol.Solve(md)
    if sol.StatusName(stt) in ("FEASIBLE", "OPTIMAL"):
        chosen = {}
        for (m, a), v in sel.items():
            if sol.Value(v):
                chosen[m] = a
        for m in freed:
            a = chosen.get(m, st.rng.integers(m))  # unused freed moduli: random residue
            st.cov[int(a)::m] += 1
            st.res[m] = int(a)
    else:
        for m in freed:
            st.cov[st.res[m]::m] += 1
    st.E = int((st.cov == 0).sum())
    return st.E

def main():
    N = int(sys.argv[1])
    budget = float(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rng = np.random.default_rng(seed)
    P = build(N)
    print(f"N={N} |pool|={len(P)} mass={sum(1/m for m in P):.4f}", flush=True)
    st = State(N, P, rng)
    print(f"greedy init E={st.E} ({st.E/N:.5f})", flush=True)
    t0 = time.time()
    T, alpha = 4.0, 0.999992
    best = st.E
    it = last_improve = 0
    Parr = np.array(P)
    while time.time() - t0 < budget and st.E > 0:
        it += 1
        # 70% repair-targeted: pick an uncovered point, a modulus, set residue to cover it
        if rng.random() < 0.7 and st.E > 0:
            unc = np.nonzero(st.cov == 0)[0]
            x = int(unc[rng.integers(len(unc))])
            m = int(Parr[rng.integers(len(Parr))])
            a_new = x % m
        else:
            m = int(Parr[rng.integers(len(Parr))])
            a_new = int(rng.integers(m))
        d = st.move_delta(m, a_new)
        if d <= 0 or rng.random() < np.exp(-d / T):
            st.apply(m, a_new)
        T = max(T * alpha, 0.05)
        if st.E < best:
            best = st.E
            last_improve = it
            if it % 50 == 0 or best < 200:
                print(f"it={it} T={T:.3f} best={best} ({best/N:.5f}) {time.time()-t0:.0f}s", flush=True)
        if it - last_improve > 60000:
            e = exact_repair(st, k=28, tlim=150.0)
            print(f"[repair] it={it} E->{e} {time.time()-t0:.0f}s", flush=True)
            if e < best:
                best = e
            last_improve = it
            T = 4.0  # reheat
    print(f"final best={best} E={st.E} its={it} {time.time()-t0:.0f}s", flush=True)
    if st.E == 0:
        print("PHASE-B COVERING FOUND — exact verification:")
        cov = bytearray(N)
        for m, a in sorted(st.res.items()):
            for x in range(a, N, m):
                cov[x] = 1
        print("PASS" if all(cov) else "FAIL")
        for m in sorted(st.res):
            print(st.res[m], m)

if __name__ == "__main__":
    main()

"""V2 attack 7: SAT + CEGAR encoding (fundamentally different search dynamics).

Encoding: fix the hamiltonian cycle as C_n. Variables x_e for every candidate
chord e = (u,v), |u-v| mod n not in {1, n-1}. Constraints: every vertex has
exactly 2 chords (CardEnc equals). A model gives a 4-regular graph containing
C_n. CEGAR loop: exact HC enumeration (hc.c, printcyc mode) extracts a second
HC if one exists; since HC-presence is monotone in edges, the set S of chords
used by that second HC yields a sound blocking clause OR(not x_e, e in S). We
also add all 2n dihedral images of the clause (C_n's automorphisms). UNSAT =>
exhaustive proof that no witness with HC = C_n exists at this n (i.e. none at
all, since any witness can be normalized). SAT with no second HC => WITNESS.

Usage: python3 sat_cegar.py n [time_budget_s]
"""
import sys, time
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
import subprocess, os

HC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hc")

def second_hc(n, chords):
    """Return list of chord-edges used by some HC != C_n, or None if unique."""
    cyc = [(i, (i + 1) % n) for i in range(n)]
    edges = cyc + chords
    inp = f"{n} {len(edges)} -3\n" + "\n".join(f"{u} {v}" for u, v in edges)
    out = subprocess.run([HC], input=inp, capture_output=True, text=True).stdout
    cycset = {frozenset(e) for e in cyc}
    for line in out.splitlines():
        if not line.startswith("CYC"):
            continue
        seq = list(map(int, line.split()[1:]))
        es = [frozenset((seq[i], seq[(i + 1) % n])) for i in range(n)]
        used_chords = [e for e in es if e not in cycset]
        if used_chords:
            return [tuple(sorted(e)) for e in used_chords]
    return None

def main(n, budget, case=None):
    """case=(d1,d2): restrict to vertex 0 having chords of cycle-lengths d1 and d2
    (2 <= d1 <= d2 <= n//2). The <=C(n/2-1,2)+n/2-1 cases partition the search space
    (every 4-regular completion gives vertex 0 exactly two chords, whose lengths are
    some such pair), so per-n UNSAT for all cases = UNSAT overall. Enables parallel
    cube-and-conquer."""
    pool = IDPool()
    var = {}
    for u in range(n):
        for v in range(u + 2, n):
            if u == 0 and v == n - 1:
                continue
            var[(u, v)] = pool.id(("x", u, v))
    inv = {i: e for e, i in var.items()}
    cnf = []
    for w in range(n):
        lits = [var[e] for e in var if w in e]
        cnf.extend(CardEnc.equals(lits=lits, bound=2, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
    if case:
        d1, d2 = case
        def len_chords(d):
            out = [var[e] for e in ((0, d), (0, n - d)) if e in var]
            return list(set(out))
        if d1 == d2:
            for e in len_chords(d1):
                pass
            # both chords of vertex 0 have length d1: (0,d1) and (0,n-d1) both present
            if len(len_chords(d1)) < 2:
                print(f"UNSAT n={n} case={case} (trivially: not enough distinct chords)",
                      flush=True)
                return "unsat"
            for l in len_chords(d1):
                cnf.append([l])
        else:
            cnf.append(len_chords(d1))
            cnf.append(len_chords(d2))
    solver = Cadical153(bootstrap_with=cnf)
    t0 = time.time()
    it = 0
    def images(S):
        out = set()
        for r in range(n):
            for sgn in (1, -1):
                T = []
                for (u, v) in S:
                    a, b = (sgn * u + r) % n, (sgn * v + r) % n
                    a, b = min(a, b), max(a, b)
                    if (a, b) not in var:  # image hits a cycle edge slot: impossible for chords
                        break
                    T.append((a, b))
                else:
                    out.add(frozenset(T))
        return out
    while time.time() - t0 < budget:
        if not solver.solve():
            print(f"UNSAT n={n} case={case} after {it} refinements, t={time.time()-t0:.0f}s",
                  flush=True)
            return "unsat"
        model = set(l for l in solver.get_model() if l > 0)
        chords = [e for e, i in var.items() if i in model]
        S = second_hc(n, chords)
        it += 1
        if S is not None:
            # greedy minimization: a smaller chord set that still forces a 2nd HC
            # gives an exponentially stronger blocking clause (bans all supersets)
            changed = True
            while changed:
                changed = False
                for e in list(S):
                    S2 = second_hc(n, [c for c in S if c != e])
                    if S2 is not None:
                        S = S2
                        changed = True
                        break
        if S is None:
            with open("WITNESS.txt", "a") as f:
                f.write(f"SAT-CEGAR WITNESS n={n} chords={sorted(chords)}\n")
            print(f"WITNESS n={n} chords={sorted(chords)}", flush=True)
            return "witness"
        for T in images(S):
            solver.add_clause([-var[e] for e in T])
        if it % 200 == 0:
            print(f"n={n} it={it} t={time.time()-t0:.0f}s last_clause_len={len(S)}",
                  flush=True)
    print(f"TIMEOUT n={n} after {it} refinements", flush=True)
    return "timeout"

if __name__ == "__main__":
    n_ = int(sys.argv[1])
    b_ = float(sys.argv[2]) if len(sys.argv) > 2 else 3600
    if len(sys.argv) > 4:
        main(n_, b_, case=(int(sys.argv[3]), int(sys.argv[4])))
    else:
        main(n_, b_)

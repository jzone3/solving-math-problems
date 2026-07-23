"""V2 attack 8: Fleischner-primitive search (structure-guided reduction).

Reduction: if H is a simple graph with deg(s) = deg(t) = 3, all other degrees 4,
and H has EXACTLY ONE hamiltonian s-t path, then a ring of m >= 3 copies of H
(joining t_i to s_{i+1} by an edge) is a simple 4-regular graph. Every HC of the
ring must use all 2m junction edges (each gadget has exactly two edges leaving
it, and an HC must enter and leave every gadget), hence traverses each copy as a
hamiltonian s-t path; therefore #HC(ring) = (#ham s-t paths of H)^... = 1 iff
unique per copy. A unique-path gadget at ANY order n gives a Sheehan
counterexample on 3n vertices. This is exactly the primitive behind Fleischner's
J. Graph Theory 75 (2014) Lemma 1 constructions (his gadgets have extra deg-3
vertices; the open question is whether an all-deg-4-internal one exists).

Encoding: WLOG the unique ham path is 0-1-...-n-1 (relabel), s=0, t=n-1.
Vars x_e over non-path pairs; every vertex needs exactly 2 chords (s,t: 1 path
edge + 2 chords = deg 3; interior: 2 + 2 = deg 4). CEGAR oracle: # ham s-t paths
via hc.c on the augmented graph G + apex adjacent to {s,t} (HCs of augmented
graph <-> ham s-t paths). Second path -> minimized blocking clause on its chord
set + its reflection image (i -> n-1-i). UNSAT => no such gadget of order n.

Usage: python3 sat_path.py n [budget_s]
"""
import sys, time, os, subprocess
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

HC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hc")

def second_path(n, chords):
    """Chords of some ham 0-(n-1) path != the spine, or None if unique."""
    spine = [(i, i + 1) for i in range(n - 1)]
    edges = spine + chords + [(n, 0), (n, n - 1)]
    inp = f"{n+1} {len(edges)} -3\n" + "\n".join(f"{u} {v}" for u, v in edges)
    out = subprocess.run([HC], input=inp, capture_output=True, text=True).stdout
    spineset = {frozenset(e) for e in spine}
    for line in out.splitlines():
        if not line.startswith("CYC"):
            continue
        seq = list(map(int, line.split()[1:]))
        k = seq.index(n)  # apex; the s-t path is the cyclic order with apex removed
        seq = seq[k + 1:] + seq[:k]
        es = [frozenset((seq[i], seq[i + 1])) for i in range(len(seq) - 1)]
        used = [tuple(sorted(e)) for e in es if e not in spineset]
        assert all(e in chords for e in used), (used, chords)
        if used:
            return used
    return None

def main(n, budget):
    pool = IDPool()
    var = {}
    for u in range(n):
        for v in range(u + 2, n):
            var[(u, v)] = pool.id(("x", u, v))
    cnf = []
    for w in range(n):
        lits = [var[e] for e in var if w in e]
        cnf.extend(CardEnc.equals(lits=lits, bound=2, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
    solver = Cadical153(bootstrap_with=cnf)
    t0 = time.time()
    it = 0
    while time.time() - t0 < budget:
        if not solver.solve():
            print(f"UNSAT n={n} after {it} refinements, t={time.time()-t0:.0f}s "
                  f"-- no unique-ham-path gadget (deg-3 endpoints, deg-4 interior) on {n} vertices",
                  flush=True)
            return "unsat"
        model = set(l for l in solver.get_model() if l > 0)
        chords = [e for e, i in var.items() if i in model]
        S = second_path(n, chords)
        it += 1
        if S is not None:
            changed = True
            while changed:
                changed = False
                for e in list(S):
                    S2 = second_path(n, [c for c in S if c != e])
                    if S2 is not None:
                        S = S2; changed = True; break
        if S is None:
            with open("WITNESS.txt", "a") as f:
                f.write(f"GADGET-PATH WITNESS n={n} chords={sorted(chords)} "
                        f"(ring of >=3 copies is a Sheehan counterexample on 3n vertices)\n")
            print(f"WITNESS n={n} chords={sorted(chords)}", flush=True)
            return "witness"
        for T in ({tuple(sorted(e)) for e in S},
                  {tuple(sorted((n-1-u, n-1-v))) for u, v in S}):
            solver.add_clause([-var[e] for e in T])
        if it % 500 == 0:
            print(f"n={n} it={it} t={time.time()-t0:.0f}s", flush=True)
    print(f"TIMEOUT n={n} after {it} refinements", flush=True)
    return "timeout"

if __name__ == "__main__":
    main(int(sys.argv[1]), float(sys.argv[2]) if len(sys.argv) > 2 else 86400)

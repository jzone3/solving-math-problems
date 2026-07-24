"""Constructive CEGAR search for the smallest non-k-colorable subgraph of a fixed
geometric universe U (P23, scope: constructive SAT over a fixed universe).

Problem solved:  min |S|  over  S subset of U  with  chi(U[S]) >= k+1
  k=3 -> smallest 4-chromatic UDG in U   (REQUIRED sanity: Moser spindle, 7 vertices)
  k=4 -> smallest 5-chromatic UDG in U   (P23 goal: beat 509)

Method (counterexample-guided abstraction refinement, QBF-free):
  Selection variables s_v (v in U). Outer SAT with a cardinality bound |S| <= N
  (pysat ITotalizer, incremental) + a growing set C of k-colorings of U used as
  BLOCKING constraints: for each coloring c in C, S must contain an edge that is
  monochromatic under c (necessary condition for S to be non-k-colorable).
    - outer UNSAT  => no non-k-colorable S with |S| <= N exists  (LOWER BOUND).
    - outer SAT    => candidate S; verify with a plain k-coloring SAT call:
         * S non-k-colorable  => WITNESS (tighten N to |S|-1 and continue for the min).
         * S k-colorable      => extend its proper coloring greedily to all of U,
                                 add it to C as a new blocking clause (refine), retry.
  Symmetry breaking: lex-leader over the D6 automorphisms of U (rotations/reflections),
  sound because every such map is a graph automorphism (preserves unit distances).

Inner/outer solving uses pysat (fast, many small calls). Any claimed WITNESS is then
re-checked independently with exact arithmetic + kissat + drat-trim by verify_sms.py.
"""
import sys, os, pickle, time
from pysat.solvers import Cadical195
from pysat.card import ITotalizer


def load(path):
    with open(path, "rb") as f:
        d = pickle.load(f)
    n = len(d["points"])
    adj = [[] for _ in range(n)]
    for (u, v) in d["edges"]:
        adj[u].append(v)
        adj[v].append(u)
    d["n"] = n
    d["adj"] = adj
    return d


# ---------- inner: is the induced subgraph on `sel` k-colorable? ----------
def kcolor_subgraph(sel, adj, k):
    """Return (True, coloring) if U[sel] is k-colorable else (False, None).
    coloring: dict v-> color in 0..k-1 (only for v in sel)."""
    sel_set = set(sel)
    idx = {v: i for i, v in enumerate(sel)}
    m = len(sel)
    cnf = []
    var = lambda i, c: i * k + c + 1
    for i in range(m):
        cnf.append([var(i, c) for c in range(k)])
    for v in sel:
        for w in adj[v]:
            if w in sel_set and v < w:
                iu, iw = idx[v], idx[w]
                for c in range(k):
                    cnf.append([-var(iu, c), -var(iw, c)])
    s = Cadical195()
    for cl in cnf:
        s.add_clause(cl)
    ok = s.solve()
    coloring = None
    if ok:
        model = set(l for l in s.get_model() if l > 0)
        coloring = {}
        for v in sel:
            i = idx[v]
            for c in range(k):
                if var(i, c) in model:
                    coloring[v] = c
                    break
    s.delete()
    return ok, coloring


def greedy_extend(coloring, n, adj, k):
    """Extend a proper coloring of a subset to all of U, greedily minimizing
    monochromatic edges (proper where possible). Returns full coloring list."""
    full = [coloring.get(v, -1) for v in range(n)]
    order = sorted(range(n), key=lambda v: (full[v] != -1, -len(adj[v])))
    for v in order:
        if full[v] != -1:
            continue
        cnt = [0] * k
        for w in adj[v]:
            if full[w] != -1:
                cnt[full[w]] += 1
        full[v] = min(range(k), key=lambda c: cnt[c])
    return full


def mono_edges(full, edges):
    return [(u, v) for (u, v) in edges if full[u] == full[v]]


class Outer:
    """Persistent outer SAT instance: s vars 1..n, ITotalizer cardinality, block
    clauses, lex-leader symmetry breaking."""

    def __init__(self, univ, ub):
        self.n = univ["n"]
        self.edges = univ["edges"]
        self.s = Cadical195()
        self.svar = [v + 1 for v in range(self.n)]  # s_v = v+1
        self.top = self.n
        self.itot = ITotalizer(lits=self.svar, ubound=ub, top_id=self.top)
        for cl in self.itot.cnf.clauses:
            self.s.add_clause(cl)
        self.top = self.itot.top_id
        self._add_symmetry(univ.get("perms", []))
        self.ncolorings = 0

    def _newvar(self):
        self.top += 1
        return self.top

    def _add_symmetry(self, perms):
        # lex-leader: s <=_lex perm(s) for each non-identity automorphism
        nsb = 0
        for perm in perms:
            if perm == list(range(self.n)):
                continue
            # a_i = s_i, b_i = s_{perm[i]}; enforce a <=_lex b
            eq_prev = None  # var meaning prefix [0..i-1] equal; None = True
            for i in range(self.n):
                a = self.svar[i]
                b = self.svar[perm[i]]
                # (eq_prev & a) -> b
                if eq_prev is None:
                    self.s.add_clause([-a, b])
                else:
                    self.s.add_clause([-eq_prev, -a, b])
                # eq_i <-> eq_prev & (a==b); build eq_i
                eqab = self._newvar()  # a==b
                # eqab <-> (a==b): (a=b) true when both same
                self.s.add_clause([-eqab, -a, b])
                self.s.add_clause([-eqab, a, -b])
                self.s.add_clause([eqab, a, b])
                self.s.add_clause([eqab, -a, -b])
                if eq_prev is None:
                    eq_i = eqab
                else:
                    eq_i = self._newvar()
                    self.s.add_clause([-eq_i, eq_prev])
                    self.s.add_clause([-eq_i, eqab])
                    self.s.add_clause([eq_i, -eq_prev, -eqab])
                eq_prev = eq_i
                nsb += 1
        self.nsb = nsb

    def add_coloring(self, full):
        me = mono_edges(full, self.edges)
        if not me:
            self.s.add_clause([])  # universe is k-colorable -> UNSAT
            self.ncolorings += 1
            return 0
        bvars = []
        for (u, v) in me:
            b = self._newvar()
            self.s.add_clause([-b, self.svar[u]])
            self.s.add_clause([-b, self.svar[v]])
            bvars.append(b)
        self.s.add_clause(bvars)
        self.ncolorings += 1
        return len(me)

    def solve(self, N):
        # enforce sum s <= N via assumption ~rhs[N]  (rhs[N] == sum>=N+1)
        assumps = []
        if N < len(self.itot.rhs):
            assumps = [-self.itot.rhs[N]]
        ok = self.s.solve(assumptions=assumps)
        if not ok:
            return None
        model = set(l for l in self.s.get_model() if l > 0)
        return [v for v in range(self.n) if self.svar[v] in model]


def search(univ, k, Nstart, max_iter=100000, log=print):
    adj = univ["adj"]
    edges = univ["edges"]
    n = univ["n"]
    outer = Outer(univ, ub=Nstart)
    log(f"[cegar] n={n} edges={len(edges)} k={k} (find chi>={k+1}) "
        f"Nstart={Nstart} sym-clauses={outer.nsb}")
    N = Nstart
    best = None
    t0 = time.time()
    it = 0
    while it < max_iter:
        it += 1
        cand = outer.solve(N)
        if cand is None:
            log(f"[cegar] iter {it}: outer UNSAT at N={N} "
                f"({outer.ncolorings} colorings, {time.time()-t0:.1f}s) "
                f"=> no non-{k}-colorable S with |S|<={N}")
            break
        colorable, coloring = kcolor_subgraph(cand, adj, k)
        if not colorable:
            best = list(cand)
            log(f"[cegar] iter {it}: WITNESS |S|={len(cand)} is non-{k}-colorable "
                f"(chi>={k+1}); tightening to N={len(cand)-1} "
                f"[{outer.ncolorings} colorings, {time.time()-t0:.1f}s]")
            N = len(cand) - 1
            if N < 1:
                break
        else:
            full = greedy_extend(coloring, n, adj, k)
            nme = outer.add_coloring(full)
            if it % 25 == 0 or nme == 0:
                log(f"[cegar] iter {it}: cand |S|={len(cand)} {k}-colorable; "
                    f"+coloring ({nme} mono edges), N={N}, "
                    f"colorings={outer.ncolorings}, {time.time()-t0:.1f}s")
    return best


def main():
    ap = sys.argv
    if len(ap) < 2:
        print("usage: cegar.py <universe.pkl> [k=3] [Nstart=12] [out.pkl]")
        return
    path = ap[1]
    k = int(ap[2]) if len(ap) > 2 else 3
    Nstart = int(ap[3]) if len(ap) > 3 else 12
    out = ap[4] if len(ap) > 4 else None
    univ = load(path)
    best = search(univ, k, Nstart)
    if best is None:
        print(f"[cegar] RESULT: no non-{k}-colorable subset with |S|<=Nstart found "
              f"(lower bound established up to that N).")
    else:
        print(f"[cegar] RESULT: smallest non-{k}-colorable subset found has "
              f"|S|={len(best)} vertices: {sorted(best)}")
        if out:
            with open(out, "wb") as f:
                pickle.dump({"witness": sorted(best), "k": k,
                             "universe": path}, f)
            print(f"[cegar] wrote witness -> {out}")


if __name__ == "__main__":
    main()

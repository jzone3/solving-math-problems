#!/usr/bin/env python3
"""Generate DIMACS CNF encodings of "G127 -/-> (3,3)^e" (SAT <=> good 2-coloring
exists; UNSAT <=> G127 arrows (3,3)^e, giving Fe(3,3;4) <= 127).

Variables: one per edge (True = red, False = blue), edges sorted with edges
incident to vertex 0 first (lex prefix used by symmetry breaking).
Base clauses: for each triangle {x,y,z}: (x|y|z) & (~x|~y|~z).

Symmetry breaking (sound, coloring-side only):
The formula is invariant under (a) edge permutations induced by graph
automorphisms x -> a*x + b (a cubic residue) -- these permute triangles -- and
(b) the global color flip. For any subgroup/subset S of that invariance group,
adding lex-leader constraints "X <=_lex sigma(X)" for sigma in S is sound
(Crawford et al. 1996): every satisfying coloring has a lex-minimal image
under the full group, which satisfies all constraints; hence satisfiability
is preserved, and UNSAT of the augmented formula implies UNSAT of the base.

Outputs:
  plain.cnf : base + single unit clause var(e0)=red (justified by color flip)
  sb.cnf    : base + lex-leader for {sigma, sigma*flip : sigma in Stab(0)}
              (Stab(0) = 42 multiplications by cubic residues; 84 sequences)
              with lex prefix = the 42 star edges of vertex 0 + next 58 edges.
"""
import sys, os

p = 127
C = sorted({pow(x, 3, p) for x in range(1, p)})
adj = [set() for _ in range(p)]
for u in range(p):
    for c in C:
        adj[u].add((u + c) % p)

edges_star = sorted((0, c) for c in C)
edges_rest = sorted((u, v) for u in range(1, p) for v in adj[u] if u < v)
edges = edges_star + edges_rest
var = {e: i + 1 for i, e in enumerate(edges)}
nv = len(edges)
assert nv == 2667

tris = []
for (u, v) in edges:
    for w in sorted(adj[u] & adj[v]):
        if w > v:
            tris.append((u, v, w))
assert len(tris) == 9779

base = []
for (u, v, w) in tris:
    a, b, c = var[(u, v)], var[(u, w)], var[(v, w)]
    base.append((a, b, c))
    base.append((-a, -b, -c))


def ev(e):
    u, v = e
    return var[(u, v) if u < v else (v, u)]


def perm_of(a, b):
    """edge image under x -> a*x + b"""
    def f(e):
        u, v = e
        return ev(((a * u + b) % p, (a * v + b) % p))
    return f


def lex_clauses(seq_pairs, next_var):
    """X <=_lex Y over pairs (x_i, y_i) of literals; returns clauses, next_var.
    y chain: y0 = T; (~y_i | ~x_i | y_i'... ) standard encoding."""
    cls = []
    yprev = None
    for i, (x, y) in enumerate(seq_pairs):
        if yprev is None:
            cls.append((-x, y))          # x <= y at position 0
            if i == len(seq_pairs) - 1:
                break
            ynew = next_var; next_var += 1
            # ynew -> (x == y)
            cls.append((-ynew, -x, y))
            cls.append((-ynew, x, -y))
            # (x == y) -> ynew
            cls.append((ynew, -x, -y))
            cls.append((ynew, x, y))
        else:
            cls.append((-yprev, -x, y))
            if i == len(seq_pairs) - 1:
                break
            ynew = next_var; next_var += 1
            cls.append((-ynew, yprev))
            cls.append((-ynew, -x, y))
            cls.append((-ynew, x, -y))
            cls.append((ynew, -yprev, -x, -y))
            cls.append((ynew, -yprev, x, y))
        yprev = ynew
    return cls, next_var


def write_cnf(path, nvars, clauses):
    with open(path, "w") as f:
        f.write(f"p cnf {nvars} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")


out = os.path.dirname(os.path.abspath(__file__))

# triangle list as 0-based edge indices (for anneal.c), same edge order
with open(os.path.join(out, "g127.tri_edges"), "w") as f:
    for (u, v, w) in tris:
        f.write(f"{var[(u,v)]-1} {var[(u,w)]-1} {var[(v,w)]-1}\n")

# plain: fix edge (0,1) red (var of (0,1))
plain = list(base) + [(var[(0, 1)],)]
write_cnf(os.path.join(out, "plain.cnf"), nv, plain)

# sb: lex-leader over Stab(0) x {id, flip}, prefix length 100
PREFIX = 100
prefix_vars = [var[e] for e in edges[:PREFIX]]
sb = list(base)
next_var = nv + 1
for a in C:
    f = perm_of(a, 0)
    for flip in (False, True):
        if a == 1 and not flip:
            continue  # identity: trivial
        pairs = []
        for e in edges[:PREFIX]:
            x = var[e]
            y = f(e)
            pairs.append((x, -y if flip else y))
        cls, next_var = lex_clauses(pairs, next_var)
        sb.extend(cls)
write_cnf(os.path.join(out, "sb.cnf"), next_var - 1, sb)
print(f"plain.cnf: {nv} vars, {len(plain)} clauses")
print(f"sb.cnf: {next_var-1} vars, {len(sb)} clauses")

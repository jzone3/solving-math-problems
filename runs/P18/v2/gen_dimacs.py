#!/usr/bin/env python3
"""Emit the sat_cover.py CNF as DIMACS (for kissat + DRAT proof logging).

Identical encoding to sat_cover.py (same variable numbering: y[m][a] first,
then sequential-counter AMO auxiliaries). Also writes a .map file listing
"var m a" so a SAT model can be decoded and re-verified.

Usage: python3 gen_dimacs.py L out.cnf out.map
"""
import sys
from sat_cover import build, pool_for

def main():
    L = int(sys.argv[1])
    out, mp = sys.argv[2], sys.argv[3]
    P, var, clauses, nv = build(L, symbreak=True)
    top = max((abs(l) for cl in clauses for l in cl), default=nv)
    with open(out, "w") as f:
        f.write(f"p cnf {top} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
    with open(mp, "w") as f:
        for (m, a), v in sorted(var.items(), key=lambda kv: kv[1]):
            f.write(f"{v} {m} {a}\n")
    print(f"L={L} vars={top} clauses={len(clauses)} -> {out}")

if __name__ == "__main__":
    main()

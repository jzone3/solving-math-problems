#!/usr/bin/env python3
"""Composition-closure audit of the CWM database.

Existence-level closure ops over cells (n, k), seeded by DB statuses Yes/All:
  1. padding:  CW(m, k) and m | n  =>  CW(n, k)         [f(x) -> f(x^{n/m})]
  2. Kronecker: CW(n1,k1), CW(n2,k2), gcd(n1,n2)=1 => CW(n1n2, k1k2)
Both are classical and witness-effective (explicit witness derivable when the
seed sets are in the DB).

We compute the closure restricted to the DB's parameter domain and diff against
DB statuses: any DB 'Open' cell in the closure is a resolvable/mislabeled cell;
any DB 'No' cell in the closure would signal a contradiction (bug in DB or in
our ops).
"""
from math import gcd
from extract_table import load, table

d = table(load())
domain = set(d.keys())
yes = {c for c, v in d.items() if v["status"] in ("Yes", "All")}
no = {c for c, v in d.items() if v["status"] == "No"}
opn = {c for c, v in d.items() if v["status"] == "Open"}
print(f"domain {len(domain)}  yes {len(yes)}  no {len(no)}  open {len(opn)}")

closure = set(yes)
derived_by = {}
changed = True
rounds = 0
while changed:
    changed = False
    rounds += 1
    cur = list(closure)
    # padding
    for (m, k) in cur:
        for (n, k2) in domain:
            if k2 == k and n != m and n % m == 0 and (n, k) not in closure:
                closure.add((n, k))
                derived_by[(n, k)] = ("pad", (m, k))
                changed = True
    # kronecker
    for i, (n1, k1) in enumerate(cur):
        for (n2, k2) in cur:
            if n1 <= n2 and gcd(n1, n2) == 1:
                c = (n1 * n2, k1 * k2)
                if c in domain and c not in closure:
                    closure.add(c)
                    derived_by[c] = ("kron", (n1, k1), (n2, k2))
                    changed = True
print(f"closure size {len(closure)} after {rounds} rounds")

bad_no = sorted(closure & no)
new_yes = sorted(closure & opn)
print("\n'No' cells reachable by closure (CONTRADICTIONS):", bad_no)
print(f"\n'Open' cells reachable by closure ({len(new_yes)}):")
for c in new_yes:
    print(" ", c, derived_by.get(c))

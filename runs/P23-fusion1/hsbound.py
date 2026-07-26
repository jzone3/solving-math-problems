"""Report the current lower bound: the minimum hitting set of the banked clauses.

Any completion of the shared core must hit every banked clause, so this is a
valid lower bound on the size of any completion drawn from the candidate set --
and if it ever exceeds 42 there is no 508 in that set.
"""
import json
import pickle
import sys

import numpy as np
from scipy.optimize import LinearConstraint, milp

BANK = sys.argv[1] if len(sys.argv) > 1 else 'hsbank_union.jsonl'
clauses = [json.loads(l) for l in open(BANK) if l.strip() and l.strip() != '[]']
clauses = [c for c in {frozenset(c) for c in clauses}]
vs = sorted({v for c in clauses for v in c})
idx = {v: i for i, v in enumerate(vs)}
A = np.zeros((len(clauses), len(vs)))
for r, c in enumerate(clauses):
    for v in c:
        A[r, idx[v]] = 1.0
res = milp(c=np.ones(len(vs)), constraints=[LinearConstraint(A, lb=1,
                                                             ub=np.inf)],
           integrality=np.ones(len(vs)), bounds=(0, 1))
print(f'{BANK}: {len(clauses)} distinct clauses over {len(vs)} candidates, '
      f'minimum hitting set = {int(round(res.fun))}')

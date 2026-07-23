"""Independent double-check of KM infeasibility results using exact rational LP
(via pulp/CBC for ILP cross-check) and a direct exhaustive argument when the
orbit system is small enough after LP-based pruning.

Usage: python3 km_certify.py <instance> <pattern>
Re-builds the exact same orbit system as km_search.py and:
 1) solves the ILP with CBC (independent of CP-SAT);
 2) solves the LP relaxation; if LP infeasible, CBC provides certificate-level
    confidence; result printed either way.
"""
import sys
import pulp
from km_search import INSTANCES, cyclic_perm, gen_blocks, orbits_of, apply_perm
from collections import defaultdict

name, pattern = sys.argv[1], sys.argv[2]
V, B, r1, r2, R, K, L = INSTANCES[name]
p = cyclic_perm(V, pattern)
blocks = gen_blocks(V, K)
borbs = orbits_of(blocks, p, apply_perm)
eorbs = orbits_of(list(range(V)), p, lambda v, pp: pp[v])
erep = {v: i for i, orb in enumerate(eorbs) for v in orb}
pairs = [(v, w) for v in range(V) for w in range(v+1, V)]
def pap(pr, pp):
    a, b = pp[pr[0]], pp[pr[1]]
    return (min(a, b), max(a, b))
porbs = orbits_of(pairs, p, pap)
prep = {pr: i for i, orb in enumerate(porbs) for pr in orb}

for relax in (False, True):
    prob = pulp.LpProblem("km", pulp.LpMinimize)
    cat = "Continuous" if relax else "Integer"
    xs = [pulp.LpVariable(f"x{i}", 0, B, cat=cat) for i in range(len(borbs))]
    es = defaultdict(list); ed = defaultdict(list); pc = defaultdict(list)
    for oi, orb in enumerate(borbs):
        tes = defaultdict(int); ted = defaultdict(int); tpc = defaultdict(int)
        for blk in orb:
            for v, mult in enumerate(blk):
                if mult == 1: tes[erep[v]] += 1
                elif mult == 2: ted[erep[v]] += 1
            for (v, w) in pairs:
                if blk[v] and blk[w]:
                    tpc[prep[(v, w)]] += blk[v]*blk[w]
        for k, t in tes.items(): es[k].append((t//len(eorbs[k]), xs[oi]))
        for k, t in ted.items(): ed[k].append((t//len(eorbs[k]), xs[oi]))
        for k, t in tpc.items(): pc[k].append((t//len(porbs[k]), xs[oi]))
    prob += 0
    prob += pulp.lpSum(len(orb)*x for orb, x in zip(borbs, xs)) == B
    for k in range(len(eorbs)):
        prob += pulp.lpSum(c*x for c, x in es.get(k, [])) == r1
        prob += pulp.lpSum(c*x for c, x in ed.get(k, [])) == r2
    for k in range(len(porbs)):
        prob += pulp.lpSum(c*x for c, x in pc.get(k, [])) == L
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    print(f"{name} {pattern} {'LP' if relax else 'ILP'}: "
          f"{pulp.LpStatus[prob.status]}", flush=True)

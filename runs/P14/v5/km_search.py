"""Kramer–Mesner prescribed-automorphism search for the 4 open BTD instances.

Assume a permutation group G = <sigma> acts on the V elements and permutes the
blocks of the design. Then the design is a union of block orbits, and all
constraints collapse to one per orbit of elements / pairs:
  - sum over chosen block-orbits of (#blocks) = B
  - per element-orbit: single-count = r1, double-count = r2 (constant on orbit)
  - per pair-orbit: coverage sum m_v m_w = Lambda (constant on orbit)
Repeated blocks are allowed (BTDs need not be simple): orbit multiplicities
x_o are nonnegative integers.

A solution gives an explicit design (verified by verify_witness.py) => SOLVED.
Infeasibility only rules out designs admitting that automorphism (not global).
"""
import sys, itertools
from collections import defaultdict
from ortools.sat.python import cp_model

INSTANCES = {
    "I1": (14, 18, 7, 1, 9, 7, 4),
    "I2": (12, 15, 6, 2, 10, 8, 6),
    "I3": (12, 20, 4, 3, 10, 6, 4),
    "I4": (14, 28, 8, 3, 14, 7, 6),
    # known-existing sanity tests
    "T1": (4, 8, 2, 3, 8, 4, 6),
    "T2": (8, 20, 8, 1, 10, 4, 4),
}

def cyclic_perm(V, pattern):
    """pattern examples: 'Z7x2' two 7-cycles on 14; 'Z2' product of 2-cycles on all;
    'Z3' product of 3-cycles; 'Z14' single cycle; 'Z12'; 'Z4'; 'Z6'."""
    if pattern == "Z14": return [ (i+1) % 14 for i in range(14) ]
    if pattern == "Z12": return [ (i+1) % 12 for i in range(12) ]
    if pattern == "Z7x2":
        p = list(range(14))
        for s in (0, 7):
            for i in range(7): p[s+i] = s + (i+1) % 7
        return p
    if pattern.startswith("Zk"):  # Zk on V: k-cycles
        pass
    k = int(pattern[1:])
    p = list(range(V))
    for s in range(0, V - V % k, k):
        for i in range(k): p[s+i] = s + (i+1) % k
    return p

def gen_blocks(V, K):
    blocks = []
    for ddd in range(0, K//2 + 1):
        for doubles in itertools.combinations(range(V), ddd):
            rest = [v for v in range(V) if v not in doubles]
            for singles in itertools.combinations(rest, K - 2*ddd):
                m = [0]*V
                for v in doubles: m[v] = 2
                for v in singles: m[v] = 1
                blocks.append(tuple(m))
    return blocks

def apply_perm(block, p):
    m = [0]*len(block)
    for v, mult in enumerate(block):
        m[p[v]] = mult
    return tuple(m)

def orbits_of(items, p, apply_fn):
    seen = {}
    orbs = []
    for it in items:
        if it in seen: continue
        orb = [it]
        seen[it] = True
        cur = apply_fn(it, p)
        while cur != it:
            orb.append(cur); seen[cur] = True
            cur = apply_fn(cur, p)
        orbs.append(orb)
    return orbs

def km(name, pattern, tl=1800, workers=8):
    V, B, r1, r2, R, K, L = INSTANCES[name]
    p = cyclic_perm(V, pattern)
    blocks = gen_blocks(V, K)
    borbs = orbits_of(blocks, p, apply_perm)
    # element orbits
    eorbs = orbits_of(list(range(V)), p, lambda v, pp: pp[v])
    erep = {v: i for i, orb in enumerate(eorbs) for v in orb}
    # pair orbits
    pairs = [(v, w) for v in range(V) for w in range(v+1, V)]
    def pap(pr, pp):
        a, b = pp[pr[0]], pp[pr[1]]
        return (min(a, b), max(a, b))
    porbs = orbits_of(pairs, p, pap)
    prep = {pr: i for i, orb in enumerate(porbs) for pr in orb}
    # per block-orbit contributions
    m_ = cp_model.CpModel()
    xs = []
    size = []
    elem_single = defaultdict(list)  # eorb -> (coef, var)
    elem_double = defaultdict(list)
    pair_cov = defaultdict(list)
    for oi, orb in enumerate(borbs):
        x = m_.NewIntVar(0, B, f"x{oi}")
        xs.append(x); size.append(len(orb))
        # contributions per representative element/pair orbit: compute totals
        es = defaultdict(int); ed = defaultdict(int); pc = defaultdict(int)
        for blk in orb:
            for v, mult in enumerate(blk):
                if mult == 1: es[erep[v]] += 1
                elif mult == 2: ed[erep[v]] += 1
            for (v, w) in pairs:
                if blk[v] and blk[w]:
                    pc[prep[(v, w)]] += blk[v]*blk[w]
        # per-orbit constants: divide by orbit length of that element/pair orbit
        for k, tot in es.items():
            assert tot % len(eorbs[k]) == 0
            elem_single[k].append((tot // len(eorbs[k]), x))
        for k, tot in ed.items():
            assert tot % len(eorbs[k]) == 0
            elem_double[k].append((tot // len(eorbs[k]), x))
        for k, tot in pc.items():
            assert tot % len(porbs[k]) == 0
            pair_cov[k].append((tot // len(porbs[k]), x))
    m_.Add(sum(s*x for s, x in zip(size, xs)) == B)
    for k in range(len(eorbs)):
        m_.Add(sum(c*x for c, x in elem_single.get(k, [])) == r1)
        m_.Add(sum(c*x for c, x in elem_double.get(k, [])) == r2)
    for k in range(len(porbs)):
        m_.Add(sum(c*x for c, x in pair_cov.get(k, [])) == L)
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = tl
    sol.parameters.num_search_workers = workers
    st = sol.Solve(m_)
    stname = sol.StatusName(st)
    print(f"{name} {pattern}: {stname} wall={sol.WallTime():.1f}s #orbits={len(borbs)}",
          flush=True)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = []
        for oi, orb in enumerate(borbs):
            for _ in range(sol.Value(xs[oi])):
                chosen.extend(orb)
        mat = [[0]*len(chosen) for _ in range(V)]
        for b, blk in enumerate(chosen):
            for v in range(V): mat[v][b] = blk[v]
        fn = f"witness_{name}_{pattern}.txt"
        with open(fn, "w") as f:
            f.write(f"{V} {len(chosen)} {r1} {r2} {R} {K} {L}\n")
            for v in range(V):
                f.write("".join(map(str, mat[v])) + "\n")
        print(f"  witness written to {fn}")
        return True
    return False

if __name__ == "__main__":
    name, pattern = sys.argv[1], sys.argv[2]
    tl = float(sys.argv[3]) if len(sys.argv) > 3 else 1800
    km(name, pattern, tl)

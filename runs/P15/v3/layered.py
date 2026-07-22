#!/usr/bin/env python3
"""P15 V3 layered incremental SAT: build covering system prime-power layer by layer.

State after layer k: modulus N_k = prod of first k prime powers, hole set H_k subset Z_{N_k}
of uncovered residues. At each layer, MaxSAT chooses residues for unused divisors of N_k
(all >= m) to cover as many holes as possible; leftover holes lift to the next layer.
Coverage clauses only range over holes, so N_k can grow far beyond direct-SAT range.
Distinct moduli enforced globally (each modulus value used at most once over all layers).
"""
import argparse, json, sys, time
from pysat.formula import WCNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.examples.rc2 import RC2
from pysat.solvers import Cadical153, Glucose4


def divisors(N):
    ds = []
    i = 1
    while i * i <= N:
        if N % i == 0:
            ds.append(i)
            if i != N // i:
                ds.append(N // i)
        i += 1
    return sorted(ds)


def layer_solve(holes, mods, per_layer_budget=120):
    """Choose one residue per modulus (optional), minimizing # holes left
    (unweighted MaxSAT), then greedily prune redundant classes preferring to
    give back the smallest (scarcest) moduli.
    Variables only for (n, a) with a = h mod n for some hole h."""
    pool = IDPool()
    wcnf = WCNF()
    var = {}          # (n, a) -> lit
    hits = {h: [] for h in holes}
    for n in mods:
        byres = {}
        for h in holes:
            byres.setdefault(h % n, []).append(h)
        lits = []
        for a, hs in byres.items():
            v = pool.id(("x", n, a))
            var[(n, a)] = v
            lits.append(v)
            for h in hs:
                hits[h].append(v)
        if len(lits) > 1:
            amo = CardEnc.atmost(lits=lits, bound=1, vpool=pool, encoding=EncType.ladder)
            for cl in amo.clauses:
                wcnf.append(cl)
    covvars = []
    for h in holes:
        cv = pool.id(("cov", h))
        covvars.append(cv)
        # cov_h -> OR(hits) suffices for maximization
        wcnf.append([-cv] + hits[h])
        wcnf.append([cv], weight=1)
    t0 = time.time()
    # anytime linear search: at-most-k holes uncovered, decreasing k.
    # NOTE: wall-clock timers don't work (C solve holds the GIL), so we use
    # per-call conflict budgets and check the deadline between calls.
    s = Glucose4(bootstrap_with=wcnf.hard)
    best_model, cost = None, len(holes)
    from pysat.card import ITotalizer
    it = ITotalizer(lits=[-v for v in covvars], ubound=len(holes), top_id=pool.top + 1)
    for cl in it.cnf.clauses:
        s.add_clause(cl)
    deadline = time.time() + per_layer_budget
    CONF_CHUNK = 100000
    while True:
        rem = deadline - time.time()
        if rem <= 0 and best_model is not None:
            break
        assum = [-it.rhs[cost - 1]] if cost > 0 else []
        s.conf_budget(CONF_CHUNK)
        res = s.solve_limited(assumptions=assum)
        if res is True:
            best_model = s.get_model()
            cost = sum(1 for v in covvars if best_model[v - 1] < 0)
            if cost == 0:
                break
            continue
        if res is None and best_model is None:
            continue      # keep trying until we have at least one model
        break             # UNSAT (optimum reached) or budget exhausted
    if best_model is None:
        s.solve()
        best_model = s.get_model()
        cost = sum(1 for v in covvars if best_model[v - 1] < 0)
    s.delete()
    it.delete()
    model = set(l for l in best_model if l > 0)
    chosen = [(a, n) for (n, a), v in var.items() if v in model]
    # prune redundant classes, smallest moduli first (they're the scarce resource)
    chosen.sort(key=lambda an: an[1])
    kept = list(chosen)
    for cand in list(chosen):
        others = [c for c in kept if c != cand]
        a, n = cand
        covered_by_others = all(
            any(h % nn == aa for aa, nn in others)
            for h in holes if h % n == a
        )
        if covered_by_others:
            kept = others
    return kept, cost, time.time() - t0


def run(m, ladder, hole_cap=200000, verbose=True, budget=120, extend=()):
    """ladder: list of prime factors, e.g. [2,2,2,3,3,5,7]. extend: extra factors
    appended one at a time while holes remain. Returns (cover, lcm) or (None, lcm)."""
    Nk = 1
    holes = [0]                     # holes mod 1: everything uncovered
    used = set()
    cover = []
    ladder = list(ladder) + list(extend)
    for idx, q in enumerate(ladder):
        newN = Nk * q
        holes = [h + j * Nk for h in holes for j in range(q)]
        if len(holes) > hole_cap:
            print(f"  hole cap exceeded ({len(holes)}) at layer {idx}", flush=True)
            return None, newN
        Nk = newN
        mods = [d for d in divisors(Nk) if d >= m and d not in used]
        if not mods:
            continue
        chosen, cost, dt = layer_solve(holes, mods, per_layer_budget=budget)
        for a, n in chosen:
            used.add(n)
            cover.append((a, n))
        holes = [h for h in holes if all(h % n != a for a, n in chosen)]
        if verbose:
            print(f"  layer {idx} q={q} N={Nk} mods_avail={len(mods)} used={len(chosen)} "
                  f"holes_left={len(holes)} rc2={dt:.1f}s", flush=True)
        if not holes:
            return cover, Nk
    return (None, Nk)


def verify(cover, m):
    from math import lcm
    N = 1
    for a, n in cover:
        N = lcm(N, n)
    mods = [n for _, n in cover]
    assert len(mods) == len(set(mods)), "duplicate modulus"
    assert min(mods) >= m, "min modulus violated"
    # CRT-free check over Z_N (fine for moderate N)
    cov = bytearray(N)
    for a, n in cover:
        for t in range(a % n, N, n):
            cov[t] = 1
    return all(cov), N


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("m", type=int)
    ap.add_argument("ladder", help="comma-separated prime powers, e.g. 8,9,5,7,11")
    ap.add_argument("--out", default=None)
    ap.add_argument("--holecap", type=int, default=200000)
    ap.add_argument("--budget", type=float, default=120)
    ap.add_argument("--extend", default="")
    args = ap.parse_args()
    ladder = [int(x) for x in args.ladder.split(",")]
    ext = [int(x) for x in args.extend.split(",")] if args.extend else []
    cover, N = run(args.m, ladder, hole_cap=args.holecap, budget=args.budget, extend=ext)
    if cover is None:
        print("FAILED (holes remain or cap exceeded), lcm reached", N)
        sys.exit(1)
    ok, N = verify(cover, args.m)
    print(f"cover found: {len(cover)} congruences, lcm={N}, verified={ok}")
    if ok and args.out:
        json.dump({"m": args.m, "N": N, "cover": cover}, open(args.out, "w"))
        print("written", args.out)

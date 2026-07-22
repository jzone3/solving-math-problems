#!/usr/bin/env python3
"""P11 V2: multiplier-orbit exhaustion for circulant weighing matrices CW(n,k).

Premise: if a CW(n,k) exists admitting a numerical multiplier subgroup
H <= Z_n^*, then some translate of its first row is fixed by H, i.e. constant
on the orbits of H acting on Z_n by multiplication.  We enumerate ALL
subgroups H of Z_n^* whose orbit count is <= --max-orbits, and for each,
exhaustively assign values in {0,+1,-1} to orbits (DFS with pruning),
requiring total weight k and all nontrivial periodic autocorrelations zero.

Also supports "signed" invariance a_{t i} = chi(t) a_i for each character
chi: H -> {+1,-1} (multiplier with sign), via --signed.

Pruning in the DFS:
  * exact subset-sum feasibility on remaining orbit sizes (weight must hit k),
  * reachability of a valid total entry-sum (must satisfy (sum a)^2 = k),
  * negation symmetry: first nonzero orbit forced to +1.
Leaves get an exact integer O(n^2) autocorrelation check.

Exact integer arithmetic throughout.  Per-(H,chi) time budget so an
over-large case is reported as EXCEEDED rather than silently hanging.

Usage: python3 orbit_search.py n k [--max-orbits M] [--signed]
                                   [--case-timeout SECS]
"""
import sys, time
from math import gcd, isqrt


def units(n):
    return [x for x in range(1, n) if gcd(x, n) == 1]


def subgroups(n):
    """All subgroups of Z_n^* as frozensets (closure over products of cyclic ones)."""
    U = units(n)
    subs = set()
    cyc = []
    for g in U:
        h, cur = {1}, g
        while cur != 1:
            h.add(cur)
            cur = (cur * g) % n
        f = frozenset(h)
        subs.add(f)
        cyc.append(f)

    def prod(A, B):
        return frozenset((a * b) % n for a in A for b in B)

    frontier = set(subs)
    while frontier:
        new = set()
        for A in frontier:
            for B in cyc:
                P = prod(A, B)
                if P not in subs and P not in new:
                    new.add(P)
        subs |= new
        frontier = new
    return sorted(subs, key=len, reverse=True)


def orbits_of(n, H):
    seen = [False] * n
    orbs = []
    for x in range(n):
        if not seen[x]:
            o = {(h * x) % n for h in H}
            for y in o:
                seen[y] = True
            orbs.append(sorted(o))
    return orbs


def characters(H, n):
    """All characters H -> {+-1} of the abelian group H (multiplicative mod n)."""
    Hl = sorted(H)
    gens = []
    span = {1}
    for g in Hl:
        if g not in span:
            gens.append(g)
            newspan = set()
            for s in span:
                cur = s
                while True:
                    newspan.add(cur)
                    cur = (cur * g) % n
                    if cur == s:
                        break
            span = newspan
    chars, seen = [], set()
    for mask in range(1 << len(gens)):
        val = {1: 1}
        ok = True
        frontier = [1]
        while frontier and ok:
            nf = []
            for x in frontier:
                for i, g in enumerate(gens):
                    y = (x * g) % n
                    v = val[x] * (-1 if (mask >> i) & 1 else 1)
                    if y in val:
                        if val[y] != v:
                            ok = False
                            break
                    else:
                        val[y] = v
                        nf.append(y)
                if not ok:
                    break
            frontier = nf
        if ok and len(val) == len(Hl):
            key = tuple(val[h] for h in Hl)
            if key not in seen:
                seen.add(key)
                chars.append(val)
    return chars


def autocorr_ok(a, n, k):
    if sum(1 for x in a if x != 0) != k:
        return False
    for t in range(1, n // 2 + 1):
        s = 0
        for i in range(n):
            s += a[i] * a[(i + t) % n]
        if s != 0:
            return False
    return True


class CaseTimeout(Exception):
    pass


def search_case(n, k, pats, case_timeout, stats):
    """DFS over orbit values. pats: list of (size, entries|None, entry_sum).
    Returns list of witnesses."""
    s0 = isqrt(k)
    assert s0 * s0 == k
    order = sorted(range(len(pats)), key=lambda i: -pats[i][0])
    sizes = [pats[i][0] for i in order]
    esums = [pats[i][2] for i in order]
    usable = [pats[i][1] is not None for i in order]
    r = len(order)
    # suffix info for pruning
    suf_size = [0] * (r + 1)
    suf_abs_sum = [0] * (r + 1)
    for i in range(r - 1, -1, -1):
        suf_size[i] = suf_size[i + 1] + (sizes[i] if usable[i] else 0)
        suf_abs_sum[i] = suf_abs_sum[i + 1] + (abs(esums[i]) if usable[i] else 0)
    # exact subset-sum feasibility table: feas[i] = set of achievable weights from idx i
    feas = [set() for _ in range(r + 1)]
    feas[r] = {0}
    for i in range(r - 1, -1, -1):
        f = set(feas[i + 1])
        if usable[i]:
            f |= {w + sizes[i] for w in feas[i + 1] if w + sizes[i] <= k}
        feas[i] = f

    witnesses = []
    a = [0] * n
    t_end = time.time() + case_timeout
    node = [0]

    def dfs(idx, rem, cur_sum, any_nonzero):
        node[0] += 1
        if node[0] % 100000 == 0 and time.time() > t_end:
            raise CaseTimeout
        if rem == 0:
            # remaining orbits all zero; check total sum condition then autocorr
            if cur_sum * cur_sum == k:
                stats['leaves'] += 1
                if autocorr_ok(a, n, k):
                    witnesses.append(list(a))
            return
        if idx >= r or rem not in feas[idx]:
            return
        # sum reachability: |target_sum - cur_sum| <= suf_abs_sum[idx] for some target ±s0
        if min(abs(s0 - cur_sum), abs(-s0 - cur_sum)) > suf_abs_sum[idx]:
            return
        oi = order[idx]
        # value 0
        dfs(idx + 1, rem, cur_sum, any_nonzero)
        if usable[idx] and sizes[idx] <= rem:
            ent = pats[oi][1]
            for v in ((1,) if not any_nonzero else (1, -1)):
                for p, sgn in ent.items():
                    a[p] = sgn * v
                dfs(idx + 1, rem - sizes[idx], cur_sum + v * esums[idx], True)
                for p in ent:
                    a[p] = 0

    dfs(0, k, 0, False)
    stats['nodes'] += node[0]
    return witnesses


def build_pats(n, H, orbs, chi):
    pats = []
    for o in orbs:
        x = o[0]
        ent, ok = {}, True
        for h in H:
            p = (h * x) % n
            s = 1 if chi is None else chi[h]
            if p in ent:
                if ent[p] != s:
                    ok = False
                    break
            else:
                ent[p] = s
        if ok:
            pats.append((len(o), ent, sum(ent.values())))
        else:
            pats.append((len(o), None, 0))
    return pats


def search_cell(n, k, max_orbits=40, signed=False, case_timeout=900, log=print):
    t0 = time.time()
    subs = subgroups(n)
    log(f"# CW({n},{k}): |Z_{n}^*|={len(units(n))}, {len(subs)} subgroups, "
        f"max_orbits={max_orbits} signed={signed} case_timeout={case_timeout}s", flush=True)
    witnesses = []
    exceeded = []
    done = 0
    for H in subs:
        if len(H) == 1:
            continue
        orbs = orbits_of(n, H)
        r = len(orbs)
        if r > max_orbits:
            continue
        chars = characters(H, n) if signed else [None]
        for ci, chi in enumerate(chars):
            if chi is not None and all(v == 1 for v in chi.values()):
                continue  # trivial character == unsigned case, covered in plain run
            pats = build_pats(n, H, orbs, chi)
            stats = {'nodes': 0, 'leaves': 0}
            tc = time.time()
            try:
                ws = search_case(n, k, pats, case_timeout, stats)
            except CaseTimeout:
                exceeded.append((sorted(H), ci))
                log(f"  EXCEEDED |H|={len(H)} r={r} chi#{ci} after {case_timeout}s", flush=True)
                continue
            done += 1
            log(f"  case |H|={len(H)} r={r} chi#{ci}: nodes={stats['nodes']} "
                f"leaves={stats['leaves']} wit={len(ws)} {time.time()-tc:.1f}s", flush=True)
            if ws:
                log(f"!! WITNESS with H={sorted(H)} chi#{ci}", flush=True)
                witnesses.extend(ws)
    log(f"# done CW({n},{k}): {done} cases complete, {len(exceeded)} exceeded, "
        f"{time.time()-t0:.1f}s, {len(witnesses)} witnesses", flush=True)
    if exceeded:
        log(f"# exceeded cases: {exceeded}", flush=True)
    return witnesses


if __name__ == "__main__":
    n, k = int(sys.argv[1]), int(sys.argv[2])
    signed = "--signed" in sys.argv
    mo, ct = 40, 900
    for i, arg in enumerate(sys.argv):
        if arg == "--max-orbits":
            mo = int(sys.argv[i + 1])
        if arg == "--case-timeout":
            ct = int(sys.argv[i + 1])
    ws = search_cell(n, k, max_orbits=mo, signed=signed, case_timeout=ct)
    for w in ws:
        print("WITNESS", w, flush=True)
    print("TOTAL_WITNESSES", len(ws), flush=True)

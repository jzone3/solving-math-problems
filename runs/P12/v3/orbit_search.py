#!/usr/bin/env python3
"""Algebraic attack part 5: partial multiplicative-orbit constructions.

The rigidity theorem (NOTES.md sec 2) kills squares invariant under a group,
but NOT squares consisting of some full orbits under H <= Z_p^* (acting by
multiplication) PLUS a few free rows: the whole square is then not invariant,
so no contradiction applies.

Structure: |H| = d, k base rows each expanded to d scaled copies {h*b : h in H},
plus r = p - k*d free rows.

OBSTRUCTION THEOREM (NOTES.md sec 2c): the uncovered distance-1 pair set U is
H-invariant, so its in-edges and out-edges at the fixed symbol 0 come in
multiples of d; the r free rows (Hamiltonian paths, each visiting 0) supply
between r and 2r edges at 0, at most r in and r out. Hence r >= d is REQUIRED:
all maximal-orbit configs (r = p mod d < d) are impossible, matching the
empirical m*d plateaus. Only sub-maximal k (r = p - kd >= d) remain searchable.

DFS places base rows cell-by-cell, committing all d scaled copies of each new
adjacency simultaneously (d-fold constraint propagation => strong pruning),
then completes free rows. Symmetry breaking: base row is the orbit
representative whose first entry is minimal within {first entries of h*b}.

Usage: orbit_search.py p d [time_budget]
"""
import sys
import time

sys.path.insert(0, ".")
from t2lib import check_t2


def subgroup(p, d):
    # unique subgroup of order d of cyclic Z_p^*
    for g in range(2, p):
        s, x = set(), 1
        for _ in range(p - 1):
            x = x * g % p
            s.add(x)
        if len(s) == p - 1:
            break
    e = (p - 1) // d
    h = pow(g, e, p)
    H, x = [], 1
    for _ in range(d):
        H.append(x)
        x = x * h % p
    return sorted(H)


def search(p, d, k=None, time_budget=3600, report_every=60):
    H = subgroup(p, d)
    m = k if k is not None else p // d
    r = p - m * d
    n = p
    t0 = time.time()
    occ1 = [[False] * n for _ in range(n)]
    occ2 = [[False] * n for _ in range(n)]
    best = [0, None]
    base_rows = []
    free_rows = []
    last_report = [t0]

    def pairs_of(x, y):
        return [(h * x % p, h * y % p) for h in H]

    def try_commit(x, y, occ):
        ps = pairs_of(x, y)
        for a, b in ps:
            if occ[a][b]:
                return None
        for a, b in ps:
            occ[a][b] = True
        return ps

    def uncommit(ps, occ):
        for a, b in ps:
            occ[a][b] = False

    def current_rows():
        rows = []
        for b in base_rows:
            for h in H:
                rows.append([h * x % p for x in b])
        rows += [list(fr) for fr in free_rows]
        return rows

    def note_progress():
        nrows = len(base_rows) * d + len(free_rows)
        if nrows > best[0]:
            best[0] = nrows
            best[1] = current_rows()
        if report_every and time.time() - last_report[0] > report_every:
            last_report[0] = time.time()
            print(f"  [{time.time()-t0:.0f}s] depth base={len(base_rows)} free={len(free_rows)} best={best[0]}/{p}", flush=True)

    class Found(Exception):
        pass

    def gen_base(cur, used, bidx):
        if time.time() - t0 > time_budget:
            raise TimeoutError
        L = len(cur)
        if L == n:
            if base_rows and list(cur) <= base_rows[-1]:
                return  # keep base rows lex-increasing (order symmetry)
            base_rows.append(list(cur))
            note_progress()
            if len(base_rows) == m:
                dfs_free([], set(), None)
            else:
                gen_base([], set(), bidx + 1)
            base_rows.pop()
            return
        for x in range(n):
            if x in used:
                continue
            # orbit representative normalization: first entry must be
            # minimal among {h*first} (or 0); also order base rows by first entry.
            if L == 0:
                if x != 0 and x != min(h * x % p for h in H):
                    continue
            c1 = c2 = None
            if L >= 1:
                c1 = try_commit(cur[-1], x, occ1)
                if c1 is None:
                    continue
            if L >= 2:
                c2 = try_commit(cur[-2], x, occ2)
                if c2 is None:
                    uncommit(c1, occ1)
                    continue
            cur.append(x)
            used.add(x)
            gen_base(cur, used, bidx)
            cur.pop()
            used.discard(x)
            if c1:
                uncommit(c1, occ1)
            if c2:
                uncommit(c2, occ2)

    def dfs_free(cur, used, _):
        if time.time() - t0 > time_budget:
            raise TimeoutError
        L = len(cur)
        if L == n:
            free_rows.append(list(cur))
            note_progress()
            if len(free_rows) == r:
                best[0] = p
                best[1] = current_rows()
                raise Found
            dfs_free([], set(), None)
            free_rows.pop()
            return
        for x in range(n):
            if x in used:
                continue
            if L >= 1 and occ1[cur[-1]][x]:
                continue
            if L >= 2 and occ2[cur[-2]][x]:
                continue
            if L >= 1:
                occ1[cur[-1]][x] = True
            if L >= 2:
                occ2[cur[-2]][x] = True
            cur.append(x)
            used.add(x)
            dfs_free(cur, used, None)
            cur.pop()
            used.discard(x)
            if L >= 1:
                occ1[cur[-1]][x] = False
            if L >= 2:
                occ2[cur[-2]][x] = False

    status = "exhausted"
    try:
        gen_base([], set(), 0)
    except Found:
        status = "FOUND"
    except TimeoutError:
        status = "timeout"
    return status, best


if __name__ == "__main__":
    p = int(sys.argv[1])
    d = int(sys.argv[2])
    k = int(sys.argv[3])
    tb = float(sys.argv[4]) if len(sys.argv) > 4 else 3600
    print(f"p={p} d={d} k={k} H={subgroup(p,d)} free={p - k*d}", flush=True)
    status, best = search(p, d, k=k, time_budget=tb)
    print(f"p={p} d={d} k={k}: {status}, best {best[0]}/{p}", flush=True)
    if best[1] and best[0] == p:
        ok = check_t2(best[1], p)
        print("valid:", ok)
        if ok:
            with open(f"found_orbit_p{p}_d{d}_k{k}.txt", "w") as f:
                for row in best[1]:
                    f.write(" ".join(map(str, row)) + "\n")

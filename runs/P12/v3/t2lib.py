"""Shared T2(n) machinery for V3 (algebraic) run."""
import random


def check_t2(rows, n):
    occ1 = set()
    occ2 = set()
    for r in rows:
        if sorted(r) != list(range(n)):
            return False
        for i in range(n - 1):
            p = (r[i], r[i + 1])
            if p in occ1:
                return False
            occ1.add(p)
        for i in range(n - 2):
            p = (r[i], r[i + 2])
            if p in occ2:
                return False
            occ2.add(p)
    return len(rows) == n and len(occ1) == n * (n - 1)


def compatible_partial(rows, n):
    """rows form a valid partial T2 (at-most-once conditions)."""
    occ1 = set()
    occ2 = set()
    for r in rows:
        for i in range(n - 1):
            p = (r[i], r[i + 1])
            if p in occ1:
                return False
            occ1.add(p)
        for i in range(n - 2):
            p = (r[i], r[i + 2])
            if p in occ2:
                return False
            occ2.add(p)
    return True


def dfs_t2(n, fixed_rows=None, time_budget=None, count_all=False, rng=None):
    """Row-by-row + cell-by-cell DFS for a T2(n) extending fixed_rows.

    Returns a full solution (list of rows) or None. Row 1 defaults to identity
    (symbol-relabeling symmetry) when no fixed rows are given.
    If count_all, exhaustively counts completions (returns count).
    """
    import time
    t0 = time.time()
    occ1 = [[False] * n for _ in range(n)]
    occ2 = [[False] * n for _ in range(n)]
    rows = []

    def place_row(r):
        for i in range(n - 1):
            occ1[r[i]][r[i + 1]] = True
        for i in range(n - 2):
            occ2[r[i]][r[i + 2]] = True
        rows.append(r)

    def unplace_row():
        r = rows.pop()
        for i in range(n - 1):
            occ1[r[i]][r[i + 1]] = False
        for i in range(n - 2):
            occ2[r[i]][r[i + 2]] = False

    if fixed_rows is None:
        fixed_rows = [list(range(n))]
    for r in fixed_rows:
        for i in range(n - 1):
            if occ1[r[i]][r[i + 1]]:
                return None
        place_row(list(r))

    count = [0]
    sol = [None]
    nfixed = len(rows)

    def extend_row(cur, used, tight):
        """Generate completions of current row prefix cur.

        tight: row so far equals prefix of previous free row (lex order
        symmetry breaking among the free rows)."""
        if time_budget and time.time() - t0 > time_budget:
            raise TimeoutError
        if len(cur) == n:
            place_row(list(cur))
            if len(rows) == n:
                count[0] += 1
                sol[0] = [list(r) for r in rows]
                unplace_row()
                return not count_all
            done = extend_row([], set(), len(rows) > nfixed)
            unplace_row()
            return done
        lo = rows[-1][len(cur)] if tight and len(rows) > nfixed else 0
        cands = []
        for x in range(lo, n):
            if x in used:
                continue
            if cur:
                if occ1[cur[-1]][x]:
                    continue
            if len(cur) >= 2 and occ2[cur[-2]][x]:
                continue
            cands.append(x)
        if rng:
            rng.shuffle(cands)
        for x in cands:
            L = len(cur)
            if L >= 1:
                occ1[cur[-1]][x] = True
            if L >= 2:
                occ2[cur[-2]][x] = True
            cur.append(x)
            used.add(x)
            done = extend_row(cur, used, tight and x == lo)
            cur.pop()
            used.discard(x)
            if L >= 1:
                occ1[cur[-1] if L >= 1 else 0][x] = False
            if L >= 2:
                occ2[cur[-2]][x] = False
            if done:
                return True
        return False

    try:
        done = extend_row([], set(), False) if len(rows) < n else True
        if len(rows) == n and sol[0] is None:
            sol[0] = [list(r) for r in rows]
            count[0] = 1
    except TimeoutError:
        pass
    if count_all:
        return count[0]
    return sol[0]

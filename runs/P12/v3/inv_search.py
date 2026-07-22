#!/usr/bin/env python3
"""Algebraic attack part 3: solutions invariant under twisted symmetries.

Key structural fact (see NOTES.md): if a T2(n) is invariant (as a set of
rows) under a nontrivial symbol permutation sigma, then all row-orbits have
size ord(sigma), so ord(sigma) | n. For n = 11, 13 (prime) this forces sigma
to be an n-cycle ~ x -> x+1, making the square a translate square, which
needs a 2-sequencing of Z_n -- shown nonexistent (seq_search.py). So pure
symbol symmetries are DEAD for 11 and 13.

BUT the T2 axioms are also preserved by reversing every row. So consider
tau = (reverse all rows) o (symbol map sigma) with sigma an involution.
tau-invariant squares can exist for odd n: rows split into
  - 'self' rows r with r[n-1-j] = sigma(r[j]) (middle entry sigma-fixed),
  - mirror pairs {r, sigma(r) reversed}.
Number of self rows == n (mod 2). We DFS over this reduced space for each
conjugacy class of involutions (t = #fixed symbols, t odd).
"""
import sys
import time

sys.path.insert(0, ".")
from t2lib import check_t2


def make_sigma(n, t):
    """Involution fixing 0..t-1, swapping (t+2i, t+2i+1)."""
    s = list(range(n))
    for i in range(t, n - 1, 2):
        s[i], s[i + 1] = s[i + 1], s[i]
    return s


def search(n, t, time_budget=600, report=None):
    sigma = make_sigma(n, t)
    t0 = time.time()
    occ1 = [[False] * n for _ in range(n)]
    occ2 = [[False] * n for _ in range(n)]
    rows = []
    best = [0, None]

    def try_place(r):
        """Place full row if compatible; return True if placed."""
        for i in range(n - 1):
            if occ1[r[i]][r[i + 1]]:
                return False
        seen2 = set()
        for i in range(n - 2):
            p = (r[i], r[i + 2])
            if occ2[r[i]][r[i + 2]] or p in seen2:
                return False
            seen2.add(p)
        seen1 = set()
        for i in range(n - 1):
            p = (r[i], r[i + 1])
            if p in seen1:
                return False
            seen1.add(p)
        for i in range(n - 1):
            occ1[r[i]][r[i + 1]] = True
        for i in range(n - 2):
            occ2[r[i]][r[i + 2]] = True
        rows.append(r)
        return True

    def unplace():
        r = rows.pop()
        for i in range(n - 1):
            occ1[r[i]][r[i + 1]] = False
        for i in range(n - 2):
            occ2[r[i]][r[i + 2]] = False

    def mirror(r):
        return [sigma[r[n - 1 - j]] for j in range(n)]

    h = n // 2

    def gen_self_rows(cur, used, cb, last, tight):
        """Self rows: choose cur[0..h-1]; cur[h] sigma-fixed; rest forced.
        last/tight: lex symmetry breaking vs previous representative row."""
        if time.time() - t0 > time_budget:
            raise TimeoutError
        L = len(cur)
        if L == h:
            lo = last[h] if tight else 0
            for m in range(lo, t):
                if m in used:
                    continue
                r = cur + [m] + [sigma[cur[h - 1 - i]] for i in range(h)]
                if len(set(r)) == n:
                    if tight and m == last[h] and r <= last:
                        continue
                    cb(r)
            return
        lo = last[L] if tight else 0
        for x in range(lo, n):
            if x in used or sigma[x] in used:
                continue
            if cur and occ1[cur[-1]][x]:
                continue
            if L >= 2 and occ2[cur[-2]][x]:
                continue
            cur.append(x)
            used.add(x)
            used.add(sigma[x])
            gen_self_rows(cur, used, cb, last, tight and x == lo)
            cur.pop()
            used.discard(x)
            if sigma[x] != x:
                used.discard(sigma[x])

    def gen_free_rows(cur, used, cb, last, tight):
        if time.time() - t0 > time_budget:
            raise TimeoutError
        L = len(cur)
        if L == n:
            if not (tight):  # tight at full length means equal to last: skip
                cb(list(cur))
            return
        lo = last[L] if tight else 0
        for x in range(lo, n):
            if x in used:
                continue
            if cur and occ1[cur[-1]][x]:
                continue
            if L >= 2 and occ2[cur[-2]][x]:
                continue
            cur.append(x)
            used.add(x)
            gen_free_rows(cur, used, cb, last, tight and x == lo)
            cur.pop()
            used.discard(x)

    class Found(Exception):
        pass

    def rec(last_rep):
        if len(rows) > best[0]:
            best[0] = len(rows)
            best[1] = [list(r) for r in rows]
            if report:
                report(best)
        if len(rows) == n:
            raise Found

        def cb_self(r):
            if try_place(r):
                rec(r)
                unplace()

        def cb_free(r):
            m = mirror(r)
            if m <= r:  # pair symmetry breaking: representative is lex-min
                return
            if try_place(r):
                if try_place(m):
                    rec(r)
                    unplace()
                unplace()

        tight = last_rep is not None
        last = last_rep if tight else [0] * n
        gen_self_rows([], set(), cb_self, last, tight)
        gen_free_rows([], set(), cb_free, last, tight)

    try:
        rec(None)
        return False, best
    except Found:
        return True, best
    except TimeoutError:
        return False, best


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 600
    for t in range(1, n + 1, 2):
        if t == n:
            continue  # sigma = id => pure reversal => rows pair up, n odd dead
        st = time.time()
        found, best = search(n, t, time_budget=budget)
        print(f"n={n} t={t}: found={found} best={best[0]}/{n} time={time.time()-st:.1f}s", flush=True)
        if found:
            for r in best[1]:
                print("  ", r)
            print("valid:", check_t2(best[1], n))

#!/usr/bin/env python3
"""Check condition (C3): does the graph C_n + chords have an h-IDS w.r.t. h = C_n?

h-IDS (Thomassen): S independent in (V, E(h)) (no two h-consecutive vertices) and
dominating in (V, F) (every v not in S has an F-neighbour in S), F = chord set.
If an h-IDS exists, a second HC exists (Thomassen Thm 4) — so any true candidate must
have NO h-IDS. Exhaustive DFS over S; n <= 40 fine.

Usage: hids.py "... n=22 chords: 0-5 1-7 ..."
"""
import sys, re

def parse(argtext):
    n = int(re.search(r"n=(\d+)", argtext).group(1))
    chords = [(int(a), int(b)) for a, b in re.findall(r"(\d+)-(\d+)", argtext.split("chords:")[1])]
    return n, chords

def has_hids(n, chords):
    fadj = [[] for _ in range(n)]
    for a, b in chords:
        fadj[a].append(b); fadj[b].append(a)
    # DFS over vertices 0..n-1, state: chosen set S (no two h-consecutive, cyclic),
    # prune on domination feasibility: vertex v is "settled" once v and all its
    # F-neighbours have been decided; then require v in S or some F-neighbour in S.
    S = [False] * n
    decided = [False] * n

    def dominated_check(v):
        if S[v]:
            return True
        return any(S[w] for w in fadj[v])

    def dfs(i):
        if i == n:
            return all(dominated_check(v) for v in range(n))
        # option 1: v=i not in S
        S[i] = False
        # settled vertices: any u <= i whose F-neighbours are all <= i can be checked
        ok = True
        u = i - 1
        # cheap prune: check vertex i- max chord reach fully decided
        for u in range(i + 1):
            if all(w <= i for w in fadj[u]) and not dominated_check(u):
                ok = False
                break
        if ok and dfs(i + 1):
            return True
        # option 2: v=i in S, if allowed (h-independence, cyclic)
        if not (i > 0 and S[i - 1]) and not (i == n - 1 and S[0]):
            S[i] = True
            ok = True
            for u in range(i + 1):
                if all(w <= i for w in fadj[u]) and not dominated_check(u):
                    ok = False
                    break
            if ok and dfs(i + 1):
                return True
            S[i] = False
        return False

    return dfs(0)

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) or sys.stdin.read()
    n, chords = parse(text)
    print("has h-IDS:", has_hids(n, chords))

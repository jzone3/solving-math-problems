#!/usr/bin/env python3
"""Independent verifier for P01 V5 candidates (also the template for solutions/P01/verify.py).

Input: n and a chord list (the graph is C_n plus those chords).
Checks: (1) graph is simple and 4-regular; (2) exact number of Hamiltonian cycles,
counted by a pure-python backtracking entirely independent of the C search code.
Prints PASS if the graph is 4-regular, simple, and uniquely hamiltonian.

Usage: verify_candidate.py "IMPROVE 1 n=22 chords: 0-5 1-7 ..."   (or the raw chord spec)
"""
import sys, re

def parse(argtext):
    m = re.search(r"n=(\d+)", argtext)
    n = int(m.group(1))
    chords = [(int(a), int(b)) for a, b in re.findall(r"(\d+)-(\d+)", argtext.split("chords:")[1])]
    return n, chords

def count_hc(n, chords, limit=None):
    adj = [set(((v + 1) % n, (v - 1) % n)) for v in range(n)]
    seen = set()
    for a, b in chords:
        assert a != b, "loop"
        assert (a - b) % n not in (1, n - 1), "chord parallel to cycle edge"
        key = (min(a, b), max(a, b))
        assert key not in seen, "duplicate chord"
        seen.add(key)
        adj[a].add(b); adj[b].add(a)
    for v in range(n):
        assert len(adj[v]) == 4, f"vertex {v} degree {len(adj[v])} != 4"
    # backtracking count of HCs through vertex 0; fix direction via first<last neighbour
    count = 0
    path = [0]
    visited = [False] * n
    visited[0] = True
    sys.setrecursionlimit(10000)

    def bt(u, depth):
        nonlocal count
        if limit is not None and count >= limit:
            return
        if depth == n:
            if 0 in adj[u] and path[1] < u:  # close cycle; direction canonicalisation
                count += 1
            return
        for w in adj[u]:
            if not visited[w]:
                # prune: any unvisited vertex with <2 usable neighbours kills extension
                visited[w] = True
                path.append(w)
                ok = True
                for x in range(n):
                    if not visited[x]:
                        usable = sum(1 for y in adj[x] if (not visited[y]) or y == w or y == 0)
                        if usable < 2:
                            ok = False
                            break
                if ok:
                    bt(w, depth + 1)
                path.pop()
                visited[w] = False

    bt(0, 1)
    return count

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) or sys.stdin.read()
    n, chords = parse(text)
    c = count_hc(n, chords)
    print(f"n={n} #HC={c}")
    if c == 1:
        print("PASS: 4-regular simple uniquely hamiltonian graph!")
    else:
        print(f"not uniquely hamiltonian (count={c})")

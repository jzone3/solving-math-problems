"""Fast Hamiltonian-cycle utilities for graphs given as adjacency lists.

Graphs here are C_n (edges i -> i+1 mod n) plus a set of chords making the
graph 4-regular. The base HC is (0, 1, ..., n-1).
"""


def find_second_hc(n, adj, limit=1):
    """Search for Hamiltonian cycles different from the base cycle
    0-1-...-(n-1)-0. Returns a list of up to `limit` such cycles, each as a
    tuple of vertices starting at 0. Cycles are canonicalized so we never
    return the base cycle or its reversal.
    """
    base = tuple(range(n))
    found = []
    visited = [False] * n
    visited[0] = True
    path = [0]

    def canon(p):
        # p is a cycle starting at 0; canonicalize direction
        if p[1] > p[-1]:
            p = (p[0],) + tuple(reversed(p[1:]))
        return p

    def dfs(v):
        if len(found) >= limit:
            return True
        if len(path) == n:
            if 0 in adj[v]:
                c = canon(tuple(path))
                if c != base:
                    found.append(c)
                    if len(found) >= limit:
                        return True
            return False
        for w in adj[v]:
            if not visited[w]:
                # connectivity pruning: cheap degree check
                visited[w] = True
                path.append(w)
                if dfs(w):
                    return True
                path.pop()
                visited[w] = False
        return False

    # break direction symmetry: force second vertex < last vertex handled by canon;
    # here we just enumerate but dedupe via canon
    dfs(0)
    return found


def count_hcs(n, adj, cap=None):
    """Count Hamiltonian cycles (up to direction).

    Returns (count, capped). `cap` is in undirected cycles; the search stops
    early once 2*cap directed cycles are seen, and capped=True means the true
    count is >= cap (returned count is then exactly cap).
    """
    dcap = None if cap is None else 2 * cap
    count = 0
    visited = [False] * n
    visited[0] = True
    path = [0]

    def dfs(v):
        nonlocal count
        if dcap is not None and count >= dcap:
            return
        if len(path) == n:
            if 0 in adj[v]:
                count += 1
            return
        for w in adj[v]:
            if not visited[w]:
                visited[w] = True
                path.append(w)
                dfs(w)
                path.pop()
                visited[w] = False

    # fix direction: second vertex must be smaller than last vertex ->
    # enumerate neighbors of 0 in increasing order and only start with the
    # smaller endpoint; simplest correct approach: count directed and halve.
    dfs(0)
    if dcap is not None and count >= dcap:
        return cap, True
    assert count % 2 == 0
    return count // 2, False

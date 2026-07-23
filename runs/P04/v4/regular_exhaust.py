"""Exhaustive Hajos check over geng-generated regular graphs (graph6 on stdin).

Pipeline: nauty-geng -c -d6 -D6 n res/mod | python3 regular_exhaust.py n K out.txt

Fast path: randomized Hierholzer Euler tour, split into simple cycles at first
vertex repeat; retry a few times hoping for <= K cycles. Slow path: exact
CP-SAT oracle (mincyc.decomposable_within). Logs only slow-path graphs and a
final summary; any violation is logged loudly with its graph6 string.
"""
import sys, random, time
import mincyc as M


def g6_to_edges(line):
    s = line.strip()
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for x in data[1:]:
        for i in range(5, -1, -1):
            bits.append((x >> i) & 1)
    edges = []
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                edges.append((i, j))
            k += 1
    return n, edges


def euler_split_count(n, edges, rng):
    adj = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        adj[u].append((v, idx))
        adj[v].append((u, idx))
    for a in adj:
        rng.shuffle(a)
    used = [False] * len(edges)
    ptr = [0] * n
    # Hierholzer
    stack = [edges[0][0]]
    tour = []
    while stack:
        v = stack[-1]
        while ptr[v] < len(adj[v]) and used[adj[v][ptr[v]][1]]:
            ptr[v] += 1
        if ptr[v] == len(adj[v]):
            tour.append(stack.pop())
        else:
            w, idx = adj[v][ptr[v]]
            used[idx] = True
            stack.append(w)
    # split tour into simple cycles
    pos = {}
    st = []
    ncyc = 0
    for v in tour:
        if v in pos:
            i = pos[v]
            for u in st[i + 1:]:
                del pos[u]
            del st[i + 1:]
            ncyc += 1
        else:
            pos[v] = len(st)
            st.append(v)
    return ncyc


def main():
    n = int(sys.argv[1])
    K = int(sys.argv[2])
    tries = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    rng = random.Random(12345)
    total = fast = slow = 0
    viol = []
    t0 = time.time()
    for line in sys.stdin:
        if not line.strip():
            continue
        total += 1
        nn, E = g6_to_edges(line)
        assert nn == n
        ok = False
        for _ in range(tries):
            if euler_split_count(n, E, rng) <= K:
                ok = True
                break
        if ok:
            fast += 1
        else:
            slow += 1
            feas, _ = M.decomposable_within(n, E, K, time_limit=300.0, workers=2)
            if feas is True:
                print(f"SLOWPASS {line.strip()}", flush=True)
            else:
                viol.append(line.strip())
                print(f"VIOLATION?! feas={feas} g6={line.strip()}", flush=True)
        if total % 20000 == 0:
            print(f"progress {total} fast={fast} slow={slow} t={time.time()-t0:.0f}s", flush=True)
    print(f"DONE total={total} fast={fast} slow={slow} violations={len(viol)} t={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()

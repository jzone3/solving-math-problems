"""Wave 2b: blow-ups, products, line graphs and named triangle-dense graphs."""
import itertools, time
import mincyc as M
from circulants import check_and_log


def lex_cycle_blowup(k, t, inner_clique):
    """C_k[K_t] if inner_clique else C_k[empty_t]; n = k*t."""
    n = k * t
    V = lambda i, a: i * t + a
    E = set()
    for i in range(k):
        for a in range(t):
            for b in range(t):
                E.add(tuple(sorted((V(i, a), V((i + 1) % k, b)))))
            if inner_clique:
                for b in range(a + 1, t):
                    E.add((V(i, a), V(i, b)))
    return n, sorted(E)


def line_graph_complete(m):
    """T(m) = L(K_m), n = C(m,2), degree 2(m-2)."""
    verts = list(itertools.combinations(range(m), 2))
    idx = {v: i for i, v in enumerate(verts)}
    E = []
    for i, e in enumerate(verts):
        for j in range(i + 1, len(verts)):
            f = verts[j]
            if set(e) & set(f):
                E.append((i, j))
    return len(verts), E


def complete_multipartite(parts):
    n = sum(parts)
    ids = []
    s = 0
    for p in parts:
        ids.append(list(range(s, s + p)))
        s += p
    E = []
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            for a in ids[i]:
                for b in ids[j]:
                    E.append((a, b))
    return n, E


def cocktail(k):  # K_{2k} minus PM = K_{2x...}; complete multipartite 2^k
    return complete_multipartite([2] * k)


def main():
    lf = open("blowups.txt", "a")
    tests = []
    # cycle blow-ups (2t- or (3t-1)-regular; need even degree)
    for k in range(3, 9):
        for t in (2, 3, 4):
            n, E = lex_cycle_blowup(k, t, False)  # 2t-regular, even
            if 13 <= n <= 26:
                tests.append((f"C{k}[E{t}]", n, E))
            n, E = lex_cycle_blowup(k, t, True)   # (2t + t-1)-regular
            if 13 <= n <= 26 and (3 * t - 1) % 2 == 0:
                tests.append((f"C{k}[K{t}]", n, E))
    # triangular graphs T(m), m even -> 2(m-2)-regular
    for m in (6, 7):
        n, E = line_graph_complete(m)
        if n <= 26:
            tests.append((f"T({m})", n, E))
    # complete multipartite with even degrees
    for parts in [(3, 3, 3, 3, 3), (5, 5, 5), (3, 3, 3, 3), (4, 4, 4, 4),
                  (2, 2, 2, 2, 2, 2, 2), (2, 2, 2, 2, 2, 2, 2, 2),
                  (6, 6, 6), (4, 4, 4, 4, 4), (3, 3, 3, 3, 3, 3),
                  (1, 2, 2, 2, 2, 2, 2), (7, 7, 7), (5, 5, 5, 5)]:
        n, E = complete_multipartite(list(parts))
        if 13 <= n <= 26:
            tests.append((f"K{parts}", n, E))
    for name, n, E in tests:
        deg = [0] * n
        for u, v in E:
            deg[u] += 1
            deg[v] += 1
        if any(d % 2 for d in deg):
            print(f"skip {name} (odd degree)")
            continue
        r = check_and_log(name, n, E, lf, time_limit=1200)
        if r == "WITNESS":
            return
    lf.write("=== blowups done ===\n")


if __name__ == "__main__":
    main()

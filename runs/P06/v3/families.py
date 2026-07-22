"""Large-n asymptotics for near-clique / star-like families under the padded
objective  Phi(H) = max_{k>=0} [ dev^2 - R^2 ](H + k*K1),
where dev^2(n) = A/n - 4m^2/n^2, A = sum d(d+1), maximized at n* = 8m^2/A
(clamped to n >= nH).  Phi > 0  <=>  counterexample to WoW 129.

Each family returns (nH, A, m, R) with R computed in mpmath (60 dps) from
edge classes.  Equality benchmark: K_t (Phi = 0 exactly, via K_t+(t-2)K1).
"""
from mpmath import mp, mpf, sqrt as msqrt
mp.dps = 60


def phi(nH, A, m, R):
    """max over integer n >= nH of dev^2 - R^2."""
    if m == 0:
        return None, None
    nstar = mpf(8) * m * m / A
    cands = {nH}
    if nstar > nH:
        cands.add(int(nstar)); cands.add(int(nstar) + 1)
    best = None
    for n in cands:
        dev2 = mpf(A) / n - mpf(4 * m * m) / (n * n)
        v = dev2 - R * R
        if best is None or v > best[1]:
            best = (n, v)
    return best


def from_edge_classes(classes):
    """classes: list of (count, du, dv). Returns A, m, R and degree check."""
    m = sum(c for c, _, _ in classes)
    R = sum(mpf(c) / msqrt(mpf(du) * dv) for c, du, dv in classes)
    return m, R


def fam_clique(t):
    # K_t
    degsum2 = t * (t - 1) ** 2
    A = degsum2 + t * (t - 1)
    m, R = from_edge_classes([(t * (t - 1) // 2, t - 1, t - 1)])
    return t, A, m, R


def fam_clique_plus_vertex(t, j):
    # K_t plus one vertex adjacent to j clique vertices
    A = j * (t * t + t) + (t - j) * (t * t - t) + j * (j + 1)
    cls = [(j * (t - j), t, t - 1), ((t - j) * (t - j - 1) // 2, t - 1, t - 1),
           (j * (j - 1) // 2, t, t), (j, j, t)]
    m, R = from_edge_classes([c for c in cls if c[0] > 0])
    return t + 1, A, m, R


def fam_clique_minus_star(t, j):
    # K_t minus j edges at one vertex (its degree t-1-j, endpoints t-2)
    degs = [t - 1 - j] + [t - 2] * j + [t - 1] * (t - 1 - j)
    A = sum(d * (d + 1) for d in degs)
    cls = [((t - 1 - j), t - 1 - j, t - 1),
           (j * (t - 1 - j), t - 2, t - 1),
           (j * (j - 1) // 2, t - 2, t - 2),
           ((t - 1 - j) * (t - 2 - j) // 2, t - 1, t - 1)]
    m, R = from_edge_classes([c for c in cls if c[0] > 0])
    return t, A, m, R


def fam_clique_minus_matching(t, j):
    # K_t minus a matching of j edges
    degs = [t - 2] * (2 * j) + [t - 1] * (t - 2 * j)
    A = sum(d * (d + 1) for d in degs)
    n22 = 2 * j * (2 * j - 1) // 2 - j   # pairs among matched verts minus removed
    cls = [(n22, t - 2, t - 2),
           (2 * j * (t - 2 * j), t - 2, t - 1),
           ((t - 2 * j) * (t - 2 * j - 1) // 2, t - 1, t - 1)]
    m, R = from_edge_classes([c for c in cls if c[0] > 0])
    return t, A, m, R


def fam_two_cliques_sharing(t, s):
    # two K_t sharing s vertices (2t-s vertices)
    # shared verts: degree 2t-s-1... shared vertices adjacent to all others? no:
    # shared vertex adjacent to all of both cliques: degree (2t - s - 1)
    # non-shared: degree t-1
    n = 2 * t - s
    degs = [2 * t - s - 1] * s + [t - 1] * (2 * (t - s))
    A = sum(d * (d + 1) for d in degs)
    cls = [(s * (s - 1) // 2, 2 * t - s - 1, 2 * t - s - 1),
           (s * 2 * (t - s), 2 * t - s - 1, t - 1),
           (2 * ((t - s) * (t - s - 1) // 2), t - 1, t - 1)]
    m, R = from_edge_classes([c for c in cls if c[0] > 0])
    return n, A, m, R


def fam_complete_split(n, s):
    # K_s join empty(n-s)
    degs = [n - 1] * s + [s] * (n - s)
    A = sum(d * (d + 1) for d in degs)
    cls = [(s * (s - 1) // 2, n - 1, n - 1), (s * (n - s), n - 1, s)]
    m, R = from_edge_classes([c for c in cls if c[0] > 0])
    return n, A, m, R


def fam_pineapple(p, q):
    # K_p with q pendant vertices on one apex
    degs = [p - 1 + q] + [p - 1] * (p - 1) + [1] * q
    A = sum(d * (d + 1) for d in degs)
    cls = [((p - 1), p - 1 + q, p - 1),
           ((p - 1) * (p - 2) // 2, p - 1, p - 1),
           (q, 1, p - 1 + q)]
    m, R = from_edge_classes([c for c in cls if c[0] > 0])
    return p + q, A, m, R


def fam_kite(p, q):
    # K_p plus pendant path of length q
    degs = [p - 1] * (p - 1) + [p] + [2] * (q - 1) + [1]
    A = sum(d * (d + 1) for d in degs)
    cls = [((p - 1) * (p - 2) // 2, p - 1, p - 1), ((p - 1), p, p - 1)]
    if q == 1:
        cls.append((1, p, 1))
    else:
        cls.append((1, p, 2))
        cls.append((q - 2, 2, 2))
        cls.append((1, 2, 1))
    m, R = from_edge_classes([c for c in cls if c[0] > 0])
    return p + q, A, m, R


if __name__ == "__main__":
    print("== sanity: cliques give Phi = 0 ==")
    for t in (5, 50, 500, 5000):
        nH, A, m, R = fam_clique(t)
        n, v = phi(nH, A, m, R)
        print(f"K_{t}: n_opt={n} Phi={mp.nstr(v, 8)}")

    def scan(name, gen):
        best = None
        for args, tup in gen:
            n, v = phi(*tup)
            if best is None or v > best[0]:
                best = (v, args, n)
        v, args, n = best
        print(f"{name}: best Phi={mp.nstr(v, 8)} at {args} (n_opt={n})")

    for t in (20, 100, 1000, 10000):
        scan(f"clique+vertex t={t}",
             (((t, j), fam_clique_plus_vertex(t, j)) for j in range(1, t + 1)))
        scan(f"clique-star t={t}",
             (((t, j), fam_clique_minus_star(t, j)) for j in range(1, t - 1)))
        scan(f"clique-matching t={t}",
             (((t, j), fam_clique_minus_matching(t, j)) for j in range(1, t // 2)))
        scan(f"two cliques t={t}",
             (((t, s), fam_two_cliques_sharing(t, s)) for s in range(1, t)))
    for n in (30, 100, 1000, 10000):
        scan(f"complete split n={n}",
             (((n, s), fam_complete_split(n, s)) for s in range(1, n)))
        scan(f"pineapple n={n}",
             (((p, n - p), fam_pineapple(p, n - p)) for p in range(2, n)))
        scan(f"kite n={n}",
             (((p, n - p), fam_kite(p, n - p)) for p in range(2, n)))

"""Structured-family scan for Bollobas-Nikiforov (borrowed V2 ideas after V1 exhaustion).

Families with two potentially-large eigenvalues or known extremal behavior:
- Kneser graphs K(n,k), Johnson graphs J(n,k)
- Paley graphs (prime q <= 149)
- book graphs B(p,q) = K_p joined with empty graph I_q, generalized: K_p + (K_a u K_b) joins
- double kites, two cliques sharing s vertices, two cliques joined by matchings/bridges
- complements of the above where cheap
Exact omega via bn_core.max_clique (sizes kept <= ~150 where BnB is OK for these shapes).
"""
import itertools

from bn_core import evaluate

def report(name, n, adj, results):
    score, ratio, l1, l2, m, w = evaluate(n, adj)
    results.append((ratio, score, name, n, m, w, l1, l2))
    if score > 1e-6:
        print(f"VIOLATION {name} score={score}", flush=True)


def add_edge(adj, i, j):
    adj[i] |= 1 << j
    adj[j] |= 1 << i


def kneser(n, k):
    sets = list(itertools.combinations(range(n), k))
    N = len(sets)
    masks = [sum(1 << x for x in s) for s in sets]
    adj = [0] * N
    for a in range(N):
        for b in range(a + 1, N):
            if not (masks[a] & masks[b]):
                add_edge(adj, a, b)
    return N, adj


def johnson(n, k):
    sets = list(itertools.combinations(range(n), k))
    N = len(sets)
    masks = [sum(1 << x for x in s) for s in sets]
    adj = [0] * N
    for a in range(N):
        for b in range(a + 1, N):
            if bin(masks[a] & masks[b]).count("1") == k - 1:
                add_edge(adj, a, b)
    return N, adj


def paley(q):
    residues = {(x * x) % q for x in range(1, q)}
    adj = [0] * q
    for a in range(q):
        for b in range(a + 1, q):
            if (a - b) % q in residues:
                add_edge(adj, a, b)
    return q, adj


def two_cliques_share(a, b, s):
    """K_a and K_b sharing s common vertices."""
    n = a + b - s
    adj = [0] * n
    for i, j in itertools.combinations(range(a), 2):
        add_edge(adj, i, j)
    verts_b = list(range(a - s, a)) + list(range(a, n))
    for i, j in itertools.combinations(verts_b, 2):
        add_edge(adj, i, j)
    return n, adj


def join(n1, adj1, n2, adj2):
    n = n1 + n2
    adj = [adj1[i] for i in range(n1)] + [adj2[i] << n1 for i in range(n2)]
    for i in range(n1):
        for j in range(n1, n):
            add_edge(adj, i, j)
    return n, adj


def empty(k):
    return k, [0] * k


def clique(k):
    adj = [0] * k
    for i, j in itertools.combinations(range(k), 2):
        add_edge(adj, i, j)
    return k, adj


def disjoint(n1, adj1, n2, adj2):
    return n1 + n2, [adj1[i] for i in range(n1)] + [adj2[i] << n1 for i in range(n2)]


def main():
    results = []
    for n in range(5, 13):
        for k in range(2, n // 2 + 1):
            N, adj = kneser(n, k)
            if N <= 130 and sum(bin(x).count("1") for x in adj) > 0:
                report(f"Kneser({n},{k})", N, adj, results)
            N, adj = johnson(n, k)
            if N <= 130:
                report(f"Johnson({n},{k})", N, adj, results)
    for q in [5, 13, 17, 29, 37, 41, 53, 61, 73, 89, 97, 101, 109, 113, 137, 149]:
        n, adj = paley(q)
        report(f"Paley({q})", n, adj, results)
    for a in range(3, 16):
        for b in range(3, 16):
            for s in range(1, min(a, b)):
                n, adj = two_cliques_share(a, b, s)
                if n <= 40:
                    report(f"2cliques({a},{b},s={s})", n, adj, results)
    # joins: K_p + (K_a u K_b)  (two big eigenvalues by design)
    for p in range(0, 10):
        for a in range(2, 14):
            for b in range(2, a + 1):
                nu, au = disjoint(*clique(a), *clique(b))
                if p:
                    n, adj = join(*clique(p), nu, au)
                else:
                    n, adj = nu, au
                report(f"K{p}+(K{a} u K{b})", n, adj, results)
    # books: K_p + empty(q)
    for p in range(2, 14):
        for q in range(1, 30):
            n, adj = join(*clique(p), *empty(q))
            report(f"K{p}+I{q}", n, adj, results)
    # K_p + (K_a u K_b u K_c)
    for p in range(0, 8):
        for a in range(2, 10):
            for b in range(2, a + 1):
                for c in range(2, b + 1):
                    nu, au = disjoint(*disjoint(*clique(a), *clique(b)), *clique(c))
                    if p:
                        n, adj = join(*clique(p), nu, au)
                    else:
                        n, adj = nu, au
                    report(f"K{p}+(K{a} u K{b} u K{c})", n, adj, results)
    results.sort(reverse=True)
    print("\nTop 25 by ratio:")
    for r in results[:25]:
        print(f"  ratio={r[0]:.8f} score={r[1]:.4f} {r[2]} n={r[3]} m={r[4]} w={r[5]} "
              f"l1={r[6]:.3f} l2={r[7]:.3f}")


if __name__ == "__main__":
    main()

"""Wave 3b: Eulerian Cayley graphs of dihedral groups D_m (order n = 2m).

Elements: rotations r^0..r^{m-1}, reflections s r^0..s r^{m-1}.
Connection set T (symmetric, no identity): rotation part R subseteq {1..m-1}
closed under negation mod m; reflection part F subseteq {0..m-1} (each s r^j is
an involution).  Degree = |R| + |F|; Eulerian needs |R|+|F| even, connectivity
of <T>.  Exhaustive for m <= 9 (n <= 18); random-sampled for 10 <= m <= 13.
"""
import itertools, random, sys, time
import mincyc as M
from circulants import check_and_log


def cayley_dihedral(m, R, F):
    """Vertices 0..m-1 = r^i, m..2m-1 = s r^i.  s r^i * r^k = s r^{i+k}? Use
    right multiplication: edge {g, g*t}."""
    n = 2 * m
    E = set()
    for i in range(m):
        for k in R:
            E.add(tuple(sorted((i, (i + k) % m))))               # r^i * r^k
            E.add(tuple(sorted((m + i, m + (i - k) % m))))       # (sr^i)*r^k = s r^{i-k}? see below
        for j in F:
            # r^i * (s r^j) = s r^{j - i}?  With convention r^a s = s r^{-a}:
            # r^i * s r^j = s r^{j-i}; edge between rotation i and reflection (j-i) mod m
            E.add(tuple(sorted((i, m + (j - i) % m))))
    return n, sorted(E)


def connected(n, E):
    adj = [[] for _ in range(n)]
    for u, v in E:
        adj[u].append(v)
        adj[v].append(u)
    seen = {0}
    st = [0]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                st.append(y)
    return len(seen) == n


def rotation_subsets(m):
    """Inverse-closed subsets of {1..m-1}: choose union of pairs {k, m-k}."""
    pairs = []
    for k in range(1, m // 2 + 1):
        if k == m - k:
            pairs.append((k,))
        else:
            pairs.append((k, m - k))
    for mask in range(2 ** len(pairs)):
        S = []
        for i, p in enumerate(pairs):
            if mask >> i & 1:
                S.extend(p)
        yield tuple(sorted(S))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "exhaustive"
    lf = open("dihedral.txt", "a")
    checked = 0
    if mode == "exhaustive":
        for m in range(7, 10):  # n = 14, 16, 18
            for R in rotation_subsets(m):
                for fsize in range(0, m + 1):
                    for F in itertools.combinations(range(m), fsize):
                        if (len(R) + len(F)) % 2 or len(R) + len(F) < 4:
                            continue
                        n, E = cayley_dihedral(m, R, F)
                        if not connected(n, E):
                            continue
                        r = check_and_log(f"D{m}R{R}F{F}", n, E, lf, 600)
                        if r == "WITNESS":
                            return
                        if r != "skip":
                            checked += 1
        lf.write(f"=== dihedral exhaustive m=7..9 done checked={checked} ===\n")
    else:
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        samples = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
        rng = random.Random(seed)
        for s in range(samples):
            m = rng.choice([10, 11, 12, 13])
            Rs = list(rotation_subsets(m))
            R = rng.choice(Rs)
            F = tuple(sorted(rng.sample(range(m), rng.randrange(0, m + 1))))
            if (len(R) + len(F)) % 2 or len(R) + len(F) < 4:
                continue
            n, E = cayley_dihedral(m, R, F)
            if not connected(n, E):
                continue
            r = check_and_log(f"D{m}R{R}F{F}", n, E, lf, 600)
            if r == "WITNESS":
                return
            checked += 1
        lf.write(f"=== dihedral sampled m=10..13 done checked={checked} ===\n")
    print("done", checked)


if __name__ == "__main__":
    main()

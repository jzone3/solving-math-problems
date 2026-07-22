"""Generalized Schrijver ring family (Feofiloff survey Figure 8): ring of
length 2i.  Vertices O_1..O_{2i} (outer) and I_1..I_{2i} (inner), indices
mod 2i.  For each odd k: solid O_k->O_{k+1}, O_k->I_{k-1}, I_k->I_{k+1};
null O_k->O_{k-1}, O_k->I_k, I_k->I_{k-1}.  For each even k: null O_k->I_k.
i=3 gives Schrijver's D1 (machine-checked isomorphic behavior: tau=2, nu=1);
odd i>=3 are counterexamples, even i are not (survey §7)."""


def ring(i):
    m = 2 * i

    def O(k):
        return (k - 1) % m

    def I(k):
        return m + (k - 1) % m

    solid, null = [], []
    for k in range(1, m + 1):
        if k % 2 == 1:
            solid += [(O(k), O(k + 1)), (O(k), I(k - 1)), (I(k), I(k + 1))]
            null += [(O(k), O(k - 1)), (O(k), I(k)), (I(k), I(k - 1))]
        else:
            null += [(O(k), I(k))]
    n = 2 * m
    arcs = solid + null
    w = [1] * len(solid) + [0] * len(null)
    return n, arcs, w


if __name__ == "__main__":
    import core
    for i in (3, 4, 5):
        n, arcs, w = ring(i)
        t, _ = core.tau(n, arcs, w)
        t2, v = core.nu(n, arcs, w)
        print(f"ring({i}): |V|={n} |A|={len(arcs)} tau={t} nu={v}")

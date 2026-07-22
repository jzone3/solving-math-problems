"""Shared helpers for P12 V4 (Tuscan-2 squares via CP-SAT / hybrid LNS)."""


def cost(array):
    """Violation cost: (#duplicate dist-1 slots) + (#duplicate dist-2 slots).

    Since the number of dist-1 slots equals the number of ordered pairs,
    zero duplicates at dist 1 implies exact coverage; dist-2 only needs
    at-most-once. cost==0 iff valid T2(n).
    """
    n = len(array)
    seen1 = set()
    seen2 = set()
    c = 0
    for r in array:
        for i in range(n - 1):
            p = (r[i], r[i + 1])
            if p in seen1:
                c += 1
            else:
                seen1.add(p)
        for i in range(n - 2):
            p = (r[i], r[i + 2])
            if p in seen2:
                c += 1
            else:
                seen2.add(p)
    return c


def write_witness(array, path):
    with open(path, "w") as f:
        for r in array:
            f.write(" ".join(map(str, r)) + "\n")

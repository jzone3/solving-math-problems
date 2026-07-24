"""Phase 26: exact-cover restructuring search for Nielsen 4.5's tenth
input (obstruction A).

Region to re-cover, inside one fixed context cell (5-digit m, 7-level
l, 11-level k -- context factors are identical for both colliding
slots, so a per-context solution replicates across contexts with
automatically distinct moduli):

    R = (1 mod 9  U  3 mod 9)  n  B,   B = the 2-branch {v2 >= 3 cells}

Model: a congruence with modulus 2^a * 3^b * (context) covers exactly
one (a,b)-cell of the dyadic-triadic tree; each modulus VALUE may be
used at most once inside the context (distinct moduli).  A vector
(a,b) is FREE iff no modulus of the concrete secs 3.1-3.6 emission
has valuations (v2,v3)=(a,b) with v5>=1, v7>=1, v11>=1, v13=0.

Question: does a finite set of free vectors exactly pack R?
"""
import emitcore, emit33, emit34, emit35, emit36


def vals(n):
    out = []
    for p in (2, 3, 5, 7, 11, 13):
        d = 0
        while n % p == 0:
            n //= p
            d += 1
        out.append(d)
    return out


def used_ab():
    used = set()
    for src in (emitcore.emit(), emit33.emit(), emit34.emit34()[0],
                emit35.emit()[0], emit36.emit36()[0]):
        for _, n in src:
            a, b, c, d, e, f = vals(n)
            if c >= 1 and d >= 1 and e >= 1 and f == 0:
                used.add((a, b))
    return used


AMAX, BMAX = 14, 8


def pack(used):
    """Greedy top-down packing of R with free (a,b) cells.

    R's cells at 3-depth 2: two 9-cells (1 and 3 mod 9), each with
    2-part B = one cell for every a >= 3 (the 8^ chain).  We walk each
    chain cell (a, 2) and, if that vector is used, split it (into two
    children (a+1,2)? no -- same 'a+1' collides with the chain's own
    next cell) -- so instead split 3-adically: cell (a,2) -> three
    cells (a,3), which may each be split further.  A cell is DONE when
    its vector is free and unclaimed; claim it.  Depth-limited."""
    claimed = set(used)
    plan = []

    def cover(a, b):
        if a > AMAX or b > BMAX:
            return False
        if (a, b) not in claimed:
            claimed.add((a, b))
            plan.append((a, b))
            return True
        # split ternary: three children share vector (a, b+1) -- they
        # need THREE distinct moduli with the same (a,b+1)... only one
        # available.  So cover one child by (a,b+1) and recurse on the
        # other two.  Equivalently binary split: two children (a+1,b).
        # try binary split first
        ok_bin = _split(a, b, 'bin')
        if ok_bin:
            return True
        return _split(a, b, 'ter')

    def _split(a, b, kind):
        snapshot = (set(claimed), list(plan))
        n, (da, db) = (2, (1, 0)) if kind == 'bin' else (3, (0, 1))
        for _ in range(n):
            if not cover(a + da, b + db):
                claimed.clear(); claimed.update(snapshot[0])
                plan[:] = snapshot[1]
                return False
        return True

    ok = True
    for cell3 in ('1mod9', '3mod9'):
        for a in range(3, AMAX + 1):   # the 8^ chain cells
            if not cover(a, 2):
                print(f"FAIL at {cell3} chain cell a={a}")
                ok = False
                break
        if not ok:
            break
    return ok, plan


if __name__ == '__main__':
    u = used_ab()
    print("used (a,b) vectors in context (c,d,e>=1, f=0):", sorted(u))
    free = [(a, b) for a in range(AMAX + 1) for b in range(2, BMAX + 1)
            if (a, b) not in u]
    print("free vectors in box:", free[:40], "..." if len(free) > 40 else "")
    ok, plan = pack(u)
    print("PACKING", "SUCCEEDED" if ok else "FAILED")
    if ok:
        print("plan (a,b) cells claimed:", plan)

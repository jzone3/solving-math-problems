"""Symbolic closure & verification layer for the Nielsen arrow DSL.

Materializing every arrow (n >= P-1 levels for multiplier prime P) explodes
with nesting.  Instead we verify the SYMBOLIC system, using Nielsen's
Section-3 finitization: an arrow q^ whose q-1 inputs are covered at every
level covers its whole cell once its leftover chain is closed by tail
classes P^t * M * q^i for a large fresh prime P.  Distinctness of the
completed (infinite-family) system reduces to finite checks:

  1. concrete (level-1) moduli pairwise distinct   [Ctx.take enforces]
  2. deep-copy families pairwise disjoint          [check_families]
  3. all moduli >= L, including first arrow levels [take + check below]
  4. no unfilled Hole cells                        [caller-declared]
  5. X cells (claimed covered elsewhere) ledgered for cross-check

A class taken under nested arrows q1,...,qk replicates with moduli
m * q1^e1 * ... * qk^ek (e >= 0).  We conservatively check the full
exponent grids of any two classes are disjoint:
  collide((m1,S1),(m2,S2)) iff stripping primes S1|S2 leaves equal cores
  and, for r in S1\\S2, v_r(m1) <= v_r(m2) (symmetrically for S2\\S1).
"""
from math import gcd

from arrow_dsl import Hole, subcell, qval


def _strip(m, primes):
    for q in primes:
        m //= q ** qval(m, q)
    return m


def collide(m1, s1, m2, s2):
    u = set(s1) | set(s2)
    if _strip(m1, u) != _strip(m2, u):
        return False
    for r in set(s1) - set(s2):
        if qval(m2, r) < qval(m1, r):
            return False
    for r in set(s2) - set(s1):
        if qval(m1, r) < qval(m2, r):
            return False
    return True


def finalize_symbolic(ctx):
    """Expand every pending arrow at level 1 only, under the enclosing
    arrow-prime set; deep levels are represented by the family grid and
    the leftover chains close via a fresh global multiplier prime."""
    errs = []
    while ctx.pending:
        rec = ctx.pending.pop(0)
        q, a, M = rec["q"], rec["a"], rec["M"]
        aset = frozenset(rec["aset"]) | {q}
        if M * q < ctx.L:
            errs.append(f"arrow {rec['path']}: first level {M * q} "
                        f"< L={ctx.L}")
        old = ctx.arrowset
        ctx.arrowset = aset
        for j, inp in enumerate(rec["inputs"], 1):
            if inp is None or (isinstance(inp, Hole) and not inp.name):
                errs.append(f"arrow {rec['path']} (q={q}, mod {M}) "
                            f"input {j} unfilled")
                continue
            sa, sm = subcell(a, M, q, j)
            try:
                inp.eval(ctx, sa, sm, f"{rec['path']}/sym{q}#{j}")
            except AssertionError as e:
                errs.append(str(e))
        ctx.arrowset = old
    return errs


def check_families(ctx):
    errs = []
    fams = [(m, s, p) for (m, s, p) in ctx.families]
    n = len(fams)
    for i in range(n):
        m1, s1, p1 = fams[i]
        if not s1:
            continue  # concrete-only classes handled by take()
        for j in range(n):
            if i == j:
                continue
            m2, s2, p2 = fams[j]
            if i > j and s2:
                continue  # symmetric pair already checked
            if collide(m1, s1, m2, s2):
                errs.append(f"family collision: ({m1},{sorted(s1)}) "
                            f"[{p1}] vs ({m2},{sorted(s2)}) [{p2}]")
    return errs


def _subtract(cells, b, K):
    """Remove class (b mod K) from a set of cells (a mod M)."""
    out = []
    for a, M in cells:
        g = gcd(M, K)
        if a % g != b % g:
            out.append((a, M))
            continue
        lcm = M // g * K
        k = lcm // M
        for i in range(k):
            c = (a + i * M) % lcm
            if c % K != b % K:
                out.append((c, lcm))
    return out


def check_xcells(ctx, covered):
    """Each X cell must be inside the union of fully-covered regions
    (concrete classes + closed arrow cells), and must not meet any
    still-open hole cell (holes puncture arrow-cell coverage)."""
    errs = []
    holecells = [c for cells in ctx.holes.values() for c in cells]
    for xa, xm, xpath in ctx.xcells:
        for ha, hm in holecells:
            g = gcd(xm, hm)
            if xa % g == ha % g:
                errs.append(f"x-cell {xa}%{xm} [{xpath}] meets open "
                            f"hole {ha}%{hm}")
        rem = [(xa, xm)]
        for b, K in covered:
            rem = _subtract(rem, b, K)
            if not rem:
                break
        if rem:
            errs.append(f"x-cell {xa}%{xm} [{xpath}] not covered; "
                        f"residual {rem[:4]}...")
    return errs


def symbolic_verify(ctx, expect_holes=(), regions=None):
    covered = ([(rec["a"] % rec["M"], rec["M"]) for rec in ctx.pending]
               if regions is None else list(regions))
    lines = finalize_symbolic(ctx)
    if regions is None:
        covered += list(ctx.out)
    lines += check_xcells(ctx, covered)
    bad = [h for h in sorted(ctx.holes) if h not in expect_holes]
    if bad:
        lines.append(f"UNFILLED holes: {bad}")
    lines += check_families(ctx)
    ok = not lines
    lines.append(f"classes(level-1): {len(ctx.out)}, "
                 f"under-arrow: {sum(1 for _, s, _ in ctx.families if s)}, "
                 f"x-cells: {len(ctx.xcells)}")
    return ok, lines

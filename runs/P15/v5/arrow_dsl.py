"""Executable semantics for Nielsen's arrow notation ("A covering system
whose smallest modulus is 40", Sections 2-3).

Cell = congruence class (a, M).  Branching a cell along prime q: the q
subcells a + t*M (mod q*M), t = 0..q-1, are ordered by the representative
rep in [1..q^(e+1)] of their residue mod q^(e+1) (where q^e || M, 0 -> q^(e+1)):
input j corresponds to the unique subcell with rep in ((j-1)q^e, j*q^e].
Verified against the paper's examples: 2( ,2(2( ,1), )) = 6 (mod 8);
3( ,2(1, ), ) = 5 (mod 6); Example 1 (3^(arrow)(1, 2^(arrow))).

Expressions:
  Hole(name)      empty input, recorded for later sections
  X()             input inherited/covered elsewhere (verified globally later)
  One(s=1)        cover cell with single class (a mod s*M)
  Mul(s, expr)    restrict nothing, but multiply modulus: "s . expr" is
                  expr evaluated with modulus scaled by s (e.g. 25 . 1)
                  -- implemented by One for the common "s . 1" case.
  Split(q, [inputs])   q(alpha_1..alpha_q)
  Arrow(q, [inputs], p=None, n=None)   q^arrow(alpha_1..alpha_{q-1});
        levels k=1..n cover inputs j=1..q-1 on windows 1..q-1, recursing
        into window q; final leftover closed with multiplier p:
        j (mod p) /\ leftover-cell-at-level(n+1-j), j = 1..p.

Ctx carries min modulus L and a global used-moduli registry; Arrow picks
(p, n) to keep every modulus fresh and >= L.
"""
from math import gcd


def crt(r1, m1, r2, m2):
    g = gcd(m1, m2)
    assert (r1 - r2) % g == 0, "incompatible crt"
    l = m1 // g * m2
    if m2 // g == 1:
        return r1 % l, l
    inv = pow(m1 // g, -1, m2 // g)
    x = (r1 + (m1 // g) * (((r2 - r1) // g) * inv % (m2 // g)) * g) % l
    return x, l


def _sieve(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\0\0"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = b"\0" * len(s[i * i::i])
    return [i for i in range(2, n + 1) if s[i]]


PRIMES = _sieve(300000)
RESERVE = [p for p in PRIMES if p > 200]


def qval(M, q):
    e = 0
    while M % q == 0:
        M //= q
        e += 1
    return e


def subcell(a, M, q, j):
    """input j (1-based) of branching cell (a mod M) along q."""
    e = qval(M, q)
    qe1 = q ** (e + 1)
    lo, hi = (j - 1) * q ** e, j * q ** e
    for t in range(q):
        x = (a + t * M) % qe1
        rep = x if x != 0 else qe1
        if lo < rep <= hi:
            return (a + t * M) % (q * M), q * M
    raise AssertionError("no subcell in window")


class Ctx:
    def __init__(self, L):
        self.L = L
        self.used = set()
        self.out = []
        self.holes = {}
        self.xcells = []   # cells claimed covered elsewhere (checked later)
        self.pending = []  # deferred arrows, closed at finalize()
        self.named = {}    # arrow name -> pending record
        self.paths = {}    # modulus -> path (debug)
        self.reserved = {}  # integer -> count held for pending arrows
        self.fin_calls = 0

    def finisher(self, a, M, path="", depth=0):
        """Close cell (a mod M) unconditionally with fresh reserve-prime
        2-chains (engine-E mechanism; replaces Nielsen's shared-p arrow
        tails, trading modulus thrift for collision-freedom)."""
        self.fin_calls += 1
        assert depth <= 300, f"finisher depth M={M} used={M in self.used} res={M in self.reserved} path={path}"
        if M >= self.L and M not in self.used and M not in self.reserved:
            self.take(a, M, f"{path}/fin")
            return
        for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59):
            for p in PRIMES[:200]:
                if M % p == 0 or p == q:
                    continue
                K = max(p - 1, 1)
                while p * M * q ** (K + 1 - p) < self.L:
                    K += 1
                lev = [M * q ** k for k in range(1, K + 1)]
                tail = [p * M * q ** (K + 1 - j) for j in range(1, p + 1)]
                if any(m in self.used or m in self.reserved
                       for m in lev) or \
                        any(m in self.used or m in self.reserved
                            for m in tail):
                    continue
                for m in lev + tail:  # guard from nested finishers
                    self.reserved[m] = self.reserved.get(m, 0) + 1
                ca, cm = a, M
                cells = [(ca, cm)]
                for k in range(1, K + 1):
                    for w in range(1, q):
                        sa, sm = subcell(ca, cm, q, w)
                        if w == 1:
                            self.take(sa, sm, f"{path}/fin{q}l{k}")
                        else:
                            self.finisher(sa, sm, f"{path}/w{w}",
                                          depth + 1)
                    ca, cm = subcell(ca, cm, q, q)
                    cells.append((ca, cm))
                for j in range(1, p + 1):
                    la, lm = cells[K + 1 - j]
                    r, mm = crt(la, lm, j % p, p)
                    self.take(r, mm, f"{path}/fin{p}t{j}")
                for m in lev + tail:
                    c = self.reserved.get(m, 0) - 1
                    if c:
                        self.reserved[m] = c
                    else:
                        self.reserved.pop(m, None)
                return
        diag = []
        for q in (2, 3, 5, 7):
            l1 = M * q
            diag.append((q, l1 in self.used, self.reserved.get(l1, 0),
                         self.paths.get(l1)))
        raise RuntimeError(
            f"finisher supply exhausted M={M} depth={depth} "
            f"path={path} diag={diag}")

    def take(self, a, M, path=""):
        assert M >= self.L, f"modulus {M} < L={self.L} at {path}"
        assert M not in self.used, \
            f"duplicate modulus {M}: {path} vs {self.paths.get(M)}"
        self.used.add(M)
        self.paths[M] = path
        self.out.append((a % M, M))


class Expr:
    def eval(self, ctx, a, M, path=""):
        raise NotImplementedError


class Hole(Expr):
    def __init__(self, name=None):
        self.name = name

    def eval(self, ctx, a, M, path=""):
        ctx.holes.setdefault(self.name or path, []).append((a % M, M))


class X(Expr):
    def eval(self, ctx, a, M, path=""):
        ctx.xcells.append((a % M, M, path))


class One(Expr):
    def __init__(self, s=1):
        self.s = s

    def eval(self, ctx, a, M, path=""):
        ctx.take(a % (self.s * M), self.s * M, path)


class Split(Expr):
    def __init__(self, q, inputs):
        assert len(inputs) == q, f"Split({q}) needs {q} inputs"
        self.q, self.inputs = q, inputs

    def eval(self, ctx, a, M, path=""):
        for j, inp in enumerate(self.inputs, 1):
            if inp is None:
                continue
            sa, sm = subcell(a, M, self.q, j)
            inp.eval(ctx, sa, sm, f"{path}/{self.q}#{j}")


class Arrow(Expr):
    def __init__(self, q, inputs, p=None, n=None, name=None):
        assert len(inputs) == q - 1, f"Arrow({q}) needs {q-1} inputs"
        self.q, self.inputs, self.p, self.n = q, inputs, p, n
        self.name = name

    def _pick(self, ctx, a, M, mults):
        q = self.q
        for p in mults:
            if gcd(p, q * M) != 1:
                continue
            n = max(p - 1, 1)
            while M * q ** n < ctx.L:
                n += 1
            # level moduli are forced (M*q^k); a collision there means the
            # transcription itself is wrong -- fail loudly
            for k in range(1, n + 1):
                if M * q ** k in ctx.used:
                    raise RuntimeError(
                        f"level modulus {M}*{q}^{k} already used "
                        f"({q}-arrow at mod {M})")
            for _ in range(400):
                if M * q ** n in ctx.used:
                    raise RuntimeError(
                        f"level modulus {M}*{q}^{n} already used "
                        f"({q}-arrow at mod {M})")
                tail = [p * M * q ** (n + 1 - j) for j in range(1, p + 1)]
                mods = [M * q ** k for k in range(1, n + 1)] + tail
                if all(m >= ctx.L for m in mods) and \
                        all(m not in ctx.used for m in tail) and \
                        len(set(mods)) == len(mods):
                    return p, n
                n += 1
        raise RuntimeError(f"no (p,n) for {q}-arrow at mod {M}")

    def eval(self, ctx, a, M, path=""):
        if self.p is not None and self.n is not None:
            _close(ctx, self.q, list(self.inputs), a, M, path,
                   self.p, self.n)
            return
        rec = {"q": self.q, "inputs": list(self.inputs), "a": a, "M": M,
               "path": path, "p": self.p, "n": self.n}
        ctx.pending.append(rec)
        if self.name:
            ctx.named[self.name] = rec


def _structural(inputs):
    return any(inp is not None and not isinstance(inp, (One, X, Hole))
               for inp in inputs)


def _close(ctx, q, inputs, a, M, path, p=None, n=None):
    if p is not None and n is not None:
        # explicit (p, n): Nielsen-style shared tail (used in tests)
        ca, cm = a, M
        leftovers = [(ca, cm)]
        for k in range(1, n + 1):
            for j, inp in enumerate(inputs, 1):
                if inp is None:
                    continue
                sa, sm = subcell(ca, cm, q, j)
                inp.eval(ctx, sa, sm, f"{path}/{q}^{k}#{j}")
            ca, cm = subcell(ca, cm, q, q)
            leftovers.append((ca, cm))
        for j in range(1, p + 1):
            la, lm = leftovers[n + 1 - j]
            r, m = crt(la, lm, j % p, p)
            ctx.take(r, m, f"{path}/tail{j}")
        return
    # deferred closure: minimal fresh level depth, then finisher
    n = 1
    while M * q ** n < ctx.L or M * q ** n in ctx.used or \
            (n < 2 and _structural(inputs)):
        n += 1
        assert n < 500
    ca, cm = a, M
    for k in range(1, n + 1):
        for j, inp in enumerate(inputs, 1):
            if inp is None:
                continue
            sa, sm = subcell(ca, cm, q, j)
            inp.eval(ctx, sa, sm, f"{path}/{q}^{k}#{j}")
        ca, cm = subcell(ca, cm, q, q)
    ctx.finisher(ca, cm, f"{path}/close")


def _reserve(ctx, rec, sign=1):
    m = rec["M"]
    for _ in range(8):
        m *= rec["q"]
        if m > 10 ** 40:
            break
        c = ctx.reserved.get(m, 0) + sign
        if c:
            ctx.reserved[m] = c
        else:
            ctx.reserved.pop(m, None)


def finalize(ctx):
    """Close all deferred arrows (multipliers made explicit 'at a later
    stage', per the paper).  Closing may spawn nested pending arrows."""
    for rec in ctx.pending:
        _reserve(ctx, rec)
    guard = 0
    while ctx.pending:
        guard += 1
        assert guard < 10 ** 6
        # structural arrows first: their level moduli are small forced
        # integers; all-One arrows close later
        idx = next((i for i, r in enumerate(ctx.pending)
                    if _structural(r["inputs"])), 0)
        rec = ctx.pending.pop(idx)
        _reserve(ctx, rec, -1)
        npend = len(ctx.pending)
        _close(ctx, rec["q"], rec["inputs"], rec["a"], rec["M"],
               rec["path"], rec["p"], rec["n"])
        for spawned in ctx.pending[npend:]:
            _reserve(ctx, spawned)


def fill_arrow(ctx, name, j, expr):
    """Replace input j of a named deferred arrow (Nielsen's tower-sharing:
    later sections fill inputs of arrows declared earlier)."""
    rec = ctx.named[name]
    old = rec["inputs"][j - 1]
    assert old is None or isinstance(old, (Hole, X)), \
        f"input {j} of {name} already filled"
    rec["inputs"][j - 1] = expr


def measure(cells):
    from fractions import Fraction
    return sum(Fraction(1, M) for _, M in cells)

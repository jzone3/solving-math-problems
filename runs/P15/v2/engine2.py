#!/usr/bin/env python3
"""P15 V2 engine v2: stage-based CRT-layered set cover with overlap.

State after stage i: tower modulus M_i = prod p^e_p, uncovered set U_i of
residues mod M_i, set of used modulus values, list of congruences.

Step with prime p: M' = M*p; children of each u: u + k*M, k=0..p-1.
Then place congruences (a mod v), v a divisor of M' with T <= v <= Vmax and
value v unused; each kills every child ≡ a (mod v). Greedy: sweep candidate
values v ascending, choose residue a among uncovered children maximizing kills,
accept if kills >= efficiency threshold.

U is stored as a numpy matrix of residues modulo each prime power in the tower
(CRT coordinates), so M can exceed 2^63. u mod v is reconstructed vectorially
for v <= Vmax via CRT.
"""
import argparse
import sys
import time
import numpy as np


def primes_upto(n):
    sieve = np.ones(n + 1, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i:: i] = False
    return [int(x) for x in np.nonzero(sieve)[0]]


class State:
    def __init__(self, T, vmax):
        self.T = T
        self.vmax = vmax
        self.primes = []          # tower primes in order of first use
        self.exps = {}            # p -> exponent in M
        self.cols = {}            # p -> np.array (residue of each u mod p^e), int64
        self.n = 1                # |U|
        self.used = set()
        self.congs = []           # (a, v) with a determined via CRT coords at kill time
        self.M_log = 0.0

    def M_divisors(self, extra_p=None):
        """Divisors v of M (optionally M*extra_p) with T <= v <= vmax."""
        pe = dict(self.exps)
        if extra_p is not None:
            pe[extra_p] = pe.get(extra_p, 0) + 1
        items = sorted(pe.items())
        out = []

        def dfs(i, val):
            if val > self.vmax:
                return
            if i == len(items):
                if val >= self.T:
                    out.append(val)
                return
            p, e = items[i]
            v = val
            for _ in range(e + 1):
                dfs(i + 1, v)
                v *= p
                if v > self.vmax:
                    break
        dfs(0, 1)
        return sorted(out)

    def residues_mod(self, v):
        """Vector of u mod v for all u in U (v | M, v <= vmax). CRT combine."""
        r = np.zeros(self.n, dtype=np.int64)
        rem = v
        parts = []
        for p in self.primes:
            e = 0
            q = 1
            while rem % p == 0:
                rem //= p
                e += 1
                q *= p
            if e:
                pe_full = p ** self.exps[p]
                parts.append((q, self.cols[p] % q))
        assert rem == 1
        # CRT: combine parts
        m = 1
        for q, res in parts:
            if m == 1:
                r = res.astype(np.int64).copy()
                m = q
            else:
                # r' ≡ r (mod m), ≡ res (mod q)
                inv = pow(m % q, -1, q)
                t = ((res - r) % q) * inv % q
                r = r + m * t
                m *= q
        return r % v

    def step(self, p, eff=0.5, min_kill=1, verbose=True):
        """Advance tower by one factor of p, then greedy-place values."""
        t0 = time.time()
        e_old = self.exps.get(p, 0)
        q_old = p ** e_old
        q_new = q_old * p
        # expand children
        n0 = self.n
        idx = np.repeat(np.arange(n0), p)
        for pp in self.primes:
            if pp != p:
                self.cols[pp] = self.cols[pp][idx]
        k = np.tile(np.arange(p, dtype=np.int64), n0)
        if p in self.exps:
            self.cols[p] = self.cols[p][idx] + k * q_old
            self.exps[p] = e_old + 1
        else:
            self.primes.append(p)
            self.cols[p] = k
            self.exps[p] = 1
        self.n = n0 * p
        self.M_log += np.log(p)
        # candidate fresh values: divisors of new M in [T, vmax], unused
        vals = [v for v in self.M_divisors() if v not in self.used]
        alive = np.ones(self.n, dtype=bool)
        kills_total = 0
        used_here = 0
        for v in vals:
            if not alive.any():
                break
            r = self.residues_mod(v)
            ra = r[alive]
            if ra.size == 0:
                break
            cnt = np.bincount(ra, minlength=v)
            a = int(cnt.argmax())
            c = int(cnt[a])
            # efficiency: expected count per class is alive/v
            if c < min_kill or (c < eff * alive.sum() / v and c < min_kill + 1):
                continue
            self.used.add(v)
            self.congs.append((self._lift_residue(v, a), v))
            alive &= ~(r == a)
            kills_total += c
            used_here += 1
        # compact
        for pp in self.primes:
            self.cols[pp] = self.cols[pp][alive]
        self.n = int(alive.sum())
        if verbose:
            print(f"  step p={p}: |U| {n0} -> {self.n} "
                  f"(x{p} then -{kills_total} via {used_here} values, "
                  f"supply={len(vals)}) t={time.time()-t0:.1f}s", flush=True)
        return self.n

    def _lift_residue(self, v, a):
        return a  # residue a mod v is already the congruence

    def finished(self):
        return self.n == 0


def run(T, vmax, plan, eff, out=None, verbose=True):
    st = State(T, vmax)
    for p in plan:
        st.step(p, eff=eff, verbose=verbose)
        if st.finished():
            break
    print(f"T={T}: final |U|={st.n}, congs={len(st.congs)}, "
          f"log10(M)={st.M_log/np.log(10):.1f}")
    if st.finished() and out:
        with open(out, "w") as f:
            f.write(f"# T={T} vmax={vmax} plan={plan[:len(plan)]}\n")
            for a, v in st.congs:
                f.write(f"{a} {v}\n")
        print(f"wrote {len(st.congs)} congruences -> {out}")
    return st


def copy_state(st):
    import copy
    s2 = State(st.T, st.vmax)
    s2.primes = list(st.primes)
    s2.exps = dict(st.exps)
    s2.cols = {p: st.cols[p].copy() for p in st.cols}
    s2.n = st.n
    s2.used = set(st.used)
    s2.congs = list(st.congs)
    s2.M_log = st.M_log
    return s2


def auto_run(T, vmax, caps, eff, out=None, max_steps=60, sim_limit=3_000_000,
             verbose=True):
    """Adaptive plan: at each step, simulate all candidate primes and take the
    one minimizing |U_after| (ties -> smaller p). caps: dict p -> max exponent."""
    st = State(T, vmax)
    for stepno in range(max_steps):
        cands = [p for p in sorted(caps) if st.exps.get(p, 0) < caps[p]]
        best = None
        for p in cands:
            if st.n * p > sim_limit:
                continue
            s2 = copy_state(st)
            s2.step(p, eff=eff, verbose=False)
            score = (s2.n, p)
            if best is None or score < best[0]:
                best = (score, p, s2)
        if best is None:
            print(f"no candidate fits sim_limit at |U|={st.n}; aborting")
            break
        _, p, st = best
        if verbose:
            print(f"[{stepno}] chose p={p}: |U|={st.n} congs={len(st.congs)} "
                  f"exps={ {q: st.exps[q] for q in st.primes} }", flush=True)
        if st.finished():
            break
    print(f"T={T}: final |U|={st.n}, congs={len(st.congs)}, "
          f"log10(M)={st.M_log/np.log(10):.1f}")
    if st.finished() and out:
        with open(out, "w") as f:
            f.write(f"# T={T} vmax={vmax} auto caps={caps}\n")
            for a, v in st.congs:
                f.write(f"{a} {v}\n")
        print(f"wrote {len(st.congs)} congruences -> {out}")
    return st


def heuristic_run(T, vmax, caps, eff, out=None, max_steps=80,
                  hard_limit=60_000_000, verbose=True):
    """In-place run; next prime p maximizes the *fresh value supply reciprocal
    sum* of M*p (upper bound on measure killable this step), normalized by the
    growth factor p. Endgame: any supply >= |U| finishes greedily."""
    st = State(T, vmax)
    for stepno in range(max_steps):
        cands = [p for p in sorted(caps) if st.exps.get(p, 0) < caps[p]
                 and st.n * p <= hard_limit]
        if not cands:
            print(f"no candidate under hard_limit at |U|={st.n}; aborting")
            break
        best_p, best_score = None, None
        for p in cands:
            vals = [v for v in st.M_divisors(extra_p=p) if v not in st.used]
            recip = sum(1.0 / v for v in vals)
            # measure killable per unit of log-growth
            score = recip / np.log(p)
            if best_score is None or score > best_score:
                best_p, best_score = p, score
        st.step(best_p, eff=eff, verbose=verbose)
        if verbose:
            print(f"[{stepno}] p={best_p} |U|={st.n} congs={len(st.congs)} "
                  f"exps={ {q: st.exps[q] for q in st.primes} }", flush=True)
        if st.finished():
            break
    print(f"T={T}: final |U|={st.n}, congs={len(st.congs)}, "
          f"log10(M)={st.M_log/np.log(10):.1f}")
    if st.finished() and out:
        with open(out, "w") as f:
            f.write(f"# T={T} vmax={vmax} heuristic caps={caps}\n")
            for a, v in st.congs:
                f.write(f"{a} {v}\n")
        print(f"wrote {len(st.congs)} congruences -> {out}")
    return st


def parse_plan(s):
    """e.g. '2^6,3^4,5^2,7,11,13' -> [2,2,2,2,2,2,3,3,3,3,5,5,7,11,13]"""
    plan = []
    for tok in s.split(","):
        if "^" in tok:
            b, e = tok.split("^")
            plan += [int(b)] * int(e)
        else:
            plan.append(int(tok))
    return plan


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("--vmax", type=int, default=1_000_000)
    ap.add_argument("--plan")
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--heur", action="store_true")
    ap.add_argument("--hard-limit", type=int, default=60_000_000)
    ap.add_argument("--maxprime", type=int, default=101)
    ap.add_argument("--sim-limit", type=int, default=3_000_000)
    ap.add_argument("--max-steps", type=int, default=60)
    ap.add_argument("--eff", type=float, default=0.5)
    ap.add_argument("-o", "--out")
    args = ap.parse_args()
    caps = {}
    for p in primes_upto(args.maxprime):
        caps[p] = 10 if p == 2 else 6 if p == 3 else 4 if p <= 7 else 2
    if args.heur:
        heuristic_run(args.T, args.vmax, caps, args.eff, args.out,
                      max_steps=args.max_steps, hard_limit=args.hard_limit)
    elif args.auto:
        auto_run(args.T, args.vmax, caps, args.eff, args.out,
                 max_steps=args.max_steps, sim_limit=args.sim_limit)
    else:
        run(args.T, args.vmax, parse_plan(args.plan), args.eff, args.out)

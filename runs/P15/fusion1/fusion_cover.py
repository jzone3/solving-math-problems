#!/usr/bin/env python3
"""Experiment A: exact CRT greedy followed by fresh-prime residual closure."""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLKIT = ROOT / "toolkit"
sys.path.insert(0, str(TOOLKIT))
from fc_tree2 import Builder, parse_fact  # noqa: E402
from engine_e import Builder as EBuilder, TAIL_PRIMES, crt  # noqa: E402


def reserve_primes(nmax, used):
    return [p for p in TAIL_PRIMES if p > 100 and p <= nmax and p not in used]


def close_residual(greedy, minimum, max_mod, prime_max, log):
    """Close each exact residual coset, isolating repeated M values.

    The first cell at a given M uses Engine E's ordinary 2-chain finisher.
    Further cells at the same M are split into children modulo a private odd
    prime q, and each child is finitized independently.  Thus no bare
    M*2^k ladder is shared by two original residual cells.
    """
    out = list(greedy.chosen)
    used = {n for _, n in out}
    caps = {p: 1000 for p in TAIL_PRIMES if p <= 50000}
    fin = EBuilder(minimum, caps, max_mod=max_mod, max_depth=250)
    fin.used = set(used)
    fin.by_mod = {n: a for a, n in out}
    fin.out = list(out)
    seen_m = set()
    qs = iter(reserve_primes(prime_max, used))
    def prefixed(a, m, q, depth=0):
        if depth > 250:
            raise RuntimeError("prefix depth")
        if m >= minimum and m not in fin.used:
            fin.take(a, m, [])
            return
        for p in TAIL_PRIMES:
            if p <= 199 or p == q or m % p == 0:
                continue
            K = max(p - 1, 1)
            while p * m * q ** (K + 1 - p) < minimum:
                K += 1
            tail = [p * m * q ** (K + 1 - j)
                    for j in range(1, p + 1)]
            if m * q ** K * p > max_mod or any(x in fin.used for x in tail):
                continue
            for j, mm in enumerate(tail, 1):
                anc = m * q ** (K + 1 - j)
                fin.take(crt(a % anc, anc, j % p, p), mm, [])
            for k in range(1, K + 1):
                step = m * q ** (k - 1)
                mod_k = m * q ** k
                for i in range(1, q):
                    prefixed(a + i * step, mod_k, q, depth + 1)
            return
        raise RuntimeError("prefixed finisher supply")
    cells = [(int(r), int(m)) for m, rs in greedy.frags.items()
             for r in rs]
    cells.sort(key=lambda x: (x[1], x[0]))
    t0 = time.time()
    for i, (a, m) in enumerate(cells, 1):
        try:
            if m not in seen_m:
                before = len(fin.out)
                fin.finisher(a, m)
                seen_m.add(m)
            else:
                q = next(qs)
                if m % q == 0:
                    raise RuntimeError("reserve prime divides residual M")
                prefixed(a, m, q)
                log.append("same-M M=%d prefix=%d" % (m, q))
        except Exception as exc:
            log.append("FAIL residual #%d a=%d M=%d: %s" % (i, a, m, exc))
            return None, cells, i
        if i % 25 == 0:
            print("  residual %d/%d, output=%d, M=%d, %.1fs" %
                  (i, len(cells), len(fin.out), m, time.time() - t0),
                  flush=True)
    return fin.out, cells, len(cells)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("M", type=int)
    ap.add_argument("--fact", default="2^9,3^6,5^4,7^3,11^2,13,17,19")
    ap.add_argument("--greedy-seconds", type=float, default=300)
    ap.add_argument("--prime-max", type=int, default=200000)
    ap.add_argument("--max-mod", type=int, default=10**80)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    pps = parse_fact(args.fact)
    b = Builder(args.M, pps)
    print("FUSION M=%d N=%d divisors=%d reciprocal=%.6f" %
          (args.M, b.N, len(b.mods), sum(1.0 / n for n in b.mods)),
          flush=True)
    t0 = time.time()
    ok = b.run(args.greedy_seconds)
    print("GREEDY ok=%s chosen=%d mass=%.12g residual=%d elapsed=%.1fs" %
          (ok, len(b.chosen), b.mass(), b.nfrags(), time.time() - t0),
          flush=True)
    if not b.frags or not any(len(v) for v in b.frags.values()):
        congs = sorted(b.chosen, key=lambda x: x[1])
    else:
        notes = []
        congs, cells, done = close_residual(
            b, args.M, args.max_mod, args.prime_max, notes)
        print("FINISH residual=%d processed=%d output=%s elapsed=%.1fs" %
              (len(cells), done, "success" if congs is not None else "FAIL",
               time.time() - t0), flush=True)
        for line in notes[-10:]:
            print("  %s" % line, flush=True)
        if congs is None:
            partial = Path(args.out or
                           ("partial_m%d.json" % args.M))
            partial.write_text(json.dumps(
                {"minmod": args.M, "partial": True,
                 "congruences": [[int(a), int(n)] for a, n in b.chosen]}))
            return 1
        congs = sorted(congs, key=lambda x: x[1])
    fn = Path(args.out or ("witness_m%d.json" % args.M))
    fn.write_text(json.dumps(
        {"minmod": args.M,
         "congruences": [[int(a), int(n)] for a, n in congs]}))
    print("SUCCESS M=%d congruences=%d min=%d max=%d file=%s total=%.1fs" %
          (args.M, len(congs), min(n for _, n in congs),
           max(n for _, n in congs), fn, time.time() - t0), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

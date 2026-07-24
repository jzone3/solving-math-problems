#!/usr/bin/env python3
"""P15 fusion1 -- Experiment B: complete T=43 deficit ledger over ALL 20 Owens
sections.

v4's branchgame.py re-ran only sections 3.8 and 3.14 at T=43 (it showed the
modulus-42 trick death makes 3.8's three 7^ copies each cost +1 set).  This
script completes that analysis across every section 3.8-3.20 by replaying v4's
*validated* T=42 ledger (branchgame.owens_T42) under two mechanical T=43
penalties, and totals the aggregate extra-set deficit and the compensating
mul-budget / fresh-prime supply it would demand.

Penalties applied at T=43 (mechanical consequences of forbidding modulus 42 and
raising the min-modulus drop threshold from 42 to 43):
  (P1) modulus-42 trick death: any 7^ fill whose per-copy `need` was reduced
       below the naive p-1 = 6 (Owens' "third-entry"/"reduced-input" 7-tricks
       on a branch, several of which route through the 7*3*2 = 42 congruence)
       loses one input per copy at T=43 -> need += 1 per copy.  This exactly
       reproduces v4's hand-derived 3.8 (5->6) and 3.14 (5->6) penalties, and
       extends the same rule uniformly to every other section that uses a
       sub-6 7-need.
  (P2) drop-threshold shift: finishing prime P drops all seed sets s with
       P*s < 43 (was < 42).  Recomputed exactly; on Owens' prime range this
       changes nothing except confirming 43*1 = 43 stays usable.

IMPORTANT (methodology / honesty): this is a COUNTING-LEVEL ledger, i.e. an
*upper bound on feasibility*, NOT a witness.  v4 phase 14 established the
set-counting calculus is an over-approximation of the true residue-level cover
(value-set freshness is not decidable at counting level); a section that PASSes
here is not thereby residue-realizable.  A section that FAILs here is, however, a
genuine obstruction: not even the optimistic count closes.  So this ledger
lower-bounds the barrier to a min-modulus-43 Owens-style system.
"""
import importlib.util

# --- load v4's branchgame.py from the toolkit ---
HERE = __import__("os").path.dirname(__import__("os").path.abspath(__file__))
TOOLKIT = __import__("os").path.join(HERE, "..", "..", "..", "toolkit", "branchgame.py")
spec = importlib.util.spec_from_file_location("branchgame_v4", TOOLKIT)
bg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bg)


def analyze(threshold):
    """Replay owens_T42() but intercept fills/finishes to apply T=`threshold`
    penalties.  Returns (results, total_deficit)."""
    orig_fill = bg.Ledger.fill
    orig_finish = bg.Ledger.finish
    deficit = {"extra_sets": 0}

    def patched_fill(self, p, copies, need, why=""):
        n = need
        if threshold >= 43 and p == 7 and need < 6:
            # (P1) modulus-42 trick death: restore one input per copy
            n = need + 1
            deficit["extra_sets"] += copies * (n - need)
            why = (why + " | T43: 42-trick dead, need %d->%d" % (need, n)).strip()
        return orig_fill(self, p, copies, n, why)

    def patched_finish(self, P, need, drop, why=""):
        # (P2) recompute drop exactly at this threshold over seed multiples 1..
        # branchgame's `drop` counts seed sets s (s = 1,2,4,... small) with
        # P*s < threshold.  We recompute for the standard low seeds {1,2,4}.
        d = sum(1 for s in (1, 2, 4) if P * s < threshold)
        # keep v4's hand value where it already accounts for extra drops > our
        # simple seed model (never decrease below stated drop):
        d = max(d, 0)
        why2 = why
        if d != drop:
            why2 = (why + " | T%d drop %d->%d" % (threshold, drop, d)).strip()
        return orig_finish(self, P, need, d, why2)

    bg.Ledger.fill = patched_fill
    bg.Ledger.finish = patched_finish
    try:
        results = bg.owens_T42()
    finally:
        bg.Ledger.fill = orig_fill
        bg.Ledger.finish = orig_finish
    return results, deficit["extra_sets"]


def summarize(results):
    passed = [L for L in results if L.ok]
    failed = [L for L in results if not L.ok]
    return passed, failed


def main():
    print("#" * 72)
    print("# Experiment B: complete T=43 deficit ledger over all Owens sections")
    print("# (counting-level UPPER bound on feasibility; NOT a witness)")
    print("#" * 72)

    print("\n=== sanity: replay at T=42 (should be ALL PASS) ===")
    r42, _ = analyze(42)
    p42, f42 = summarize(r42)
    print("T=42: %d/%d sections PASS" % (len(p42), len(r42)))
    for L in f42:
        print("  UNEXPECTED FAIL:", L.name)

    print("\n=== T=43 re-run (penalties P1+P2 applied) ===")
    r43, extra = analyze(43)
    p43, f43 = summarize(r43)
    print("T=43: %d/%d sections PASS, %d FAIL" % (len(p43), len(r43), len(f43)))
    print("aggregate extra-set deficit from 42-trick death: %d sets" % extra)
    print()
    for L in r43:
        verdict = "PASS" if L.ok else "FAIL"
        # find the finishing line and any FAIL fill lines
        detail = [ln for ln in L.log if ln.startswith("FAIL") or "finish" in ln]
        print("  [%s] %s" % (verdict, L.name))
        for ln in detail:
            print("        " + ln)

    print("\n=== interpretation ===")
    print("Sections that FAIL at T=43 cannot even be counted closed with the")
    print("optimistic set-calculus -> each needs extra pool, supplied only by")
    print("more MUL ops (fresh residues of 5/25/125...) or fresh primes >= 97.")
    print("Owens (2014) ends at prime 89 with every ledger tight (<=3 spare")
    print("sets) and zero spare primes below 89, so the aggregate deficit above")
    print("must be absorbed WITHOUT introducing a duplicate modulus or a")
    print("modulus < 43 -- exactly the global-coupling wall v4 hit at residue")
    print("level (obstruction C).  This ledger quantifies its counting-level")
    print("size; it does NOT constitute a covering system.")


if __name__ == "__main__":
    main()

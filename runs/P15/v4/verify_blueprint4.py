#!/usr/bin/env python3
"""
P15 V4: consolidated independent replay of BLUEPRINT v4 (T=43).

This is NOT a covering-system witness verifier (no residue-level system
is claimed).  It independently re-runs, from one entry point, every
machine-checked component of blueprint v4 and prints PASS only if all
components succeed:

  1. blueprint43d.py  - all 13 T=43 counting ledgers at true mint costs;
  2. blueprint43b.py  - the re-aim lemma (exact cover of the dead
                        42-cell over lcm 504; usage/free classification);
  3. blueprint43c.py  - explicit modulus freshness of sec 3.8's odd-5
                        mints (zero collisions to 10^6);
  4. sections43.py    - global stratum assignment for all 7 penalized
                        sections (+ 5 routing side conditions);
  5. spares43.py      - freshness of the 4 spare-set instantiations on
                        the relocated cells {84,126,168,504}.

Remaining open burden (not checked, not claimed): residue-level
emission of the integrated system + end-to-end coverage verification.
"""
import io
import sys
import importlib.util


def run(path):
    spec = importlib.util.spec_from_file_location(path.rstrip(".py"), path)
    mod = importlib.util.module_from_spec(spec)
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        spec.loader.exec_module(mod)
        if hasattr(mod, "main"):
            pass  # modules run at import (their __main__ guards vary)
    finally:
        sys.stdout = old
    return buf.getvalue()


def main():
    checks = [
        ("ledgers", "blueprint43d.py",
         lambda o: "ALL LEDGERS PASS" in o and "FAIL" not in o),
        ("re-aim", "blueprint43b.py",
         lambda o: "FAIL" not in o and "exact" in o.lower() or
                   "PASS" in o and "FAIL" not in o),
        ("sec3.8 mints", "blueprint43c.py",
         lambda o: "PASS" in o and "FAIL" not in o),
        ("strata", "sections43.py",
         lambda o: "CONSISTENT" in o and "FAIL" not in o),
        ("spares", "spares43.py",
         lambda o: "discharged" in o and "FAIL" not in o),
    ]
    all_ok = True
    for name, path, pred in checks:
        # scripts with __main__ guards: execute their entry explicitly
        out = run_with_main(path)
        ok = pred(out)
        all_ok &= ok
        print(f"[{name:12s}] {path:20s} {'PASS' if ok else 'FAIL'}")
    print()
    if all_ok:
        print("BLUEPRINT v4 REPLAY: PASS (counting + stratum level; "
              "residue-level emission remains open)")
    else:
        print("BLUEPRINT v4 REPLAY: FAIL")
        sys.exit(1)


def run_with_main(path):
    src = open(path).read()
    src = src.replace('if __name__ == "__main__":', "if True:")
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    g = {"__name__": path, "__file__": path}
    try:
        exec(compile(src, path, "exec"), g)
    finally:
        sys.stdout = old
    return buf.getvalue()


if __name__ == "__main__":
    main()

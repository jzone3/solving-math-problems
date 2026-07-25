#!/usr/bin/env python3
"""Run all independent verifiers on the saved P15 witnesses.

The verify_sieve verifier requires every modulus to divide the witness LCM
N; that condition holds for these divisor-based witnesses.
"""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WITNESS_DIR = Path(__file__).resolve().parent
VERIFIERS = (
    ("v1", ROOT / "toolkit" / "verify_v1.py"),
    ("subtract", ROOT / "toolkit" / "verify_subtract.py"),
    ("sieve", ROOT / "toolkit" / "verify_sieve.py"),
)


def final_line(output):
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[-1] if lines else "<no output>"


def run_verifier(verifier, witness):
    proc = subprocess.run(
        [sys.executable, str(verifier), str(witness)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return final_line(proc.stdout), proc.returncode


def main():
    rows = []
    all_ok = True
    for m in range(3, 17):
        witness = WITNESS_DIR / f"witness_m{m}.json"
        if not witness.exists():
            continue
        with witness.open() as f:
            data = json.load(f)
        count = len(data["congruences"])
        results = {}
        for name, verifier in VERIFIERS:
            line, code = run_verifier(verifier, witness)
            results[name] = f"{line} (exit {code})"
            all_ok &= code == 0 and line.startswith("PASS:")
        rows.append((m, count, results))

    print("m | congruence count | v1 | subtract | sieve")
    print("--|------------------|----|----------|------")
    for m, count, results in rows:
        print("%d | %d | %s | %s | %s" %
              (m, count, results["v1"], results["subtract"],
               results["sieve"]))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

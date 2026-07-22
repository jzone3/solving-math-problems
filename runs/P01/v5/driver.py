#!/usr/bin/env python3
"""Grow-and-polish driver: takes best states from annealer logs, grows them n -> n+1
by splitting a chord through a freshly inserted cycle vertex, then polishes with the
C annealer in seeded (resume) mode. Escalates progressively.

Usage: driver.py <n> <chords...as "a-b" tokens or log line> --out prefix
Mostly used programmatically via grow_state().
"""
import re, random, subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
ANNEAL = os.path.join(HERE, "anneal2")

def parse_state(text):
    n = int(re.search(r"n=(\d+)", text).group(1))
    chords = [(int(a), int(b)) for a, b in re.findall(r"(\d+)-(\d+)", text.split("chords:")[1])]
    return n, chords

def grow_state(n, chords, rng):
    """Insert new vertex n between n-1 and 0 on the cycle; split a random chord (a,b)
    into (a,n),(n,b). New chords must not be cycle edges: a,b not in {n-1, 0} -> for
    new vertex n, cycle nbrs are n-1 and 0."""
    for _ in range(200):
        a, b = chords[rng.randrange(len(chords))]
        if a in (0, n - 1) or b in (0, n - 1):
            continue
        newch = [c for c in chords if c != (a, b)] + [(a, n), (b, n)]
        return n + 1, newch
    return None

def write_statefile(path, chords):
    with open(path, "w") as f:
        f.write(str(len(chords)) + "\n")
        for a, b in chords:
            f.write(f"{a} {b}\n")

def polish(n, chords, seed, iters, cutoff, restarts=8, timeout=None):
    sf = f"/tmp/state_n{n}_{seed}.txt"
    write_statefile(sf, chords)
    p = subprocess.run([ANNEAL, str(n), str(seed), str(iters), str(cutoff),
                        str(restarts), sf], capture_output=True, text=True, timeout=timeout)
    best = None
    for line in p.stdout.splitlines():
        if line.startswith(("IMPROVE", "WITNESS")):
            best = line
    return best, p.returncode

if __name__ == "__main__":
    text = sys.stdin.read()
    n, chords = parse_state(text)
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
    target = int(sys.argv[2]) if len(sys.argv) > 2 else n + 10
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 200000
    state = (n, chords)
    while state[0] < target:
        g = grow_state(state[0], state[1], rng)
        if g is None:
            print("grow failed", file=sys.stderr); break
        n2, ch2 = g
        best, rc = polish(n2, ch2, rng.randrange(10**6), iters, 20000)
        if best is None:
            print(f"n={n2}: polish produced nothing", file=sys.stderr); break
        print(best, flush=True)
        if rc == 42:
            print("WITNESS FOUND — stop and verify!", flush=True); break
        state = parse_state(best)

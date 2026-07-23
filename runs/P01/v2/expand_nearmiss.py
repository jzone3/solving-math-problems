"""V2 attack 6: blow up near-misses by vertex insertion.

A near-miss = C_n + partial chord set, HC-count 1, rem stubs unfillable.
Inserting a new vertex x on the cycle between i and i+1 keeps unique
hamiltonicity (any HC of the new graph contracts to one of the old through
edge (i,i+1); the unique old HC uses every cycle edge). x arrives with 2 free
chord stubs, which may unlock pairings for the deficient vertices. Iterate:
parse nearmiss.txt states, try every insertion point, re-run seeded DFS at n+1.

Usage: python3 expand_nearmiss.py <budget_per_state_s> [maxnodes]
"""
import re, subprocess, sys
from hcutil import hc_count

def parse(line):
    m = re.match(r"NEAR n=(\d+) multi=(\d+) rem=(\d+) chords:((?: \(\d+,\d+\))*)", line)
    if not m:
        return None
    n, multi, rem = int(m.group(1)), int(m.group(2)), int(m.group(3))
    chords = [tuple(map(int, p)) for p in re.findall(r"\((\d+),(\d+)\)", m.group(4))]
    return n, multi, rem, chords

def insert(n, chords, pos):
    """Insert new vertex after cycle position pos: old vertex v -> v if v<=pos else v+1."""
    f = lambda v: v if v <= pos else v + 1
    return n + 1, [(f(u), f(v)) for u, v in chords]

def run(budget, maxnodes):
    seen = set()
    for line in open("nearmiss.txt"):
        st = parse(line.strip())
        if st is None:
            continue
        n, multi, rem, chords = st
        key = (n, tuple(sorted(chords)))
        if key in seen or rem > 8:
            continue
        seen.add(key)
        for pos in range(n):
            n2, ch2 = insert(n, chords, pos)
            cyc = [(i, (i + 1) % n2) for i in range(n2)]
            assert hc_count(n2, [(min(e), max(e)) for e in cyc] + list(ch2)) == 1
            inp = f"{len(ch2)}\n" + "\n".join(f"{u} {v}" for u, v in ch2)
            mode = "seedmulti" if multi else "seed"
            r = subprocess.run(["./dfs4", str(n2), str(pos + 77), str(budget), maxnodes, mode],
                               input=inp, capture_output=True, text=True)
            out = r.stdout.strip()
            if "WITNESS" in out or r.returncode == 42:
                print(f"WITNESS from insertion n={n}->{n2} pos={pos}", flush=True)
                return
            best = re.findall(r"best rem=(\d+)", out)
            b = min(map(int, best)) if best else None
            print(f"n={n}->{n2} pos={pos} rem_was={rem} best_now={b}", flush=True)

if __name__ == "__main__":
    budget = sys.argv[1] if len(sys.argv) > 1 else "30"
    maxnodes = sys.argv[2] if len(sys.argv) > 2 else "2000000"
    run(budget, maxnodes)

"""Driver: exhaust ALL connected Eulerian graphs on n=13 with min degree >= 6
via complements (sparse side: geng -d2 -D6 13, evenfilt, complement, check).
Slices START..1999 of 2000; appends per-slice results to comp13_full.log.
"""
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

DONE_FILE = "comp13_full.log"
MOD = 2000

def run_slice(i):
    r = subprocess.run(["python3", "sweep_complement.py", "13", "2", "6",
                        str(i), str(MOD)], capture_output=True, text=True)
    with open(DONE_FILE, "a") as f:
        tail = [l for l in r.stdout.splitlines() if l.startswith(("DONE", "HARD", "***"))]
        for l in tail:
            f.write(l + "\n")
        if r.returncode != 0:
            f.write(f"ERROR slice {i} rc={r.returncode}: {r.stderr[-500:]}\n")
    return i

def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for i in ex.map(run_slice, range(start, MOD)):
            print(f"slice {i} done", flush=True)

if __name__ == "__main__":
    main()

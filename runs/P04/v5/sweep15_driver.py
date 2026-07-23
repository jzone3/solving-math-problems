"""Driver: complete the exhaustive 6-regular n=15 sweep, slices START..399 of 400,
with a pool of worker subprocesses. Appends one DONE line per slice to
sweep15_full.log; any counterexample is written by sweep_regular.py itself.
"""
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

DONE_FILE = "sweep15_full.log"

def run_slice(i):
    t0 = time.time()
    r = subprocess.run(["python3", "sweep_regular.py", "15", str(i), "400"],
                       capture_output=True, text=True)
    with open(DONE_FILE, "a") as f:
        tail = [l for l in r.stdout.splitlines() if l.startswith(("DONE", "HARD", "***"))]
        for l in tail:
            f.write(l + "\n")
        if r.returncode != 0:
            f.write(f"ERROR slice {i} rc={r.returncode}: {r.stderr[-500:]}\n")
    return i

def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for i in ex.map(run_slice, range(start, 400)):
            print(f"slice {i} done", flush=True)

if __name__ == "__main__":
    main()

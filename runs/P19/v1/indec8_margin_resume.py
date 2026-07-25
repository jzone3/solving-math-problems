"""Resume margin check for L=8 from tail index SKIP (enumeration is deterministic)."""
import sys, time
import multiprocessing as mp
from indec6 import enum_wide, is_wide, decomposable

LO, HI = 21, 34
SKIP = int(sys.argv[1]) if len(sys.argv) > 1 else 0


def work(tail):
    count = 0
    bad = []
    for l1 in range(max(tail[0], LO), HI + 1):
        lam = (l1,) + tail
        if not is_wide(lam):
            continue
        count += 1
        if not decomposable(lam):
            bad.append(lam)
    return count, bad


def main():
    t0 = time.time()
    tails = enum_wide(7, HI)
    print(f"tails: {len(tails)}, resuming at {SKIP} ({time.time()-t0:.1f}s)", flush=True)
    tails = tails[SKIP:]
    total = 0
    allbad = []
    done = 0
    with mp.Pool(mp.cpu_count()) as pool:
        for count, bad in pool.imap_unordered(work, tails, chunksize=256):
            total += count
            allbad.extend(bad)
            done += 1
            if done % 500000 == 0:
                print(f"  {SKIP+done} tails, {total} wides checked, bad={allbad} ({time.time()-t0:.1f}s)", flush=True)
    print(f"resumed range done: {total} wides with lam1 in [{LO},{HI}] from tail {SKIP}; "
          f"indecomposable: {allbad} ({time.time()-t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()

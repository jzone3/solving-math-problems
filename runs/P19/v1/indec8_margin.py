"""Margin check for L=8: verify NO indecomposable wide 8-part partition has
first part in [LO, HI]. Parallel over 7-part wide tails."""
import sys, time
import multiprocessing as mp
from indec6 import enum_wide, is_wide, decomposable

LO = int(sys.argv[1]) if len(sys.argv) > 1 else 21
HI = int(sys.argv[2]) if len(sys.argv) > 2 else 34


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
    print(f"wide 7-part tails with parts<={HI}: {len(tails)} ({time.time()-t0:.1f}s)", flush=True)
    total = 0
    allbad = []
    done = 0
    with mp.Pool(mp.cpu_count()) as pool:
        for count, bad in pool.imap_unordered(work, tails, chunksize=256):
            total += count
            allbad.extend(bad)
            done += 1
            if done % 500000 == 0:
                print(f"  {done}/{len(tails)} tails, {total} wides checked, bad={allbad} ({time.time()-t0:.1f}s)", flush=True)
    print(f"checked {total} wide 8-part partitions with lam1 in [{LO},{HI}]; "
          f"indecomposable: {allbad} ({time.time()-t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()

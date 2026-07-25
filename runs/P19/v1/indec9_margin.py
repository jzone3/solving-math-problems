"""Margin check for L=9: verify NO indecomposable wide 9-part partition has
first part in [LO, HI]. Streams wide 8-part tails with parts <= HI; workers
recycled to bound cache growth. Usage: python3 indec9_margin.py LO HI [SKIP]"""
import sys, time, itertools
import multiprocessing as mp
from indec6 import is_wide, decomposable

LO = int(sys.argv[1]) if len(sys.argv) > 1 else 23
HI = int(sys.argv[2]) if len(sys.argv) > 2 else 32
SKIP = int(sys.argv[3]) if len(sys.argv) > 3 else 0


def wide_iter(L, B):
    prefix = []

    def rec():
        k = len(prefix)
        if k == L:
            yield tuple(prefix)
            return
        hi = prefix[-1] if prefix else B
        for v in range(hi, 0, -1):
            prefix.append(v)
            if is_wide(tuple(prefix)):
                yield from rec()
            prefix.pop()

    yield from rec()


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
    tails = itertools.islice(wide_iter(8, HI), SKIP, None)
    total = 0
    allbad = []
    done = 0
    with mp.Pool(mp.cpu_count(), maxtasksperchild=50) as pool:
        for count, bad in pool.imap_unordered(work, tails, chunksize=256):
            total += count
            allbad.extend(bad)
            done += 1
            if done % 500000 == 0:
                print(f"  {SKIP+done} tails, {total} wides checked, bad={allbad} ({time.time()-t0:.1f}s)", flush=True)
    print(f"range done: {total} wides with lam1 in [{LO},{HI}] from tail {SKIP}; "
          f"tails processed {done}; indecomposable: {allbad} ({time.time()-t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()

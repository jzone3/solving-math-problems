"""Memory-safe margin check for L=8 (streams wide 7-part tails instead of
materializing 17.9M tuples; the first attempt was OOM-killed because forked
pool workers un-shared the giant list via refcount COW).

Verifies NO indecomposable wide 8-part partition has first part in [LO, HI].
Usage: python3 indec8_margin2.py [SKIP]
"""
import sys, time, itertools
import multiprocessing as mp
from indec6 import is_wide, decomposable

LO, HI = 21, 34
SKIP = int(sys.argv[1]) if len(sys.argv) > 1 else 0


def wide_iter(L, B):
    """generator over wide partitions with exactly L parts, first part <= B"""
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
    tails = itertools.islice(wide_iter(7, HI), SKIP, None)
    total = 0
    allbad = []
    done = 0
    # maxtasksperchild bounds the unbounded lru_cache growth in workers
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

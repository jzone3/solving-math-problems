"""L=9 indecomposable wide partitions: streamed, memory-safe parallel
decomposability filter + CP-SAT Latin test with exact re-check.
Usage: python3 indec9.py [B] [SKIP]"""
import sys, time, itertools
import multiprocessing as mp
from indec6 import is_wide, decomposable, is_latin_cpsat

L = 9


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


def work(lam):
    return lam, decomposable(lam)


def main():
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 22
    SKIP = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    t0 = time.time()
    wides = itertools.islice(wide_iter(L, B), SKIP, None)
    indecs = []
    done = 0
    with mp.Pool(mp.cpu_count(), maxtasksperchild=50) as pool:
        for lam, dec in pool.imap_unordered(work, wides, chunksize=256):
            done += 1
            if not dec:
                indecs.append(lam)
            if done % 200000 == 0:
                print(f"  {SKIP+done} filtered, {len(indecs)} indec so far ({time.time()-t0:.1f}s)", flush=True)
    print(f"filtered {SKIP+done} wide {L}-part partitions (B={B}); "
          f"indecomposable in this range: {len(indecs)} ({time.time()-t0:.1f}s)", flush=True)
    if indecs:
        print(f"max first part: {max(l[0] for l in indecs)} (bound B={B}), max |lam|={max(sum(l) for l in indecs)}", flush=True)
        with open(f"indec9_list_{SKIP}.txt", "w") as f:
            for lam in sorted(indecs, key=sum):
                f.write(repr(lam) + "\n")
    bad = []
    for i, lam in enumerate(sorted(indecs, key=sum)):
        res = is_latin_cpsat(lam)
        if res != "SAT":
            bad.append((lam, res))
            print(f"*** {lam} -> {res}", flush=True)
        if (i + 1) % 5000 == 0:
            print(f"  latin-tested {i+1}/{len(indecs)} ({time.time()-t0:.1f}s)", flush=True)
    print(f"done: {len(indecs)} indecomposables tested, non-SAT: {bad} ({time.time()-t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()

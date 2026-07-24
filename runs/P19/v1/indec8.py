"""L=8 indecomposable wide partitions: parallel decomposability filter.
Usage: python3 indec8.py [B]"""
import sys, time
import multiprocessing as mp
from indec6 import enum_wide, decomposable, is_latin_cpsat


def work(lam):
    return lam, decomposable(lam)


def main():
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    t0 = time.time()
    wides = enum_wide(8, B)
    print(f"L=8 B={B}: {len(wides)} wide partitions ({time.time()-t0:.1f}s)", flush=True)
    indecs = []
    done = 0
    with mp.Pool(mp.cpu_count()) as pool:
        for lam, dec in pool.imap_unordered(work, wides, chunksize=256):
            done += 1
            if not dec:
                indecs.append(lam)
            if done % 200000 == 0:
                print(f"  {done}/{len(wides)} filtered, {len(indecs)} indec so far ({time.time()-t0:.1f}s)", flush=True)
    print(f"indecomposable: {len(indecs)} ({time.time()-t0:.1f}s)", flush=True)
    if indecs:
        print(f"max first part: {max(l[0] for l in indecs)} (bound B={B}), max |lam|={max(sum(l) for l in indecs)}", flush=True)
        with open("indec8_list.txt", "w") as f:
            for lam in sorted(indecs, key=sum):
                f.write(repr(lam) + "\n")
    bad = []
    for lam in sorted(indecs, key=sum):
        res = is_latin_cpsat(lam)
        if res != "SAT":
            bad.append((lam, res))
            print(f"*** {lam} -> {res}", flush=True)
    print(f"done: {len(indecs)} indecomposables tested, non-SAT: {bad} ({time.time()-t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()

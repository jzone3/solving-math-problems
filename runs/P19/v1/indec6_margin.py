"""Margin check for indec6: verify NO indecomposable wide 6-part partition
has first part in [LO, HI]. Enumerates wide 6-part partitions with
lam1 in that range (tail (lam2..lam6) is itself a wide 5-part partition)
and checks each is decomposable."""
import sys, time
from indec6 import enum_wide, is_wide, decomposable

LO = int(sys.argv[1]) if len(sys.argv) > 1 else 31
HI = int(sys.argv[2]) if len(sys.argv) > 2 else 45

t0 = time.time()
tails = enum_wide(5, HI)
print(f"wide 5-part tails with parts<={HI}: {len(tails)} ({time.time()-t0:.1f}s)", flush=True)
count = 0
bad = []
for tail in tails:
    for l1 in range(max(tail[0], LO), HI + 1):
        lam = (l1,) + tail
        if not is_wide(lam):
            continue
        count += 1
        if not decomposable(lam):
            bad.append(lam)
            print("*** INDECOMPOSABLE:", lam, flush=True)
print(f"checked {count} wide 6-part partitions with lam1 in [{LO},{HI}]; "
      f"indecomposable: {bad} ({time.time()-t0:.1f}s)", flush=True)

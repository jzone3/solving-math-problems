#!/usr/bin/env python3
"""Machine evidence for the rigidity theorem (see NOTES.md sec. 2b).

Theorem: for odd n, no Tuscan-1 (hence no Tuscan-2) square is invariant under
any twisted symmetry tau = rev o sigma (sigma an involution != id): the
'anti-fixed' pairs (a, sigma(a)), a not sigma-fixed, would be covered twice.

This control run searches for twisted-symmetric TUSCAN-1 squares (distance-2
constraint disabled) of small odd orders; the theorem predicts the search
space contains no solutions, and indeed every branch dies at <= n-1 rows.
"""
import time

src = open(__file__.replace("control_tuscan1", "inv_search")).read()
src = src.replace("occ2[r[i]][r[i + 2]] or p in seen2", "False")
src = src.replace(
    "if L >= 2 and occ2[cur[-2]][x]:\n                continue",
    "if False:\n                continue",
)
ns = {"__name__": "ctl"}
exec(compile(src, "inv_search_tuscan1", "exec"), ns)

if __name__ == "__main__":
    for n in (5, 7, 9):
        for t in range(1, n, 2):
            st = time.time()
            found, best = ns["search"](n, t, time_budget=120)
            print(
                f"Tuscan-1 twisted-symmetric n={n} t={t}: found={found} "
                f"best={best[0]}/{n} time={time.time()-st:.1f}s",
                flush=True,
            )
            assert not found, "theorem violated?!"

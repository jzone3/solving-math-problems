#!/usr/bin/env python3
"""ILP polish: fix an INCOMPLETE engine4 cover by liberating a subset of used
values and re-placing them optimally on the residual (targeted columns only).

Liberate set S = values with the fewest exclusive points (plus all values whose
class touches a hole is unnecessary: any value can hit any point). Targets =
holes + points exclusively covered by S. Columns: (v in S, residue t mod v)
for targets t (plus the old residue as fallback). Feasibility ILP via HiGHS.
Iterates with growing S until covered or S exhausted.
"""
import argparse
import numpy as np
import highspy


def load(path):
    congs = []
    meta = ""
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                meta = line.strip()
                continue
            a, v = map(int, line.split())
            congs.append((a, v))
    return congs, meta


def polish(N, congs, s_size=40, time_limit=300, max_rounds=8, verbose=True):
    congs = list(congs)
    for rnd in range(max_rounds):
        cnt = np.zeros(N, dtype=np.uint16)
        for a, v in congs:
            cnt[a::v] += 1
        holes = np.flatnonzero(cnt == 0)
        if holes.size == 0:
            return congs, 0
        # exclusive coverage per placement
        excl = []
        for i, (a, v) in enumerate(congs):
            idx = np.arange(a, N, v)
            excl.append((int((cnt[idx] == 1).sum()), i))
        excl.sort()
        S_idx = [i for _, i in excl[:s_size]]
        S = [congs[i] for i in S_idx]
        # liberate S
        for a, v in S:
            cnt[a::v] -= 1
        targets = np.flatnonzero(cnt == 0)
        if verbose:
            print(f" round {rnd}: holes={holes.size} |S|={len(S)} "
                  f"targets={targets.size}", flush=True)
        tlist = targets.tolist()
        tpos = {t: j for j, t in enumerate(tlist)}
        # columns
        cols = []  # (v, a, [target rows])
        for _, v in S:
            resid = {}
            for t in tlist:
                resid.setdefault(t % v, []).append(tpos[t])
            for a, rows in resid.items():
                cols.append((v, a, rows))
        # ILP
        h = highspy.Highs()
        h.setOptionValue("output_flag", False)
        h.setOptionValue("time_limit", float(time_limit))
        inf = highspy.kHighsInf
        ncols = len(cols)
        h.addVars(ncols, np.zeros(ncols), np.ones(ncols))
        h.changeColsIntegrality(ncols, np.arange(ncols, dtype=np.int32),
                                np.array([highspy.HighsVarType.kInteger] * ncols))
        h.changeColsCost(ncols, np.arange(ncols, dtype=np.int32), np.zeros(ncols))
        # per-value usage <= 1
        byv = {}
        for j, (v, a, rows) in enumerate(cols):
            byv.setdefault(v, []).append(j)
        for v, js in byv.items():
            h.addRow(-inf, 1.0, len(js), np.array(js, dtype=np.int32),
                     np.ones(len(js)))
        # per-target coverage >= 1
        bytarget = [[] for _ in tlist]
        for j, (v, a, rows) in enumerate(cols):
            for rrow in rows:
                bytarget[rrow].append(j)
        infeasible = False
        for rrow, js in enumerate(bytarget):
            if not js:
                infeasible = True
                break
            h.addRow(1.0, inf, len(js), np.array(js, dtype=np.int32),
                     np.ones(len(js)))
        if infeasible:
            if verbose:
                print("  target with no candidate column; growing S")
            s_size = int(s_size * 1.7)
            continue
        h.run()
        name = h.modelStatusToString(h.getModelStatus())
        if not name.lower().startswith("optimal"):
            if verbose:
                print(f"  ILP {name}; growing S")
            s_size = int(s_size * 1.7)
            continue
        sol = h.getSolution().col_value
        chosen = {}
        for j, (v, a, rows) in enumerate(cols):
            if sol[j] > 0.5:
                chosen[v] = a
        # rebuild congs: keep non-S, add chosen placements (unused S values
        # keep their old residue to not lose coverage)
        S_set = set(S_idx)
        newc = [c for i, c in enumerate(congs) if i not in S_set]
        for a_old, v in S:
            newc.append((chosen.get(v, a_old), v))
        congs = newc
    cnt = np.zeros(N, dtype=np.uint16)
    for a, v in congs:
        cnt[a::v] += 1
    return congs, int((cnt == 0).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part_file")
    ap.add_argument("-N", type=int, required=True)
    ap.add_argument("--s-size", type=int, default=40)
    ap.add_argument("--time-limit", type=float, default=300)
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args()
    congs, meta = load(args.part_file)
    congs, rem = polish(args.N, congs, s_size=args.s_size,
                        time_limit=args.time_limit)
    print(f"after polish: uncovered={rem}")
    if rem == 0:
        with open(args.out, "w") as f:
            f.write(f"{meta} + ilp_polish\n")
            for a, v in sorted(congs, key=lambda t: t[1]):
                f.write(f"{a} {v}\n")
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()

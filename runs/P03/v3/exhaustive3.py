"""tau=3-TARGETED exhaustive scan (V3) for big slices (e.g. n=8 oriented nonplanar).

Only hunts tau=3 Woodall counterexamples: applies the cheap ACZ rho>=4 degree filter
BEFORE dicut enumeration, then requires tau==3, not source-sink connected, then
SAT-checks 3-dijoin packing. (Planarity already filtered upstream via geng file.)

Usage: nauty-directg -o < slice.g6 | python3 exhaustive3.py [label]
"""
import sys

from pysat.solvers import Minicard


def sat_pack3(m, md):
    cnf = []
    for i in range(m):
        vs = [3 * i + 1, 3 * i + 2, 3 * i + 3]
        cnf.append(vs)
        cnf.append([-vs[0], -vs[1]])
        cnf.append([-vs[0], -vs[2]])
        cnf.append([-vs[1], -vs[2]])
    for d in md:
        for c in range(3):
            cnf.append([3 * i + c + 1 for i in d])
    with Minicard(bootstrap_with=cnf) as s:
        return s.solve()


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "slice"
    total = rho_pass = tau3 = ss_pass = 0
    sat_calls = cex = 0
    for line in sys.stdin:
        if not line or line[0] != '&':
            continue
        data = [ord(c) - 63 for c in line[1:].rstrip()]
        n = data[0]
        total += 1
        if total % 2000000 == 0:
            print(f"[{label}] ...{total} rho_pass={rho_pass} tau3={tau3} "
                  f"ss_pass={ss_pass} sat={sat_calls}", file=sys.stderr, flush=True)
        # decode adjacency bits row-major n*n
        arcs = []
        inmask = [0] * n
        outmask = [0] * n
        imb = [0] * n
        idx = 0
        u = 0
        v = 0
        for x in data[1:]:
            for k in range(5, -1, -1):
                if idx >= n * n:
                    break
                if (x >> k) & 1:
                    u, v = divmod(idx, n)
                    arcs.append((u, v))
                    inmask[v] |= 1 << u
                    outmask[u] |= 1 << v
                    imb[u] += 1
                    imb[v] -= 1
                idx += 1
        # ACZ filter: rho >= 4  <=>  sum((imb mod 3)) >= 12
        s = 0
        for x in imb:
            s += x % 3
        if s < 12:
            continue
        rho_pass += 1
        # tau via closed-set enumeration
        m = len(arcs)
        full = (1 << n) - 1
        tau = None
        cutsets = []
        for U in range(1, full):
            out = 0
            bad = False
            Uv = U
            v = 0
            while Uv:
                if Uv & 1:
                    if inmask[v] & ~U:
                        bad = True
                        break
                    out |= outmask[v]
                Uv >>= 1
                v += 1
            if bad or not (out & ~U):
                continue
            cnt = 0
            Uv = U
            v = 0
            while Uv:
                if Uv & 1:
                    x = outmask[v] & ~U
                    while x:
                        x &= x - 1
                        cnt += 1
                Uv >>= 1
                v += 1
            cutsets.append(U)
            if tau is None or cnt < tau:
                tau = cnt
                if tau < 3:
                    break
        if tau != 3:
            continue
        tau3 += 1
        # not source-sink connected filter (Schrijver safe class)
        srcs = [v for v in range(n) if inmask[v] == 0]
        sinks = [v for v in range(n) if outmask[v] == 0]
        ssc = True
        for sv in srcs:
            seen = 1 << sv
            stack = [sv]
            while stack:
                y = stack.pop()
                x = outmask[y] & ~seen
                while x:
                    b = x & -x
                    x ^= b
                    w = b.bit_length() - 1
                    seen |= b
                    stack.append(w)
            if any(not (seen >> t) & 1 for t in sinks):
                ssc = False
                break
        if ssc:
            continue
        ss_pass += 1
        # minimal dicuts as arc-index sets
        dicuts = set()
        for U in cutsets:
            cut = frozenset(i for i, (a, b) in enumerate(arcs)
                            if (U >> a) & 1 and not (U >> b) & 1)
            if cut:
                dicuts.add(cut)
        ds = sorted(dicuts, key=len)
        md = []
        for d in ds:
            if not any(x <= d for x in md):
                md.append(d)
        sat_calls += 1
        if not sat_pack3(m, md):
            cex += 1
            print(f"[{label}] COUNTEREXAMPLE digraph6={line.strip()} arcs={arcs}",
                  flush=True)
    print(f"[{label}] TOTAL={total} rho_pass={rho_pass} tau3={tau3} "
          f"not_ss={ss_pass} sat_calls={sat_calls} counterexamples={cex}", flush=True)


if __name__ == "__main__":
    main()

"""Independent certified verifier for a CEGAR witness (P23-sms).

Given a universe pkl and a witness (list of vertex indices), this:
  [1] recomputes the induced subgraph's edges from EXACT algebraic coordinates
      (norm2 == 1 in the exact field; no floating point in the decision),
  [2] runs kissat on the k-coloring CNF and requires s UNSATISFIABLE  (chi >= k+1),
  [3] hands kissat's DRAT proof to drat-trim and requires  s VERIFIED,
  [4] runs kissat on the (k+1)-coloring CNF and requires SAT        (chi <= k+1),
  so chi(U[S]) == k+1 exactly, machine-certified.
Prints PASS only if every gate passes.
"""
import sys, os, pickle, subprocess, tempfile, argparse
from mfield import MField

KISSAT = os.path.expanduser("~/p23/kissat/build/kissat")
DRATTRIM = os.path.expanduser("~/p23/drat-trim/drat-trim")


def induced_edges(fld, pts):
    ONE = fld.ONE
    E = []
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if fld.norm2(pts[i], pts[j]) == ONE:
                E.append((i, j))
    return E


def color_cnf(n, edges, k):
    cls = []
    var = lambda v, c: v * k + c + 1
    for v in range(n):
        cls.append([var(v, c) for c in range(k)])
    for (u, v) in edges:
        for c in range(k):
            cls.append([-var(u, c), -var(v, c)])
    return n * k, cls


def write_cnf(path, nv, cls):
    with open(path, "w") as f:
        f.write(f"p cnf {nv} {len(cls)}\n")
        for c in cls:
            f.write(" ".join(map(str, c)) + " 0\n")


def run_kissat(nv, cls, proof=None):
    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as f:
        cnf = f.name
    write_cnf(cnf, nv, cls)
    cmd = [KISSAT, "-q", cnf] + ([proof] if proof else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    res = "UNSAT" if "s UNSATISFIABLE" in r.stdout else (
        "SAT" if "s SATISFIABLE" in r.stdout else "UNKNOWN")
    return res, cnf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("universe")
    ap.add_argument("witness", help="pkl with 'witness' list, or comma indices")
    ap.add_argument("--k", type=int, default=3, help="chi>=k+1 to certify")
    ap.add_argument("--drat", action="store_true")
    a = ap.parse_args()

    with open(a.universe, "rb") as f:
        univ = pickle.load(f)
    primes = univ["primes"]
    allpts = univ["points"]
    fld = MField(primes)

    if a.witness.endswith(".pkl"):
        with open(a.witness, "rb") as f:
            w = pickle.load(f)
        idx = sorted(w["witness"])
        k = w.get("k", a.k)
    else:
        idx = sorted(int(x) for x in a.witness.split(","))
        k = a.k

    pts = [allpts[i] for i in idx]
    n = len(pts)
    # [0] distinctness
    assert len(set(pts)) == n, "duplicate coordinates in witness"
    # [1] exact edges
    E = induced_edges(fld, pts)
    print(f"[1] {n} vertices, {len(E)} exact unit edges (field Q{tuple('sqrt%d'%p for p in primes)})")

    # [2] kissat: k-coloring UNSAT
    nv, cls = color_cnf(n, E, k)
    proof = None
    if a.drat:
        proof = tempfile.NamedTemporaryFile(suffix=".drat", delete=False).name
    res, cnf = run_kissat(nv, cls, proof)
    print(f"[2] kissat {k}-coloring: {res}  (want UNSAT => chi>={k+1})")
    ok = res == "UNSAT"

    # [3] drat-trim
    if a.drat and ok:
        r = subprocess.run([DRATTRIM, cnf, proof], capture_output=True, text=True)
        verified = "s VERIFIED" in r.stdout
        print(f"[3] drat-trim: {'s VERIFIED' if verified else 'NOT VERIFIED'}")
        ok = ok and verified

    # [4] (k+1)-coloring SAT => chi <= k+1
    nv2, cls2 = color_cnf(n, E, k + 1)
    res2, _ = run_kissat(nv2, cls2)
    print(f"[4] kissat {k+1}-coloring: {res2}  (want SAT => chi<={k+1})")
    ok = ok and (res2 == "SAT")

    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

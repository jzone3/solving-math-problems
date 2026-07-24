#!/usr/bin/env python3
"""Count plain-CNF unit propagation assignments for dense cubes."""
import json
from pathlib import Path


def parse_cnf(path):
    lines = path.read_text().splitlines()
    nv, _ = map(int, lines[0].split()[2:4])
    clauses = [tuple(map(int, line.split()[:-1])) for line in lines[1:] if line and not line.startswith("c")]
    return nv, clauses


def propagate(nv, clauses, lits):
    values = [0] * (nv + 1)
    trail = []
    for lit in lits:
        var, val = abs(lit), 1 if lit > 0 else -1
        if values[var] and values[var] != val:
            return len(trail), True
        if not values[var]:
            values[var] = val
            trail.append(var)
    changed = True
    while changed:
        changed = False
        for clause in clauses:
            sat = False
            unassigned = []
            for lit in clause:
                value = values[abs(lit)]
                if value == (1 if lit > 0 else -1):
                    sat = True
                    break
                if value == 0:
                    unassigned.append(lit)
            if sat:
                continue
            if not unassigned:
                return len(trail), True
            if len(unassigned) == 1:
                lit = unassigned[0]
                var, val = abs(lit), 1 if lit > 0 else -1
                if values[var] and values[var] != val:
                    return len(trail), True
                if not values[var]:
                    values[var] = val
                    trail.append(var)
                    changed = True
    return len(trail), False


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("table", type=Path)
    parser.add_argument("--base", type=Path, default=Path("../v2/plain.cnf"))
    parser.add_argument("--out", type=Path, default=Path("dense_up.json"))
    args = parser.parse_args()
    nv, clauses = parse_cnf(args.base)
    rows = json.loads(args.table.read_text())
    out = []
    for ri, row in enumerate(rows):
        counts = []
        for sample in row["samples"]:
            global_vars = sample.get("global_vars", [abs(x) for x in sample["lits"]])
            assert sorted(global_vars) == sorted(abs(x) for x in sample["lits"])
            assert len(set(global_vars)) == len(global_vars)
            assert all(1 <= x <= nv for x in global_vars)
            assigned, conflict = propagate(nv, clauses, sample["lits"])
            counts.append({"assigned": assigned, "extra": assigned - len(sample["lits"]), "conflict": conflict})
        out.append({"row": ri, "edges": row["edges"], "counts": counts})
        extras = sorted(x["extra"] for x in counts)
        print(
            f"row={ri} |S|={row['edges']} UP extra min/median/max="
            f"{extras[0]}/{extras[len(extras)//2]}/{extras[-1]} "
            f"conflicts={sum(x['conflict'] for x in counts)}"
        )
    args.out.write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

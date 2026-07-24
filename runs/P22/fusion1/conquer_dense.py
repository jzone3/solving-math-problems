#!/usr/bin/env python3
"""Parallel kissat measurements for cubes emitted by dense_cube.py."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


def read_base(path):
    lines = path.read_text().splitlines()
    header = next(i for i, line in enumerate(lines) if line.startswith("p cnf "))
    _, _, nv, nc = lines[header].split()[:4]
    return int(nv), int(nc), lines[header + 1 :]


def run_one(job):
    idx, row_idx, sample, base_path, timeout, workdir = job
    nv, nc, clauses = read_base(Path(base_path))
    literals = sample["lits"]
    global_vars = sample.get("global_vars", [abs(x) for x in literals])
    assert sorted(global_vars) == sorted(abs(x) for x in literals)
    assert len(set(global_vars)) == len(global_vars)
    assert all(1 <= x <= nv for x in global_vars)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cnf", prefix=f"dense_{row_idx}_{idx}_", dir=workdir, delete=False
    ) as f:
        cnf_path = Path(f.name)
        f.write(f"p cnf {nv} {nc + len(literals)}\n")
        f.writelines(line + "\n" for line in clauses)
        for lit in literals:
            f.write(f"{lit} 0\n")
    start = time.monotonic()
    try:
        proc = subprocess.run(
            ["kissat", "--quiet", f"--time={timeout}", str(cnf_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout + 10,
        )
        if proc.returncode == 0 and time.monotonic() - start >= timeout - 1:
            status = "TIMEOUT"
        else:
            status = {10: "SAT", 20: "UNSAT"}.get(proc.returncode, f"RC{proc.returncode}")
    except subprocess.TimeoutExpired:
        status = "TIMEOUT"
    elapsed = time.monotonic() - start
    try:
        cnf_path.unlink()
    except FileNotFoundError:
        pass
    return {
        "row": row_idx,
        "index": idx,
        "status": status,
        "seconds": round(elapsed, 3),
        "cube_literals": len(literals),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("table", type=Path)
    parser.add_argument("--base", type=Path, default=Path("../v2/plain.cnf"))
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out", type=Path, default=Path("dense_results.json"))
    args = parser.parse_args()
    rows = json.loads(args.table.read_text())
    jobs = []
    for row_idx, row in enumerate(rows):
        for idx, sample in enumerate(row["samples"]):
            jobs.append(
                (
                    idx,
                    row_idx,
                    sample,
                    str(args.base.resolve()),
                    args.timeout,
                    str(args.out.parent.resolve()),
                )
            )
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_one, job) for job in jobs]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(
                f"row={result['row']} cube={result['index']} "
                f"{result['status']} {result['seconds']:.3f}s",
                flush=True,
            )
    results.sort(key=lambda x: (x["row"], x["index"]))
    args.out.write_text(json.dumps(results, indent=2))
    for row_idx, row in enumerate(rows):
        subset = [x for x in results if x["row"] == row_idx]
        counts = {}
        for result in subset:
            counts[result["status"]] = counts.get(result["status"], 0) + 1
        times = [x["seconds"] for x in subset]
        print(
            f"row={row_idx} |S|={row['edges']} n={len(subset)} counts={counts} "
            f"min={min(times):.3f}s median={sorted(times)[len(times)//2]:.3f}s "
            f"max={max(times):.3f}s"
        )
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()

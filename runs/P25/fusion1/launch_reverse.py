#!/usr/bin/env python3
"""Launch reverse sorted undecided classes with SAT workers and ILP fallback.

The launcher keeps four SAT processes active.  A completed SAT timeout queues
its class for one of two ILP workers; SAT UNSAT is recorded immediately.
"""
import ast
import os
import re
import subprocess
import sys
import time
from collections import deque

ROOT = os.path.dirname(os.path.abspath(__file__))
LOGDIR = os.path.join(ROOT, "logs")
V1LOG = "/home/ubuntu/repos/solving-math-problems/runs/P25/v1/logs"
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 72
SAT_LIMIT = float(sys.argv[2]) if len(sys.argv) > 2 else 7200
ILP_LIMIT = float(sys.argv[3]) if len(sys.argv) > 3 else 14400
os.makedirs(LOGDIR, exist_ok=True)


def classes():
    rows = set()
    for name in sorted(os.listdir(V1LOG)):
        if not name.startswith("feas"):
            continue
        for line in open(os.path.join(V1LOG, name)):
            if not line.startswith("UNDECIDED"):
                continue
            m = re.match(r"UNDECIDED lam=(\[[^\]]*\]) assign=(\([^)]*\))", line)
            if m:
                rows.add((m.group(1), m.group(2)))
    return list(reversed(sorted(rows)))


def slug(lam, assign):
    return "lam_" + lam.strip("[]").replace(", ", "_") + "__" + assign.replace("'", "")


def main():
    pending = deque(classes())
    sat = {}
    ilp = {}
    confirm = {}
    ilp_queue = deque()
    confirm_queue = deque()
    with open(os.path.join(LOGDIR, "launcher.log"), "a") as log:
        log.write(f"START classes={len(pending)} target={TARGET}\n")
        while pending or sat or ilp or confirm or ilp_queue or confirm_queue:
            while pending and len(sat) < 4:
                lam, assign = pending.popleft()
                d = os.path.join(LOGDIR, slug(lam, assign))
                os.makedirs(d, exist_ok=True)
                cmd = [sys.executable, os.path.join(ROOT, "orbit_sat_feas.py"),
                       str(TARGET), lam, assign, d, str(SAT_LIMIT)]
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True)
                sat[p.pid] = (p, lam, assign, d, time.monotonic())
                log.write(f"SAT_START lam={lam} assign={assign}\n")
                log.flush()
            for pid, (p, lam, assign, d, started) in list(sat.items()):
                if p.poll() is None:
                    continue
                out = p.stdout.read()
                log.write(out)
                log.write(f"SAT_DONE elapsed={time.monotonic()-started:.3f}\n")
                log.flush()
                del sat[pid]
                if "RESULT UNDECIDED" in out:
                    ilp_queue.append((lam, assign, d))
                elif "RESULT UNSAT" in out:
                    confirm_queue.append((lam, assign, d))
                elif "RESULT SAT" in out:
                    print("FEASIBLE: stop requested", flush=True)
                    return
            if confirm_queue and not confirm:
                lam, assign, d = confirm_queue.popleft()
                cmd = [sys.executable, os.path.join(ROOT, "orbit_sat_feas.py"),
                       str(TARGET), lam, assign, d, str(SAT_LIMIT), "--proof"]
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, text=True)
                confirm[p.pid] = (p, lam, assign, d)
                log.write(f"DRAT_CONFIRM_START lam={lam} assign={assign}\n")
                log.flush()
            for pid, (p, lam, assign, d) in list(confirm.items()):
                if p.poll() is None:
                    continue
                log.write(p.stdout.read())
                log.write(f"DRAT_CONFIRM_DONE lam={lam} assign={assign}\n")
                log.flush()
                del confirm[pid]
            while ilp_queue and len(ilp) < 2:
                lam, assign, d = ilp_queue.popleft()
                cmd = [sys.executable, os.path.join(ROOT, "orbit_ilp_feas.py"),
                       str(TARGET), str(ILP_LIMIT), "2", lam, assign, d]
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True)
                ilp[p.pid] = (p, lam, assign, d)
                log.write(f"ILP_START lam={lam} assign={assign}\n")
                log.flush()
            for pid, (p, lam, assign, d) in list(ilp.items()):
                if p.poll() is None:
                    continue
                log.write(p.stdout.read())
                log.write(f"ILP_DONE lam={lam} assign={assign}\n")
                log.flush()
                del ilp[pid]
            time.sleep(1)
        log.write("COMPLETE\n")


if __name__ == "__main__":
    main()

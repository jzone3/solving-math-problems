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


def sat_completed():
    """Classes already given a full SAT budget in a prior fusion1 run."""
    done = set()
    path = os.path.join(LOGDIR, "launcher.log")
    if not os.path.exists(path):
        return done
    pattern = re.compile(
        r"RESULT UNDECIDED lam=(\[[^\]]*\]) assign=(\([^)]*\)).*seconds=([0-9.]+)")
    for line in open(path):
        match = pattern.search(line)
        if match and float(match.group(3)) >= SAT_LIMIT - 1.0:
            done.add((match.group(1), match.group(2)))
    return done


def main():
    pending = deque(classes())
    pending_pb = deque(classes())
    sat_done = sat_completed()
    sat = {}
    pb = {}
    ilp = {}
    confirm = {}
    # A persisted full-budget SAT timeout remains eligible for the different
    # ILP engine after a scheduler restart.
    ilp_queue = deque(
        (lam, assign, os.path.join(LOGDIR, slug(lam, assign)))
        for lam, assign in sorted(sat_done, reverse=True))
    confirm_queue = deque()
    with open(os.path.join(LOGDIR, "launcher.log"), "a") as log:
        log.write(f"START classes={len(pending)} target={TARGET}\n")
        log.write(f"SAT_STATE_SKIP count={len(sat_done)}\n")
        while pending or pending_pb or sat or pb or ilp or confirm or ilp_queue or confirm_queue:
            while pending and len(sat) < 4:
                lam, assign = pending.popleft()
                if (lam, assign) in sat_done:
                    log.write(f"SAT_SKIP lam={lam} assign={assign} prior_full_budget=1\n")
                    log.flush()
                    continue
                d = os.path.join(LOGDIR, slug(lam, assign))
                os.makedirs(d, exist_ok=True)
                cmd = [sys.executable, os.path.join(ROOT, "orbit_sat_feas.py"),
                       str(TARGET), lam, assign, d, str(SAT_LIMIT)]
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True)
                sat[p.pid] = (p, lam, assign, d, time.monotonic())
                log.write(f"SAT_START lam={lam} assign={assign}\n")
                log.flush()
            while pending_pb and len(pb) < 2:
                lam, assign = pending_pb.popleft()
                d = os.path.join(LOGDIR, "pb_" + slug(lam, assign))
                os.makedirs(d, exist_ok=True)
                cmd = [sys.executable, os.path.join(ROOT, "orbit_pb_feas.py"),
                       str(TARGET), lam, assign, d, str(SAT_LIMIT)]
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True)
                pb[p.pid] = (p, lam, assign, d, time.monotonic())
                log.write(f"PB_START lam={lam} assign={assign}\n")
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
            for pid, (p, lam, assign, d, started) in list(pb.items()):
                if p.poll() is None:
                    continue
                out = p.stdout.read()
                log.write(out)
                log.write(f"PB_DONE elapsed={time.monotonic()-started:.3f}\n")
                log.flush()
                del pb[pid]
                if "RESULT SAT" in out:
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
                out = p.stdout.read()
                log.write(out)
                log.write(f"ILP_DONE lam={lam} assign={assign}\n")
                log.flush()
                if "UNDECIDED" in out:
                    with open(os.path.join(LOGDIR, "cube_queue.txt"), "a") as cube:
                        cube.write(f"lam={lam} assign={assign} reason=SAT+ILP_UNDECIDED\n")
                del ilp[pid]
            time.sleep(1)
        log.write("COMPLETE\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env bash
set -u
ROOT=/home/ubuntu/repos/solving-math-problems/runs/P22/fusion1/h3
BIN=/home/ubuntu/.local/bin
cd "$ROOT"
run_one() {
  local solver="$1" input="$2" tag="$3"
  local out="${tag}.out" err="${tag}.err" wrap="${tag}.wrapper.out"
  echo "START solver=$solver input=$input tag=$tag" | tee "$wrap"
  local start end rc
  start=$(date +%s.%N)
  set +e
  (
    ulimit -v 25165824
    exec python3 - "$BIN/$solver" "$ROOT/$input" "$ROOT/$out" "$ROOT/$err" <<'PY'
import resource
import subprocess
import sys
import time

solver, input_path, out_path, err_path = sys.argv[1:]
start = time.monotonic()
with open(out_path, "w") as out, open(err_path, "w") as err:
    proc = subprocess.Popen(
        ["timeout", "--signal=TERM", "--kill-after=30", "3000", solver, input_path],
        stdout=out,
        stderr=err,
    )
    rc = proc.wait()
elapsed = time.monotonic() - start
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
print(f"PY_WRAPPER_RC={rc}", file=sys.stderr)
print(f"PY_WRAPPER_WALL_SECONDS={elapsed:.3f}", file=sys.stderr)
print(f"PY_WRAPPER_MAX_RSS_KB={ru.ru_maxrss}", file=sys.stderr)
sys.exit(rc)
PY
  ) 2>>"$wrap"
  rc=$?
  end=$(date +%s.%N)
  set -e
  python3 - "$start" "$end" "$rc" "$out" "$err" >> "$wrap" <<'PY'
import sys
start,end,rc,out,err=sys.argv[1:]
print(f"END rc={rc} wall_seconds={float(end)-float(start):.3f}")
for path in (out,err):
    try:
        lines=open(path,errors='replace').read().splitlines()
    except OSError: lines=[]
    for line in reversed(lines):
        if line.startswith(('s ','c ','v ','Restart','decisions','conflicts','propagations','memory allocation','ERROR','SIG RECEIVED')):
            print(f"last[{path.rsplit('/',1)[-1]}]={line}")
            break
PY
  # A solver result must be explicit; preserve timeout/OOM/unknown otherwise.
  if grep -Eiq '(^|[[:space:]])(s[[:space:]]+)?(TRUE|SATISFIABLE|FALSE|UNSATISFIABLE)([[:space:]]|$)' "$out" "$err"; then
    echo "DECISION_DETECTED tag=$tag" | tee -a "$wrap"
    return 10
  fi
  return 0
}
for spec in \
  'qute qbf_bloqqer_sym.qdimacs qbf_qute_bloqqer_sym' \
  'qute qbf_bloqqer_nosym.qdimacs qbf_qute_bloqqer_nosym' \
  'rareqs qbf_bloqqer_sym.qdimacs qbf_rareqs_bloqqer_sym' \
  'rareqs qbf_bloqqer_nosym.qdimacs qbf_rareqs_bloqqer_nosym'; do
  read -r solver input tag <<< "$spec"
  run_one "$solver" "$input" "$tag"
  rc=$?
  if [ "$rc" -eq 10 ]; then exit 0; fi
done

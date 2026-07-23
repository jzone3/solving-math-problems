#!/bin/bash
# Distributed cube worker. usage: cube_worker.sh N L RESIDUE MOD [JOBS]
# Solves cubes with index % MOD == RESIDUE for the standard-form T2(N) CNF,
# appends results to runs/P12/v3/cubes${N}_results/res${RESIDUE}.txt and
# pushes to the current branch periodically.
set -u
cd "$(dirname "$0")"
N=$1; L=$2; RES=$3; MOD=$4; J=${5:-8}
K=${KISSAT:-/tmp/kissat/build/kissat}
if [ ! -x "$K" ]; then
  git clone -q --depth 1 https://github.com/arminbiere/kissat.git /tmp/kissat
  (cd /tmp/kissat && ./configure && make -s -j"$(nproc)") || exit 1
fi
BASE=t2sf_$N.cnf
[ -f $BASE ] || python3 gen_cnf.py $N $BASE
D=cubes${N}_L${L}
[ -d $D ] || python3 gen_cubes.py $N $L $BASE $D
OUT=cubes${N}_results
mkdir -p $OUT
RF=$OUT/res${RES}.txt
touch $RF

solve_one() {
  f=$1
  id=$(basename $f .cnf)
  grep -q "^$id " "$RF" && return 0
  "$K" -q "$f" > "$f.log" 2>&1
  ec=$?
  if [ $ec -eq 10 ]; then
    echo "$id SAT" >> "$RF"
    grep '^v' "$f.log" >> "$OUT/${id}_model.txt"
  elif [ $ec -eq 20 ]; then
    echo "$id UNSAT" >> "$RF"
  else
    echo "$id UNKNOWN($ec)" >> "$RF"
  fi
  rm -f "$f.log"
}
export -f solve_one; export K RF OUT

push_results() {
  git add "$OUT" && git commit -q -m "cube results N=$N res=$RES ($(wc -l < $RF) done)" || return 0
  for a in 1 2 3 4 5; do
    git pull -q --rebase && git push -q && return 0
    sleep $((RANDOM % 20 + 5))
  done
}

FILES=$(ls $D/cube*.cnf | awk -v r=$RES -v m=$MOD 'NR % m == (r+1) % m')
echo "$FILES" | xargs -P $J -I{} bash -c 'solve_one {}' &
XP=$!
while kill -0 $XP 2>/dev/null; do
  for i in $(seq 20); do sleep 30; kill -0 $XP 2>/dev/null || break; done
  push_results
done
push_results
echo "worker res=$RES done: $(wc -l < $RF) cubes"

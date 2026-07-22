#!/bin/bash
# Usage: run_campaign.sh <n> <girthflag-or-none> <mod> <procs>
# Runs all residues 0..mod-1 with <procs> parallel workers, logging per-residue.
set -u
N=$1; G=$2; MOD=$3; P=$4
[ "$G" = "none" ] && G=""
DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$DIR/logs/n${N}${G:+_$G}_mod${MOD}"
mkdir -p "$LOG"
seq 0 $((MOD-1)) | xargs -P "$P" -I{} sh -c \
  "$DIR/search1h $N $G -mod $MOD -res {} > $LOG/res{}.out 2> $LOG/res{}.err && echo done > $LOG/res{}.ok"
echo "campaign n=$N g='$G' mod=$MOD finished: $(ls $LOG/*.ok 2>/dev/null | wc -l)/$MOD ok"
grep -h DONE "$LOG"/*.err | awk '{for(i=1;i<=NF;i++){split($i,a,"=");s[a[1]]+=a[2]}} END{print "totals nodes="s["nodes"], "hc_calls="s["hc_calls"], "leaves="s["leaves"]}'

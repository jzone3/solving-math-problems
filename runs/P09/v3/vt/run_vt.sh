#!/bin/bash
# Check all vertex-transitive graphs n=10..47 (Holt-Royle census, Zenodo 4010122)
# against Bollobas-Nikiforov via the check64 threshold checker.
set -u
cd "$(dirname "$0")"
for n in $(seq 10 47); do
  [ -f "done_$n" ] && continue
  tarf="alltrans$n.tar"
  if [ ! -f "$tarf" ]; then
    curl -sL -o "$tarf" "https://zenodo.org/api/records/4010122/files/alltrans$n.tar/content" || { echo "DL FAIL $n"; continue; }
  fi
  tar xf "$tarf" 2>/dev/null
  : > "vt_$n.out"
  for gz in alltrans${n}_*.gz; do
    zcat "$gz" | ../check64 >> "vt_$n.out"
  done
  grep -h CANDIDATE "vt_$n.out" > "vt_${n}.cand" || true
  total=$(grep -h '^DONE' "vt_$n.out" | awk '{split($2,a,"="); s+=a[2]} END{print s}')
  echo "n=$n graphs=$total candidates=$(wc -l < vt_${n}.cand)" | tee -a summary.txt
  rm -f alltrans${n}_*.gz "$tarf"
  touch "done_$n"
done
echo ALLDONE | tee -a summary.txt

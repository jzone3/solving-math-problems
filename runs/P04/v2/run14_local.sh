#!/bin/bash
cd "$(dirname "$0")"
mkdir -p out14
seq 704 1023 | xargs -P 8 -I{} sh -c \
  '[ -f out14/done_{} ] || { ~/nauty2_8_9/geng -q -c -d5 13 {}/1024 | ./hajos_check14 {} > out14/hard_{}.g6 2> out14/log_{}.txt && touch out14/done_{}; }'

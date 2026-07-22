#!/bin/bash
# Full n=13 verification run: 4096 geng shards on all cores.
cd "$(dirname "$0")"
mkdir -p out13
seq 0 4095 | xargs -P 8 -I{} sh -c \
  '~/nauty2_8_9/geng -q -c -d5 12 {}/4096 | ./hajos_check {} > out13/hard_{}.g6 2> out13/log_{}.txt && touch out13/done_{}'

# P04 V2 — n = 14 shard-verification child task

You are child worker K (an integer 0..15) of the P04-V2 frontier push, verifying
Hajós' conjecture for order-14 Eulerian graphs. Parent notes: `runs/P04/v2/NOTES.md`
on branch `runs/P04-v2` of jzone3/solving-math-problems.

Your shard range: residues r = 64·K .. 64·K+63 of geng's `r/1024` mod-split of
`geng -c -d5 13` (connected 13-vertex graphs, min degree ≥ 5).

## Setup

```bash
git clone https://github.com/jzone3/solving-math-problems ~/repos/solving-math-problems
cd ~/repos/solving-math-problems && git checkout runs/P04-v2
# nauty 2.8.9 geng
cd ~ && curl -sL https://pallini.di.uniroma1.it/nauty2_8_9.tar.gz | tar xz
cd nauty2_8_9 && ./configure && make geng -j8
cd ~/repos/solving-math-problems/runs/P04/v2
gcc -O3 -march=native -o hajos_check14 hajos_check14.c
pip3 install pulp networkx
```

Sanity check (must print `read=1 candidates=1 ok=0 hard=1` and one graph6 line;
then the ILP line must say SAT):

```bash
python3 -c "import networkx as nx; G=nx.complete_graph(13); G.remove_edge(0,1); G.remove_edge(1,2); print(nx.to_graph6_bytes(G,header=False).decode().strip())" > t.g6
./hajos_check14 5 < t.g6 | python3 exact_min_decomp.py
```

## Run

```bash
mkdir -p out14
for r in $(seq $((64*K)) $((64*K+63))); do echo $r; done | xargs -P 8 -I{} sh -c \
  '~/nauty2_8_9/geng -q -c -d5 13 {}/1024 | ./hajos_check14 {} > out14/hard_{}.g6 2> out14/log_{}.txt && touch out14/done_{}'
```

This is ~7 hours of 8-core compute. Monitor with `ls out14/done_* | wc -l` (expect 64).
Each shard is ~1.2e9 graphs, ~50 min single-core. If a shard fails, rerun it.

## After all shards finish

1. Run the exact ILP on all heuristic-hard graphs:
   `cat out14/hard_*.g6 | python3 exact_min_decomp.py > out14/ilp_results.txt`
   Any `UNSAT` line is a **potential counterexample to Hajós' conjecture** — report it
   immediately and loudly.
2. Aggregate: `cat out14/log_*.txt` — sum the read/candidates/ok/hard/bicon_skip fields.
3. Commit ONLY `out14/log_*.txt`, `out14/hard_*.g6`, `out14/ilp_results.txt` and a
   short `out14/SUMMARY.md` (totals, wall time, any anomalies) under
   `runs/P04/v2/child<K>/` (i.e. `mkdir child<K> && cp` them there), on a NEW branch
   `runs/P04-v2-child<K>` based off `runs/P04-v2`. Push. Do NOT create a PR.
4. Report back: shard range, totals line, #hard, ILP outcome, branch name.

Rules: never trust unverified arithmetic — the checker self-verifies every
decomposition; the ILP re-checks hard graphs exactly. Log anomalies. Do not modify
the checker source.

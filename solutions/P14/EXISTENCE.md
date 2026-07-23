# BTD(14,28; 8,3,14; 7,6) EXISTS (V1 run, 2026-07-23)

**Theorem (constructive).** A BTD(14,28; 8,3,14; 7,6) exists.
Witness: `witness-14-28-8-3-14-7-6.txt` (14×28 matrix over {0,1,2}).

This was the P14 instance listed as open in Handbook ch. VI.2 and apparently never
attempted by CPro1. It admits an automorphism sigma of order 3 acting on points as
(0 1 2)(3 4 5)(6 7 8) with points 9–13 fixed, with 6 block orbits of size 3 and 10
fixed blocks.

## How it was found
Prescribed-automorphism CP-SAT search (`runs/P14/v1/solve_auto.py`, config
`z3c3-6x3-10f`): constrain the incidence matrix to be sigma-invariant with the given
block-orbit structure; OR-Tools CP-SAT found the witness in **17 s** — after ~19 h of
unstructured search (CP-SAT + kissat) had failed. (Notably, the previous sweep of
order-7/13/14/5 automorphisms proved those all impossible for this instance.)

## Verification (two independent verifiers)
1. `solutions/P14/verify.py` (this repo, standalone, dependency-free):
   `python3 verify.py 14 28 8 3 14 7 6 witness-14-28-8-3-14-7-6.txt` → **PASS**
2. CPro1's original `problem_def.v()` verifier (github.com/Constructive-Codes/CPro1,
   design_definitions/balanced-ternary-design/problem_def.py) → **True**

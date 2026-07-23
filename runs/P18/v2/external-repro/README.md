# Reproductions of external artifact-repo certificates (priority check due diligence)

Repo: https://github.com/idealombrer/erdos-273-covering-pm1 @ 9d81d4ba5dea78fa66a2fb8ae21212fe5a8a7760
Re-run in this session (2026-07-23), unmodified scripts, exact-rational arithmetic:

- `idealombrer_theoremA_certify_exact.reprolog` — Theorem A certificate:
  eta(U_877) = 0.99991772 < 1 CERTIFIED (any #273 covering needs a modulus p-1 with p > 877).
- `idealombrer_unsat_lemmas_sieve.reprolog` — sieve non-covering certificates for
  moduli dividing L in {55440, 110880, 720720} (direct) and {55440, 110880, 166320} (parity).

These are *their* method (BBMST distortion sieve); reproduction confirms their computation,
not an independent proof of the sieve's correctness. Our independent SAT/CP-SAT runs on the
same L are logged in ../NOTES.md section 5.

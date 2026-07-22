# P08 — Graffiti conjectures 39 and 40 are TRUE (proof)

**Claim.** For every connected graph $G$ on $n \ge 1$ vertices, with distance
matrix $D$ (an $n\times n$ matrix, $D_{uu}=0$),

$$\mathrm{dev}(D) \;\le\; \min\{\, n^+(G),\; n^-(G) \,\},$$

where $\mathrm{dev}(D)$ is the (population) standard deviation of the $n^2$
entries of $D$, and $n^+(G)$, $n^-(G)$ are the numbers of positive and
negative eigenvalues of the adjacency matrix $A(G)$. This simultaneously
establishes Graffiti conjectures 39 ($\mathrm{dev}(D)\le n^+$) and
40 ($\mathrm{dev}(D)\le n^-$), listed as open in Roucairol–Cazenave
(ECAI 2025, Table 1, rows 39/40) and left open by Favaron–Mahéo–Saclé,
Discrete Math. 111 (1993).

The inequality is strict for all $n \ge 2$; for $n=1$ it is the equality
$0 = 0 \le 0$ (dev $=0$, $n^+=n^-=0$).

## Proof

Let $d = \operatorname{diam}(G)$ (finite, since $G$ is connected). If $n=1$
then $\mathrm{dev}=0=n^+=n^-$ and we are done; assume $n\ge 2$, so $d\ge 1$.

**Step 1 (Popoviciu): $\mathrm{dev}(D) \le d/2$.**
Every entry of $D$ lies in $[0,d]$. Popoviciu's inequality states that for any
finite list of reals contained in $[m,M]$, the population variance is at most
$(M-m)^2/4$, with equality iff half the values equal $m$ and half equal $M$.
Hence $\mathrm{dev}(D) \le d/2$.
(Elementary proof: for values $x_i\in[m,M]$ with mean $\mu$,
$$0 \;\le\; \frac1N\sum_i (M-x_i)(x_i-m) \;=\; -mM + (m+M)\mu - E[X^2],$$
so $\mathrm{Var} = E[X^2]-\mu^2 \le (M-\mu)(\mu-m) \le (M-m)^2/4$.)

**Step 2 (geodesics are induced paths).** Choose $u,v$ with
$d_G(u,v) = d$ and a shortest path $u=x_0,x_1,\dots,x_d=v$. For $|i-j|\ge 2$,
$x_i x_j \notin E(G)$ — otherwise the path could be shortcut, contradicting
minimality. Hence $\{x_0,\dots,x_d\}$ induces a path $P_{d+1}$ in $G$.

**Step 3 (path inertia).** The eigenvalues of the path $P_k$ are
$2\cos\frac{j\pi}{k+1}$, $j = 1,\dots,k$. The positive ones are those with
$j < (k+1)/2$, i.e. exactly $\lfloor k/2 \rfloor$ of them; by the symmetry
$j \leftrightarrow k+1-j$ of the spectrum about $0$, likewise exactly
$\lfloor k/2\rfloor$ negative ones. Thus
$n^+(P_{d+1}) = n^-(P_{d+1}) = \big\lfloor (d+1)/2 \big\rfloor \;\ge\; d/2 .$

**Step 4 (Cauchy interlacing / inertia monotonicity).** The adjacency matrix
of an induced subgraph $H$ of $G$ is a principal submatrix of $A(G)$. By
Cauchy interlacing, $\lambda_i(G) \ge \lambda_i(H)$ for $i \le |V(H)|$
(eigenvalues in decreasing order); applying this for $i \le n^+(H)$ gives
$n^+(G) \ge n^+(H)$, and applying it to $-A$ gives $n^-(G) \ge n^-(H)$.
With $H = P_{d+1}$ from Step 2:

$$n^+(G) \;\ge\; \Big\lfloor \tfrac{d+1}{2} \Big\rfloor \;\ge\; \tfrac d2,
\qquad
n^-(G) \;\ge\; \Big\lfloor \tfrac{d+1}{2} \Big\rfloor \;\ge\; \tfrac d2 .$$

**Conclusion.** Combining Steps 1–4:
$$\mathrm{dev}(D) \;\le\; \frac d2 \;\le\; \min\{n^+(G),\, n^-(G)\}. \qquad\blacksquare$$

**Strictness for $n\ge2$.** If $d$ is odd, $\lfloor (d+1)/2\rfloor = (d+1)/2 >
d/2 \ge \mathrm{dev}$. If $d$ is even (so $d\ge 2$), equality in Popoviciu
would require every entry of $D$ to be $0$ or $d$; but $G$ has an edge, giving
an entry $1 \notin \{0,d\}$, so $\mathrm{dev} < d/2 \le n^\pm$.

## Remarks on definitions

- $\mathrm{dev}$ matched against the reference implementation used for the open
  classification (RoucairolMilo/refutationGBR, `GenerateGraph.rs`,
  `CONJECTURE == 39/40`): population standard deviation over all $n^2$ entries
  of $D$ including the diagonal zeros. The proof only uses that entries lie in
  $[0, d]$, so it is robust to the common definitional variants
  (off-diagonal entries only, unordered pairs only, sample vs population
  normalization changes the bound by a factor $\sqrt{N/(N-1)}$ absorbed by the
  strict slack $\mathrm{dev} < d/2$ whenever $d \ge 2$; for $d=1$, i.e.
  complete graphs, all variants give $\mathrm{dev} \le \tfrac12 \cdot
  \sqrt{N/(N-1)} \le \sqrt{1/2}\cdot\;<\,1 \le n^\pm$ for $n \ge 2$ — checked
  directly in the verifier).
- Machine verification: `verify.py` (this directory) re-checks the lemmas and
  the final inequality on exhaustive small graphs, structured spectral-design
  families, and large random graphs/trees; exhaustive nauty-geng sweeps for
  $n \le 9$ live in `runs/P08/v3/`.

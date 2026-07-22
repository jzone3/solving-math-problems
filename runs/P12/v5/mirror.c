/* P12 V5: exhaustive search for T2(n) (n odd, <= 11) admitting a nontrivial automorphism.
 *
 * Lemmas (NOTES.md, C4/C5):
 *  - Symbol relabelings sigma with sigma(rows)=rows: sigma fixes no row unless sigma=id;
 *    orbits of prime order p require p | n; p = n forces a sequencing of Z_n (odd => none).
 *    Hence the only possible nontrivial automorphisms are reverse-relabel maps
 *    phi_tau : r -> tau o r o rho (rho = position reversal), and tau^2 must be id.
 *  - phi_tau permutes the n rows with orbits of size 1,2; n odd => some row r is fixed:
 *    tau = r o rho o r^{-1}. Relabeling by r^{-1} turns r into the identity row and tau
 *    into x -> (n-1) - x. So WLOG the square contains the identity row and is invariant
 *    under M(r)_j = (n-1) - r_{n-1-j}.
 *
 * This program exhausts that space: identity row + orbits {r, M(r)} (or M-fixed rows)
 * of identity-compatible permutations, branching on the smallest uncovered first-column
 * symbol (first column is a permutation - lemma C2). Deterministic branching => each
 * mirror-symmetric square found exactly once. Output: all such squares (expected: none).
 *
 * Build: gcc -O3 -march=native -fopenmp -o mirror mirror.c
 * Run: ./mirror n
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>

typedef __uint128_t u128;
static int N;

typedef struct { u128 m1, m2; uint8_t perm[16]; uint8_t last; } Cand;
static Cand *cands;
static long cstart[16], ccount[16];
static u128 ID_M1, ID_M2;
static long long solutions = 0;
static unsigned long long nodes_total = 0;

static inline u128 arcbit(int a, int b) { return (u128)1 << (a * N + b); }
static int K2 = 1; /* env T1=1 -> Tuscan-1 validation mode */

static long gcap = 0, gtot = 0;
static uint8_t grow[16];
static void gen(int pos, uint32_t inrow, u128 m1, u128 m2) {
    if (pos == N) {
        if (grow[N-1] == (uint8_t)(N-1)) return; /* last column: identity owns n-1 */
        if (gtot == gcap) { gcap = gcap ? gcap*2 : (1<<20); cands = realloc(cands, gcap*sizeof(Cand)); }
        Cand *c = &cands[gtot++];
        c->m1 = m1; c->m2 = m2; c->last = grow[N-1];
        memcpy(c->perm, grow, N);
        return;
    }
    int prev = grow[pos-1], prev2 = (pos >= 2) ? grow[pos-2] : -1;
    for (int b = 0; b < N; b++) {
        if (inrow & (1u << b)) continue;
        u128 a1 = arcbit(prev, b);
        if ((m1 | ID_M1) & a1) continue;
        u128 a2 = 0;
        if (K2 && prev2 >= 0) { a2 = arcbit(prev2, b); if ((m2 | ID_M2) & a2) continue; }
        grow[pos] = (uint8_t)b;
        gen(pos+1, inrow | (1u << b), m1 | a1, m2 | a2);
    }
}

static void mirror_of(const uint8_t *r, uint8_t *m) {
    for (int j = 0; j < N; j++) m[j] = (uint8_t)(N - 1 - r[N - 1 - j]);
}
static void masks_of(const uint8_t *r, u128 *m1, u128 *m2) {
    *m1 = 0; *m2 = 0;
    for (int j = 0; j + 1 < N; j++) *m1 |= arcbit(r[j], r[j+1]);
    if (K2) for (int j = 0; j + 2 < N; j++) *m2 |= arcbit(r[j], r[j+2]);
}

static uint8_t sol[16][16];
static int nsolrows;

static void emit(void) {
    #pragma omp critical
    {
        solutions++;
        printf("SOLUTION n=%d (mirror-symmetric)\n", N);
        for (int i = 0; i < nsolrows; i++) {
            for (int j = 0; j < N; j++) printf("%d ", sol[i][j]);
            printf("\n");
        }
        fflush(stdout);
    }
}

typedef struct { unsigned long long nodes; uint8_t rows[16][16]; int nrows; } Ctx;

static void dfs(u128 u1, u128 u2, uint32_t firstmask, uint32_t lastmask, Ctx *cx) {
    if (firstmask == (uint32_t)((1u << N) - 1)) {
        #pragma omp critical
        { nsolrows = cx->nrows; memcpy(sol, cx->rows, sizeof(sol)); }
        emit();
        return;
    }
    cx->nodes++;
    int s = __builtin_ctz(~firstmask & ((1u << N) - 1)); /* smallest free first symbol */
    for (long k = 0; k < ccount[s]; k++) {
        Cand *c = &cands[cstart[s] + k];
        if ((c->m1 & u1) || (c->m2 & u2) || (lastmask & (1u << c->last))) continue;
        uint8_t mr[16]; mirror_of(c->perm, mr);
        if (memcmp(mr, c->perm, N) == 0) {
            /* M-fixed row */
            memcpy(cx->rows[cx->nrows++], c->perm, N);
            dfs(u1 | c->m1, u2 | c->m2, firstmask | (1u << s), lastmask | (1u << c->last), cx);
            cx->nrows--;
        } else {
            int f2 = mr[0], l2 = mr[N-1];
            if (f2 == s || (firstmask & (1u << f2))) continue;
            if (l2 == c->last || (lastmask & (1u << l2))) continue;
            u128 mm1, mm2; masks_of(mr, &mm1, &mm2);
            if ((mm1 & (u1 | c->m1)) || (mm2 & (u2 | c->m2))) continue;
            memcpy(cx->rows[cx->nrows++], c->perm, N);
            memcpy(cx->rows[cx->nrows++], mr, N);
            dfs(u1 | c->m1 | mm1, u2 | c->m2 | mm2,
                firstmask | (1u << s) | (1u << f2),
                lastmask | (1u << c->last) | (1u << l2), cx);
            cx->nrows -= 2;
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s n\n", argv[0]); return 1; }
    N = atoi(argv[1]);
    if (N > 11) { fprintf(stderr, "n<=11\n"); return 1; }
    if (getenv("T1")) K2 = 0;

    ID_M1 = ID_M2 = 0;
    for (int j = 0; j+1 < N; j++) ID_M1 |= arcbit(j, j+1);
    if (K2) for (int j = 0; j+2 < N; j++) ID_M2 |= arcbit(j, j+2);
    for (int s = 1; s < N; s++) {
        cstart[s] = gtot;
        grow[0] = (uint8_t)s;
        gen(1, 1u << s, 0, 0);
        ccount[s] = gtot - cstart[s];
    }
    fprintf(stderr, "total candidates: %ld\n", gtot);

    /* parallelize over class-1 candidates (smallest free symbol after identity is 1) */
    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        Ctx cx; cx.nodes = 0; cx.nrows = 1;
        for (int j = 0; j < N; j++) cx.rows[0][j] = (uint8_t)j;
        #pragma omp for schedule(dynamic, 64)
        for (long k = 0; k < ccount[1]; k++) {
            Cand *c = &cands[cstart[1] + k];
            u128 u1 = ID_M1, u2 = ID_M2;
            uint32_t firstmask = 1u, lastmask = 1u << (N-1);
            if ((c->m1 & u1) || (c->m2 & u2) || (lastmask & (1u << c->last))) continue;
            uint8_t mr[16]; mirror_of(c->perm, mr);
            if (memcmp(mr, c->perm, N) == 0) {
                memcpy(cx.rows[1], c->perm, N); cx.nrows = 2;
                dfs(u1 | c->m1, u2 | c->m2, firstmask | 2u, lastmask | (1u << c->last), &cx);
                cx.nrows = 1;
            } else {
                int f2 = mr[0], l2 = mr[N-1];
                if (f2 == 1 || f2 == 0) continue;
                if (l2 == c->last || l2 == N-1) continue;
                u128 mm1, mm2; masks_of(mr, &mm1, &mm2);
                if ((mm1 & (u1 | c->m1)) || (mm2 & (u2 | c->m2))) continue;
                memcpy(cx.rows[1], c->perm, N);
                memcpy(cx.rows[2], mr, N); cx.nrows = 3;
                dfs(u1 | c->m1 | mm1, u2 | c->m2 | mm2,
                    firstmask | 2u | (1u << f2), lastmask | (1u << c->last) | (1u << l2), &cx);
                cx.nrows = 1;
            }
        }
        #pragma omp atomic
        nodes_total += cx.nodes;
    }
    printf("MIRROR DONE n=%d solutions=%lld nodes=%llu time=%.1fs\n",
           N, solutions, nodes_total, omp_get_wtime()-t0);
    return 0;
}

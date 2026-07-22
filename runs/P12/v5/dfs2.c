/* P12 V5: strong complete search for T2(n) via candidate lists + forward checking.
 *
 * WLOG row 0 = identity, and the first column is a permutation (lemma in NOTES.md),
 * so the remaining n-1 rows consist of exactly one identity-compatible permutation
 * starting with each symbol s = 1..n-1 (plus none starting with 0? row 0 starts with 0).
 * Wait: first column is a permutation containing 0 in row 0, so classes are s=1..n-1.
 *
 * All identity-compatible candidate rows are pre-generated per class; each stores its
 * distance-1 and distance-2 arc sets as 128-bit masks (n<=11: n*n=121 bits) plus its
 * last symbol. Search: repeatedly pick the unfilled class with fewest surviving
 * candidates (fail-first), try each, filter remaining classes by mask disjointness and
 * last-column availability. Empty class => backtrack. Exhaustive; counts all solutions
 * under the fixed normalization.
 *
 * Build: gcc -O3 -march=native -fopenmp -o dfs2 dfs2.c
 * Run: ./dfs2 n [start_idx end_idx]   (top-level split over class-1 candidates)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>

typedef __uint128_t u128;
static int N;

typedef struct { u128 m1, m2; uint8_t perm[16]; uint8_t last; } Cand;

static Cand *cands;            /* all candidates, grouped by class */
static long cstart[16], ccount[16]; /* per class (first symbol 1..N-1) */
static long long solutions = 0;
static unsigned long long nodes_total = 0;

static u128 ID_M1, ID_M2;      /* identity row arc masks */

static inline u128 arcbit(int a, int b) { return (u128)1 << (a * N + b); }

/* ---- candidate generation: identity-compatible perms starting with s ---- */
static long gcap = 0, gtot = 0;
static uint8_t grow[16];
static void gen(int s, int pos, uint32_t inrow, u128 m1, u128 m2) {
    if (pos == N) {
        if (grow[N-1] == (uint8_t)(N-1)) return; /* identity is last-in-row N-1 */
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
        if (prev2 >= 0) { a2 = arcbit(prev2, b); if ((m2 | ID_M2) & a2) continue; }
        grow[pos] = (uint8_t)b;
        gen(s, pos+1, inrow | (1u << b), m1 | a1, m2 | a2);
    }
}

/* ---- search ---- */
typedef struct {
    long *buf;      /* scratch index buffer */
    long cap, top;
    unsigned long long nodes;
} Scratch;

static void search(u128 u1, u128 u2, uint32_t lastmask,
                   long *lists[16], long sizes[16], uint32_t remclasses,
                   uint8_t chosen[16][16], int depth, Scratch *sc) {
    if (!remclasses) {
        #pragma omp critical
        {
            solutions++;
            printf("SOLUTION n=%d\n", N);
            for (int j = 0; j < N; j++) printf("%d ", j);
            printf("\n");
            for (int i = 0; i < N-1; i++) {
                for (int j = 0; j < N; j++) printf("%d ", chosen[i][j]);
                printf("\n");
            }
            fflush(stdout);
        }
        return;
    }
    sc->nodes++;
    /* pick smallest class */
    int best = -1; long bs = 1L << 60;
    for (uint32_t m = remclasses; m; m &= m-1) {
        int s = __builtin_ctz(m);
        if (sizes[s] < bs) { bs = sizes[s]; best = s; }
    }
    if (bs == 0) return;
    uint32_t nrem = remclasses & ~(1u << best);
    long *mylist = lists[best]; long mysize = sizes[best];
    for (long i = 0; i < mysize; i++) {
        Cand *c = &cands[mylist[i]];
        if ((c->m1 & u1) || (c->m2 & u2) || (lastmask & (1u << c->last))) continue;
        u128 n1 = u1 | c->m1, n2 = u2 | c->m2;
        uint32_t nl = lastmask | (1u << c->last);
        /* filter remaining classes into scratch */
        long ntop = sc->top;
        long *nlists[16]; long nsizes[16];
        int ok = 1;
        for (uint32_t m = nrem; m; m &= m-1) {
            int s = __builtin_ctz(m);
            long *dst = sc->buf + sc->top;
            long cnt = 0;
            long *src = lists[s]; long sz = sizes[s];
            for (long k = 0; k < sz; k++) {
                Cand *d = &cands[src[k]];
                if ((d->m1 & n1) || (d->m2 & n2) || (nl & (1u << d->last))) continue;
                dst[cnt++] = src[k];
            }
            if (!cnt) { ok = 0; sc->top = ntop; break; }
            nlists[s] = dst; nsizes[s] = cnt;
            sc->top += cnt;
        }
        if (ok) {
            memcpy(chosen[depth], c->perm, N);
            search(n1, n2, nl, nlists, nsizes, nrem, chosen, depth+1, sc);
            sc->top = ntop;
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s n [start end]\n", argv[0]); return 1; }
    N = atoi(argv[1]);
    if (N > 11) { fprintf(stderr, "n<=11 (mask width)\n"); return 1; }

    ID_M1 = ID_M2 = 0;
    for (int j = 0; j+1 < N; j++) ID_M1 |= arcbit(j, j+1);
    for (int j = 0; j+2 < N; j++) ID_M2 |= arcbit(j, j+2);

    for (int s = 1; s < N; s++) {
        cstart[s] = gtot;
        grow[0] = (uint8_t)s;
        gen(s, 1, 1u << s, 0, 0);
        ccount[s] = gtot - cstart[s];
        fprintf(stderr, "class %d: %ld candidates\n", s, ccount[s]);
    }
    fprintf(stderr, "total candidates: %ld (%.1f MB)\n", gtot, gtot*sizeof(Cand)/1048576.0);

    long lo = 0, hi = ccount[1];
    if (argc >= 4) { lo = atol(argv[2]); hi = atol(argv[3]); if (hi > ccount[1]) hi = ccount[1]; }

    /* master index lists */
    long *master = malloc(gtot * sizeof(long));
    for (long i = 0; i < gtot; i++) master[i] = i;

    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        Scratch sc;
        sc.cap = 64L * 1048576; /* 64M entries * 8B = 512MB per thread is too much; use 16M */
        sc.cap = 16L * 1048576;
        sc.buf = malloc(sc.cap * sizeof(long));
        sc.top = 0; sc.nodes = 0;
        uint8_t chosen[16][16];
        #pragma omp for schedule(dynamic, 1)
        for (long i = lo; i < hi; i++) {
            Cand *c = &cands[cstart[1] + i];
            u128 u1 = ID_M1 | c->m1, u2 = ID_M2 | c->m2;
            uint32_t lastmask = (1u << (N-1)) | (1u << c->last);
            /* filter classes 2..N-1 */
            long *lists[16]; long sizes[16]; uint32_t rem = 0;
            long ntop = 0; int ok = 1;
            for (int s = 2; s < N && ok; s++) {
                long *dst = sc.buf + ntop; long cnt = 0;
                for (long k = 0; k < ccount[s]; k++) {
                    Cand *d = &cands[cstart[s] + k];
                    if ((d->m1 & u1) || (d->m2 & u2) || (lastmask & (1u << d->last))) continue;
                    dst[cnt++] = cstart[s] + k;
                }
                if (!cnt) { ok = 0; break; }
                lists[s] = dst; sizes[s] = cnt; rem |= 1u << s; ntop += cnt;
            }
            if (ok) {
                sc.top = ntop;
                memcpy(chosen[0], c->perm, N);
                search(u1, u2, lastmask, lists, sizes, rem, chosen, 1, &sc);
            }
            if ((i % 200) == 0) {
                #pragma omp critical
                { fprintf(stderr, "top %ld/[%ld,%ld) t=%.0fs sols=%lld\n",
                          i, lo, hi, omp_get_wtime()-t0, solutions); fflush(stderr); }
            }
        }
        #pragma omp atomic
        nodes_total += sc.nodes;
    }
    printf("DONE n=%d range=[%ld,%ld) of %ld solutions=%lld nodes=%llu time=%.1fs\n",
           N, lo, hi, ccount[1], solutions, nodes_total, omp_get_wtime()-t0);
    return 0;
}

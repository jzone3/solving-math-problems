/* Kapralov-style compatible-row search for Tuscan-2 squares T2(n), n=11.
 *
 * Standard form (see NOTES.md): row 0 = identity, column 0 = 0..n-1, and the
 * last column is a permutation of the symbols.  For each r in 1..n-1 we
 * generate all "candidate rows": permutations starting with symbol r whose
 * distance-1 pairs avoid row 0's {(i,i+1)} and distance-2 pairs avoid
 * {(i,i+2)}.  A T2(n) in standard form = one candidate per group, pairwise
 * disjoint in d1-pairs and d2-pairs (masks over n*n bits), with distinct last
 * symbols.  DFS with full domain propagation (filter every remaining group's
 * list after each choice; fail if any group empties), always branching on the
 * smallest remaining group.
 *
 * Usage: ./t2dfs n mode [seed] [report_every]
 *   mode 0 = exhaustive DFS
 *   mode 1 = randomized restarts (shuffled lists, restart on exhaust of
 *            first-level subtree; runs forever until witness or SIGTERM)
 *   mode 2 = sliced exhaustive: ./t2dfs n 2 slice_id stride — fixes each
 *            group-1 candidate with index ≡ slice_id (mod stride) and
 *            exhausts its subtree; prints one line per completed subtree
 *            (checkpointable/parallelizable).
 * Prints the square and "WITNESS" if found (verify with solutions/P12/verify.py).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define NMAX 16
static int N;

typedef struct {
    uint64_t d1[4], d2[4];
    uint8_t perm[NMAX];
    uint8_t last;
} Row;

static Row *rows;            /* all candidates, grouped */
static long nrows, cap;
static long gstart[NMAX], gcount[NMAX]; /* per group r=1..N-1 */

static uint64_t r0d1[4], r0d2[4];

static void setbit(uint64_t *m, int a, int b) { int i = a * N + b; m[i >> 6] |= 1ULL << (i & 63); }
static int getbit(const uint64_t *m, int a, int b) { int i = a * N + b; return (m[i >> 6] >> (i & 63)) & 1; }

static void addrow(const uint8_t *p) {
    if (nrows == cap) { cap = cap ? cap * 2 : 1 << 20; rows = realloc(rows, cap * sizeof(Row)); }
    Row *r = &rows[nrows++];
    memset(r, 0, sizeof(Row));
    memcpy(r->perm, p, N);
    r->last = p[N - 1];
    for (int i = 0; i + 1 < N; i++) setbit(r->d1, p[i], p[i + 1]);
    for (int i = 0; i + 2 < N; i++) setbit(r->d2, p[i], p[i + 2]);
}

/* recursive generation with prefix pruning against row 0 */
static uint8_t buf[NMAX];
static int usedsym;
static void gen(int pos) {
    if (pos == N) { addrow(buf); return; }
    for (int s = 0; s < N; s++) {
        if (usedsym >> s & 1) continue;
        if (pos >= 1) {
            int a = buf[pos - 1];
            if (s == a + 1) continue;                 /* d1 pair used by row 0 */
        }
        if (pos >= 2) {
            int a = buf[pos - 2];
            if (s == a + 2) continue;                 /* d2 pair used by row 0 */
        }
        buf[pos] = s; usedsym |= 1 << s;
        gen(pos + 1);
        usedsym &= ~(1 << s);
    }
}

static int disj(const uint64_t *a, const uint64_t *b) {
    return !((a[0] & b[0]) | (a[1] & b[1]) | (a[2] & b[2]) | (a[3] & b[3]));
}

/* DFS state */
static uint64_t ud1[4], ud2[4];
static int ulast;             /* bitmask of used last symbols */
static long chosen[NMAX];
static int ngroups;
static long long nodes, best_depth_hits;
static int maxdepth;
static long long report_every = 100000000LL;

typedef struct { long *idx; long cnt; int grp; } Dom;

static const Row *R;

static int dfs(Dom *doms, int nd, int depth) {
    nodes++;
    if (nd == 0) return 1;
    /* pick smallest domain */
    int bi = 0;
    for (int i = 1; i < nd; i++) if (doms[i].cnt < doms[bi].cnt) bi = i;
    Dom d = doms[bi]; doms[bi] = doms[nd - 1]; doms[nd - 1] = d;
    if (depth > maxdepth) { maxdepth = depth; fprintf(stderr, "depth %d nodes %lld\n", depth, nodes); }
    if (nodes % report_every == 0) fprintf(stderr, "... nodes %lld depth %d maxdepth %d\n", nodes, depth, maxdepth);
    for (long k = 0; k < d.cnt; k++) {
        long ri = d.idx[k];
        const Row *r = &R[ri];
        if (ulast >> r->last & 1) continue;
        /* choose */
        uint64_t s1[4], s2[4];
        for (int j = 0; j < 4; j++) { s1[j] = ud1[j]; s2[j] = ud2[j]; ud1[j] |= r->d1[j]; ud2[j] |= r->d2[j]; }
        ulast |= 1 << r->last;
        chosen[d.grp] = ri;
        /* propagate: filter remaining nd-1 domains */
        Dom nds[NMAX];
        int ok = 1;
        long *pool = NULL; long poolsz = 0;
        for (int i = 0; i < nd - 1; i++) poolsz += doms[i].cnt;
        pool = malloc(poolsz * sizeof(long));
        long off = 0;
        for (int i = 0; i < nd - 1 && ok; i++) {
            long c = 0;
            long *dst = pool + off;
            for (long t = 0; t < doms[i].cnt; t++) {
                long q = doms[i].idx[t];
                if (disj(ud1, R[q].d1) && disj(ud2, R[q].d2) && !(ulast >> R[q].last & 1)) dst[c++] = q;
            }
            nds[i].idx = dst; nds[i].cnt = c; nds[i].grp = doms[i].grp;
            off += c;
            if (c == 0) ok = 0;
        }
        if (ok && dfs(nds, nd - 1, depth + 1)) { free(pool); return 1; }
        free(pool);
        /* unchoose */
        for (int j = 0; j < 4; j++) { ud1[j] = s1[j]; ud2[j] = s2[j]; }
        ulast &= ~(1 << r->last);
    }
    return 0;
}

static uint64_t rng;
static uint64_t xrnd(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }

int main(int argc, char **argv) {
    N = atoi(argv[1]);
    int mode = atoi(argv[2]);
    rng = argc > 3 ? strtoull(argv[3], 0, 10) : 12345;
    if (argc > 4) report_every = atoll(argv[4]);
    for (int i = 0; i + 1 < N; i++) setbit(r0d1, i, i + 1);
    for (int i = 0; i + 2 < N; i++) setbit(r0d2, i, i + 2);
    /* generate groups */
    for (int r = 1; r < N; r++) {
        gstart[r] = nrows;
        buf[0] = r; usedsym = 1 << r;
        gen(1);
        gcount[r] = nrows - gstart[r];
        fprintf(stderr, "group %d: %ld candidates\n", r, gcount[r]);
    }
    R = rows;
    ngroups = N - 1;
    /* initial domains */
    Dom doms[NMAX];
    long *idx0 = malloc(nrows * sizeof(long));
    for (int r = 1; r < N; r++) {
        doms[r - 1].idx = idx0 + gstart[r];
        doms[r - 1].cnt = gcount[r];
        doms[r - 1].grp = r;
        for (long k = 0; k < gcount[r]; k++) idx0[gstart[r] + k] = gstart[r] + k;
    }
    ulast = 1 << (N - 1); /* row 0 ends with N-1 */
    if (mode == 1) {
        for (int r = 0; r < ngroups; r++) {
            for (long k = doms[r].cnt - 1; k > 0; k--) {
                long j = xrnd() % (k + 1);
                long t = doms[r].idx[k]; doms[r].idx[k] = doms[r].idx[j]; doms[r].idx[j] = t;
            }
        }
    }
    if (mode == 2) {
        long slice = strtol(argv[3], 0, 10), stride = strtol(argv[4], 0, 10);
        report_every = 1LL << 62;
        Dom *g1 = NULL;
        for (int i = 0; i < ngroups; i++) if (doms[i].grp == 1) g1 = &doms[i];
        for (long k = slice; k < g1->cnt; k += stride) {
            long ri = g1->idx[k];
            const Row *r = &R[ri];
            for (int j = 0; j < 4; j++) { ud1[j] = r->d1[j]; ud2[j] = r->d2[j]; }
            for (int i = 0; i + 1 < N; i++) setbit(ud1, i, i + 1);
            for (int i = 0; i + 2 < N; i++) setbit(ud2, i, i + 2);
            ulast = (1 << (N - 1)) | (1 << r->last);
            chosen[1] = ri;
            Dom nds[NMAX];
            int nd2 = 0, ok = 1;
            long poolsz = 0;
            for (int i = 0; i < ngroups; i++) if (doms[i].grp != 1) poolsz += doms[i].cnt;
            long *pool = malloc(poolsz * sizeof(long));
            long off = 0;
            for (int i = 0; i < ngroups && ok; i++) {
                if (doms[i].grp == 1) continue;
                long c = 0; long *dst = pool + off;
                for (long t = 0; t < doms[i].cnt; t++) {
                    long q = doms[i].idx[t];
                    if (disj(ud1, R[q].d1) && disj(ud2, R[q].d2) && !(ulast >> R[q].last & 1)) dst[c++] = q;
                }
                nds[nd2].idx = dst; nds[nd2].cnt = c; nds[nd2].grp = doms[i].grp; nd2++;
                off += c;
                if (c == 0) ok = 0;
            }
            long long n0 = nodes;
            maxdepth = 0;
            int f = ok ? dfs(nds, nd2, 1) : 0;
            free(pool);
            printf("g1cand %ld done nodes %lld maxdepth %d found %d\n", k, nodes - n0, maxdepth, f);
            fflush(stdout);
            if (f) {
                printf("WITNESS\n");
                for (int c = 0; c < N; c++) printf("%d ", c);
                printf("\n");
                for (int rr = 1; rr < N; rr++) {
                    const Row *w = &R[chosen[rr]];
                    for (int c = 0; c < N; c++) printf("%d ", w->perm[c]);
                    printf("\n");
                }
                return 0;
            }
        }
        fprintf(stderr, "slice %ld/%ld complete: nodes %lld found 0\n", slice, stride, nodes);
        return 20;
    }
    int found = dfs(doms, ngroups, 0);
    fprintf(stderr, "nodes %lld maxdepth %d found %d\n", nodes, maxdepth, found);
    if (found) {
        printf("WITNESS\n");
        for (int c = 0; c < N; c++) printf("%d ", c);
        printf("\n");
        for (int r = 1; r < N; r++) {
            const Row *w = &R[chosen[r]];
            for (int c = 0; c < N; c++) printf("%d ", w->perm[c]);
            printf("\n");
        }
    }
    (void)best_depth_hits;
    return found ? 0 : 20;
}

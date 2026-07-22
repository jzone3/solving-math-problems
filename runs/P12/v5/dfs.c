/* P12 V5: complete DFS search for Tuscan-2 squares T2(n).
 *
 * Definition (Golomb-Taylor / CPro1): n x n array, each row a permutation of 0..n-1;
 * each ordered pair (a,b) appears with b directly right of a in exactly one row,
 * and with b two steps right of a in at most one row.
 *
 * Symmetry breaking (WLOG, proved in NOTES.md):
 *   - relabel symbols so one row is the identity; make it row 0;
 *   - first column of any T2(n) is a permutation; sort rows 1..n-1 by first symbol
 *     => row i starts with symbol i.
 *
 * Search: fill rows 1..n-1 left to right. State: dist-1 out-arc masks used1[a],
 * dist-2 masks used2[a], in-arc masks used1in[b]. Feasibility prune after each
 * completed row: every symbol needs enough remaining out-arcs (it is non-last in
 * all but one row) and in-arcs (non-first in all rows except its own).
 *
 * Parallelization: enumerate all valid completions of row 1, then OpenMP dynamic
 * over those seeds. Solutions printed immediately; count reported at end.
 *
 * Build: gcc -O3 -march=native -fopenmp -o dfs dfs.c
 * Run:   ./dfs n [max_seeds]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>

static int N;

typedef struct {
    uint16_t used1[16];    /* out-arcs used at distance 1: used1[a] bit b */
    uint16_t used1in[16];  /* in-arcs used at distance 1: used1in[b] bit a */
    uint16_t used2[16];    /* arcs used at distance 2 */
    uint8_t  waslast[16];  /* symbol already appeared in last column */
    uint8_t  row[16][16];
} State;

static long long solutions = 0;
static unsigned long long nodes_total = 0;

static void print_solution(const State *s, int rows_done) {
    #pragma omp critical
    {
        solutions++;
        printf("SOLUTION n=%d\n", N);
        for (int i = 0; i < rows_done; i++) {
            for (int j = 0; j < N; j++) printf("%d ", s->row[i][j]);
            printf("\n");
        }
        fflush(stdout);
    }
}

/* feasibility prune after completing `done` rows (rows 0..done-1 filled) */
static int feasible(const State *s, int done) {
    int R = N - done; /* rows remaining */
    for (int a = 0; a < N; a++) {
        int remout = (N - 1) - __builtin_popcount(s->used1[a]);
        int need_out = s->waslast[a] ? R : R - 1;
        if (remout < need_out) return 0;
        int remin = (N - 1) - __builtin_popcount(s->used1in[a]);
        /* a is first only in row a (rows are indexed by first symbol) */
        int need_in = (a >= done) ? R - 1 : R;
        if (remin < need_in) return 0;
    }
    return 1;
}

/* recursive fill of row r starting at position pos; row[r][0..pos-1] set */
static void dfs(State *s, int r, int pos, uint16_t inrow, unsigned long long *nodes) {
    if (pos == N) {
        int last = s->row[r][N-1];
        if (s->waslast[last]) return; /* last column must be a permutation */
        s->waslast[last] = 1;
        if (r == N - 1) {
            print_solution(s, N);
        } else if (feasible(s, r + 1)) {
            /* next row starts with symbol r+1 */
            s->row[r+1][0] = r + 1;
            dfs(s, r + 1, 1, (uint16_t)(1u << (r+1)), nodes);
        }
        s->waslast[last] = 0;
        return;
    }
    (*nodes)++;
    int prev = s->row[r][pos-1];
    int prev2 = (pos >= 2) ? s->row[r][pos-2] : -1;
    uint16_t cand = (uint16_t)(((1u << N) - 1) & ~inrow & ~s->used1[prev]);
    if (prev2 >= 0) cand &= (uint16_t)~s->used2[prev2];
    while (cand) {
        int b = __builtin_ctz(cand);
        cand &= (uint16_t)(cand - 1);
        s->row[r][pos] = (uint8_t)b;
        s->used1[prev] |= (uint16_t)(1u << b);
        s->used1in[b]  |= (uint16_t)(1u << prev);
        if (prev2 >= 0) s->used2[prev2] |= (uint16_t)(1u << b);
        dfs(s, r, pos + 1, (uint16_t)(inrow | (1u << b)), nodes);
        s->used1[prev] &= (uint16_t)~(1u << b);
        s->used1in[b]  &= (uint16_t)~(1u << prev);
        if (prev2 >= 0) s->used2[prev2] &= (uint16_t)~(1u << b);
    }
}

/* enumerate completions of row 1 (starting with symbol 1) as parallel seeds */
static uint8_t (*seeds)[16];
static long nseeds = 0, seedcap = 0;

static void collect_row1(State *s, int pos, uint16_t inrow) {
    if (pos == N) {
        if (nseeds == seedcap) {
            seedcap = seedcap ? seedcap * 2 : 1024;
            seeds = realloc(seeds, seedcap * sizeof(*seeds));
        }
        memcpy(seeds[nseeds++], s->row[1], N);
        return;
    }
    int prev = s->row[1][pos-1];
    int prev2 = (pos >= 2) ? s->row[1][pos-2] : -1;
    uint16_t cand = (uint16_t)(((1u << N) - 1) & ~inrow & ~s->used1[prev]);
    if (prev2 >= 0) cand &= (uint16_t)~s->used2[prev2];
    while (cand) {
        int b = __builtin_ctz(cand);
        cand &= (uint16_t)(cand - 1);
        s->row[1][pos] = (uint8_t)b;
        s->used1[prev] |= (uint16_t)(1u << b);
        if (prev2 >= 0) s->used2[prev2] |= (uint16_t)(1u << b);
        collect_row1(s, pos + 1, (uint16_t)(inrow | (1u << b)));
        s->used1[prev] &= (uint16_t)~(1u << b);
        if (prev2 >= 0) s->used2[prev2] &= (uint16_t)~(1u << b);
    }
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s n [max_seeds]\n", argv[0]); return 1; }
    N = atoi(argv[1]);
    long max_seeds = (argc > 2) ? atol(argv[2]) : -1;

    State base;
    memset(&base, 0, sizeof(base));
    for (int j = 0; j < N; j++) base.row[0][j] = (uint8_t)j;      /* row 0 = identity */
    for (int j = 0; j + 1 < N; j++) {
        base.used1[j]    |= (uint16_t)(1u << (j+1));
        base.used1in[j+1]|= (uint16_t)(1u << j);
        if (j + 2 < N) base.used2[j] |= (uint16_t)(1u << (j+2));
    }
    base.waslast[N-1] = 1;
    base.row[1][0] = 1;

    { State t = base; collect_row1(&t, 1, 1u << 1); }
    fprintf(stderr, "n=%d: %ld row-1 seeds\n", N, nseeds);
    if (max_seeds > 0 && nseeds > max_seeds) nseeds = max_seeds;

    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        unsigned long long nodes = 0;
        #pragma omp for schedule(dynamic, 1)
        for (long i = 0; i < nseeds; i++) {
            State s = base;
            memcpy(s.row[1], seeds[i], N);
            /* replay row 1 into masks */
            for (int j = 0; j + 1 < N; j++) {
                int a = s.row[1][j], b = s.row[1][j+1];
                s.used1[a]   |= (uint16_t)(1u << b);
                s.used1in[b] |= (uint16_t)(1u << a);
                if (j + 2 < N) s.used2[a] |= (uint16_t)(1u << s.row[1][j+2]);
            }
            int last = s.row[1][N-1];
            if (s.waslast[last]) continue;
            s.waslast[last] = 1;
            if (!feasible(&s, 2)) continue;
            s.row[2][0] = 2;
            dfs(&s, 2, 1, 1u << 2, &nodes);
            if ((i & 1023) == 0) {
                #pragma omp critical
                { fprintf(stderr, "seed %ld/%ld t=%.0fs sols=%lld\n", i, nseeds,
                          omp_get_wtime()-t0, solutions); fflush(stderr); }
            }
        }
        #pragma omp atomic
        nodes_total += nodes;
    }
    printf("DONE n=%d seeds=%ld solutions=%lld nodes=%llu time=%.1fs\n",
           N, nseeds, solutions, nodes_total, omp_get_wtime() - t0);
    return 0;
}

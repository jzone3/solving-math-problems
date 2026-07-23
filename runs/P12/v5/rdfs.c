/* P12 V5: randomized-restart DFS witness hunter for T2(n), n <= 16.
 *
 * Same normalized search as dfs.c (row 0 = identity, row i starts with symbol i,
 * last column a permutation, per-symbol dist-1/dist-2 arc masks), but candidate
 * symbols are tried in random order and the search restarts whenever a node budget
 * is exhausted. This is the CPro1-style randomized backtracking that solved several
 * open design instances; it finds witnesses (if any) far faster than complete search.
 *
 * Runs forever (until killed) or until a solution is found; each thread runs
 * independent restarts with its own PRNG stream. Progress:every restart batch reports
 * the best depth (rows completed) seen so far.
 *
 * Build: gcc -O3 -march=native -fopenmp -o rdfs rdfs.c
 * Run:   ./rdfs n seed [node_budget]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>

static int N;
static unsigned long long BUDGET = 200000;

typedef struct {
    uint16_t used1[16], used1in[16], used2[16];
    uint8_t  waslast[16];
    uint8_t  row[16][16];
} State;

static volatile int found = 0;
static int best_depth_global = 0;

static inline uint64_t rnd(uint64_t *s) { /* splitmix64 */
    uint64_t z = (*s += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

static void print_solution(const State *s) {
    #pragma omp critical
    {
        if (!found) {
            found = 1;
            printf("SOLUTION n=%d\n", N);
            for (int i = 0; i < N; i++) {
                for (int j = 0; j < N; j++) printf("%d ", s->row[i][j]);
                printf("\n");
            }
            fflush(stdout);
        }
    }
}

static int feasible(const State *s, int done) {
    int R = N - done;
    for (int a = 0; a < N; a++) {
        int remout = (N - 1) - __builtin_popcount(s->used1[a]);
        if (remout < (s->waslast[a] ? R : R - 1)) return 0;
        int remin = (N - 1) - __builtin_popcount(s->used1in[a]);
        if (remin < ((a >= done) ? R - 1 : R)) return 0;
    }
    return 1;
}

/* returns 1 if aborted due to budget */
static int rdfs(State *s, int r, int pos, uint16_t inrow,
                unsigned long long *nodes, uint64_t *rng, int *bestdepth) {
    if (found) return 1;
    if (pos == N) {
        int last = s->row[r][N-1];
        if (s->waslast[last]) return 0;
        if (r + 1 > *bestdepth) *bestdepth = r + 1;
        s->waslast[last] = 1;
        int abrt = 0;
        if (r == N - 1) {
            print_solution(s);
        } else if (feasible(s, r + 1)) {
            s->row[r+1][0] = (uint8_t)(r + 1);
            abrt = rdfs(s, r + 1, 1, (uint16_t)(1u << (r+1)), nodes, rng, bestdepth);
        }
        s->waslast[last] = 0;
        return abrt;
    }
    if (++(*nodes) > BUDGET) return 1;
    int prev = s->row[r][pos-1];
    int prev2 = (pos >= 2) ? s->row[r][pos-2] : -1;
    uint16_t cand = (uint16_t)(((1u << N) - 1) & ~inrow & ~s->used1[prev]);
    if (prev2 >= 0) cand &= (uint16_t)~s->used2[prev2];
    uint8_t list[16]; int m = 0;
    while (cand) { list[m++] = (uint8_t)__builtin_ctz(cand); cand &= (uint16_t)(cand-1); }
    for (int i = m - 1; i > 0; i--) { /* Fisher-Yates */
        int j = (int)(rnd(rng) % (unsigned)(i + 1));
        uint8_t t = list[i]; list[i] = list[j]; list[j] = t;
    }
    for (int i = 0; i < m; i++) {
        int b = list[i];
        s->row[r][pos] = (uint8_t)b;
        s->used1[prev] |= (uint16_t)(1u << b);
        s->used1in[b]  |= (uint16_t)(1u << prev);
        if (prev2 >= 0) s->used2[prev2] |= (uint16_t)(1u << b);
        int abrt = rdfs(s, r, pos + 1, (uint16_t)(inrow | (1u << b)), nodes, rng, bestdepth);
        s->used1[prev] &= (uint16_t)~(1u << b);
        s->used1in[b]  &= (uint16_t)~(1u << prev);
        if (prev2 >= 0) s->used2[prev2] &= (uint16_t)~(1u << b);
        if (abrt) return 1;
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s n seed [node_budget]\n", argv[0]); return 1; }
    N = atoi(argv[1]);
    uint64_t seed0 = (uint64_t)atoll(argv[2]);
    if (argc > 3) BUDGET = (unsigned long long)atoll(argv[3]);

    State base;
    memset(&base, 0, sizeof(base));
    for (int j = 0; j < N; j++) base.row[0][j] = (uint8_t)j;
    for (int j = 0; j + 1 < N; j++) {
        base.used1[j]     |= (uint16_t)(1u << (j+1));
        base.used1in[j+1] |= (uint16_t)(1u << j);
        if (j + 2 < N) base.used2[j] |= (uint16_t)(1u << (j+2));
    }
    base.waslast[N-1] = 1;

    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        uint64_t rng = seed0 * 1000003ULL + (uint64_t)omp_get_thread_num() * 77777777ULL + 1;
        int bestdepth = 1;
        unsigned long long restarts = 0;
        while (!found) {
            State s = base;
            unsigned long long nodes = 0;
            s.row[1][0] = 1;
            rdfs(&s, 1, 1, 1u << 1, &nodes, &rng, &bestdepth);
            restarts++;
            if ((restarts & 1023) == 0) {
                #pragma omp critical
                {
                    if (bestdepth > best_depth_global) best_depth_global = bestdepth;
                    fprintf(stderr, "thr %d: %llu restarts, bestdepth=%d (global %d) t=%.0fs\n",
                            omp_get_thread_num(), restarts, bestdepth, best_depth_global,
                            omp_get_wtime()-t0);
                    fflush(stderr);
                }
            }
        }
    }
    return found ? 0 : 1;
}

/* t2gen.c — memory-free randomized witness hunt for Tuscan-2 squares T2(n).
 *
 * Unlike t2dfs.c (which materializes all compatible rows; infeasible for
 * n=13: ~83M rows/group), this generates rows on the fly inside the DFS:
 * row r must start with symbol r (standard form: row 0 = identity,
 * column 0 = identity), avoid all used distance-1/distance-2 pairs, and
 * end in an unused last-column symbol. Symbol order is randomized at each
 * position; restarts with a node budget.
 *
 * Usage: ./t2gen n seed [budget_nodes_per_restart]
 * Prints WITNESS + square on success (verify with solutions/P12/verify.py).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define NMAX 16
static int N;
static uint64_t ud1[4], ud2[4];
static int ulast;
static uint8_t sq[NMAX][NMAX];
static long long nodes, budget_limit, budget;
static int maxdepth_row;

static uint64_t rng;
static uint64_t xrnd(void) {
    rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng;
}

static int pget(const uint64_t *m, int a, int b) {
    int i = a * N + b; return (m[i >> 6] >> (i & 63)) & 1;
}
static void pset(uint64_t *m, int a, int b) {
    int i = a * N + b; m[i >> 6] |= 1ULL << (i & 63);
}
static void pclr(uint64_t *m, int a, int b) {
    int i = a * N + b; m[i >> 6] &= ~(1ULL << (i & 63));
}

static int fillrow(int r, int pos, int used);
static int placerow(int r);

/* extend row r at position pos; used = bitmask of symbols in the row */
static int fillrow(int r, int pos, int used) {
    if (++nodes > budget_limit) return -1;
    if (pos == N) {
        int last = sq[r][N - 1];
        if (ulast >> last & 1) return 0;
        ulast |= 1 << last;
        int f = placerow(r + 1);
        if (f) return f;
        ulast &= ~(1 << last);
        return 0;
    }
    int ord[NMAX];
    int cnt = 0;
    for (int s = 0; s < N; s++) if (!(used >> s & 1)) ord[cnt++] = s;
    for (int i = cnt - 1; i > 0; i--) {
        int j = xrnd() % (i + 1);
        int t = ord[i]; ord[i] = ord[j]; ord[j] = t;
    }
    int a1 = sq[r][pos - 1];
    int a2 = pos >= 2 ? sq[r][pos - 2] : -1;
    for (int i = 0; i < cnt; i++) {
        int s = ord[i];
        if (pget(ud1, a1, s)) continue;
        if (a2 >= 0 && pget(ud2, a2, s)) continue;
        pset(ud1, a1, s);
        if (a2 >= 0) pset(ud2, a2, s);
        sq[r][pos] = s;
        int f = fillrow(r, pos + 1, used | 1 << s);
        if (f) return f;
        pclr(ud1, a1, s);
        if (a2 >= 0) pclr(ud2, a2, s);
    }
    return 0;
}

static int placerow(int r) {
    if (r > maxdepth_row) {
        maxdepth_row = r;
        fprintf(stderr, "row %d nodes %lld\n", r, nodes);
    }
    if (r == N) return 1;
    sq[r][0] = r;
    return fillrow(r, 1, 1 << r);
}

int main(int argc, char **argv) {
    N = atoi(argv[1]);
    rng = argc > 2 ? strtoull(argv[2], 0, 10) : 12345;
    budget = argc > 3 ? atoll(argv[3]) : 5000000;
    if (!rng) rng = 1;
    for (int c = 0; c < N; c++) sq[0][c] = c;
    long long restarts = 0;
    for (;;) {
        memset(ud1, 0, sizeof ud1);
        memset(ud2, 0, sizeof ud2);
        for (int c = 0; c + 1 < N; c++) pset(ud1, c, c + 1);
        for (int c = 0; c + 2 < N; c++) pset(ud2, c, c + 2);
        ulast = 1 << (N - 1);
        budget_limit = nodes + budget;
        int f = placerow(1);
        restarts++;
        if (f == 1) {
            printf("WITNESS\n");
            for (int r = 0; r < N; r++) {
                for (int c = 0; c < N; c++) printf("%d ", sq[r][c]);
                printf("\n");
            }
            return 0;
        }
        if (restarts % 200 == 0)
            fprintf(stderr, "restarts %lld nodes %lld maxrow %d\n",
                    restarts, nodes, maxdepth_row);
    }
}

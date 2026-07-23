/* circ.c — search circular m x (m+1) Tuscan-2 arrays (m even) and try to
 * convert each into an (m+1) x (m+1) Tuscan-2 SQUARE via the cut trick:
 *
 * A circular m x (m+1) Tuscan-2 array (n = m+1 symbols) has every ordered
 * pair exactly once at circular distance 1 (m rows x n slots = n(n-1)) and
 * exactly once at circular distance 2.  Cut each circular row between two
 * consecutive cells: each cut loses one d1 pair and two d2 pairs.  If the m
 * lost d1 edges form a directed Hamiltonian path on the n symbols, and that
 * path's own distance-2 pairs are among the 2m lost d2 pairs, then the m cut
 * rows plus the path as an (m+1)-th row form a Tuscan-2 square of order n.
 *
 * Symmetry: relabel so row 0 is the circular identity (0,1,...,n-1); each
 * row is rotated to start with symbol 0; rows ordered by their second symbol.
 *
 * Usage: ./circ n mode [seed] [budget]
 *   n = square order (= m+1, odd); mode 0 exhaustive, 1 randomized restarts.
 * Prints any Tuscan-2 square found (verify with solutions/P12/verify.py).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define NMAX 16
static int N, M;                     /* N symbols, M = N-1 circular rows */
static uint64_t ud1[4], ud2[4];      /* used pair bitmaps */
static uint8_t rowsv[NMAX][NMAX];    /* rows 0..M-1, each length N */
static long long nodes, budget_limit, budget;
static int mode, maxrow_seen;
static long long arrays_found;

static uint64_t rng = 999331;
static uint64_t xrnd(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }

static int pget(const uint64_t *m, int a, int b) { int i = a * N + b; return (m[i >> 6] >> (i & 63)) & 1; }
static void pset(uint64_t *m, int a, int b) { int i = a * N + b; m[i >> 6] |= 1ULL << (i & 63); }
static void pclr(uint64_t *m, int a, int b) { int i = a * N + b; m[i >> 6] &= ~(1ULL << (i & 63)); }

/* ---------- cut trick ---------- */
static int rsel_[NMAX], pathsym_[NMAX];

static void emit_square(void) {
    static int cposl[NMAX][NMAX];
    for (int r = 0; r < M; r++)
        for (int c = 0; c < N; c++) cposl[r][rowsv[r][c]] = c;
    /* verify path d2 subset-of-lost condition */
    uint64_t lost2[4] = {0, 0, 0, 0};
    for (int d = 0; d < M; d++) {
        int r = rsel_[d];
        int c = cposl[r][pathsym_[d]];
        pset(lost2, rowsv[r][(c - 1 + N) % N], rowsv[r][(c + 1) % N]);
        pset(lost2, rowsv[r][c], rowsv[r][(c + 2) % N]);
    }
    uint64_t seen[4] = {0, 0, 0, 0};
    for (int i = 0; i + 2 <= M; i++) {
        if (!pget(lost2, pathsym_[i], pathsym_[i + 2])) return;
        if (pget(seen, pathsym_[i], pathsym_[i + 2])) return;
        pset(seen, pathsym_[i], pathsym_[i + 2]);
    }
    printf("SQUARE\n");
    for (int d = 0; d < M; d++) {
        int r = rsel_[d];
        int cc = cposl[r][pathsym_[d]];
        for (int j = 1; j <= N; j++) printf("%d ", rowsv[r][(cc + j) % N]);
        printf("\n");
    }
    for (int i = 0; i <= M; i++) printf("%d ", pathsym_[i]);
    printf("\n");
    fflush(stdout);
    exit(0);
}

/* extend Ham path of lost edges: one edge per unused row */
static void extend(int depth, int cursym, int visited, int usedrow,
                   int cposl[NMAX][NMAX]) {
    if (depth == M) { emit_square(); return; }
    for (int r = 0; r < M; r++) {
        if (usedrow >> r & 1) continue;
        int c = cposl[r][cursym];
        int nxt = rowsv[r][(c + 1) % N];
        if (visited >> nxt & 1) continue;
        rsel_[depth] = r;
        pathsym_[depth + 1] = nxt;
        extend(depth + 1, nxt, visited | 1 << nxt, usedrow | 1 << r, cposl);
    }
}

static void try_cuts(void) {
    static int cposl[NMAX][NMAX];
    for (int r = 0; r < M; r++)
        for (int c = 0; c < N; c++) cposl[r][rowsv[r][c]] = c;
    for (int start = 0; start < N; start++) {
        pathsym_[0] = start;
        extend(0, start, 1 << start, 0, cposl);
    }
}

/* ---------- circular array DFS ---------- */
static int fillrow(int r, int pos, int used);

static int placerow(int r) {
    if (r > maxrow_seen) {
        maxrow_seen = r;
        fprintf(stderr, "circ row %d nodes %lld\n", r, nodes);
    }
    if (r == M) {
        arrays_found++;
        if (arrays_found % 1000 == 1)
            fprintf(stderr, "arrays found: %lld (nodes %lld) — trying cuts\n", arrays_found, nodes);
        try_cuts();
        return 0;   /* keep searching for more arrays */
    }
    rowsv[r][0] = 0;
    return fillrow(r, 1, 1);
}

static int fillrow(int r, int pos, int used) {
    if (++nodes > budget_limit && mode == 1) return -1;
    uint8_t *row = rowsv[r];
    if (pos == N) {
        /* close the circle: pairs (row[N-1], 0) d1; (row[N-2],0),(row[N-1],row[1]) d2 */
        int a = row[N - 1], b = row[N - 2];
        if (pget(ud1, a, 0)) return 0;
        if (pget(ud2, b, 0) || pget(ud2, a, row[1])) return 0;
        pset(ud1, a, 0); pset(ud2, b, 0); pset(ud2, a, row[1]);
        int f = placerow(r + 1);
        pclr(ud1, a, 0); pclr(ud2, b, 0); pclr(ud2, a, row[1]);
        return f;
    }
    int ord[NMAX], cnt = 0;
    for (int s = 1; s < N; s++) if (!(used >> s & 1)) ord[cnt++] = s;
    if (mode == 1)
        for (int i = cnt - 1; i > 0; i--) { int j = xrnd() % (i + 1); int t = ord[i]; ord[i] = ord[j]; ord[j] = t; }
    int a1 = row[pos - 1];
    int a2 = pos >= 2 ? row[pos - 2] : -1;
    for (int i = 0; i < cnt; i++) {
        int s = ord[i];
        /* canonical row order: second symbols strictly increasing */
        if (pos == 1 && r >= 2 && s <= rowsv[r - 1][1]) continue;
        if (pget(ud1, a1, s)) continue;
        if (a2 >= 0 && pget(ud2, a2, s)) continue;
        pset(ud1, a1, s);
        if (a2 >= 0) pset(ud2, a2, s);
        row[pos] = s;
        int f = fillrow(r, pos + 1, used | 1 << s);
        pclr(ud1, a1, s);
        if (a2 >= 0) pclr(ud2, a2, s);
        if (f) return f;
    }
    return 0;
}

int main(int argc, char **argv) {
    N = atoi(argv[1]);
    M = N - 1;
    mode = argc > 2 ? atoi(argv[2]) : 0;
    if (argc > 3) { rng = strtoull(argv[3], 0, 10); if (!rng) rng = 1; }
    budget = argc > 4 ? atoll(argv[4]) : 50000000;
    /* row 0 = circular identity 0,1,...,N-1 */
    for (int c = 0; c < N; c++) rowsv[0][c] = c;
    long long restarts = 0;
    for (;;) {
        memset(ud1, 0, sizeof ud1);
        memset(ud2, 0, sizeof ud2);
        for (int c = 0; c < N; c++) {
            pset(ud1, c, (c + 1) % N);
            pset(ud2, c, (c + 2) % N);
        }
        budget_limit = mode == 1 ? nodes + budget : (1LL << 62);
        maxrow_seen = 0;
        placerow(1);
        if (mode == 0) {
            fprintf(stderr, "EXHAUSTED: arrays %lld nodes %lld\n", arrays_found, nodes);
            return 1;
        }
        restarts++;
        if (restarts % 100 == 0)
            fprintf(stderr, "restarts %lld nodes %lld arrays %lld\n", restarts, nodes, arrays_found);
    }
}

/* Exhaustive DFS for Tuscan-2 squares T2(n), standard form.
 * v3: adds reachability pruning on top of t2dfs2's degree pruning, plus
 * optional randomized value ordering for witness hunting (-r seed).
 *
 * Encoding/symmetry breaking (complete for existence): row 0 = identity,
 * row i starts with symbol i (first column of a T2 square is forcibly a
 * permutation; relabel symbols + reorder rows brings any T2(n) to this
 * standard form).
 *
 * Pruning at each partial row (tail y, unplaced set U):
 *  - degree: succ(u) = ~used1[u] & U; if empty, u must be row end (not in
 *    lastmask, at most one such u). pred(u) via avail_in[u]; if empty prune;
 *    at most one u with pred=={y}.
 *  - reachability: all of U must be reachable from y in the dist-1
 *    availability digraph restricted to U (necessary for a Ham path).
 *
 * Usage: ./t2dfs3 n [split_mod split_res] [-r seed]
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

static int n;
static uint32_t used1[16], used2[16], avail_in[16];
static uint32_t lastmask;
static int rows[16][16];
static uint32_t fullmask;
static unsigned long long nodes = 0, sols = 0;
static long long row1count = -1;
static int split_mod = 1, split_res = 0;
static uint64_t rng = 0;
static int randomize = 0;
static unsigned long long node_limit = 0; /* 0 = no limit */
static int stop_after_first = 0;

static uint64_t xrand(void) { /* xorshift64 */
    rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng;
}

static void print_solution(void) {
    for (int r = 0; r < n; r++)
        for (int c = 0; c < n; c++) printf("%d%c", rows[r][c], c == n-1 ? '\n' : ' ');
    printf("\n");
    fflush(stdout);
}

static void search_row(int r, int pos, uint32_t inrow);

static void next_row(int r) {
    if (r == n) {
        sols++; print_solution();
        if (stop_after_first) exit(0);
        return;
    }
    rows[r][0] = r;
    search_row(r, 1, 1u << r);
}

static int feasible(int y, uint32_t U) {
    uint32_t ybit = 1u << y;
    int forced_end = 0, forced_next = 0;
    uint32_t m = U;
    while (m) {
        int u = __builtin_ctz(m);
        m &= m - 1;
        uint32_t ubit = 1u << u;
        if (!(~used1[u] & U & ~ubit)) {
            if ((lastmask & ubit) || ++forced_end > 1) return 0;
        }
        uint32_t pred = avail_in[u] & ((U | ybit) & ~ubit);
        if (!pred) return 0;
        if (pred == ybit && ++forced_next > 1) return 0;
    }
    if (!(U & ~lastmask)) return 0;
    /* reachability from y through availability digraph within U */
    uint32_t reach = ~used1[y] & U, frontier = reach;
    while (frontier) {
        uint32_t nf = 0;
        uint32_t f = frontier;
        while (f) {
            int u = __builtin_ctz(f); f &= f - 1;
            nf |= ~used1[u] & U;
        }
        nf &= ~reach;
        reach |= nf;
        frontier = nf;
    }
    if ((reach & U) != U) return 0;
    return 1;
}

static void search_row(int r, int pos, uint32_t inrow) {
    if (node_limit && ++nodes > node_limit) { fprintf(stderr, "NODE_LIMIT\n"); exit(3); }
    if (!node_limit) nodes++;
    int y = rows[r][pos-1];
    uint32_t cand = fullmask & ~inrow & ~used1[y];
    if (pos >= 2) cand &= ~used2[rows[r][pos-2]];
    if (pos == n-1) cand &= ~lastmask;
    int order[16], cnt = 0;
    while (cand) { int x = __builtin_ctz(cand); cand &= cand - 1; order[cnt++] = x; }
    if (randomize) {
        for (int i = cnt - 1; i > 0; i--) {
            int j = xrand() % (i + 1);
            int t = order[i]; order[i] = order[j]; order[j] = t;
        }
    }
    for (int i = 0; i < cnt; i++) {
        int x = order[i];
        rows[r][pos] = x;
        used1[y] |= 1u << x;
        avail_in[x] &= ~(1u << y);
        int z = -1;
        if (pos >= 2) { z = rows[r][pos-2]; used2[z] |= 1u << x; }
        if (pos == n-1) {
            lastmask |= 1u << x;
            if (r == 1) {
                row1count++;
                if (row1count % split_mod == split_res) next_row(r+1);
            } else next_row(r+1);
            lastmask &= ~(1u << x);
        } else {
            uint32_t U = fullmask & ~(inrow | (1u << x));
            if (pos + 2 > n - 1 || feasible(x, U))
                search_row(r, pos+1, inrow | (1u << x));
        }
        used1[y] &= ~(1u << x);
        avail_in[x] |= 1u << y;
        if (z >= 0) used2[z] &= ~(1u << x);
    }
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s n [split_mod split_res] [-r seed] [-L nodelimit] [-1]\n", argv[0]); return 1; }
    n = atoi(argv[1]);
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "-r")) { randomize = 1; rng = strtoull(argv[++i], 0, 10) * 2654435769ULL + 1; }
        else if (!strcmp(argv[i], "-L")) node_limit = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "-1")) stop_after_first = 1;
        else { split_mod = atoi(argv[i]); split_res = atoi(argv[++i]); }
    }
    fullmask = (1u << n) - 1;
    for (int c = 0; c < n; c++) rows[0][c] = c;
    for (int u = 0; u < n; u++) avail_in[u] = fullmask & ~(1u << u);
    for (int c = 0; c < n-1; c++) { used1[c] = 1u << (c+1); avail_in[c+1] &= ~(1u << c); }
    for (int c = 0; c < n-2; c++) used2[c] = 1u << (c+2);
    lastmask = 1u << (n-1);
    next_row(1);
    fprintf(stderr, "n=%d split=%d/%d solutions=%llu nodes=%llu row1count=%lld\n",
            n, split_res, split_mod, sols, nodes, row1count+1);
    return 0;
}

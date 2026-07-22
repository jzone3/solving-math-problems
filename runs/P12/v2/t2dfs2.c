/* Exhaustive DFS for Tuscan-2 squares T2(n), standard form, with
 * pair-availability (Hamiltonian-path degree) pruning.
 *
 * Same encoding/symmetry breaking as t2dfs.c (row i starts with symbol i,
 * row 0 = identity; complete for existence). Extra pruning at each node,
 * over the set U of symbols not yet placed in the current row:
 *   - succ(u) = symbols that can still follow u at dist 1 within this row.
 *     If succ(u) & U is empty, u must be the row's last symbol: it must not
 *     be in lastmask, and at most one such u may exist.
 *   - pred(u) = symbols in U (or the current tail y) that can precede u.
 *     If empty -> prune. At most one u may have pred(u) == {y} only.
 * avail_in[u] = mask of v with (v,u) unused at dist 1, kept incrementally.
 *
 * Usage: ./t2dfs2 n [split_mod split_res]
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static int n;
static uint32_t used1[16], used2[16], avail_in[16];
static uint32_t lastmask;
static int rows[16][16];
static uint32_t fullmask;
static unsigned long long nodes = 0, sols = 0, pruned = 0;
static long long row1count = -1;
static int split_mod = 1, split_res = 0;

static void print_solution(void) {
    for (int r = 0; r < n; r++)
        for (int c = 0; c < n; c++) printf("%d%c", rows[r][c], c == n-1 ? '\n' : ' ');
    printf("\n");
    fflush(stdout);
}

static void search_row(int r, int pos, uint32_t inrow);

static void next_row(int r) {
    if (r == n) { sols++; print_solution(); return; }
    rows[r][0] = r;
    search_row(r, 1, 1u << r);
}

/* returns 0 if the partial row (tail y, unplaced set U) is infeasible */
static int feasible(int y, uint32_t U) {
    uint32_t ybit = 1u << y;
    int forced_end = 0, forced_next = 0;
    uint32_t m = U;
    while (m) {
        int u = __builtin_ctz(m);
        m &= m - 1;
        uint32_t ubit = 1u << u;
        uint32_t succ = ~used1[u] & U & ~ubit;
        if (!succ) {
            if ((lastmask & ubit) || ++forced_end > 1) return 0;
        }
        uint32_t pred = avail_in[u] & ((U | ybit) & ~ubit);
        if (!pred) return 0;
        if (pred == ybit && ++forced_next > 1) return 0;
    }
    if (!(U & ~lastmask)) return 0; /* some symbol must be an allowed end */
    return 1;
}

static void search_row(int r, int pos, uint32_t inrow) {
    nodes++;
    int y = rows[r][pos-1];
    uint32_t cand = fullmask & ~inrow & ~used1[y];
    if (pos >= 2) cand &= ~used2[rows[r][pos-2]];
    if (pos == n-1) cand &= ~lastmask;
    while (cand) {
        int x = __builtin_ctz(cand);
        cand &= cand - 1;
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
            if (pos + 2 <= n - 1 ? feasible(x, U) : 1)
                search_row(r, pos+1, inrow | (1u << x));
            else pruned++;
        }
        used1[y] &= ~(1u << x);
        avail_in[x] |= 1u << y;
        if (z >= 0) used2[z] &= ~(1u << x);
    }
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s n [split_mod split_res]\n", argv[0]); return 1; }
    n = atoi(argv[1]);
    if (argc >= 4) { split_mod = atoi(argv[2]); split_res = atoi(argv[3]); }
    fullmask = (1u << n) - 1;
    for (int c = 0; c < n; c++) rows[0][c] = c;
    for (int u = 0; u < n; u++) avail_in[u] = fullmask & ~(1u << u);
    for (int c = 0; c < n-1; c++) { used1[c] = 1u << (c+1); avail_in[c+1] &= ~(1u << c); }
    for (int c = 0; c < n-2; c++) used2[c] = 1u << (c+2);
    lastmask = 1u << (n-1);
    next_row(1);
    fprintf(stderr, "n=%d split=%d/%d solutions=%llu nodes=%llu pruned=%llu row1count=%lld\n",
            n, split_res, split_mod, sols, nodes, pruned, row1count+1);
    return 0;
}

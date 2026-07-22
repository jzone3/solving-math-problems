/* Exhaustive DFS for Tuscan-2 squares T2(n), standard form.
 *
 * Definition (Golomb-Taylor 1985; CPro1 tuscan-2-square/problem_def.py):
 * n x n array, each row a permutation of {0..n-1}; every ordered pair (a,b)
 * appears with b directly right of a in AT MOST one row (counting forces
 * exactly one for an n-row square), and with b two steps right of a in at
 * most one row.
 *
 * Symmetry breaking (standard form, complete w.r.t. existence):
 *  - Any T2(n) can be relabelled so some row is the identity, and rows
 *    reordered. Since each symbol is first in exactly one row (out-degree
 *    counting), rows can be sorted by first symbol: row i starts with i,
 *    row 0 = identity. Every T2(n) is equivalent to one in this form, so
 *    exhausting standard forms decides existence.
 *
 * State: used1[a], used2[a] bitmasks of dist-1 / dist-2 successors used;
 * lastmask = set of symbols already used as a row's last element (each
 * symbol must be last exactly once).
 *
 * Usage: ./t2dfs n [split_mod split_res]
 *   Optional split: distribute work by a counter over row-1 (second row)
 *   completions: only process subtree where (row1_index % split_mod)==res.
 * Prints every solution found (one row per line, rows separated; solutions
 * separated by blank line) and final counts.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

static int n;
static uint32_t used1[16], used2[16];
static uint32_t lastmask;
static int rows[16][16];
static uint32_t fullmask;
static unsigned long long nodes = 0, sols = 0;
static long long row1count = -1; /* counter of completed second rows */
static int split_mod = 1, split_res = 0;

static void print_solution(void) {
    for (int r = 0; r < n; r++) {
        for (int c = 0; c < n; c++) printf("%d%c", rows[r][c], c == n-1 ? '\n' : ' ');
    }
    printf("\n");
    fflush(stdout);
}

static void search_row(int r, int pos, uint32_t inrow);

static void next_row(int r) {
    if (r == n) { sols++; print_solution(); return; }
    rows[r][0] = r;
    search_row(r, 1, 1u << r);
}

static void search_row(int r, int pos, uint32_t inrow) {
    nodes++;
    int y = rows[r][pos-1];
    uint32_t cand = fullmask & ~inrow & ~used1[y];
    if (pos >= 2) cand &= ~used2[rows[r][pos-2]];
    if (pos == n-1) cand &= ~lastmask; /* last column must be a permutation */
    while (cand) {
        int x = __builtin_ctz(cand);
        cand &= cand - 1;
        rows[r][pos] = x;
        used1[y] |= 1u << x;
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
            search_row(r, pos+1, inrow | (1u << x));
        }
        used1[y] &= ~(1u << x);
        if (z >= 0) used2[z] &= ~(1u << x);
    }
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s n [split_mod split_res]\n", argv[0]); return 1; }
    n = atoi(argv[1]);
    if (argc >= 4) { split_mod = atoi(argv[2]); split_res = atoi(argv[3]); }
    fullmask = (1u << n) - 1;
    /* row 0 = identity */
    for (int c = 0; c < n; c++) rows[0][c] = c;
    for (int c = 0; c < n-1; c++) used1[c] = 1u << (c+1);
    for (int c = 0; c < n-2; c++) used2[c] = 1u << (c+2);
    lastmask = 1u << (n-1);
    next_row(1);
    fprintf(stderr, "n=%d split=%d/%d solutions=%llu nodes=%llu row1count=%lld\n",
            n, split_res, split_mod, sols, nodes, row1count+1);
    return 0;
}

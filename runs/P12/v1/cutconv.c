/* cutconv: read circular (n-1) x n Tuscan-2 arrays from stdin (one array =
 * n-1 lines of n numbers; blank line between arrays) and run the exact
 * cut-conversion search (see mult_circ.py try_cuts docstring for the
 * characterization).  Prints SQUARE + n rows on success and exits 0.
 * Usage: ./cutconv n < arrays.txt */
#include <stdio.h>
#include <stdlib.h>

#define NMAX 16
static int N, M;
static int rows[NMAX][NMAX];
static int cpos[NMAX][NMAX];
static int erow[NMAX][NMAX], epos[NMAX][NMAX];   /* d1 edge (x,y) -> row,pos */
static int srow[NMAX][NMAX], spos[NMAX][NMAX];   /* d2 span (x,y) -> row,pos */
static int rsel[NMAX], path[NMAX + 1], cutof[NMAX];
static unsigned allowed[NMAX];                   /* bitmask of allowed cut positions; 0 = unconstrained */

static int extend(int depth, int cur, int visited, int usedrow) {
    if (depth == M) return 1;
    for (int nxt = 0; nxt < N; nxt++) {
        if (visited >> nxt & 1) continue;
        int r = erow[cur][nxt];
        if (r < 0 || (usedrow >> r & 1)) continue;
        int c = epos[cur][nxt];
        if (allowed[r] && !(allowed[r] >> c & 1)) continue;
        int crp = -1; unsigned save = 0;
        if (depth >= 1) {
            int px = path[depth - 1];
            int rp = srow[px][nxt], cp = spos[px][nxt];
            unsigned ok = (1u << cp) | (1u << ((cp + 1) % N));
            if (rp == r) {
                if (!(ok >> c & 1)) continue;
            } else if (usedrow >> rp & 1) {
                if (!(ok >> cutof[rp] & 1)) continue;
            } else {
                unsigned prev = allowed[rp];
                unsigned inter = prev ? (prev & ok) : ok;
                if (!inter) continue;
                crp = rp; save = prev;
                allowed[rp] = inter;
            }
        }
        rsel[depth] = r; cutof[r] = c;
        unsigned save_r = allowed[r]; allowed[r] = 0;
        path[depth + 1] = nxt;
        if (extend(depth + 1, nxt, visited | 1 << nxt, usedrow | 1 << r)) return 1;
        allowed[r] = save_r;
        if (crp >= 0) allowed[crp] = save;
    }
    return 0;
}

int main(int argc, char **argv) {
    N = atoi(argv[1]); M = N - 1;
    long long count = 0;
    for (;;) {
        for (int r = 0; r < M; r++)
            for (int c = 0; c < N; c++)
                if (scanf("%d", &rows[r][c]) != 1) {
                    fprintf(stderr, "cutconv: %lld arrays, none converted\n", count);
                    return 1;
                }
        count++;
        for (int a = 0; a < N; a++)
            for (int b = 0; b < N; b++) erow[a][b] = srow[a][b] = -1;
        for (int r = 0; r < M; r++)
            for (int c = 0; c < N; c++) {
                int x = rows[r][c];
                cpos[r][x] = c;
                int y1 = rows[r][(c + 1) % N], y2 = rows[r][(c + 2) % N];
                erow[x][y1] = r; epos[x][y1] = c;
                srow[x][y2] = r; spos[x][y2] = c;
            }
        for (int start = 0; start < N; start++) {
            for (int r = 0; r < M; r++) allowed[r] = 0;
            path[0] = start;
            if (extend(0, start, 1 << start, 0)) {
                printf("SQUARE (array #%lld)\n", count);
                for (int d = 0; d < M; d++) {
                    int r = rsel[d], c = cpos[r][path[d]];
                    for (int j = 1; j <= N; j++) printf("%d ", rows[r][(c + j) % N]);
                    printf("\n");
                }
                for (int i = 0; i <= M; i++) printf("%d ", path[i]);
                printf("\n");
                return 0;
            }
        }
        if (count % 100000 == 0) fprintf(stderr, "cutconv: %lld arrays tried\n", count);
    }
}

/* Reads GENREG -a stdout adjacency-list stream, tests 3-colorability.
 * Prints any graph that is NOT 3-colorable, plus a final count summary.
 * Usage: filter3col n < stream */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int n;
static int adj[64][8], deg[64];
static int color[64];

static int ok(int v, int c) {
    for (int i = 0; i < deg[v]; i++) {
        int u = adj[v][i];
        if (color[u] == c) return 0;
    }
    return 1;
}

/* backtracking with most-constrained-vertex ordering (simple static order fine for these) */
static int solve(int idx, int *order) {
    if (idx == n) return 1;
    int v = order[idx];
    int maxc = 3;
    for (int c = 0; c < maxc; c++) {
        if (ok(v, c)) {
            color[v] = c;
            if (solve(idx + 1, order)) return 1;
            color[v] = -1;
        }
    }
    return 0;
}

static int three_colorable(void) {
    /* BFS order from vertex 0 for locality */
    int order[64], seen[64], qh = 0, qt = 0;
    memset(seen, 0, sizeof(seen));
    order[qt++] = 0; seen[0] = 1;
    while (qh < qt) {
        int v = order[qh++];
        for (int i = 0; i < deg[v]; i++) {
            int u = adj[v][i];
            if (!seen[u]) { seen[u] = 1; order[qt++] = u; }
        }
    }
    for (int v = 0; v < n; v++) if (!seen[v]) order[qt++] = v; /* disconnected safety */
    for (int v = 0; v < n; v++) color[v] = -1;
    /* symmetry breaking: fix color of first vertex and restrict second */
    color[order[0]] = 0;
    int v1 = order[1];
    color[v1] = 1; /* order[1] adjacent to order[0] in BFS => colors 1 wlog */
    int r = solve(2, order);
    return r;
}

int main(int argc, char **argv) {
    n = atoi(argv[1]);
    char line[512];
    long long total = 0, bad = 0;
    while (fgets(line, sizeof(line), stdin)) {
        if (strncmp(line, "Graph", 5) != 0) continue;
        /* read n adjacency lines (skip blanks) */
        int got = 0;
        memset(deg, 0, sizeof(deg));
        while (got < n && fgets(line, sizeof(line), stdin)) {
            char *p = line;
            while (*p == ' ') p++;
            if (*p == '\n' || *p == '\0') continue;
            int v; char *q;
            v = (int)strtol(p, &q, 10);
            if (q == p) break;
            while (*q == ' ') q++;
            if (*q != ':') break;
            q++;
            v--;
            while (1) {
                char *r;
                long u = strtol(q, &r, 10);
                if (r == q) break;
                adj[v][deg[v]++] = (int)(u - 1);
                q = r;
            }
            got++;
        }
        if (got != n) continue;
        total++;
        if (!three_colorable()) {
            bad++;
            printf("NON3COL graph #%lld:\n", total);
            for (int v = 0; v < n; v++) {
                printf("%d :", v + 1);
                for (int i = 0; i < deg[v]; i++) printf(" %d", adj[v][i] + 1);
                printf("\n");
            }
            fflush(stdout);
        }
    }
    fprintf(stderr, "n=%d checked=%lld non3col=%lld\n", n, total, bad);
    return 0;
}

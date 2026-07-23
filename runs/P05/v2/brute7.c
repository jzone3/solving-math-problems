/* Exhaustive check of Gallai's 3-longest-paths property over ALL connected graphs
 * on n vertices (all edge subsets of K_n), n <= 8 practical for n=7.
 * For each connected graph: enumerate all longest paths (as vertex bitsets),
 * check every triple of distinct longest paths has a common vertex.
 * Prints PASS/FAIL. Usage: ./brute7 n
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int n, npairs;
static int pu[32], pv[32];
static unsigned adj[8];
static int best;
static unsigned lp[16384]; /* vertex sets of longest paths (deduped) */
static int nlp;

static void dfs(int v, unsigned visited, int len) {
    if (len > best) { best = len; nlp = 0; }
    if (len == best) {
        int dup = 0;
        for (int i = 0; i < nlp; i++) if (lp[i] == visited) { dup = 1; break; }
        if (!dup) { if (nlp >= 16384) { printf("CAPHIT\n"); exit(2);} lp[nlp++] = visited; }
    }
    unsigned nxt = adj[v] & ~visited;
    while (nxt) {
        int w = __builtin_ctz(nxt);
        nxt &= nxt - 1;
        dfs(w, visited | (1u << w), len + 1);
    }
}

int main(int argc, char **argv) {
    n = argc > 1 ? atoi(argv[1]) : 7;
    npairs = 0;
    for (int u = 0; u < n; u++)
        for (int v = u + 1; v < n; v++) { pu[npairs] = u; pv[npairs] = v; npairs++; }
    long total = 0;
    for (long mask = 0; mask < (1L << npairs); mask++) {
        memset(adj, 0, sizeof(adj));
        for (int i = 0; i < npairs; i++)
            if ((mask >> i) & 1) { adj[pu[i]] |= 1u << pv[i]; adj[pv[i]] |= 1u << pu[i]; }
        /* connectivity */
        unsigned seen = 1, frontier = 1;
        while (frontier) {
            unsigned nf = 0;
            while (frontier) {
                int v = __builtin_ctz(frontier);
                frontier &= frontier - 1;
                nf |= adj[v] & ~seen;
            }
            seen |= nf; frontier = nf;
        }
        if (seen != (1u << n) - 1) continue;
        total++;
        best = 0; nlp = 0;
        for (int s = 0; s < n; s++) dfs(s, 1u << s, 0);
        for (int a = 0; a < nlp; a++)
            for (int b = a + 1; b < nlp; b++) {
                unsigned ab = lp[a] & lp[b];
                if (!ab) { printf("FAIL(two disjoint) mask=%ld\n", mask); return 1; }
                for (int c = b + 1; c < nlp; c++)
                    if (!(ab & lp[c])) {
                        printf("FAIL n=%d mask=%ld\n", n, mask);
                        return 1;
                    }
            }
    }
    printf("checked %ld connected graphs on n=%d: PASS\n", total, n);
    return 0;
}

/* Exact longest path via bitmask DP.
 * stdin: n m, then m lines "u v" (0-indexed). n <= 25 recommended (memory 2^n * n bytes).
 * stdout: line 1: length (edges) of longest path.
 *         line 2: vertices of one longest path, space separated.
 * dp[mask][v] = 1 if there is a simple path covering exactly `mask` ending at v.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 1;
    unsigned int adj[32];
    memset(adj, 0, sizeof(adj));
    for (int i = 0; i < m; i++) {
        int u, v;
        scanf("%d %d", &u, &v);
        adj[u] |= 1u << v;
        adj[v] |= 1u << u;
    }
    size_t M = (size_t)1 << n;
    unsigned char *dp = calloc(M * n, 1);
    if (!dp) { fprintf(stderr, "oom\n"); return 1; }
    for (int v = 0; v < n; v++) dp[((size_t)1 << v) * n + v] = 1;
    int bestlen = 0; size_t bestmask = 1; int bestv = 0;
    for (size_t mask = 1; mask < M; mask++) {
        for (int v = 0; v < n; v++) {
            if (!dp[mask * n + v]) continue;
            int len = __builtin_popcountll(mask) - 1;
            if (len > bestlen) { bestlen = len; bestmask = mask; bestv = v; }
            unsigned int nxt = adj[v] & ~(unsigned int)mask;
            while (nxt) {
                int w = __builtin_ctz(nxt);
                nxt &= nxt - 1;
                dp[(mask | ((size_t)1 << w)) * n + w] = 1;
            }
        }
    }
    printf("%d\n", bestlen);
    /* reconstruct path ending at bestv covering bestmask */
    int path[32], plen = 0;
    size_t mask = bestmask; int v = bestv;
    path[plen++] = v;
    while (__builtin_popcountll(mask) > 1) {
        size_t pm = mask & ~((size_t)1 << v);
        int found = -1;
        for (int u = 0; u < n; u++) {
            if ((adj[u] >> v) & 1 && (pm >> u) & 1 && dp[pm * n + u]) { found = u; break; }
        }
        v = found; mask = pm; path[plen++] = v;
    }
    for (int i = plen - 1; i >= 0; i--) printf("%d ", path[i]);
    printf("\n");
    free(dp);
    return 0;
}

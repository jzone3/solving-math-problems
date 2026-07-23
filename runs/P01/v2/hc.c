/* Exact Hamiltonian cycle counter with cutoff.
 * Input (stdin): n m cutoff, then m lines "u v" (0-indexed; parallel edges allowed).
 * Output: number of Hamiltonian cycles, counted up to `cutoff` (early exit).
 * For multigraphs, parallel edges are distinct edges, so a HC using one copy vs
 * the other counts as distinct cycles (matching the uniquely-hamiltonian notion).
 * Method: backtracking path extension anchored at vertex 0, direction fixed by
 * requiring second vertex < last vertex at close time is avoided by instead
 * counting each undirected cycle twice and dividing; simpler: fix the successor
 * of vertex 0 to be the lower-indexed endpoint among the two cycle neighbors:
 * we enumerate directed cycles from 0 and divide count by 2 at the end -- with
 * cutoff applied on directed count = 2*cutoff.
 * Pruning: any unvisited vertex must have >= 2 available neighbors (unvisited or
 * the current endpoint/vertex 0); the current path endpoint must reach vertex 0
 * or an unvisited vertex.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int n, m;
static long long cutoff2, cnt;
static int *adj[128];   /* adjacency lists (vertex ids, duplicates for parallel edges) */
static int deg[128];
static int visited[128];
static int avail[128];  /* # neighbors that are unvisited (simple count incl. multiplicity) */
static int a0[128];     /* adjacent to vertex 0? */
static int path[130];
static int printcyc;    /* if set, print each found directed cycle's vertex seq */

static void dfs(int u, int depth) {
    if (cnt >= cutoff2) return;
    if (depth == n) {
        /* close cycle: count edges u->0 (multiplicity) */
        for (int i = 0; i < deg[u]; i++) if (adj[u][i] == 0) {
            cnt++;
            if (printcyc) {
                printf("CYC");
                for (int k = 0; k < n; k++) printf(" %d", path[k]);
                printf("\n");
            }
        }
        return;
    }
    /* pruning: every unvisited vertex w != anything must have avail>=2
       (needs an in and out among unvisited/endpoint); endpoint counts as available. */
    for (int i = 0; i < deg[u]; i++) {
        int v = adj[u][i];
        if (visited[v]) continue;
        visited[v] = 1; path[depth] = v;
        /* update avail for neighbors of v */
        int ok = 1;
        for (int j = 0; j < deg[v]; j++) avail[adj[v][j]]--;
        /* sound prune: an unvisited w adjacent to new endpoint v needs at least one
           further neighbor among unvisited vertices or vertex 0 */
        for (int j = 0; j < deg[v]; j++) {
            int w = adj[v][j];
            if (!visited[w] && avail[w] + a0[w] < 1) { ok = 0; break; }
        }
        if (ok) dfs(v, depth + 1);
        for (int j = 0; j < deg[v]; j++) avail[adj[v][j]]++;
        visited[v] = 0;
        if (cnt >= cutoff2) return;
    }
}

int main(void) {
    long long cutoff;
    if (scanf("%d %d %lld", &n, &m, &cutoff) != 3) return 1;
    if (cutoff < 0) { printcyc = 1; cutoff = -cutoff; }
    int *eu = malloc(m * sizeof(int)), *ev = malloc(m * sizeof(int));
    memset(deg, 0, sizeof(deg));
    for (int i = 0; i < m; i++) {
        scanf("%d %d", &eu[i], &ev[i]);
        deg[eu[i]]++; deg[ev[i]]++;
    }
    for (int v = 0; v < n; v++) { adj[v] = malloc(deg[v] * sizeof(int)); avail[v] = deg[v]; }
    int fill[128]; memset(fill, 0, sizeof(fill));
    for (int i = 0; i < m; i++) {
        adj[eu[i]][fill[eu[i]]++] = ev[i];
        adj[ev[i]][fill[ev[i]]++] = eu[i];
    }
    memset(a0, 0, sizeof(a0));
    for (int j = 0; j < deg[0]; j++) a0[adj[0][j]] = 1;
    cutoff2 = 2 * cutoff;
    memset(visited, 0, sizeof(visited));
    visited[0] = 1;
    for (int j = 0; j < deg[0]; j++) avail[adj[0][j]]--;
    cnt = 0; path[0] = 0;
    dfs(0, 1);
    long long und = cnt / 2;
    if (und > cutoff) und = cutoff;
    printf("%lld\n", und);
    return 0;
}

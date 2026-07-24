/* PRUNE hook for geng: reject partial graphs where the newest vertex
 * completes a K4. Since geng adds vertices one at a time and earlier
 * vertices' adjacencies among themselves are fixed, checking only
 * triangles within N(n-1) suffices to keep the search K4-free. */

#include "gtools.h"

int k4prune(graph *g, int n, int maxn) {
    int v = n - 1;
    setword nb = g[v];
    int nbrs[WORDSIZE], d = 0;
    for (int i = 0; i < v; i++)
        if (ISELEMENT(&nb, i)) nbrs[d++] = i;
    for (int a = 0; a < d; a++)
        for (int b = a + 1; b < d; b++) {
            if (!ISELEMENT(&g[nbrs[a]], nbrs[b])) continue;
            for (int c = b + 1; c < d; c++)
                if (ISELEMENT(&g[nbrs[a]], nbrs[c]) &&
                    ISELEMENT(&g[nbrs[b]], nbrs[c]))
                    return 1; /* K4 found -> prune */
        }
    return 0;
}

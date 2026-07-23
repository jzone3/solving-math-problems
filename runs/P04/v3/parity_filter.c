/* Fast graph6 degree-parity filter.
 * Usage: parity_filter n mode   (mode: 0 = all degrees even, 1 = all odd)
 * Reads graph6 lines (n <= 62, no header) on stdin, writes matching lines. */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    int n = atoi(argv[1]);
    int want_odd = atoi(argv[2]);
    char line[256];
    int deg[64];
    while (fgets(line, sizeof line, stdin)) {
        int len = strlen(line);
        while (len && (line[len-1] == '\n' || line[len-1] == '\r')) line[--len] = 0;
        memset(deg, 0, sizeof deg);
        /* bits of adjacency upper triangle, column-major (j from 1..n-1, i<j) */
        int idx = 0, i = 0, j = 1, ok = 1;
        for (int p = 1; p < len && j < n; p++) {
            int b = line[p] - 63;
            for (int s = 5; s >= 0 && j < n; s--) {
                if ((b >> s) & 1) { deg[i] ^= 1; deg[j] ^= 1; }
                if (++i == j) { i = 0; j++; }
            }
        }
        for (int v = 0; v < n; v++)
            if (deg[v] != want_odd) { ok = 0; break; }
        if (ok) puts(line);
    }
    return 0;
}

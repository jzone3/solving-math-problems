/* evenfilt: read graph6 lines on stdin, print only graphs whose COMPLEMENT is
   all-even-degree, i.e. every degree d satisfies (n-1-d) even. For odd n this
   means all degrees even; for even n all degrees odd. Small n (< 63) only. */
#include <stdio.h>
#include <string.h>

int main(void) {
    static char line[1 << 16];
    while (fgets(line, sizeof line, stdin)) {
        int len = strlen(line);
        while (len && (line[len-1] == '\n' || line[len-1] == '\r')) line[--len] = 0;
        if (!len) continue;
        int n = line[0] - 63;
        int deg[64];
        memset(deg, 0, sizeof deg);
        int idx = 0, nb = (len - 1) * 6;
        for (int v = 1; v < n; v++)
            for (int u = 0; u < v; u++, idx++) {
                if (idx >= nb) break;
                int c = line[1 + idx / 6] - 63;
                if ((c >> (5 - idx % 6)) & 1) { deg[u]++; deg[v]++; }
            }
        int ok = 1, want = (n - 1) & 1; /* d parity must equal (n-1) parity */
        for (int v = 0; v < n; v++) if ((deg[v] & 1) != want) { ok = 0; break; }
        if (ok) puts(line);
    }
    return 0;
}

/* Fast exhaustive scanner for Graffiti conjecture 129:
 *   dev_L(G) <= R(G),  dev_L^2 = (sum d_i(d_i+1))/n - (2m/n)^2  (degree identity),
 *   R = sum_{uv in E} 1/sqrt(d_u d_v).
 * Also scores the eigenvalue-free reduction M*: S*dev_L - m^2, S = sum sqrt(d_u d_v).
 * Reads graph6 lines (fixed n <= 62) from stdin (pipe from nauty-geng -q n).
 * Prints the top-K scores for both. Compile: gcc -O3 -o scan129 scan129.c -lm
 * Usage: nauty-geng -q 11 res/mod | ./scan129 11
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define TOPK 5

typedef struct { double s; char g6[64]; } Ent;

static void insert(Ent *top, double s, const char *g6) {
    if (s <= top[TOPK-1].s) return;
    int i = TOPK - 1;
    while (i > 0 && top[i-1].s < s) { top[i] = top[i-1]; i--; }
    top[i].s = s; strncpy(top[i].g6, g6, 63); top[i].g6[63] = 0;
}

int main(int argc, char **argv) {
    int n = atoi(argv[1]);
    int nb = (n * (n - 1) / 2 + 5) / 6;
    double isq[4096];
    for (int i = 1; i < 4096; i++) isq[i] = 1.0 / sqrt((double)i);
    Ent topC[TOPK], topM[TOPK];
    for (int i = 0; i < TOPK; i++) { topC[i].s = -1e18; topM[i].s = -1e18; topC[i].g6[0]=topM[i].g6[0]=0; }
    char line[256];
    long long cnt = 0;
    int eu[2048], ev[2048];
    while (fgets(line, sizeof line, stdin)) {
        int len = strlen(line);
        while (len && (line[len-1] == '\n' || line[len-1] == '\r')) line[--len] = 0;
        if (len != nb + 1) continue;
        int d[64] = {0}, ne = 0;
        int bitpos = 0;
        for (int j = 1; j < n; j++) {
            for (int i = 0; i < j; i++, bitpos++) {
                int c = line[1 + bitpos / 6] - 63;
                if ((c >> (5 - bitpos % 6)) & 1) {
                    d[i]++; d[j]++; eu[ne] = i; ev[ne] = j; ne++;
                }
            }
        }
        cnt++;
        if (!ne) continue;
        double m = ne, M1p = 0;
        for (int i = 0; i < n; i++) M1p += (double)d[i] * (d[i] + 1);
        double dev2 = M1p / n - 4.0 * m * m / ((double)n * n);
        double dev = sqrt(dev2 > 0 ? dev2 : 0);
        double R = 0, S = 0;
        for (int e = 0; e < ne; e++) {
            int p = d[eu[e]] * d[ev[e]];
            R += isq[p];
            S += sqrt((double)p);
        }
        insert(topC, dev - R, line);
        insert(topM, S * dev - m * m, line);
    }
    printf("graphs=%lld n=%d\n", cnt, n);
    printf("top 129 (dev_L - R, violation if >0):\n");
    for (int i = 0; i < TOPK; i++) printf("  %+.10f  %s\n", topC[i].s, topC[i].g6);
    printf("top M* (S*dev_L - m^2, violation if >0):\n");
    for (int i = 0; i < TOPK; i++) printf("  %+.10f  %s\n", topM[i].s, topM[i].g6);
    return 0;
}

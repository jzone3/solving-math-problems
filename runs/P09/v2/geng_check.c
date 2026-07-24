/* Exhaustive Bollobas-Nikiforov check over graph6 input (stdin, n <= 12).
 * For each graph: omega via bitmask branch-and-bound, lambda1/lambda2 via
 * cyclic Jacobi. Flags any graph with score > -TOL (near-miss) and any
 * score > 0 (VIOLATION). Prints summary at EOF.
 * Compile: gcc -O3 -march=native -o geng_check geng_check.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static int n;
static unsigned adjmask[16];

static int best_clique;
static void expand(unsigned R_size, unsigned P) {
    if (!P) { if ((int)R_size > best_clique) best_clique = R_size; return; }
    /* greedy bound: popcount */
    int pc = __builtin_popcount(P);
    if ((int)R_size + pc <= best_clique) return;
    while (P) {
        pc = __builtin_popcount(P);
        if ((int)R_size + pc <= best_clique) return;
        int v = __builtin_ctz(P);
        expand(R_size + 1, P & adjmask[v]);
        P &= P - 1;
    }
}

static double A[16][16];

static void jacobi_top2(double *l1, double *l2) {
    double a[16][16];
    memcpy(a, A, sizeof(a));
    for (int sweep = 0; sweep < 30; sweep++) {
        double off = 0;
        for (int p = 0; p < n; p++)
            for (int q = p + 1; q < n; q++) off += a[p][q] * a[p][q];
        if (off < 1e-22) break;
        for (int p = 0; p < n; p++)
            for (int q = p + 1; q < n; q++) {
                if (fabs(a[p][q]) < 1e-14) continue;
                double theta = (a[q][q] - a[p][p]) / (2 * a[p][q]);
                double t = (theta >= 0 ? 1.0 : -1.0) / (fabs(theta) + sqrt(theta * theta + 1));
                double c = 1 / sqrt(t * t + 1), s = t * c;
                for (int k = 0; k < n; k++) {
                    double akp = a[k][p], akq = a[k][q];
                    a[k][p] = c * akp - s * akq;
                    a[k][q] = s * akp + c * akq;
                }
                for (int k = 0; k < n; k++) {
                    double apk = a[p][k], aqk = a[q][k];
                    a[p][k] = c * apk - s * aqk;
                    a[q][k] = s * apk + c * aqk;
                }
            }
    }
    double e1 = -1e18, e2 = -1e18;
    for (int i = 0; i < n; i++) {
        double d = a[i][i];
        if (d > e1) { e2 = e1; e1 = d; }
        else if (d > e2) e2 = d;
    }
    *l1 = e1; *l2 = e2;
}

int main(int argc, char **argv) {
    double TOL = argc > 1 ? atof(argv[1]) : 1e-7;
    char line[64];
    long long count = 0, nearmiss = 0, viol = 0;
    double maxscore = -1e18;
    char maxg6[64] = "";
    while (fgets(line, sizeof(line), stdin)) {
        int len = strlen(line);
        while (len && (line[len-1] == '\n' || line[len-1] == '\r')) line[--len] = 0;
        if (!len) continue;
        /* decode graph6 */
        const unsigned char *s = (const unsigned char *)line;
        int pos = 0;
        n = s[pos++] - 63;
        if (n > 15) { fprintf(stderr, "n too big\n"); return 1; }
        memset(adjmask, 0, sizeof(adjmask));
        memset(A, 0, sizeof(A));
        int m = 0;
        int nbits = n * (n - 1) / 2;
        int bit = 0;
        unsigned cur = 0; int curbits = 0;
        for (int j = 1; j < n; j++)
            for (int i = 0; i < j; i++) {
                if (curbits == 0) { cur = s[pos++] - 63; curbits = 6; }
                int b = (cur >> (curbits - 1)) & 1; curbits--;
                bit++;
                if (b) {
                    adjmask[i] |= 1u << j; adjmask[j] |= 1u << i;
                    A[i][j] = A[j][i] = 1.0; m++;
                }
            }
        (void)nbits;
        if (m == n * (n - 1) / 2) { count++; continue; } /* complete: excluded */
        if (m == 0) { count++; continue; }
        best_clique = 1;
        expand(0, (1u << n) - 1);
        int w = best_clique;
        double l1, l2;
        jacobi_top2(&l1, &l2);
        double score = l1 * l1 + l2 * l2 - 2.0 * m * (1.0 - 1.0 / w);
        if (score > maxscore) { maxscore = score; strcpy(maxg6, line); }
        if (score > 1e-6) { viol++; printf("VIOLATION %s score=%.12g w=%d m=%d\n", line, score, w, m); }
        else if (score > -TOL) { nearmiss++; printf("BOUNDARY %s score=%.12g w=%d m=%d\n", line, score, w, m); }
        count++;
    }
    printf("checked=%lld violations=%lld boundary(>-%g)=%lld maxscore=%.12g maxg6=%s\n",
           count, viol, (double)TOL, nearmiss, maxscore, maxg6);
    return 0;
}

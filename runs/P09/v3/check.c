/* P09 Bollobas-Nikiforov exhaustive checker.
 * Reads graph6 lines (n <= 32) on stdin; for each graph computes:
 *   - m (edges), omega (exact, bitset branch and bound)
 *   - lambda1, lambda2 (cyclic Jacobi on the dense adjacency matrix)
 * Reports any graph (other than complete K_n) with
 *   lambda1^2 + lambda2^2 > 2m(1-1/omega) + EPS.
 * Also tracks and prints the maximum ratio seen.
 * Compile: gcc -O2 -o check check.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAXN 32
#define EPS 1e-7

static int n;
static unsigned adj[MAXN];

static int popcount(unsigned x) { return __builtin_popcount(x); }

/* does mask contain a k-clique? */
static int has_clique(unsigned mask, int k) {
    if (k == 0) return 1;
    if (popcount(mask) < k) return 0;
    while (mask) {
        int v = __builtin_ctz(mask);
        mask &= mask - 1;
        if (has_clique(adj[v] & mask, k - 1)) return 1;
        if (popcount(mask) < k) return 0;
    }
    return 0;
}

static int clique_number(void) {
    unsigned full = (n == 32) ? 0xffffffffu : ((1u << n) - 1);
    int k = 1;
    while (k < n && has_clique(full, k + 1)) k++;
    return k;
}

/* cyclic Jacobi eigenvalues of symmetric A (destroys A), results in ev */
static void jacobi_eig(double A[MAXN][MAXN], double *ev) {
    for (int sweep = 0; sweep < 50; sweep++) {
        double off = 0;
        for (int p = 0; p < n; p++)
            for (int q = p + 1; q < n; q++) off += A[p][q] * A[p][q];
        if (off < 1e-22) break;
        for (int p = 0; p < n; p++)
            for (int q = p + 1; q < n; q++) {
                double apq = A[p][q];
                if (fabs(apq) < 1e-14) continue;
                double theta = (A[q][q] - A[p][p]) / (2 * apq);
                double t = (theta >= 0 ? 1.0 : -1.0) /
                           (fabs(theta) + sqrt(theta * theta + 1));
                double c = 1 / sqrt(t * t + 1), s = t * c;
                for (int i = 0; i < n; i++) {
                    double aip = A[i][p], aiq = A[i][q];
                    A[i][p] = c * aip - s * aiq;
                    A[i][q] = s * aip + c * aiq;
                }
                for (int i = 0; i < n; i++) {
                    double api = A[p][i], aqi = A[q][i];
                    A[p][i] = c * api - s * aqi;
                    A[q][i] = s * api + c * aqi;
                }
            }
    }
    for (int i = 0; i < n; i++) ev[i] = A[i][i];
}

int main(void) {
    char line[256];
    long long count = 0, viol = 0;
    double maxratio = -1;
    char maxg6[256] = "";
    while (fgets(line, sizeof line, stdin)) {
        int len = strlen(line);
        while (len && (line[len - 1] == '\n' || line[len - 1] == '\r')) line[--len] = 0;
        if (!len) continue;
        /* decode graph6 */
        const unsigned char *s = (const unsigned char *)line;
        int pos = 0;
        n = s[pos++] - 63;
        if (n > MAXN) { fprintf(stderr, "n too big\n"); return 1; }
        memset(adj, 0, sizeof adj);
        int bits = 0, val = 0, m = 0;
        for (int j = 1; j < n; j++)
            for (int i = 0; i < j; i++) {
                if (bits == 0) { val = s[pos++] - 63; bits = 6; }
                bits--;
                if ((val >> bits) & 1) {
                    adj[i] |= 1u << j; adj[j] |= 1u << i; m++;
                }
            }
        count++;
        if (m == 0) continue;
        int w = clique_number();
        if (w == n) continue; /* complete graph excluded by conjecture */
        double A[MAXN][MAXN];
        memset(A, 0, sizeof A);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                A[i][j] = (adj[i] >> j) & 1 ? 1.0 : 0.0;
        double ev[MAXN];
        jacobi_eig(A, ev);
        /* top two eigenvalues */
        double l1 = -1e18, l2 = -1e18;
        for (int i = 0; i < n; i++) {
            if (ev[i] > l1) { l2 = l1; l1 = ev[i]; }
            else if (ev[i] > l2) l2 = ev[i];
        }
        double bound = 2.0 * m * (1.0 - 1.0 / w);
        double ratio = (l1 * l1 + l2 * l2) / bound;
        if (ratio > maxratio) { maxratio = ratio; strcpy(maxg6, line); }
        if (l1 * l1 + l2 * l2 > bound + EPS) {
            viol++;
            printf("VIOLATION %s n=%d m=%d w=%d l1=%.9f l2=%.9f ratio=%.12f\n",
                   line, n, m, w, l1, l2, ratio);
        }
    }
    printf("DONE graphs=%lld violations=%lld maxratio=%.12f maxg6=%s\n",
           count, viol, maxratio, maxg6);
    return 0;
}

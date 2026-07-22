/* P09 Bollobas-Nikiforov exhaustive checker (variant V4).
 *
 * Reads graph6 lines (n <= 32) on stdin. For each non-complete graph G with m
 * edges, clique number w, and adjacency eigenvalues l1 >= l2 >= ...:
 * checks the conjectured inequality  l1^2 + l2^2 <= 2m(1 - 1/w).
 *
 * Pruning: since w >= 2 for m >= 1, a violation requires s = l1^2+l2^2 > m.
 * The exact clique number (bitmask branch-and-bound) is only computed for
 * graphs passing s > m - SLACK.  Every graph gets an eigen-decomposition.
 *
 * Output:
 *   VIOLATION <g6> n=%d m=%d w=%d l1=%.12f l2=%.12f s=%.12f rhs=%.12f
 *   stderr summary: totals, number pruned, number clique-evaluated,
 *   top near-miss (max s - rhs among clique-evaluated graphs).
 *
 * Build: gcc -O3 -march=native -o checker checker.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#define MAXN 32
static double A[MAXN][MAXN];
static uint32_t adj[MAXN];

/* Jacobi eigenvalue algorithm for symmetric matrices, returns eigenvalues in ev */
static void jacobi_eig(int n, double a[MAXN][MAXN], double *ev) {
    static double m[MAXN][MAXN];
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) m[i][j] = a[i][j];
    for (int sweep = 0; sweep < 60; sweep++) {
        double off = 0;
        for (int p = 0; p < n - 1; p++)
            for (int q = p + 1; q < n; q++) off += m[p][q] * m[p][q];
        if (off < 1e-22) break;
        for (int p = 0; p < n - 1; p++) {
            for (int q = p + 1; q < n; q++) {
                double apq = m[p][q];
                if (fabs(apq) < 1e-14) continue;
                double app = m[p][p], aqq = m[q][q];
                double theta = 0.5 * (aqq - app) / apq;
                double t = (theta >= 0 ? 1.0 : -1.0) /
                           (fabs(theta) + sqrt(theta * theta + 1.0));
                double c = 1.0 / sqrt(t * t + 1.0), s = t * c;
                for (int k = 0; k < n; k++) {
                    double mkp = m[k][p], mkq = m[k][q];
                    m[k][p] = c * mkp - s * mkq;
                    m[k][q] = s * mkp + c * mkq;
                }
                for (int k = 0; k < n; k++) {
                    double mpk = m[p][k], mqk = m[q][k];
                    m[p][k] = c * mpk - s * mqk;
                    m[q][k] = s * mpk + c * mqk;
                }
            }
        }
    }
    for (int i = 0; i < n; i++) ev[i] = m[i][i];
}

/* branch-and-bound max clique on bitmask adjacency */
static int best_clique;
static int nverts;
static void expand(uint32_t cand, int size) {
    if (cand == 0) {
        if (size > best_clique) best_clique = size;
        return;
    }
    int cnt = __builtin_popcount(cand);
    if (size + cnt <= best_clique) return;
    while (cand) {
        if (size + __builtin_popcount(cand) <= best_clique) return;
        int v = __builtin_ctz(cand);
        cand &= cand - 1;
        expand(cand & adj[v], size + 1);
    }
}
static int max_clique(int n) {
    nverts = n;
    best_clique = 1;
    expand((n == 32) ? 0xFFFFFFFFu : ((1u << n) - 1), 0);
    return best_clique;
}

int main(int argc, char **argv) {
    char line[256];
    long long total = 0, evaluated = 0, violations = 0;
    double best_gap = -1e18; /* max s - rhs among clique-evaluated graphs */
    char best_g6[128] = "";
    int best_n = 0, best_m = 0, best_w = 0;
    double best_s = 0, best_rhs = 0;
    double SLACK = 1e-6;

    while (fgets(line, sizeof line, stdin)) {
        char *g6 = line;
        size_t len = strlen(g6);
        while (len && (g6[len - 1] == '\n' || g6[len - 1] == '\r')) g6[--len] = 0;
        if (!len) continue;
        /* parse graph6 (n < 63 single-byte header) */
        int n = g6[0] - 63;
        if (n < 1 || n > MAXN) { fprintf(stderr, "bad n in %s\n", g6); continue; }
        memset(adj, 0, sizeof adj);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) A[i][j] = 0.0;
        int m = 0;
        {
            int k = 0; /* bit index */
            for (int j = 1; j < n; j++) {
                for (int i = 0; i < j; i++) {
                    int byte = 1 + k / 6, bit = 5 - (k % 6);
                    k++;
                    if ((g6[byte] - 63) & (1 << bit)) {
                        A[i][j] = A[j][i] = 1.0;
                        adj[i] |= 1u << j;
                        adj[j] |= 1u << i;
                        m++;
                    }
                }
            }
        }
        total++;
        if (m == n * (n - 1) / 2) continue; /* complete graph excluded */
        if (m == 0) continue;
        double ev[MAXN];
        jacobi_eig(n, A, ev);
        /* top two eigenvalues */
        double l1 = -1e18, l2 = -1e18;
        for (int i = 0; i < n; i++) {
            if (ev[i] > l1) { l2 = l1; l1 = ev[i]; }
            else if (ev[i] > l2) l2 = ev[i];
        }
        double s = l1 * l1 + l2 * l2;
        if (s <= (double)m - SLACK) continue; /* w>=2 => rhs >= m */
        int w = max_clique(n);
        evaluated++;
        double rhs = 2.0 * m * (1.0 - 1.0 / w);
        double gap = s - rhs;
        if (gap > best_gap) {
            best_gap = gap; strncpy(best_g6, g6, 127);
            best_n = n; best_m = m; best_w = w; best_s = s; best_rhs = rhs;
        }
        if (gap > 1e-7) {
            violations++;
            printf("VIOLATION %s n=%d m=%d w=%d l1=%.12f l2=%.12f s=%.12f rhs=%.12f gap=%.3e\n",
                   g6, n, m, w, l1, l2, s, rhs, gap);
            fflush(stdout);
        }
    }
    fprintf(stderr,
        "SUMMARY total=%lld evaluated=%lld violations=%lld "
        "best_gap=%.6e best_g6=%s best_n=%d best_m=%d best_w=%d best_s=%.12f best_rhs=%.12f\n",
        total, evaluated, violations, best_gap, best_g6, best_n, best_m,
        best_w, best_s, best_rhs);
    return 0;
}

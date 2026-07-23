/* P09 Bollobas-Nikiforov fast exhaustive checker (v2).
 * Threshold logic: with t = (l1^2+l2^2)/(2m), a violation requires
 * omega <= kmax = ceil(1/(1-t)) - 1, so:
 *   - Jacobi eigensolve with loose tolerance TOL (rigorous: eigenvalues of
 *     the rotated matrix diagonal are within ||offdiag||_F of the true ones,
 *     so we pad l1,l2 upward by TOL before computing t).
 *   - if t <= 2/3 (after padding): only omega <= 2 could violate, and the
 *     triangle-free (omega=2) case is a THEOREM (Lin-Ning-Wu 2021), so skip.
 *     (omega=1 means m=0, also skipped.)
 *   - otherwise single clique query has_clique(kmax+1): if a (kmax+1)-clique
 *     exists the graph is safe; else print CANDIDATE (exact recheck offline).
 * Compile: gcc -O3 -march=native -o check2 check2.c -lm
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

/* Householder tridiagonalization of symmetric A (destroys A);
 * outputs diagonal d[0..n-1] and off-diagonal e[0..n-2]. */
static void tridiag(double A[MAXN][MAXN], double *d, double *e) {
    for (int k = 0; k < n - 2; k++) {
        double scale = 0;
        for (int i = k + 1; i < n; i++) scale += fabs(A[i][k]);
        if (scale < 1e-300) { e[k] = A[k + 1][k]; continue; }
        double sigma = 0;
        for (int i = k + 1; i < n; i++) sigma += A[i][k] * A[i][k];
        double alpha = (A[k + 1][k] >= 0 ? -sqrt(sigma) : sqrt(sigma));
        double r2 = sigma - A[k + 1][k] * alpha; /* = |v|^2 / 2 */
        if (r2 < 1e-300) { e[k] = A[k + 1][k]; continue; }
        double v[MAXN];
        v[k + 1] = A[k + 1][k] - alpha;
        for (int i = k + 2; i < n; i++) v[i] = A[i][k];
        /* A <- H A H with H = I - v v^T / r2 */
        double p[MAXN], K = 0;
        for (int i = k + 1; i < n; i++) {
            double s = 0;
            for (int j = k + 1; j < n; j++) s += A[i][j] * v[j];
            p[i] = s / r2;
        }
        for (int i = k + 1; i < n; i++) K += v[i] * p[i];
        K /= 2 * r2;
        for (int i = k + 1; i < n; i++) p[i] -= K * v[i];
        for (int i = k + 1; i < n; i++)
            for (int j = k + 1; j <= i; j++) {
                double x = A[i][j] - v[i] * p[j] - p[i] * v[j];
                A[i][j] = x; A[j][i] = x;
            }
        A[k + 1][k] = alpha; A[k][k + 1] = alpha;
        for (int i = k + 2; i < n; i++) { A[i][k] = 0; A[k][i] = 0; }
        e[k] = alpha;
    }
    e[n - 2] = A[n - 1][n - 2];
    for (int i = 0; i < n; i++) d[i] = A[i][i];
}

/* Sturm count: number of eigenvalues of tridiagonal (d,e) less than x */
static int sturm_count(const double *d, const double *e, double x) {
    int cnt = 0;
    double q = d[0] - x;
    if (q < 0) cnt++;
    for (int i = 1; i < n; i++) {
        double e2 = e[i - 1] * e[i - 1];
        q = d[i] - x - (q == 0 ? e2 / 1e-300 : e2 / q);
        if (q < 0) cnt++;
    }
    return cnt;
}

/* k-th largest eigenvalue (k=1 or 2) upper bound within tol, via bisection */
static double kth_largest(const double *d, const double *e, int k,
                          double lo, double hi, double tol) {
    /* returns hi end of bracket: rigorous upper bound */
    while (hi - lo > tol) {
        double mid = 0.5 * (lo + hi);
        /* # eigenvalues >= mid is n - sturm_count(mid) */
        if (n - sturm_count(d, e, mid) >= k) lo = mid; else hi = mid;
    }
    return hi;
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
        if (m == n * (n - 1) / 2) continue; /* complete graph excluded */
        double A[MAXN][MAXN];
        memset(A, 0, sizeof A);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                A[i][j] = (adj[i] >> j) & 1 ? 1.0 : 0.0;
        double d[MAXN], e[MAXN];
        tridiag(A, d, e);
        /* Gershgorin bounds for the tridiagonal matrix */
        double glo = 1e18, ghi = -1e18;
        for (int i = 0; i < n; i++) {
            double r = (i > 0 ? fabs(e[i - 1]) : 0) + (i < n - 1 ? fabs(e[i]) : 0);
            if (d[i] - r < glo) glo = d[i] - r;
            if (d[i] + r > ghi) ghi = d[i] + r;
        }
        double l1 = kth_largest(d, e, 1, glo, ghi, 1e-5); /* upper bounds */
        double l2 = kth_largest(d, e, 2, glo, l1 + 1e-5, 1e-5);
        double t = (l1 * l1 + l2 * l2) / (2.0 * m);
        if (t > maxratio) { maxratio = t; strcpy(maxg6, line); } /* note: t vs bound needs omega; tracked loosely */
        if (t <= 2.0 / 3.0) continue; /* omega<=2 cannot violate (LNW 2021) */
        int kmax = (t < 1.0 - 1e-12) ? (int)ceil(1.0 / (1.0 - t) - 1e-12) - 1 : n;
        if (kmax >= n || !has_clique((n == 32) ? 0xffffffffu : ((1u << n) - 1), kmax + 1)) {
            viol++;
            printf("CANDIDATE %s n=%d m=%d kmax=%d l1<=%.9f l2<=%.9f t=%.12f\n",
                   line, n, m, kmax, l1, l2, t);
        }
    }
    printf("DONE graphs=%lld candidates=%lld max_t=%.12f maxg6=%s\n",
           count, viol, maxratio, maxg6);
    return 0;
}

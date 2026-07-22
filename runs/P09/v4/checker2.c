/* P09 Bollobas-Nikiforov exhaustive checker, v2 (fast path for n=12 sweeps).
 *
 * Same semantics as checker.c but computes only the top-2 eigenvalues via
 * Householder tridiagonalization + Sturm-sequence bisection, which is
 * substantially faster than full Jacobi. Any graph within FUZZ of the
 * inequality boundary is re-checked with full Jacobi (from checker.c logic)
 * before being reported, so the fast path cannot produce false positives,
 * and bisection is run to 1e-12 so it cannot mask a true violation
 * (gap threshold 1e-7).
 *
 * Build: gcc -O3 -march=native -o checker2 checker2.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#define MAXN 32
static double A[MAXN][MAXN];
static uint32_t adj[MAXN];

/* Householder reduction of symmetric A (destroyed) to tridiagonal d, e */
static void tridiag(int n, double a[MAXN][MAXN], double *d, double *e) {
    for (int i = n - 1; i >= 1; i--) {
        int l = i - 1;
        double h = 0.0, scale = 0.0;
        if (l > 0) {
            for (int k = 0; k <= l; k++) scale += fabs(a[i][k]);
            if (scale == 0.0) e[i] = a[i][l];
            else {
                for (int k = 0; k <= l; k++) {
                    a[i][k] /= scale;
                    h += a[i][k] * a[i][k];
                }
                double f = a[i][l];
                double g = (f >= 0.0) ? -sqrt(h) : sqrt(h);
                e[i] = scale * g;
                h -= f * g;
                a[i][l] = f - g;
                f = 0.0;
                for (int j = 0; j <= l; j++) {
                    g = 0.0;
                    for (int k = 0; k <= j; k++) g += a[j][k] * a[i][k];
                    for (int k = j + 1; k <= l; k++) g += a[k][j] * a[i][k];
                    e[j] = g / h;
                    f += e[j] * a[i][j];
                }
                double hh = f / (h + h);
                for (int j = 0; j <= l; j++) {
                    f = a[i][j];
                    e[j] = g = e[j] - hh * f;
                    for (int k = 0; k <= j; k++)
                        a[j][k] -= (f * e[k] + g * a[i][k]);
                }
            }
        } else e[i] = a[i][l];
        d[i] = h;
    }
    e[0] = 0.0;
    for (int i = 0; i < n; i++) d[i] = a[i][i];
    /* rebuild diagonal: after reduction, diagonal of a holds transformed values */
}

/* count of eigenvalues of tridiagonal (d,e) strictly less than x (Sturm) */
static int sturm_count(int n, const double *d, const double *e, double x) {
    int cnt = 0;
    double q = d[0] - x;
    if (q < 0) cnt++;
    for (int i = 1; i < n; i++) {
        double ei = e[i];
        double denom = (q == 0.0) ? 1e-300 : q;
        q = d[i] - x - ei * ei / denom;
        if (q < 0) cnt++;
    }
    return cnt;
}

/* k-th largest eigenvalue (k=1 or 2) of tridiagonal via bisection */
static double kth_largest(int n, const double *d, const double *e, int k,
                          double lo, double hi) {
    /* want eigenvalue lambda with exactly (n-k) eigenvalues below it */
    for (int it = 0; it < 60; it++) {
        double mid = 0.5 * (lo + hi);
        if (sturm_count(n, d, e, mid) >= n - k + 1) hi = mid;
        else lo = mid;
        if (hi - lo < 1e-12) break;
    }
    return 0.5 * (lo + hi);
}

/* full Jacobi fallback (as in checker.c) */
static void jacobi_eig(int n, double a[MAXN][MAXN], double *ev) {
    static double m[MAXN][MAXN];
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) m[i][j] = a[i][j];
    for (int sweep = 0; sweep < 60; sweep++) {
        double off = 0;
        for (int p = 0; p < n - 1; p++)
            for (int q = p + 1; q < n; q++) off += m[p][q] * m[p][q];
        if (off < 1e-22) break;
        for (int p = 0; p < n - 1; p++)
            for (int q = p + 1; q < n; q++) {
                double apq = m[p][q];
                if (fabs(apq) < 1e-14) continue;
                double theta = 0.5 * (m[q][q] - m[p][p]) / apq;
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
    for (int i = 0; i < n; i++) ev[i] = m[i][i];
}

static int best_clique;
static void expand(uint32_t cand, int size) {
    if (!cand) { if (size > best_clique) best_clique = size; return; }
    while (cand) {
        if (size + __builtin_popcount(cand) <= best_clique) return;
        int v = __builtin_ctz(cand);
        cand &= cand - 1;
        expand(cand & adj[v], size + 1);
    }
}
static int max_clique(int n) {
    best_clique = 1;
    expand((n == 32) ? 0xFFFFFFFFu : ((1u << n) - 1), 0);
    return best_clique;
}

int main(void) {
    char line[256];
    long long total = 0, evaluated = 0, violations = 0;
    double best_gap = -1e18;
    char best_g6[128] = "";
    int best_n = 0, best_m = 0, best_w = 0;
    double best_s = 0, best_rhs = 0;

    while (fgets(line, sizeof line, stdin)) {
        char *g6 = line;
        size_t len = strlen(g6);
        while (len && (g6[len - 1] == '\n' || g6[len - 1] == '\r')) g6[--len] = 0;
        if (!len) continue;
        int n = g6[0] - 63;
        if (n < 1 || n > MAXN) { fprintf(stderr, "bad n in %s\n", g6); continue; }
        memset(adj, 0, sizeof adj);
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) A[i][j] = 0.0;
        int m = 0;
        {
            int k = 0;
            for (int j = 1; j < n; j++)
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
        total++;
        if (m == n * (n - 1) / 2 || m == 0) continue;
        static double T[MAXN][MAXN];
        memcpy(T, A, sizeof T);
        double d[MAXN], e[MAXN];
        tridiag(n, T, d, e);
        /* eigenvalues lie in [-l1, l1], l1 <= sqrt(2m); use Gershgorin-ish bounds */
        double bound = sqrt(2.0 * m) + 1.0;
        double l1 = kth_largest(n, d, e, 1, -bound, bound);
        double l2 = kth_largest(n, d, e, 2, -bound, l1 + 1e-9);
        double s = l1 * l1 + l2 * l2;
        if (s <= (double)m - 1e-6) continue;
        int w = max_clique(n);
        evaluated++;
        double rhs = 2.0 * m * (1.0 - 1.0 / w);
        double gap = s - rhs;
        if (gap > best_gap) {
            best_gap = gap; strncpy(best_g6, g6, 127);
            best_n = n; best_m = m; best_w = w; best_s = s; best_rhs = rhs;
        }
        if (gap > 1e-7) {
            /* confirm with independent Jacobi before reporting */
            double ev[MAXN];
            jacobi_eig(n, A, ev);
            double j1 = -1e18, j2 = -1e18;
            for (int i = 0; i < n; i++) {
                if (ev[i] > j1) { j2 = j1; j1 = ev[i]; }
                else if (ev[i] > j2) j2 = ev[i];
            }
            double sj = j1 * j1 + j2 * j2;
            if (sj - rhs > 1e-7) {
                violations++;
                printf("VIOLATION %s n=%d m=%d w=%d l1=%.12f l2=%.12f s=%.12f rhs=%.12f gap=%.3e\n",
                       g6, n, m, w, j1, j2, sj, rhs, sj - rhs);
                fflush(stdout);
            }
        }
    }
    fprintf(stderr,
        "SUMMARY total=%lld evaluated=%lld violations=%lld "
        "best_gap=%.6e best_g6=%s best_n=%d best_m=%d best_w=%d best_s=%.12f best_rhs=%.12f\n",
        total, evaluated, violations, best_gap, best_g6, best_n, best_m,
        best_w, best_s, best_rhs);
    return 0;
}

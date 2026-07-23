/* Exhaustive BN sweep in C for n<=16 (designed for n=12).
 *
 * Reads graph6 lines (fixed n) from stdin (pipe from nauty-geng -cq).
 * For each graph: eigenvalues via Householder tridiagonalization + QL implicit
 * shifts (dense symmetric, exact to ~1e-12), L = l1^2 + l2^2.
 * Violation of BN <=> omega < 2m/(2m-L). We compute exact max clique (bitmask
 * branch and bound) whenever 2m/(2m-L) > 2 - i.e. whenever a violation is
 * arithmetically possible for ANY clique number - and test the exact inequality.
 * Graphs with score > -1e-7 are printed for independent high-precision recheck.
 *
 * cc -O3 -march=native -o sweep12 sweep12.c -lm
 * usage: nauty-geng -cq 12 res/mod | ./sweep12 12
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static int N;

/* ---- eigenvalues of dense symmetric via tred/tql (Numerical Recipes style) ---- */
static void tred2(double a[16][16], int n, double d[], double e[]) {
    int l, k, j, i;
    double scale, hh, h, g, f;
    for (i = n - 1; i >= 1; i--) {
        l = i - 1; h = scale = 0.0;
        if (l > 0) {
            for (k = 0; k <= l; k++) scale += fabs(a[i][k]);
            if (scale == 0.0) e[i] = a[i][l];
            else {
                for (k = 0; k <= l; k++) { a[i][k] /= scale; h += a[i][k]*a[i][k]; }
                f = a[i][l];
                g = (f >= 0.0 ? -sqrt(h) : sqrt(h));
                e[i] = scale * g; h -= f * g; a[i][l] = f - g; f = 0.0;
                for (j = 0; j <= l; j++) {
                    g = 0.0;
                    for (k = 0; k <= j; k++) g += a[j][k] * a[i][k];
                    for (k = j + 1; k <= l; k++) g += a[k][j] * a[i][k];
                    e[j] = g / h; f += e[j] * a[i][j];
                }
                hh = f / (h + h);
                for (j = 0; j <= l; j++) {
                    f = a[i][j]; e[j] = g = e[j] - hh * f;
                    for (k = 0; k <= j; k++) a[j][k] -= (f * e[k] + g * a[i][k]);
                }
            }
        } else e[i] = a[i][l];
        d[i] = h;
    }
    e[0] = 0.0;
    for (i = 0; i < n; i++) d[i] = a[i][i];
}

static int tql1(double d[], double e[], int n) {
    int m, l, iter, i;
    double s, r, p, g, f, dd, c, b;
    for (i = 1; i < n; i++) e[i - 1] = e[i];
    e[n - 1] = 0.0;
    for (l = 0; l < n; l++) {
        iter = 0;
        do {
            for (m = l; m < n - 1; m++) {
                dd = fabs(d[m]) + fabs(d[m + 1]);
                if (fabs(e[m]) <= 1e-14 * dd) break;
            }
            if (m != l) {
                if (iter++ == 50) return -1;
                g = (d[l + 1] - d[l]) / (2.0 * e[l]);
                r = hypot(g, 1.0);
                g = d[m] - d[l] + e[l] / (g + (g >= 0 ? fabs(r) : -fabs(r)));
                s = c = 1.0; p = 0.0;
                for (i = m - 1; i >= l; i--) {
                    f = s * e[i]; b = c * e[i];
                    e[i + 1] = (r = hypot(f, g));
                    if (r == 0.0) { d[i + 1] -= p; e[m] = 0.0; break; }
                    s = f / r; c = g / r;
                    g = d[i + 1] - p;
                    r = (d[i] - g) * s + 2.0 * c * b;
                    d[i + 1] = g + (p = s * r);
                    g = c * r - b;
                }
                if (r == 0.0 && i >= l) continue;
                d[l] -= p; e[l] = g; e[m] = 0.0;
            }
        } while (m != l);
    }
    return 0;
}

/* ---- bitmask max clique (n <= 16) ---- */
static unsigned adjm[16];
static int best_cl;
static void expand(int rsize, unsigned P) {
    while (P) {
        if (rsize + __builtin_popcount(P) <= best_cl) return;
        int v = __builtin_ctz(P);
        P &= ~(1u << v);
        if (rsize + 1 > best_cl) best_cl = rsize + 1;
        unsigned newP = P & adjm[v];
        if (newP) expand(rsize + 1, newP);
    }
}
static int max_clique(void) {
    best_cl = 0;
    expand(0, (1u << N) - 1);
    return best_cl;
}

/* greedy clique lower bound: grow from each vertex, pick highest-degree next */
static int greedy_clique(void) {
    int best = 1;
    for (int s = 0; s < N; s++) {
        unsigned P = adjm[s];
        int sz = 1;
        while (P) {
            int bv = -1, bd = -1;
            unsigned Q = P;
            while (Q) {
                int v = __builtin_ctz(Q); Q &= Q - 1;
                int d = __builtin_popcount(P & adjm[v]);
                if (d > bd) { bd = d; bv = v; }
            }
            sz++; P &= adjm[bv];
        }
        if (sz > best) best = sz;
    }
    return best;
}

/* Sturm count: number of eigenvalues of tridiagonal (d,e) strictly less than x */
static inline int sturm(const double d[], const double e2[], int n, double x) {
    int cnt = 0;
    double q = d[0] - x;
    if (q < 0) cnt++;
    for (int i = 1; i < n; i++) {
        double denom = (q == 0.0) ? 1e-300 : q;
        q = d[i] - x - e2[i] / denom;
        if (q < 0) cnt++;
    }
    return cnt;
}

/* bisect the k-th largest eigenvalue (k=1 or 2) into [lo,hi] of width <= tol */
static void bisect_kth(const double d[], const double e2[], int n, int k,
                       double lo, double hi, double tol, double *out_lo, double *out_hi) {
    /* k-th largest is >= x iff (# eigenvalues < x) <= n - k */
    while (hi - lo > tol) {
        double mid = 0.5 * (lo + hi);
        if (sturm(d, e2, n, mid) <= n - k) lo = mid; else hi = mid;
    }
    *out_lo = lo; *out_hi = hi;
}

int main(int argc, char **argv) {
    N = atoi(argv[1]);
    int nb = N * (N - 1) / 2, nbytes = (nb + 5) / 6;
    char line[64];
    long long total = 0, cliq = 0, cand = 0;
    double worst = -1e18;
    char worst_g6[64] = "";
    int oi[128], oj[128];
    { int k = 0; for (int j = 1; j < N; j++) for (int i = 0; i < j; i++) { oi[k]=i; oj[k]=j; k++; } }
    while (fgets(line, sizeof line, stdin)) {
        total++;
        double a[16][16] = {{0}};
        for (int v = 0; v < N; v++) adjm[v] = 0;
        int m2 = 0;
        for (int k = 0; k < nb; k++) {
            int byte = line[1 + k / 6] - 63;
            if (byte & (1 << (5 - k % 6))) {
                int i = oi[k], j = oj[k];
                a[i][j] = a[j][i] = 1.0;
                adjm[i] |= 1u << j; adjm[j] |= 1u << i;
                m2 += 2;
            }
        }
        if (m2 == N * (N - 1)) continue; /* K_n */
        double d[16], e[16];
        tred2(a, N, d, e);
        if (tql1(d, e, N)) { fprintf(stderr, "EIGFAIL %s", line); continue; }
        double l1 = -1e18, l2 = -1e18;
        for (int i = 0; i < N; i++) {
            if (d[i] > l1) { l2 = l1; l1 = d[i]; }
            else if (d[i] > l2) l2 = d[i];
        }
        double L = l1 * l1 + l2 * l2;
        double dm = (double)m2;
        /* violation possible only if omega < 2m/(2m-L); omega >= 2 always */
        if (dm - L > 1e-9 && dm / (dm - L) <= 2.0) continue;
        /* clique LOWER bound w_lb suffices to certify non-violation:
           RHS 2m(1-1/w) is increasing in w, so if L < 2m(1-1/w_lb) - eps
           then L < 2m(1-1/omega) as omega >= w_lb. */
        /* cheap single greedy from a max-degree vertex first */
        {
            int s = 0, bd = -1;
            for (int v = 0; v < N; v++) {
                int dv = __builtin_popcount(adjm[v]);
                if (dv > bd) { bd = dv; s = v; }
            }
            unsigned P = adjm[s]; int sz = 1;
            while (P) {
                int bv = -1, bb = -1; unsigned Q = P;
                while (Q) { int v = __builtin_ctz(Q); Q &= Q - 1;
                    int dd = __builtin_popcount(P & adjm[v]);
                    if (dd > bb) { bb = dd; bv = v; } }
                sz++; P &= adjm[bv];
            }
            if (L < dm * (1.0 - 1.0 / (double)sz) - 1e-7) continue;
        }
        int wlb = greedy_clique();
        if (L < dm * (1.0 - 1.0 / (double)wlb) - 1e-7) continue;
        cliq++;
        int w = max_clique();
        if (w >= N) continue;
        double score = L - dm * (1.0 - 1.0 / (double)w);
        if (score > worst) { worst = score; strcpy(worst_g6, line); }
        if (score > -1e-7) {
            cand++;
            printf("CAND %s score=%.12e w=%d\n", line, score, w);
        }
    }
    fprintf(stderr, "SUMMARY n=%d total=%lld cliqued=%lld cand=%lld worst=%.12e worst_g6=%s\n",
            N, total, cliq, cand, worst, worst_g6);
    return 0;
}

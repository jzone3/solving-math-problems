/* brouwer_check.c — exhaustive Brouwer-conjecture checker for geng graph6 stream.
 *
 * Reads graph6 lines (n <= 32) on stdin. For each graph:
 *   1) Cheap prune via Grone–Merris–Bai: S_t <= sum_{i<=t} d*_i (conjugate degrees).
 *      If sum_{i<=t} d*_i <= m + t(t+1)/2 for all tested t, Brouwer holds — skip.
 *   2) Otherwise eigensolve the Laplacian (cyclic Jacobi, double) and test
 *      S_t <= m + t(t+1)/2 for t in [TMIN, TMAX].
 *
 * Complement duality BC(G, t) <=> BC(complement(G), n-1-t), plus proven cases
 * t in {1,2,n-1,n}, means testing t in {3,...,floor((n-1)/2)} over a
 * complement-closed enumeration (geng: all graphs on n vertices) covers all t.
 *
 * Near-misses (float margin > -EPS) are printed as "NEAR <margin> <t> <graph6>"
 * for exact recheck. Violations print "VIOL ...". Summary on stderr at EOF.
 *
 * Usage: geng -q N | ./brouwer_check N [TMIN TMAX]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <lapacke.h>

static int jacobi_eigen(int n, double a[][32], double eval[]) {
    int iter, p, q, i;
    for (iter = 0; iter < 100; iter++) {
        double off = 0.0;
        for (p = 0; p < n; p++)
            for (q = p + 1; q < n; q++) off += a[p][q] * a[p][q];
        if (off < 1e-18) break;
        for (p = 0; p < n; p++) {
            for (q = p + 1; q < n; q++) {
                double apq = a[p][q];
                if (fabs(apq) < 1e-14) continue;
                double app = a[p][p], aqq = a[q][q];
                double theta = (aqq - app) / (2.0 * apq);
                double t = (theta >= 0 ? 1.0 : -1.0) /
                           (fabs(theta) + sqrt(theta * theta + 1.0));
                double c = 1.0 / sqrt(t * t + 1.0), s = t * c;
                for (i = 0; i < n; i++) {
                    double aip = a[i][p], aiq = a[i][q];
                    a[i][p] = c * aip - s * aiq;
                    a[i][q] = s * aip + c * aiq;
                }
                for (i = 0; i < n; i++) {
                    double api = a[p][i], aqi = a[q][i];
                    a[p][i] = c * api - s * aqi;
                    a[q][i] = s * api + c * aqi;
                }
            }
        }
    }
    for (i = 0; i < n; i++) eval[i] = a[i][i];
    /* sort descending (insertion, n small) */
    for (p = 1; p < n; p++) {
        double v = eval[p];
        for (q = p - 1; q >= 0 && eval[q] < v; q--) eval[q + 1] = eval[q];
        eval[q + 1] = v;
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s n [tmin tmax]\n", argv[0]); return 1; }
    int n = atoi(argv[1]);
    int TMIN = argc > 2 ? atoi(argv[2]) : 3;
    int TMAX = argc > 3 ? atoi(argv[3]) : (n - 1) / 2;
    const double EPS = 1e-6;

    char line[256];
    unsigned adj[32];
    int deg[32];
    long long total = 0, eigensolved = 0, nearmiss = 0, viol = 0;
    double maxmargin = -1e18;
    double mmax[600]; long long mcount[600];
    for (int i = 0; i < 600; i++) { mmax[i] = -1e18; mcount[i] = 0; }

    int nbits = n * (n - 1) / 2;
    int nbytes = (nbits + 5) / 6;

    while (fgets(line, sizeof line, stdin)) {
        if (line[0] - 63 != n) continue;   /* skip malformed / header lines */
        total++;
        memset(adj, 0, sizeof adj);
        memset(deg, 0, sizeof deg);
        int m = 0;
        {
            int bit = 0, i = 0, j = 1, k;
            for (k = 0; k < nbytes; k++) {
                int c = line[1 + k] - 63;
                int b;
                for (b = 5; b >= 0 && bit < nbits; b--, bit++) {
                    if (c & (1 << b)) {
                        adj[i] |= 1u << j; adj[j] |= 1u << i;
                        deg[i]++; deg[j]++; m++;
                    }
                    if (++i == j) { i = 0; j++; }
                }
            }
        }
        /* conjugate degree prune */
        int cnt[33];
        memset(cnt, 0, sizeof cnt);
        for (int i = 0; i < n; i++) cnt[deg[i]]++;
        /* d*_k = #{i: deg_i >= k} */
        int need = 0;
        int fail[33]; /* t values failing Bai prune on G */
        {
            long s = 0;
            int geq = n; /* #deg >= 0 */
            for (int k = 1; k <= TMAX; k++) {
                geq -= cnt[k - 1];
                s += geq;
                fail[k] = 0;
                if (k >= TMIN && s > (long)m + (long)k * (k + 1) / 2) { fail[k] = 1; need = 1; }
            }
        }
        if (need) {
            /* second prune: Bai on complement at t' = n-1-t (BC duality) */
            int ccnt[33];
            memset(ccnt, 0, sizeof ccnt);
            for (int i = 0; i < n; i++) ccnt[n - 1 - deg[i]]++;
            int cm = n * (n - 1) / 2 - m;
            long cs = 0;
            int geq = n;
            long csum[33];
            for (int k = 1; k <= n; k++) {
                geq -= ccnt[k - 1];
                cs += geq;
                csum[k] = cs;
            }
            need = 0;
            for (int t = TMIN; t <= TMAX; t++) {
                if (!fail[t]) continue;
                int tp = n - 1 - t;
                if (tp >= 1 && tp <= n &&
                    csum[tp] <= (long)cm + (long)tp * (tp + 1) / 2) continue;
                need = 1;
            }
        }
        if (!need) continue;
        eigensolved++;
        mcount[m]++;
        double a[32][32];
        memset(a, 0, sizeof a);
        for (int i = 0; i < n; i++) {
            a[i][i] = deg[i];
            for (int j = 0; j < n; j++)
                if (i != j && (adj[i] >> j & 1)) a[i][j] = -1.0;
        }
        double ev[32], amat[32*32];
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) amat[i*n+j]=a[i][j];
        LAPACKE_dsyev(LAPACK_ROW_MAJOR, 'N', 'U', n, amat, n, ev);
        for (int i = 0; i < n/2; i++) { double tmp=ev[i]; ev[i]=ev[n-1-i]; ev[n-1-i]=tmp; }
        double s = 0;
        for (int t = 1; t <= TMAX; t++) {
            s += ev[t - 1];
            if (t < TMIN) continue;
            double margin = s - m - (double)t * (t + 1) / 2.0;
            if (margin > maxmargin) maxmargin = margin;
            if (margin > mmax[m]) mmax[m] = margin;
            if (margin > EPS) {
                viol++;
                line[strcspn(line, "\r\n")] = 0;
                printf("VIOL %.9f %d %s\n", margin, t, line);
            } else if (margin > -EPS) {
                nearmiss++;
                line[strcspn(line, "\r\n")] = 0;
                printf("NEAR %.9f %d %s\n", margin, t, line);
            }
        }
    }
    for (int i = 0; i < 600; i++)
        if (mcount[i]) fprintf(stderr, "M %d eig=%lld maxmargin=%.9f\n", i, mcount[i], mmax[i]);
    fprintf(stderr,
            "SUMMARY n=%d t=[%d,%d] total=%lld eigensolved=%lld near=%lld viol=%lld maxmargin=%.9f\n",
            n, TMIN, TMAX, total, eigensolved, nearmiss, viol, maxmargin);
    return viol ? 2 : 0;
}

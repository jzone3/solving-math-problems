/* P09: graphon-step relaxation attack (extension of blowup.c).
 *
 * For a support pattern H on k vertices (parts are independent sets), consider
 * step-graphons W with W_ij in (0,1] exactly on the edges of H (0 elsewhere)
 * and part fractions c on the simplex. The n-blowup G_n with random bipartite
 * densities W_ij has, a.a.s., omega(G_n) = omega(H) (cliques use pairwise-
 * positive-density parts), while
 *     lambda_i(G_n) ~ n * mu_i(C^{1/2} W C^{1/2}),   2m ~ n^2 * S,
 *     S = sum_{ij} c_i c_j W_ij.
 * Conjecture in the limit: F = mu_1^2 + mu_2^2 - S(1 - 1/omega(H)) <= 0.
 * Any F > 0 rounds to a finite counterexample (with second-order corrections;
 * would be confirmed exactly by solutions/P09/verify.py on a concrete graph).
 *
 * Optimizes F jointly over (W restricted to edges of H, clamped to
 * [WMIN, 1]) and c (simplex) with multi-restart adaptive ascent.
 *
 * Usage: ./blowup2 [report_tol] [restarts]   (patterns graph6 on stdin)
 * Build: gcc -O3 -march=native -o blowup2 blowup2.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#define MAXK 12
#define MAXE (MAXK * (MAXK - 1) / 2)
#define WMIN 1e-4
static int K, NE;
static int EU[MAXE], EV[MAXE];
static uint32_t adj[MAXK];

static void jacobi_eig(int n, double m0[MAXK][MAXK], double *ev) {
    static double m[MAXK][MAXK];
    memcpy(m, m0, sizeof m);
    for (int sweep = 0; sweep < 50; sweep++) {
        double off = 0;
        for (int p = 0; p < n - 1; p++)
            for (int q = p + 1; q < n; q++) off += m[p][q] * m[p][q];
        if (off < 1e-24) break;
        for (int p = 0; p < n - 1; p++)
            for (int q = p + 1; q < n; q++) {
                double apq = m[p][q];
                if (fabs(apq) < 1e-15) continue;
                double theta = 0.5 * (m[q][q] - m[p][p]) / apq;
                double t = (theta >= 0 ? 1.0 : -1.0) /
                           (fabs(theta) + sqrt(theta * theta + 1.0));
                double c = 1.0 / sqrt(t * t + 1.0), s = t * c;
                for (int r = 0; r < n; r++) {
                    double mrp = m[r][p], mrq = m[r][q];
                    m[r][p] = c * mrp - s * mrq;
                    m[r][q] = s * mrp + c * mrq;
                }
                for (int r = 0; r < n; r++) {
                    double mpr = m[p][r], mqr = m[q][r];
                    m[p][r] = c * mpr - s * mqr;
                    m[q][r] = s * mpr + c * mqr;
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
    expand((1u << n) - 1, 0);
    return best_clique;
}

static double omega_factor;

/* parameter vector x: x[0..NE-1] = W on edges (in [WMIN,1]); x[NE..NE+K-1] = c */
static double F(const double *x) {
    static double M[MAXK][MAXK];
    const double *w = x, *c = x + NE;
    double sq[MAXK], S = 0;
    for (int i = 0; i < K; i++) sq[i] = sqrt(c[i] > 0 ? c[i] : 0);
    memset(M, 0, sizeof M);
    for (int e = 0; e < NE; e++) {
        int i = EU[e], j = EV[e];
        M[i][j] = M[j][i] = w[e] * sq[i] * sq[j];
        S += 2.0 * w[e] * c[i] * c[j];
    }
    double ev[MAXK];
    jacobi_eig(K, M, ev);
    double l1 = -1e18, l2 = -1e18;
    for (int i = 0; i < K; i++) {
        if (ev[i] > l1) { l2 = l1; l1 = ev[i]; }
        else if (ev[i] > l2) l2 = ev[i];
    }
    /* blowup limit: lambda_2(G_n)/n -> max(mu_2, 0) (bulk zeros dominate) */
    if (l2 < 0) l2 = 0;
    return l1 * l1 + l2 * l2 - S * omega_factor;
}

static unsigned long long rng_state = 6364136223846793005ull;
static double rnd(void) {
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 7;
    rng_state ^= rng_state << 17;
    return (double)(rng_state >> 11) / 9007199254740992.0;
}

static void project(double *x) {
    for (int e = 0; e < NE; e++) {
        if (x[e] < WMIN) x[e] = WMIN;
        if (x[e] > 1.0) x[e] = 1.0;
    }
    double z = 0;
    for (int i = 0; i < K; i++) {
        if (x[NE + i] < 0) x[NE + i] = 0;
        z += x[NE + i];
    }
    for (int i = 0; i < K; i++) x[NE + i] /= z;
}

static double optimize(double *x) {
    int D = NE + K;
    double step = 0.25;
    double f = F(x);
    for (int it = 0; it < 600 && step > 1e-10; it++) {
        double g[MAXE + MAXK];
        double h = 1e-6;
        for (int d = 0; d < D; d++) {
            double tmp[MAXE + MAXK];
            memcpy(tmp, x, D * sizeof(double));
            tmp[d] += h;
            project(tmp);
            g[d] = (F(tmp) - f) / h;
        }
        double gmax = 0;
        for (int d = 0; d < D; d++) if (fabs(g[d]) > gmax) gmax = fabs(g[d]);
        if (gmax < 1e-12) break;
        int improved = 0;
        while (step > 1e-10) {
            double xn[MAXE + MAXK];
            for (int d = 0; d < D; d++) xn[d] = x[d] + step * g[d] / gmax;
            project(xn);
            double fn = F(xn);
            if (fn > f + 1e-16) {
                memcpy(x, xn, D * sizeof(double));
                f = fn;
                step *= 1.3;
                if (step > 0.5) step = 0.5;
                improved = 1;
                break;
            }
            step *= 0.5;
        }
        if (!improved) break;
    }
    return f;
}

int main(int argc, char **argv) {
    double report_tol = argc > 1 ? atof(argv[1]) : 1e-7;
    int restarts = argc > 2 ? atoi(argv[2]) : 6;
    char line[256];
    long long total = 0;
    double gbest = -1e18;
    char gbest_g6[128] = "";

    while (fgets(line, sizeof line, stdin)) {
        char *g6 = line;
        size_t len = strlen(g6);
        while (len && (g6[len - 1] == '\n' || g6[len - 1] == '\r')) g6[--len] = 0;
        if (!len) continue;
        int k = g6[0] - 63;
        if (k < 2 || k > MAXK) continue;
        K = k;
        NE = 0;
        memset(adj, 0, sizeof adj);
        int m = 0;
        {
            int b = 0;
            for (int j = 1; j < k; j++)
                for (int i = 0; i < j; i++) {
                    int byte = 1 + b / 6, bit = 5 - (b % 6);
                    b++;
                    if ((g6[byte] - 63) & (1 << bit)) {
                        EU[NE] = i; EV[NE] = j; NE++;
                        adj[i] |= 1u << j; adj[j] |= 1u << i;
                        m++;
                    }
                }
        }
        if (m == 0) continue;
        total++;
        int w = max_clique(k);
        omega_factor = 1.0 - 1.0 / w;
        double best = -1e18, bx[MAXE + MAXK];
        for (int r = 0; r < restarts; r++) {
            double x[MAXE + MAXK];
            if (r == 0) {
                for (int e = 0; e < NE; e++) x[e] = 1.0;
                for (int i = 0; i < K; i++) x[NE + i] = 1.0 / K;
            } else {
                for (int e = 0; e < NE; e++) x[e] = 0.2 + 0.8 * rnd();
                for (int i = 0; i < K; i++) { double u = rnd(); x[NE + i] = 0.02 + u * u; }
            }
            project(x);
            double f = optimize(x);
            if (f > best) { best = f; memcpy(bx, x, sizeof bx); }
        }
        if (best > gbest) { gbest = best; strncpy(gbest_g6, g6, 127); }
        if (best > report_tol) {
            printf("POSITIVE %s k=%d w=%d F=%.12e W=", g6, k, w, best);
            for (int e = 0; e < NE; e++) printf("%.4f%c", bx[e], e == NE - 1 ? ' ' : ',');
            printf("c=");
            for (int i = 0; i < K; i++) printf("%.6f%c", bx[NE + i], i == K - 1 ? '\n' : ',');
            fflush(stdout);
        }
    }
    fprintf(stderr, "BLOWUP2-SUMMARY patterns=%lld global_best_F=%.6e g6=%s\n",
            total, gbest, gbest_g6);
    return 0;
}

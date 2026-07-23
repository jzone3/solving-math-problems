/* P09 Bollobas-Nikiforov: weighted-blowup / continuous-relaxation attack.
 *
 * For a pattern graph H on k vertices with clique number w, the balanced-limit
 * of blowups of H with part fractions c (c_i >= 0, sum c_i = 1, parts are
 * independent sets, so omega(blowup) = w) has, per vertex-count n -> infinity:
 *     lambda_i(G) ~ n * mu_i,   mu_i = eigenvalues of  C^{1/2} A_H C^{1/2},
 *     2m(G)      ~ n^2 * S,     S    = sum_{ij} c_i c_j A_ij.
 * So the conjectured inequality in the blowup limit reads
 *     F(c) = mu_1^2 + mu_2^2 - S * (1 - 1/w)  <=  0.
 * Any pattern + weights with F(c) > 0 (strictly, beyond finite-size correction
 * terms) yields an explicit finite counterexample by rounding n*c_i.
 *
 * This program reads graph6 patterns on stdin and maximizes F over the simplex
 * with multi-restart adaptive exponentiated-gradient ascent (finite-difference
 * gradients, Jacobi eigensolver). Note F_max >= 0 always: supporting c on a
 * maximum clique reproduces the Turan equality case. We look for F > TOL.
 *
 * Output: per-pattern best F if F > report threshold; global summary on stderr.
 * Build: gcc -O3 -march=native -o blowup blowup.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#define MAXK 16
static int K;
static double A[MAXK][MAXK];
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

static double omega_factor; /* 1 - 1/w */

static double F(const double *c) {
    static double M[MAXK][MAXK];
    double sq[MAXK];
    double S = 0;
    for (int i = 0; i < K; i++) sq[i] = sqrt(c[i] > 0 ? c[i] : 0);
    for (int i = 0; i < K; i++)
        for (int j = 0; j < K; j++) {
            M[i][j] = A[i][j] * sq[i] * sq[j];
            S += A[i][j] * c[i] * c[j];
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

static unsigned long long rng_state = 88172645463325252ull;
static double rnd(void) {
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 7;
    rng_state ^= rng_state << 17;
    return (double)(rng_state >> 11) / 9007199254740992.0;
}

/* exponentiated-gradient ascent with finite-difference gradient */
static double optimize(double *c) {
    double eta = 0.5;
    double f = F(c);
    for (int it = 0; it < 400 && eta > 1e-9; it++) {
        double g[MAXK], cn[MAXK];
        double h = 1e-6;
        /* finite-difference gradient on the simplex (renormalized bump) */
        for (int i = 0; i < K; i++) {
            double tmp[MAXK];
            double z = 1.0 + h;
            for (int j = 0; j < K; j++) tmp[j] = c[j] / z;
            tmp[i] = (c[i] + h) / z;
            g[i] = (F(tmp) - f) / h;
        }
        double gmax = 0;
        for (int i = 0; i < K; i++) if (fabs(g[i]) > gmax) gmax = fabs(g[i]);
        if (gmax < 1e-12) break;
        int improved = 0;
        while (eta > 1e-9) {
            double z = 0;
            for (int i = 0; i < K; i++) { cn[i] = c[i] * exp(eta * g[i] / gmax); z += cn[i]; }
            for (int i = 0; i < K; i++) cn[i] /= z;
            double fn = F(cn);
            if (fn > f + 1e-15) {
                memcpy(c, cn, K * sizeof(double));
                f = fn;
                eta *= 1.3;
                if (eta > 2.0) eta = 2.0;
                improved = 1;
                break;
            }
            eta *= 0.5;
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
    double gbest_c[MAXK];
    int gbest_k = 0;

    while (fgets(line, sizeof line, stdin)) {
        char *g6 = line;
        size_t len = strlen(g6);
        while (len && (g6[len - 1] == '\n' || g6[len - 1] == '\r')) g6[--len] = 0;
        if (!len) continue;
        int k = g6[0] - 63;
        if (k < 2 || k > MAXK) continue;
        K = k;
        memset(adj, 0, sizeof adj);
        int m = 0;
        for (int i = 0; i < k; i++)
            for (int j = 0; j < k; j++) A[i][j] = 0;
        {
            int b = 0;
            for (int j = 1; j < k; j++)
                for (int i = 0; i < j; i++) {
                    int byte = 1 + b / 6, bit = 5 - (b % 6);
                    b++;
                    if ((g6[byte] - 63) & (1 << bit)) {
                        A[i][j] = A[j][i] = 1.0;
                        adj[i] |= 1u << j; adj[j] |= 1u << i;
                        m++;
                    }
                }
        }
        if (m == 0) continue;
        total++;
        int w = max_clique(k);
        if (m == k * (k - 1) / 2) continue; /* complete pattern: Turan equality */
        omega_factor = 1.0 - 1.0 / w;
        double best = -1e18, bc[MAXK];
        for (int r = 0; r < restarts; r++) {
            double c[MAXK], z = 0;
            if (r == 0) { for (int i = 0; i < k; i++) c[i] = 1.0; }
            else if (r == 1) {
                /* degree-weighted start */
                for (int i = 0; i < k; i++) c[i] = 0.05 + __builtin_popcount(adj[i]);
            } else {
                for (int i = 0; i < k; i++) { double u = rnd(); c[i] = 0.02 + u * u; }
            }
            z = 0; for (int i = 0; i < k; i++) z += c[i];
            for (int i = 0; i < k; i++) c[i] /= z;
            double f = optimize(c);
            if (f > best) { best = f; memcpy(bc, c, sizeof bc); }
        }
        if (best > gbest) {
            gbest = best; strncpy(gbest_g6, g6, 127); gbest_k = k;
            memcpy(gbest_c, bc, sizeof gbest_c);
        }
        if (best > report_tol) {
            printf("POSITIVE %s k=%d w=%d F=%.12e c=", g6, k, w, best);
            for (int i = 0; i < k; i++) printf("%.6f%c", bc[i], i == k - 1 ? '\n' : ',');
            fflush(stdout);
        }
    }
    fprintf(stderr, "BLOWUP-SUMMARY patterns=%lld global_best_F=%.6e g6=%s k=%d c=",
            total, gbest, gbest_g6, gbest_k);
    for (int i = 0; i < gbest_k; i++)
        fprintf(stderr, "%.6f%c", gbest_c[i], i == gbest_k - 1 ? '\n' : ',');
    return 0;
}

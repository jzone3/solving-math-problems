/* P09 Bollobas-Nikiforov: free-form weighted-graph gradient ascent (round 11).
 *
 * Search space: symmetric W in [0,1]^{n x n}, zero diagonal (the full cube
 * of edge-weighted graphs on n vertices; binary points = ordinary graphs).
 * Objective (exact at binary points, where it equals the B-N gap):
 *     F(W) = l1(W)^2 + l2(W)^2 - 2m(W) * t(W),
 * with 2m = sum of all entries of W and t(W) = max_{x in simplex} x^T W x,
 * the Motzkin-Straus program: at binary W, t = 1 - 1/omega exactly.
 * t is computed by replicator dynamics from several starts; l1,l2 and
 * eigenvectors by Jacobi.  Ascent by projected gradient with adaptive step:
 *     dF/dW_ij = 4 l1 v1_i v1_j + 4 l2 v2_i v2_j - 2 t - 4 m x_i x_j.
 * Any binary (or roundable) maximizer with F > 1e-7 is a counterexample
 * candidate (re-verify with verify.py).
 *
 * Usage: ./flow n restarts iters seed
 * Build: gcc -O3 -march=native -o flow flow.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAXN 48
static int N;
static double W[MAXN][MAXN];

static unsigned long long rs;
static double rnd(void) {
    rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17;
    return (double)(rs >> 11) / 9007199254740992.0;
}

/* Jacobi eigendecomposition: A destroyed, eigenvalues in d, vectors in V cols */
static void jacobi(int n, double A[MAXN][MAXN], double *d, double V[MAXN][MAXN]) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) V[i][j] = (i == j);
    }
    for (int sweep = 0; sweep < 100; sweep++) {
        double off = 0;
        for (int p = 0; p < n; p++)
            for (int q = p + 1; q < n; q++) off += A[p][q] * A[p][q];
        if (off < 1e-22) break;
        for (int p = 0; p < n; p++)
            for (int q = p + 1; q < n; q++) {
                if (fabs(A[p][q]) < 1e-14) continue;
                double theta = (A[q][q] - A[p][p]) / (2.0 * A[p][q]);
                double t = (theta >= 0 ? 1.0 : -1.0) / (fabs(theta) + sqrt(theta * theta + 1.0));
                double c = 1.0 / sqrt(t * t + 1.0), s = t * c;
                for (int k = 0; k < n; k++) {
                    double akp = A[k][p], akq = A[k][q];
                    A[k][p] = c * akp - s * akq;
                    A[k][q] = s * akp + c * akq;
                }
                for (int k = 0; k < n; k++) {
                    double apk = A[p][k], aqk = A[q][k];
                    A[p][k] = c * apk - s * aqk;
                    A[q][k] = s * apk + c * aqk;
                }
                for (int k = 0; k < n; k++) {
                    double vkp = V[k][p], vkq = V[k][q];
                    V[k][p] = c * vkp - s * vkq;
                    V[k][q] = s * vkp + c * vkq;
                }
            }
    }
    for (int i = 0; i < n; i++) d[i] = A[i][i];
}

/* Motzkin-Straus value + maximizer x via replicator dynamics, multi-start */
static double motzkin(double x_out[MAXN]) {
    double best = -1;
    for (int st = 0; st < 6; st++) {
        double x[MAXN], y[MAXN];
        double s = 0;
        for (int i = 0; i < N; i++) { x[i] = (st == 0) ? 1.0 : 0.05 + rnd(); s += x[i]; }
        for (int i = 0; i < N; i++) x[i] /= s;
        double val = 0;
        for (int it = 0; it < 4000; it++) {
            double q = 0;
            for (int i = 0; i < N; i++) {
                double wi = 0;
                for (int j = 0; j < N; j++) wi += W[i][j] * x[j];
                y[i] = x[i] * wi;
                q += y[i];
            }
            if (q < 1e-15) break;
            double diff = 0;
            for (int i = 0; i < N; i++) {
                double nx = y[i] / q;
                diff += fabs(nx - x[i]);
                x[i] = nx;
            }
            val = q;
            if (diff < 1e-13) break;
        }
        if (val > best) {
            best = val;
            if (x_out) memcpy(x_out, x, sizeof(double) * N);
        }
    }
    return best;
}

static double eval(double *l1o, double *l2o, double v1[MAXN], double v2[MAXN],
                   double *mo, double *to, double x[MAXN]) {
    static double A[MAXN][MAXN], V[MAXN][MAXN];
    memcpy(A, W, sizeof W);
    double d[MAXN];
    jacobi(N, A, d, V);
    int i1 = 0, i2 = -1;
    for (int i = 1; i < N; i++) if (d[i] > d[i1]) i1 = i;
    for (int i = 0; i < N; i++) if (i != i1 && (i2 < 0 || d[i] > d[i2])) i2 = i;
    double l1 = d[i1], l2 = d[i2];
    double m2 = 0;
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) m2 += W[i][j];
    double t = motzkin(x);
    if (l1o) {
        *l1o = l1; *l2o = l2; *mo = m2 / 2; *to = t;
        for (int i = 0; i < N; i++) { v1[i] = V[i][i1]; v2[i] = V[i][i2]; }
    }
    return l1 * l1 + l2 * l2 - m2 * t;
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s n restarts iters seed\n", argv[0]); return 1; }
    N = atoi(argv[1]);
    int restarts = atoi(argv[2]);
    int iters = atoi(argv[3]);
    rs = strtoull(argv[4], 0, 10) * 2654435761ull + 88172645463325252ull;

    double gbest = -1e18;
    for (int r = 0; r < restarts; r++) {
        double dens = 0.2 + 0.7 * rnd();
        for (int i = 0; i < N; i++)
            for (int j = 0; j < N; j++) W[i][j] = 0;
        if (r % 3 == 2) {
            /* noisy complete-multipartite start */
            int parts = 2 + (int)(rnd() * 6), pt[MAXN];
            for (int i = 0; i < N; i++) pt[i] = (int)(rnd() * parts);
            for (int j = 1; j < N; j++)
                for (int i = 0; i < j; i++) {
                    double w = (pt[i] != pt[j]) ? 0.9 + 0.1 * rnd() : 0.1 * rnd();
                    W[i][j] = W[j][i] = w;
                }
        } else {
            for (int j = 1; j < N; j++)
                for (int i = 0; i < j; i++) {
                    double w = (rnd() < dens) ? 0.5 + 0.5 * rnd() : 0.3 * rnd();
                    W[i][j] = W[j][i] = w;
                }
        }
        double step = 0.05;
        double l1, l2, m, t, v1[MAXN], v2[MAXN], x[MAXN];
        double cur = eval(&l1, &l2, v1, v2, &m, &t, x);
        for (int it = 0; it < iters; it++) {
            static double G[MAXN][MAXN], Wsave[MAXN][MAXN];
            for (int j = 1; j < N; j++)
                for (int i = 0; i < j; i++) {
                    double g = 4 * l1 * v1[i] * v1[j] + 4 * l2 * v2[i] * v2[j]
                             - 2 * t - 4 * m * x[i] * x[j];
                    G[i][j] = g;
                }
            memcpy(Wsave, W, sizeof W);
            for (int j = 1; j < N; j++)
                for (int i = 0; i < j; i++) {
                    double w = W[i][j] + step * G[i][j];
                    if (w < 0) w = 0;
                    if (w > 1) w = 1;
                    W[i][j] = W[j][i] = w;
                }
            double nv = eval(&l1, &l2, v1, v2, &m, &t, x);
            if (nv >= cur - 1e-12) {
                cur = nv;
                step *= 1.1;
                if (step > 0.5) step = 0.5;
            } else {
                memcpy(W, Wsave, sizeof W);
                step *= 0.5;
                double tmp[MAXN];
                cur = eval(&l1, &l2, v1, v2, &m, &t, tmp);
                memcpy(x, tmp, sizeof tmp);
                if (step < 1e-9) break;
            }
        }
        /* count fractional entries and report */
        int frac = 0;
        for (int j = 1; j < N; j++)
            for (int i = 0; i < j; i++)
                if (W[i][j] > 1e-6 && W[i][j] < 1 - 1e-6) frac++;
        /* threshold-round to binary and evaluate the discrete gap too */
        static double Wc[MAXN][MAXN];
        memcpy(Wc, W, sizeof W);
        double bestround = -1e18;
        double thr_used = 0.5;
        for (int ti = 1; ti <= 9; ti++) {
            double thr = ti / 10.0;
            for (int i = 0; i < N; i++)
                for (int j = 0; j < N; j++)
                    W[i][j] = (i != j && Wc[i][j] >= thr) ? 1.0 : 0.0;
            double tmpx[MAXN];
            double fd = eval(0, 0, 0, 0, 0, 0, tmpx);
            if (fd > bestround) { bestround = fd; thr_used = thr; }
        }
        memcpy(W, Wc, sizeof Wc);
        if (bestround > gbest) gbest = bestround;
        if (cur > gbest) gbest = cur;
        fprintf(stderr, "restart n=%d r=%d F=%.6e round_F=%.6e thr=%.1f frac=%d m=%.2f t=%.4f (omega~%.2f)\n",
                N, r, cur, bestround, thr_used, frac, m, t, 1.0 / (1.0 - t));
        if (cur > 1e-7 || bestround > 1e-7) {
            printf("CANDIDATE n=%d F=%.6e frac=%d W=\n", N, cur, frac);
            for (int i = 0; i < N; i++) {
                for (int j = 0; j < N; j++) printf("%.4f ", W[i][j]);
                printf("\n");
            }
            fflush(stdout);
        }
        fflush(stderr);
    }
    fprintf(stderr, "FLOW-SUMMARY n=%d restarts=%d iters=%d best_F=%.6e\n",
            N, restarts, iters, gbest);
    return 0;
}

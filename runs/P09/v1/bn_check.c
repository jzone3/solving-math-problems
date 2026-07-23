/* Fast Bollobas-Nikiforov checker for geng graph6 output (fixed n <= 32).
 *
 * For each graph: decode g6, compute top-2 adjacency eigenvalues via Householder
 * tridiagonalization + Sturm bisection, r = 2m - l1^2 - l2^2.
 * Violation <=> omega * r < 2m (omega small helps). Since omega >= 2 when m > 0,
 * survivors of the cheap test  2r < 2m + MARG  are resolved with a greedy clique
 * lower bound and an exact branch-and-bound MaxClique; any graph with
 * omega*r < 2m - MARG (a candidate violation) is printed for exact re-verification.
 *
 * Usage: geng -q n | ./bn_check n [tag]
 * Compile: gcc -O3 -march=native -o bn_check bn_check.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

static int N;
static uint32_t adjm[32];

/* ---------- exact max clique (Tomita-style, greedy coloring bound) ---------- */
static int mc_best;
static void mc_expand(uint32_t P, int size) {
    if (!P) { if (size > mc_best) mc_best = size; return; }
    /* greedy coloring bound */
    int v_list[32], color[32], nv = 0;
    uint32_t Q = P;
    while (Q) { int v = __builtin_ctz(Q); Q &= Q - 1; v_list[nv++] = v; }
    uint32_t classes[32]; int nc = 0;
    for (int i = 0; i < nv; i++) {
        int v = v_list[i], c = 0;
        while (c < nc && (classes[c] & adjm[v])) c++;
        if (c == nc) classes[nc++] = 0;
        classes[c] |= 1u << v;
        color[i] = c + 1;
    }
    /* sort vertices by color ascending (stable insertion sort) */
    for (int i = 1; i < nv; i++) {
        int v = v_list[i], c = color[i], j = i - 1;
        while (j >= 0 && color[j] > c) {
            v_list[j+1] = v_list[j]; color[j+1] = color[j]; j--;
        }
        v_list[j+1] = v; color[j+1] = c;
    }
    /* process in reverse (highest color first); prune when bound too small */
    for (int i = nv - 1; i >= 0; i--) {
        int v = v_list[i];
        if (size + color[i] <= mc_best) return;
        mc_expand(P & adjm[v], size + 1);
        P &= ~(1u << v);
    }
}
static int max_clique(void) {
    mc_best = 0;
    mc_expand((N >= 32 ? 0xFFFFFFFFu : ((1u << N) - 1)), 0);
    return mc_best;
}
static int greedy_clique(void) {
    int order[32];
    for (int i = 0; i < N; i++) order[i] = i;
    /* sort by degree desc (insertion) */
    for (int i = 1; i < N; i++) {
        int v = order[i], j = i - 1;
        while (j >= 0 && __builtin_popcount(adjm[order[j]]) < __builtin_popcount(adjm[v]))
            { order[j+1] = order[j]; j--; }
        order[j+1] = v;
    }
    uint32_t cand = (N >= 32 ? 0xFFFFFFFFu : ((1u << N) - 1));
    int size = 0;
    for (int i = 0; i < N; i++) {
        int v = order[i];
        if (cand & (1u << v)) { size++; cand &= adjm[v]; }
    }
    return size;
}

/* ---------- top-2 eigenvalues: tridiagonalize + Sturm bisection ----------
 * If thr >= 0, returns 1 early as soon as l1^2 + l2^2 <= thr is certain (SAFE),
 * and 0 when it is certain that l1^2 + l2^2 > thr (caller must resolve exactly);
 * *l1/*l2 are then best current estimates (call again with thr < 0 for full
 * precision). If thr < 0, computes l1, l2 to full precision and returns 0. */
static int top2_eigs(double *l1, double *l2, double thr) {
    double a[32][32];
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            a[i][j] = (adjm[i] >> j) & 1 ? 1.0 : 0.0;
    double d[32], e[32];
    /* Householder tridiagonalization (from Numerical Recipes tred2, eigenvalues only) */
    for (int i = N - 1; i >= 1; i--) {
        int l = i - 1;
        double h = 0.0, scale = 0.0;
        if (l > 0) {
            for (int k = 0; k <= l; k++) scale += fabs(a[i][k]);
            if (scale == 0.0) e[i] = a[i][l];
            else {
                for (int k = 0; k <= l; k++) { a[i][k] /= scale; h += a[i][k] * a[i][k]; }
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
                    for (int k = 0; k <= j; k++) a[j][k] -= (f * e[k] + g * a[i][k]);
                }
            }
        } else e[i] = a[i][l];
        d[i] = h;
    }
    e[0] = 0.0;
    for (int i = 0; i < N; i++) d[i] = a[i][i];
    /* d = diagonal, e[1..] = off-diagonal of tridiagonal matrix */
    double diag[32], off2[32];
    for (int i = 0; i < N; i++) diag[i] = d[i];
    off2[0] = 0.0;
    for (int i = 1; i < N; i++) off2[i] = e[i] * e[i];
    /* Sturm count: number of eigenvalues < x */
    /* Gershgorin bounds */
    double lo = -32.0, hi = 32.0;
    /* find k-th largest eigenvalue (k=1,2) by bisection */
    for (int k = 1; k <= 2; k++) {
        double a0 = lo, b0 = hi;
        if (k == 2) b0 = *l1 + 1e-9;
        int want = N - k; /* eigenvalues below target */
        for (int it = 0; it < 42; it++) {
            if (thr >= 0.0) {
                if (k == 1) {
                    if (2.0 * b0 * b0 <= thr && b0 >= 0) return 1;      /* SAFE */
                    if (a0 > 0 && a0 * a0 > thr) { *l1 = a0; *l2 = a0; return 0; }
                } else {
                    double base = (*l1) * (*l1);
                    double amax = a0 * a0 > b0 * b0 ? a0 * a0 : b0 * b0;
                    double amin = (a0 > 0) ? a0 * a0 : (b0 < 0 ? b0 * b0 : 0.0);
                    if (base + amax <= thr) return 1;
                    if (base + amin > thr) { *l2 = a0; return 0; }
                }
            }
            double x = 0.5 * (a0 + b0);
            int cnt = 0;
            double q = diag[0] - x;
            if (q < 0) cnt++;
            for (int i = 1; i < N; i++) {
                q = diag[i] - x - (q == 0.0 ? off2[i] / 1e-300 : off2[i] / q);
                if (q < 0) cnt++;
            }
            if (cnt <= want) a0 = x; else b0 = x;
        }
        double val = 0.5 * (a0 + b0);
        if (k == 1) *l1 = val; else *l2 = val;
    }
    if (thr >= 0.0) {
        double s = (*l1) * (*l1) + (*l2) * (*l2);
        return s <= thr ? 1 : 0;
    }
    return 0;
}

int main(int argc, char **argv) {
    N = atoi(argv[1]);
    const char *tag = argc > 2 ? argv[2] : "";
    int nb = N * (N - 1) / 2;
    int nchars = (nb + 5) / 6;
    int linelen = 1 + nchars + 1;
    unsigned char *buf = malloc((size_t)linelen * 100000);
    long long total = 0, survivors = 0, candidates = 0;
    double bestscore = -1e18;
    char bestg6[64] = "";
    const double MARG = 1e-5;
    size_t got;
    while ((got = fread(buf, 1, (size_t)linelen * 100000, stdin)) > 0) {
        if (got % linelen) { fprintf(stderr, "partial read!\n"); return 1; }
        long k = got / linelen;
        for (long g = 0; g < k; g++) {
            unsigned char *line = buf + g * linelen;
            total++;
            memset(adjm, 0, sizeof(adjm));
            int m = 0;
            int bit = 0;
            /* decode: bits column-major over pairs (i<j) */
            for (int j = 1; j < N; j++) {
                for (int i = 0; i < j; i++, bit++) {
                    int ch = line[1 + bit / 6] - 63;
                    if ((ch >> (5 - bit % 6)) & 1) {
                        adjm[i] |= 1u << j;
                        adjm[j] |= 1u << i;
                        m++;
                    }
                }
            }
            if (m == 0 || m == nb) continue; /* empty or complete */
            double m2 = 2.0 * m;
            int gcl = greedy_clique();
            double thr = (gcl < N) ? m2 * (1.0 - 1.0 / gcl) - MARG : -1.0;
            double l1, l2;
            if (gcl < N && top2_eigs(&l1, &l2, thr)) continue; /* safe via greedy omega */
            top2_eigs(&l1, &l2, -1.0); /* full precision for the rare survivors */
            double r = m2 - l1 * l1 - l2 * l2;
            survivors++;
            int om = max_clique();
            if (om >= N) continue; /* complete (shouldn't reach) */
            if (om * r >= m2 - MARG) continue;
            candidates++;
            double score = l1 * l1 + l2 * l2 - m2 * (1.0 - 1.0 / om);
            line[linelen - 1] = 0;
            printf("CANDIDATE n=%d g6=%s score=%.9f l1=%.9f l2=%.9f m=%d omega=%d\n",
                   N, line, score, l1, l2, m, om);
            if (score > bestscore) { bestscore = score; strncpy(bestg6, (char*)line, 63); }
        }
    }
    fprintf(stderr, "[%s] n=%d total=%lld survivors=%lld candidates=%lld best=%.6e %s\n",
            tag, N, total, survivors, candidates, bestscore, bestg6);
    return 0;
}

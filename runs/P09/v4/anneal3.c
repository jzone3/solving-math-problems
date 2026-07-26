/* P09 Bollobas-Nikiforov: fixed-omega constrained annealing (round 8).
 *
 * Searches only graphs with clique number omega <= CAP (targeting the
 * smallest structurally open subcases beyond triangle-free: omega = 3,4,5).
 * Maximizes gap(G) = l1^2 + l2^2 - 2m(1 - 1/omega) by simulated annealing
 * on edge flips; any flip creating a (CAP+1)-clique is rejected, keeping
 * the walk inside the omega <= CAP stratum. Exact omega via bitmask B&B;
 * top-2 eigenvalues via Householder tridiagonalization + Sturm bisection.
 * Initial states are random CAP-partite graphs (omega <= CAP guaranteed).
 * Any gap > 1e-7 is a counterexample candidate (re-verify with verify.py).
 *
 * Usage: ./anneal3 n cap restarts steps seed [density]
 * Build: gcc -O3 -march=native -o anneal3 anneal3.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#define MAXN 64
static int N, CAP;
static double A[MAXN][MAXN];
static uint64_t adj[MAXN];

static void tridiag(int n, double a[MAXN][MAXN], double *d, double *e) {
    for (int i = n - 1; i >= 1; i--) {
        int l = i - 1;
        double h = 0.0, scale = 0.0;
        if (l > 0) {
            for (int k = 0; k <= l; k++) scale += fabs(a[i][k]);
            if (scale == 0.0) e[i] = a[i][l];
            else {
                for (int k = 0; k <= l; k++) { a[i][k] /= scale; h += a[i][k] * a[i][k]; }
                double f = a[i][l];
                double g = (f >= 0.0) ? -sqrt(h) : sqrt(h);
                e[i] = scale * g; h -= f * g; a[i][l] = f - g; f = 0.0;
                for (int j = 0; j <= l; j++) {
                    g = 0.0;
                    for (int k = 0; k <= j; k++) g += a[j][k] * a[i][k];
                    for (int k = j + 1; k <= l; k++) g += a[k][j] * a[i][k];
                    e[j] = g / h; f += e[j] * a[i][j];
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
    for (int i = 0; i < n; i++) d[i] = a[i][i];
}

static int sturm_count(int n, const double *d, const double *e, double x) {
    int cnt = 0;
    double q = d[0] - x;
    if (q < 0) cnt++;
    for (int i = 1; i < n; i++) {
        double denom = (q == 0.0) ? 1e-300 : q;
        q = d[i] - x - e[i] * e[i] / denom;
        if (q < 0) cnt++;
    }
    return cnt;
}

static double kth_largest(int n, const double *d, const double *e, int k, double lo, double hi) {
    for (int it = 0; it < 55; it++) {
        double mid = 0.5 * (lo + hi);
        if (sturm_count(n, d, e, mid) >= n - k + 1) hi = mid;
        else lo = mid;
        if (hi - lo < 1e-11) break;
    }
    return 0.5 * (lo + hi);
}

static int best_clique;
static void expand(uint64_t cand, int size) {
    if (!cand) { if (size > best_clique) best_clique = size; return; }
    while (cand) {
        if (size + __builtin_popcountll(cand) <= best_clique) return;
        int v = __builtin_ctzll(cand);
        cand &= cand - 1;
        expand(cand & adj[v], size + 1);
    }
}
static int max_clique(void) {
    best_clique = 1;
    expand((N == 64) ? ~0ull : ((1ull << N) - 1), 0);
    return best_clique;
}

/* does adding edge (i,j) create a (CAP+1)-clique? check cliques through both */
static int creates_big_clique(int i, int j) {
    /* common neighborhood of i and j; a CAP-clique inside it + {i,j} would
       exceed CAP after the edge exists.  Edge already set when called. */
    best_clique = 2;
    uint64_t common = adj[i] & adj[j];
    /* find largest clique in common nbhd, extended by {i,j} */
    int save = best_clique;
    best_clique = 0;
    expand(common, 0);
    int c = best_clique;
    (void)save;
    return c + 2 > CAP;
}

static double gap_of(int *m_out, int *w_out, double *l1o, double *l2o) {
    static double T[MAXN][MAXN];
    memcpy(T, A, sizeof T);
    double d[MAXN], e[MAXN];
    tridiag(N, T, d, e);
    int m = 0;
    for (int i = 0; i < N; i++) m += __builtin_popcountll(adj[i]);
    m /= 2;
    if (m == 0) return -1e18;
    double bound = sqrt(2.0 * m) + 1.0;
    double l1 = kth_largest(N, d, e, 1, -bound, bound);
    double l2 = kth_largest(N, d, e, 2, -bound, l1 + 1e-9);
    int w = max_clique();
    double rhs = 2.0 * m * (1.0 - 1.0 / w);
    if (m_out) { *m_out = m; *w_out = w; *l1o = l1; *l2o = l2; }
    return l1 * l1 + l2 * l2 - rhs;
}

static unsigned long long rs;
static double rnd(void) {
    rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17;
    return (double)(rs >> 11) / 9007199254740992.0;
}

static void set_edge(int i, int j, int v) {
    A[i][j] = A[j][i] = v;
    if (v) { adj[i] |= 1ull << j; adj[j] |= 1ull << i; }
    else { adj[i] &= ~(1ull << j); adj[j] &= ~(1ull << i); }
}

static void print_g6(FILE *f) {
    fprintf(f, "%c", N + 63);
    int b = 0, acc = 0;
    for (int j = 1; j < N; j++)
        for (int i = 0; i < j; i++) {
            acc = (acc << 1) | (A[i][j] > 0.5 ? 1 : 0);
            if (++b == 6) { fputc(acc + 63, f); b = 0; acc = 0; }
        }
    if (b) { acc <<= (6 - b); fputc(acc + 63, f); }
    fputc('\n', f);
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: %s n cap restarts steps seed [density]\n", argv[0]); return 1; }
    N = atoi(argv[1]);
    CAP = atoi(argv[2]);
    int restarts = atoi(argv[3]);
    long steps = atol(argv[4]);
    rs = strtoull(argv[5], 0, 10) * 2654435761ull + 88172645463325252ull;
    double density = argc > 6 ? atof(argv[6]) : -1.0;

    double gbest = -1e18;
    for (int r = 0; r < restarts; r++) {
        double dens = density > 0 ? density : 0.3 + 0.65 * rnd();
        memset(A, 0, sizeof A);
        memset(adj, 0, sizeof adj);
        int part[MAXN];
        for (int i = 0; i < N; i++) part[i] = (int)(rnd() * CAP);
        for (int j = 1; j < N; j++)
            for (int i = 0; i < j; i++)
                if (part[i] != part[j] && rnd() < dens) set_edge(i, j, 1);
        double cur = gap_of(0, 0, 0, 0);
        double best = cur;
        double T0 = 0.3 * N, T1 = 1e-3;
        for (long s = 0; s < steps; s++) {
            double T = T0 * pow(T1 / T0, (double)s / steps);
            int i = (int)(rnd() * N), j = (int)(rnd() * N);
            if (i == j) continue;
            int old = A[i][j] > 0.5;
            set_edge(i, j, !old);
            if (!old && creates_big_clique(i, j)) { set_edge(i, j, old); continue; }
            double g = gap_of(0, 0, 0, 0);
            if (g >= cur || rnd() < exp((g - cur) / T)) cur = g;
            else set_edge(i, j, old);
            if (cur > best) {
                best = cur;
                if (best > 1e-7) {
                    int m, w; double l1, l2;
                    double gg = gap_of(&m, &w, &l1, &l2);
                    printf("CANDIDATE n=%d m=%d w=%d l1=%.10f l2=%.10f gap=%.6e g6=", N, m, w, l1, l2, gg);
                    print_g6(stdout);
                    fflush(stdout);
                }
            }
        }
        if (best > gbest) gbest = best;
        fprintf(stderr, "restart n=%d cap=%d r=%d dens=%.2f best_gap=%.6e\n", N, CAP, r, dens, best);
        fflush(stderr);
    }
    fprintf(stderr, "ANNEAL3-SUMMARY n=%d cap=%d restarts=%d steps=%ld best_gap=%.6e\n", N, CAP, restarts, steps, gbest);
    return 0;
}
